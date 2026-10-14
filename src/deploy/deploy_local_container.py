"""
Self-Hosted Local Docker Container Runtime & Public HTTPS Tunnel Provisioner.

Implements `functional_specification_018.md` §3 and §4:
1. Builds `lag-policy-engine:local` from `Dockerfile` with zero baked-in secrets.
2. Launches `lag-policy-engine-local` on local Docker network `lag-net` (port 7860),
   injecting `HF_TOKEN`, `HUGGINGFACE_API_KEY` (preserving the `ACT-KG-` token for
   LLM synthesis), and `CONGRESS_API_KEY` exclusively at runtime from `.env`, with
   `NEO4J_URI="embedded://exports/lta_knowledge_graph.json"`.
3. Verifies local readiness via `GET http://127.0.0.1:7860/api/health`.
4. Provisions `lag-policy-engine-tunnel` (`cloudflare/cloudflared:latest`) on `lag-net`
   to expose a zero-cost public HTTPS ingress URL (`https://*.trycloudflare.com`) over
   standard TLS (port 443) and verifies public HTTPS reachability.
"""

from __future__ import annotations
import os
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Dict, Optional
from dotenv import dotenv_values
import httpx


IMAGE_TAG = "lag-policy-engine:local"
BACKEND_CONTAINER = "lag-policy-engine-local"
TUNNEL_CONTAINER = "lag-policy-engine-tunnel"
DOCKER_NETWORK = "lag-net"
LOCAL_HEALTH_URL = "http://127.0.0.1:7860/api/health"
TRYCLOUDFLARE_REGEX = re.compile(r"https://[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.trycloudflare\.com")


def _run_cmd(cmd: list[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(cmd)} failed (exit {proc.returncode}):\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        )
    return proc


def _verify_zero_hardcoded_secrets(root: Path, env_vars: Dict[str, Optional[str]]) -> None:
    """Fail-fast check guaranteeing neither Dockerfile nor docker-compose.yml contains secret values."""
    secret_values = [
        v for k, v in env_vars.items()
        if k in {"HF_TOKEN", "HUGGINGFACE_API_KEY", "HF_DEPLOY_TOKEN", "HF_DEEPSEEK_TOKEN", "CONGRESS_API_KEY", "NEO4J_PASSWORD"}
        and v and len(v) >= 6
    ]
    for rel_file in ("Dockerfile", "docker-compose.yml"):
        fpath = root / rel_file
        if not fpath.exists():
            continue
        content = fpath.read_text(encoding="utf-8")
        for secret in secret_values:
            if secret and secret in content:
                raise RuntimeError(f"Secret isolation violation: credential detected in '{rel_file}'.")


def _extract_existing_tunnel_url() -> Optional[str]:
    """Checks if `lag-policy-engine-tunnel` is already running and reachable over public HTTPS."""
    insp = _run_cmd(["docker", "inspect", "-f", "{{.State.Running}}", TUNNEL_CONTAINER], check=False)
    if insp.returncode != 0 or insp.stdout.strip() != "true":
        return None
    logs = _run_cmd(["docker", "logs", TUNNEL_CONTAINER], check=False)
    combined = f"{logs.stdout}\n{logs.stderr}"
    matches = TRYCLOUDFLARE_REGEX.findall(combined)
    if not matches:
        return None
    candidate_url = matches[-1].rstrip("/")
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            res = client.get(f"{candidate_url}/api/health")
            if res.status_code == 200 and res.json().get("neo4j_connected") is True:
                return candidate_url
    except Exception:
        pass
    return None


def deploy_local_container_with_https_ingress(
    project_root: Optional[Path] = None,
    force_new_tunnel: bool = False,
    poll_timeout_seconds: int = 120,
) -> Dict[str, Any]:
    """Builds and starts the local backend container and public HTTPS ingress tunnel."""
    root = project_root or Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f"Required runtime environment file not found at '{env_path}'.")

    env_vars = dotenv_values(env_path)
    hf_token = env_vars.get("HF_TOKEN") or env_vars.get("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    hf_deepseek_token = env_vars.get("HF_DEEPSEEK_TOKEN") or os.getenv("HF_DEEPSEEK_TOKEN") or ""
    congress_key = env_vars.get("CONGRESS_API_KEY") or os.getenv("CONGRESS_API_KEY") or ""
    if not hf_token:
        raise RuntimeError("Missing HF_TOKEN / HUGGINGFACE_API_KEY in .env for GraphRAG LLM synthesis.")

    _verify_zero_hardcoded_secrets(root, env_vars)

    # 1. Ensure Docker network `lag-net` exists
    net_check = _run_cmd(["docker", "network", "inspect", DOCKER_NETWORK], check=False)
    if net_check.returncode != 0:
        _run_cmd(["docker", "network", "create", DOCKER_NETWORK], cwd=root)

    # 2. Build local container image `lag-policy-engine:local`
    print(f"[Local Container] Building image {IMAGE_TAG}...", flush=True)
    _run_cmd(["docker", "build", "-t", IMAGE_TAG, "."], cwd=root)

    # 3. Start (or recreate) `lag-policy-engine-local` with runtime secret injection
    _run_cmd(["docker", "rm", "-f", BACKEND_CONTAINER], check=False)
    print(f"[Local Container] Starting container {BACKEND_CONTAINER} on {DOCKER_NETWORK}...", flush=True)
    _run_cmd(
        [
            "docker", "run", "-d",
            "--name", BACKEND_CONTAINER,
            "--restart", "unless-stopped",
            "--network", DOCKER_NETWORK,
            "-p", "127.0.0.1:7860:7860",
            "-e", f"HF_TOKEN={hf_token}",
            "-e", f"HUGGINGFACE_API_KEY={hf_token}",
            "-e", f"HF_DEEPSEEK_TOKEN={hf_deepseek_token}",
            "-e", f"CONGRESS_API_KEY={congress_key}",
            "-e", "NEO4J_URI=embedded://exports/lta_knowledge_graph.json",
            "-e", "PORT=7860",
            "-e", "API_PORT=7860",
            IMAGE_TAG,
        ],
        cwd=root,
    )

    # 4. Poll local container health endpoint `http://127.0.0.1:7860/api/health`
    local_deadline = time.monotonic() + 45
    local_health: Optional[Dict[str, Any]] = None
    while time.monotonic() < local_deadline:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(LOCAL_HEALTH_URL)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "ok" and data.get("neo4j_connected") is True:
                        local_health = data
                        print(f"[Local Container] {LOCAL_HEALTH_URL} -> 200 OK", flush=True)
                        break
        except Exception:
            pass
        time.sleep(1.5)

    if not local_health:
        logs = _run_cmd(["docker", "logs", BACKEND_CONTAINER], check=False)
        raise RuntimeError(
            f"Local container '{BACKEND_CONTAINER}' failed health check at {LOCAL_HEALTH_URL}.\nLogs:\n{logs.stdout}\n{logs.stderr}"
        )

    # 5. Reuse healthy public HTTPS tunnel if active, or start a fresh `cloudflare/cloudflared:latest` container
    public_https_url = None if force_new_tunnel else _extract_existing_tunnel_url()
    if not public_https_url:
        _run_cmd(["docker", "rm", "-f", TUNNEL_CONTAINER], check=False)
        print(f"[HTTPS Tunnel] Starting {TUNNEL_CONTAINER} (cloudflare/cloudflared:latest)...", flush=True)
        _run_cmd(
            [
                "docker", "run", "-d",
                "--name", TUNNEL_CONTAINER,
                "--restart", "unless-stopped",
                "--network", DOCKER_NETWORK,
                "cloudflare/cloudflared:latest",
                "tunnel", "--no-autoupdate", "--url", f"http://{BACKEND_CONTAINER}:7860",
            ],
            cwd=root,
        )

        tunnel_deadline = time.monotonic() + 60
        while time.monotonic() < tunnel_deadline:
            logs = _run_cmd(["docker", "logs", TUNNEL_CONTAINER], check=False)
            combined = f"{logs.stdout}\n{logs.stderr}"
            matches = TRYCLOUDFLARE_REGEX.findall(combined)
            if matches:
                public_https_url = matches[-1].rstrip("/")
                print(f"[HTTPS Tunnel] Assigned URL: {public_https_url}", flush=True)
                break
            time.sleep(2.0)

    if not public_https_url:
        logs = _run_cmd(["docker", "logs", TUNNEL_CONTAINER], check=False)
        raise RuntimeError(
            f"Failed to obtain public HTTPS ingress URL from '{TUNNEL_CONTAINER}'.\nLogs:\n{logs.stdout}\n{logs.stderr}"
        )

    # 6. Poll public HTTPS ingress URL over the internet until `/api/health` returns 200 OK
    public_deadline = time.monotonic() + poll_timeout_seconds
    public_health: Optional[Dict[str, Any]] = None
    while time.monotonic() < public_deadline:
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(f"{public_https_url}/api/health")
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "ok" and data.get("neo4j_connected") is True:
                        public_health = data
                        print(f"[HTTPS Tunnel] {public_https_url}/api/health -> 200 OK", flush=True)
                        break
        except Exception:
            pass
        time.sleep(2.5)

    if not public_health:
        raise RuntimeError(
            f"Timed out after {poll_timeout_seconds}s waiting for public HTTPS ingress '{public_https_url}/api/health'."
        )

    return {
        "image_tag": IMAGE_TAG,
        "backend_container": BACKEND_CONTAINER,
        "tunnel_container": TUNNEL_CONTAINER,
        "docker_network": DOCKER_NETWORK,
        "local_url": "http://127.0.0.1:7860",
        "public_https_url": public_https_url,
        "health": public_health,
    }


if __name__ == "__main__":
    import json
    info = deploy_local_container_with_https_ingress()
    print(json.dumps(info, indent=2))
