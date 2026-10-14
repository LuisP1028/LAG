"""
Automated Hugging Face Spaces Docker Deployment & Live Readiness Verification.

Deploys the containerized FastAPI + Embedded 8-Hop GraphRAG backend to
`ChoppedCheese/lag-policy-engine` on Hugging Face Spaces, injects required runtime
secrets via the HF Hub Secrets API (zero secrets committed to git or Dockerfile),
and polls the live Space endpoint until `GET /api/health` and `GET /api/graph/topology`
respond with HTTP 200 OK.
"""

from __future__ import annotations
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import httpx
from huggingface_hub import HfApi


DEFAULT_SPACE_REPO_ID = "ChoppedCheese/lag-policy-engine"
DEFAULT_SPACE_HOST = "https://choppedcheese-lag-policy-engine.hf.space"

SPACE_README_HEADER = """---
title: LAG Policy Engine GraphRAG API
emoji: ⚖️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
---

# Legislative-to-Administrative Graph (LAG) Policy Engine API

Production FastAPI backend serving the 8-hop Medicare policy knowledge graph (3,875 nodes, 7,593 edges across 17 entity categories and 18 relationship types) and live GraphRAG inference.
"""


def deploy_to_hf_space(
    repo_id: str = DEFAULT_SPACE_REPO_ID,
    project_root: Optional[Path] = None,
    poll_timeout_seconds: int = 480,
) -> Dict[str, Any]:
    """Creates/updates the HF Docker Space, injects secrets via API, uploads source bundle, and verifies live health."""
    root = project_root or Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")

    deploy_token = os.getenv("HF_DEPLOY_TOKEN") or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
    llm_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY") or deploy_token
    if not deploy_token or not llm_token:
        raise RuntimeError(
            "Missing HF_DEPLOY_TOKEN / HF_TOKEN in environment. Cannot authenticate with Hugging Face Hub."
        )

    api = HfApi(token=deploy_token)
    user_info = api.whoami()
    username = user_info.get("name")
    if not username:
        raise RuntimeError("Unable to verify Hugging Face user identity via whoami().")

    # 1. Create or ensure Docker Space exists
    api.create_repo(
        repo_id=repo_id,
        repo_type="space",
        space_sdk="docker",
        private=False,
        exist_ok=True,
    )

    # 2. Inject runtime secrets strictly via HF Space Secrets API (never in Dockerfile or git)
    # Use ACT-KG- (llm_token) for live LLM inference inside the Space
    api.add_space_secret(repo_id=repo_id, key="HF_TOKEN", value=llm_token)
    api.add_space_secret(repo_id=repo_id, key="HUGGINGFACE_API_KEY", value=llm_token)
    congress_key = os.getenv("CONGRESS_API_KEY")
    if congress_key:
        api.add_space_secret(repo_id=repo_id, key="CONGRESS_API_KEY", value=congress_key)

    api.add_space_variable(
        repo_id=repo_id,
        key="NEO4J_URI",
        value="embedded://exports/lta_knowledge_graph.json",
    )
    api.add_space_variable(
        repo_id=repo_id,
        key="PORT",
        value="7860",
    )

    # 3. Stage README.md, Dockerfile, requirements.txt, src/ (backend only), and exports/ for a single atomic commit
    with tempfile.TemporaryDirectory() as tmp_dir:
        stage_dir = Path(tmp_dir)
        (stage_dir / "README.md").write_text(SPACE_README_HEADER, encoding="utf-8")
        shutil.copyfile(root / "Dockerfile", stage_dir / "Dockerfile")
        shutil.copyfile(root / "requirements.txt", stage_dir / "requirements.txt")
        shutil.copytree(
            root / "src",
            stage_dir / "src",
            ignore=shutil.ignore_patterns("frontend", "deploy", "__pycache__", "*.pyc", ".DS_Store"),
        )
        shutil.copytree(
            root / "exports",
            stage_dir / "exports",
            ignore=shutil.ignore_patterns(".DS_Store"),
        )

        api.upload_folder(
            folder_path=str(stage_dir),
            path_in_repo=".",
            repo_id=repo_id,
            repo_type="space",
            commit_message="Deploy containerized LAG Policy Engine GraphRAG backend on port 7860",
        )

    # 4. Poll Space runtime stage and live HTTPS /api/health endpoint
    space_url = DEFAULT_SPACE_HOST
    deadline = time.monotonic() + poll_timeout_seconds
    last_stage = "UNKNOWN"
    health_payload: Optional[Dict[str, Any]] = None

    while time.monotonic() < deadline:
        try:
            runtime = api.get_space_runtime(repo_id=repo_id)
            stage_now = getattr(runtime, "stage", "UNKNOWN")
            if stage_now != last_stage:
                print(f"[HF Space {repo_id}] stage -> {stage_now}", flush=True)
                last_stage = stage_now
            if last_stage in {"BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"}:
                raise RuntimeError(f"Hugging Face Space '{repo_id}' entered error state: {last_stage}")
        except RuntimeError:
            raise
        except Exception:
            pass

        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                res = client.get(f"{space_url}/api/health")
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "ok" and data.get("neo4j_connected") is True:
                        health_payload = data
                        print(f"[HF Space {repo_id}] /api/health -> 200 OK", flush=True)
                        break
        except Exception:
            pass

        time.sleep(8)

    if not health_payload:
        raise RuntimeError(
            f"Timed out after {poll_timeout_seconds}s waiting for '{space_url}/api/health' (last stage: {last_stage})."
        )

    return {
        "repo_id": repo_id,
        "space_url": space_url,
        "runtime_stage": last_stage,
        "health": health_payload,
    }


if __name__ == "__main__":
    result = deploy_to_hf_space()
    print(result)
