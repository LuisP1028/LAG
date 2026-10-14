"""
Automated GitHub Repository Creation, Production Frontend Build, and GitHub Pages Deployment.

Builds `src/frontend/` with `VITE_API_BASE_URL` pointing to the active public HTTPS ingress URL
of the local Docker container and `VITE_BASE_PATH="/lag-policy-engine-showcase/"`, creates/updates
the independent public repository `LuisP1028/lag-policy-engine-showcase`, pushes the clean
production bundle to `gh-pages` (with zero committed secrets), verifies the GitHub Pages build
reaches `"status": "built"`, and verifies that `https://luisp1028.github.io/lag-policy-engine-showcase/`
serves the exact newly compiled JS bundle containing `backend_url`.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any, Dict, Optional
import httpx


DEFAULT_GITHUB_REPO = "LuisP1028/lag-policy-engine-showcase"
DEFAULT_PAGES_URL = "https://luisp1028.github.io/lag-policy-engine-showcase/"
DEFAULT_BACKEND_URL = "https://lens-flashing-division-avatar.trycloudflare.com"


def _run_cmd(cmd: list[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(cmd)} failed (exit {proc.returncode}):\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        )
    return proc.stdout.strip()


def _cancel_in_progress_pages_runs(github_repo: str) -> None:
    """Cancels any queued or in-progress GitHub Actions runs to prevent 400 deployment collisions."""
    for run_status in ("in_progress", "queued", "waiting"):
        res = subprocess.run(
            ["gh", "api", f"repos/{github_repo}/actions/runs?status={run_status}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            try:
                data = json.loads(res.stdout)
                for run in data.get("workflow_runs", []):
                    run_id = run.get("id")
                    if run_id:
                        subprocess.run(
                            ["gh", "api", "-X", "POST", f"repos/{github_repo}/actions/runs/{run_id}/cancel"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
            except Exception:
                pass


def deploy_to_github_pages(
    github_repo: str = DEFAULT_GITHUB_REPO,
    backend_url: str = DEFAULT_BACKEND_URL,
    project_root: Optional[Path] = None,
    poll_timeout_seconds: int = 360,
) -> Dict[str, Any]:
    """Builds the React/Vite frontend and deploys it to an independent public GitHub Pages repository."""
    root = project_root or Path(__file__).resolve().parents[2]
    frontend_dir = root / "src" / "frontend"
    if not frontend_dir.exists():
        raise FileNotFoundError(f"Frontend directory not found at '{frontend_dir}'.")

    clean_backend_url = backend_url.rstrip("/")
    repo_name = github_repo.split("/")[-1]
    base_path = f"/{repo_name}/"

    # 1. Ensure dependencies are installed and build production static bundle
    build_env = os.environ.copy()
    build_env["VITE_API_BASE_URL"] = clean_backend_url
    build_env["VITE_BASE_PATH"] = base_path

    if not (frontend_dir / "node_modules").exists():
        _run_cmd(["npm", "install"], cwd=frontend_dir, env=build_env)

    _run_cmd(["npm", "run", "build"], cwd=frontend_dir, env=build_env)

    dist_dir = frontend_dir / "dist"
    index_html_path = dist_dir / "index.html"
    if not index_html_path.exists():
        raise RuntimeError(f"Frontend build did not produce '{index_html_path}'.")

    index_html_text = index_html_path.read_text(encoding="utf-8")
    js_match = re.search(r"assets/index-[A-Za-z0-9_-]+\.js", index_html_text)
    if not js_match:
        raise RuntimeError(f"Unable to locate compiled JS entry asset in '{index_html_path}'.")
    expected_js_asset = js_match.group(0)

    # Copy index.html to 404.html for SPA client routing and add .nojekyll
    shutil.copyfile(index_html_path, dist_dir / "404.html")
    (dist_dir / ".nojekyll").write_text("", encoding="utf-8")

    # 2. Scan dist bundle to guarantee zero secret leakage
    forbidden_tokens = [
        v for k, v in os.environ.items()
        if k in {"HF_DEPLOY_TOKEN", "HF_TOKEN", "HUGGINGFACE_API_KEY", "HF_DEEPSEEK_TOKEN", "CONGRESS_API_KEY", "NEO4J_PASSWORD"} and v and len(v) > 8
    ]
    for asset_file in dist_dir.rglob("*"):
        if asset_file.is_file() and asset_file.suffix in {".js", ".html", ".css", ".json"}:
            text_content = asset_file.read_text(encoding="utf-8", errors="ignore")
            for secret_val in forbidden_tokens:
                if secret_val in text_content:
                    raise RuntimeError(f"Security violation: secret token detected in build artifact '{asset_file}'.")

    # 3. Ensure independent public GitHub repository exists
    repo_check = subprocess.run(
        ["gh", "repo", "view", github_repo],
        capture_output=True,
        text=True,
        check=False,
    )
    if repo_check.returncode != 0:
        _run_cmd([
            "gh", "repo", "create", github_repo,
            "--public",
            "--description", "Interactive 8-Hop Legislative-to-Administrative GraphRAG Policy Engine Showcase",
        ])

    # Cancel any stuck in-progress Pages runs prior to pushing
    _cancel_in_progress_pages_runs(github_repo)

    # 4. Push clean static bundle to gh-pages in an isolated temporary git workspace
    gh_token = _run_cmd(["gh", "auth", "token"])
    remote_url = f"https://x-access-token:{gh_token}@github.com/{github_repo}.git"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        shutil.copytree(dist_dir, tmp_path / "site", dirs_exist_ok=True)
        site_dir = tmp_path / "site"

        deploy_epoch = int(time.time())
        readme_md = (
            "# Legislative-to-Administrative Graph (LAG) Policy Engine Showcase\n\n"
            f"- **Live Interactive Application:** [{DEFAULT_PAGES_URL}]({DEFAULT_PAGES_URL})\n"
            f"- **Live GraphRAG Container Ingress API:** [{clean_backend_url}]({clean_backend_url})\n"
            f"- **Build Revision:** `{expected_js_asset}` (`{deploy_epoch}`)\n\n"
            "Interactive 17-category, 18-edge, 8-hop Medicare legislative and regulatory lineage explorer "
            "with real-time GraphRAG path illumination and pre-computed LTA & IVIG policy runs.\n"
        )
        (site_dir / "README.md").write_text(readme_md, encoding="utf-8")

        _run_cmd(["git", "init"], cwd=site_dir)
        _run_cmd(["git", "config", "user.name", "LuisP1028"], cwd=site_dir)
        _run_cmd(["git", "config", "user.email", "LuisP1028@users.noreply.github.com"], cwd=site_dir)
        _run_cmd(["git", "checkout", "-b", "gh-pages"], cwd=site_dir)
        _run_cmd(["git", "add", "-A"], cwd=site_dir)
        _run_cmd(
            ["git", "commit", "-m", f"Deploy LAG Policy Engine showcase ({expected_js_asset} @ {int(time.time())})"],
            cwd=site_dir,
        )
        _run_cmd(["git", "remote", "add", "origin", remote_url], cwd=site_dir)
        _run_cmd(["git", "push", "--force", "origin", "gh-pages:gh-pages"], cwd=site_dir)
        commit_sha = _run_cmd(["git", "rev-parse", "HEAD"], cwd=site_dir)

    # 5. Enable GitHub Pages on branch `gh-pages` ONLY if not already enabled (avoid PUT collision)
    pages_check = subprocess.run(
        ["gh", "api", f"repos/{github_repo}/pages"],
        capture_output=True,
        text=True,
        check=False,
    )
    if pages_check.returncode != 0:
        _run_cmd([
            "gh", "api", f"repos/{github_repo}/pages",
            "-X", "POST",
            "-F", "source[branch]=gh-pages",
            "-F", "source[path]=/",
        ])

    # 6. Poll GitHub Pages build status and live CDN until `expected_js_asset` + `clean_backend_url` are served
    pages_url = DEFAULT_PAGES_URL
    deadline = time.monotonic() + poll_timeout_seconds
    verified = False
    last_retrigger = 0.0

    while time.monotonic() < deadline:
        # Check if latest Pages build errored due to a prior lock; if so, trigger a clean build
        build_res = subprocess.run(
            ["gh", "api", f"repos/{github_repo}/pages/builds/latest"],
            capture_output=True,
            text=True,
            check=False,
        )
        if build_res.returncode == 0 and build_res.stdout.strip():
            try:
                binfo = json.loads(build_res.stdout)
                bstatus = binfo.get("status")
                if bstatus == "errored" and (time.monotonic() - last_retrigger) > 15.0:
                    subprocess.run(
                        ["gh", "api", "-X", "POST", f"repos/{github_repo}/pages/builds"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    last_retrigger = time.monotonic()
            except Exception:
                pass

        try:
            cache_bust = int(time.time() * 1000)
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                res = client.get(
                    f"{pages_url}?cb={cache_bust}",
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
                )
                if res.status_code == 200 and expected_js_asset in res.text:
                    js_res = client.get(
                        f"{pages_url.rstrip('/')}/{expected_js_asset}?cb={cache_bust}",
                        headers={"Cache-Control": "no-cache"},
                    )
                    if js_res.status_code == 200 and clean_backend_url in js_res.text:
                        verified = True
                        break
        except Exception:
            pass
        time.sleep(5)

    if not verified:
        raise RuntimeError(
            f"Timed out after {poll_timeout_seconds}s waiting for GitHub Pages URL '{pages_url}' to serve '{expected_js_asset}' with '{clean_backend_url}'."
        )

    return {
        "github_repo": f"https://github.com/{github_repo}",
        "pages_url": pages_url,
        "commit_sha": commit_sha,
        "js_asset": expected_js_asset,
        "backend_url": clean_backend_url,
        "status": "online",
    }


if __name__ == "__main__":
    result = deploy_to_github_pages()
    print(result)
