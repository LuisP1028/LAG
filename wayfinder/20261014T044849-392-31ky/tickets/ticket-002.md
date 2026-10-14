# Ticket 002: Hugging Face Space Containerization, Secret Injection & Live Runtime Provisioning (`ChoppedCheese/lag-policy-engine`)

- **Ticket ID:** `ticket-002`
- **Title:** Hugging Face Space Containerization, Secret Injection & Live Runtime Provisioning (`ChoppedCheese/lag-policy-engine`)
- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked By:** `ticket-001`
- **Governing Specification:** `functional_specification_016.md` (§1, §4.1 Engine API & Endpoints, §5.1.2 Hugging Face Runtime Availability)

---

## 1. Decision Question

How must the Backend Engine Runtime Layer be packaged, configured with secrets, deployed to Hugging Face Spaces, and verified over HTTPS so that the live Space exposes all required endpoints without baking any sensitive credentials into the `Dockerfile` or repository history?

---

## 2. Empirical Datasource & Platform Qualification

1. **Authenticated Hugging Face Account (`mcp_huggingface_hf_whoami`):**
   - User namespace: `ChoppedCheese` (`https://huggingface.co/ChoppedCheese`, Account ID: `662eff76b10f82aa4fb0d8ce`).
   - Token permissions verified: `repo.write`, `repo.content.read`, `repo.contribute.write`, `inference.serverless.write`.
2. **Target Space Identifier & Direct Runtime URL:**
   - Repository ID: `ChoppedCheese/lag-policy-engine` (`repo_type="space"`, `space_sdk="docker"`, public).
   - Space Hub URL: `https://huggingface.co/spaces/ChoppedCheese/lag-policy-engine`
   - Direct HTTPS Runtime Origin: `https://choppedcheese-lag-policy-engine.hf.space` (verified empirically against `ChoppedCheese`'s active Docker Spaces returning `HTTP/2 200`).
3. **Secret Management & Configuration Integrity (§4.1 Constraints):**
   - Local `.env` at `/Users/diesel/Desktop/LAG/.env` holds `HF_TOKEN`, `HUGGINGFACE_API_KEY`, and `CONGRESS_API_KEY`.
   - These secrets must NEVER be written into `Dockerfile`, `README.md`, or committed source files.
   - Instead, the deployment script (`src/deploy/deploy_hf_space.py`) injects `HF_TOKEN`, `HUGGINGFACE_API_KEY`, and `CONGRESS_API_KEY` directly into the Hugging Face Space Secrets API (`add_space_secret` via `huggingface_hub.HfApi` or `POST https://huggingface.co/api/spaces/ChoppedCheese/lag-policy-engine/secrets`).

---

## 3. Locked Architectural Decision

### 3.1 Containerization Artifacts (`Dockerfile` & `requirements.txt`)
1. **Create `requirements.txt` at repository root:**
   ```text
   fastapi>=0.110.0
   uvicorn[standard]>=0.27.0
   pydantic>=2.6.0
   python-dotenv>=1.0.1
   httpx>=0.27.0
   neo4j>=5.18.0
   ```
2. **Create `Dockerfile` at repository root (Hugging Face Spaces Docker SDK compliant):**
   - Base image: `python:3.11-slim`
   - Creates non-root user `user` with UID `1000` (`useradd -m -u 1000 user`) as mandated by Hugging Face Spaces Docker security policy.
   - Installs `requirements.txt` with `--no-cache-dir`.
   - Copies only backend code and pre-computed graph exports:
     - `src/__init__.py` (if present), `src/api/`, `src/graph/`, `src/graphrag/`
     - `exports/lta_knowledge_graph.json`, `exports/ivig_knowledge_graph.json`
     - `LANGUAGE.md`
   - Sets non-sensitive runtime environment defaults:
     - `ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH`
     - `ENV PYTHONPATH=/app`
     - `ENV PORT=7860`
     - `ENV API_PORT=7860`
     - `ENV NEO4J_URI="embedded://exports/lta_knowledge_graph.json"`
   - Exposes `7860` and starts `uvicorn src.api.server:app --host 0.0.0.0 --port 7860`.
   - Zero API keys or credentials appear anywhere in `Dockerfile`.

### 3.2 Automated Hugging Face Space Provisioning Module (`src/deploy/deploy_hf_space.py`)
Create `src/deploy/__init__.py` and `src/deploy/deploy_hf_space.py` with function `deploy_backend_to_hf_space(space_id: str = "ChoppedCheese/lag-policy-engine", wait_for_running: bool = True) -> Dict[str, Any]`:
1. **Token Resolution:**
   - Resolves Hugging Face Hub write token from environment (`HF_TOKEN` or `~/.cache/huggingface/token` or `/Users/diesel/Desktop/LAG/.env` loaded strictly in-memory via `dotenv_values`). Fails fast with `RuntimeError` if no token is available.
2. **Space Repository Creation:**
   - Calls Hugging Face Hub REST API (`POST https://huggingface.co/api/repos/create` with `{"type": "space", "name": "lag-policy-engine", "sdk": "docker", "private": false}` or `huggingface_hub.HfApi.create_repo(repo_id=space_id, repo_type="space", space_sdk="docker", private=False, exist_ok=True)`).
3. **Secret Injection via Hugging Face API (Zero Disk Secrets):**
   - Reads `HF_TOKEN`, `HUGGINGFACE_API_KEY`, and `CONGRESS_API_KEY` in-memory from environment / `/Users/diesel/Desktop/LAG/.env`.
   - Calls `POST https://huggingface.co/api/spaces/ChoppedCheese/lag-policy-engine/secrets` (or `HfApi.add_space_secret`) for each non-empty secret key (`HF_TOKEN`, `HUGGINGFACE_API_KEY`, `CONGRESS_API_KEY`).
4. **Staging & Git/Commit Upload to Space:**
   - Stages a clean bundle containing:
     - `README.md` with Hugging Face Space YAML frontmatter:
       ```yaml
       ---
       title: LAG Policy GraphRAG Engine API
       emoji: ⚖️
       colorFrom: indigo
       colorTo: amber
       sdk: docker
       app_port: 7860
       pinned: false
       ---
       ```
     - `Dockerfile`
     - `requirements.txt`
     - `src/api/`, `src/graph/`, `src/graphrag/`
     - `exports/lta_knowledge_graph.json`, `exports/ivig_knowledge_graph.json`
   - Scans staged files to enforce that zero `.env` files or secret token literals (`gho_`, `hf_`) exist in the staged tree (fail-fast `RuntimeError` on violation).
   - Pushes the staged bundle to `https://huggingface.co/spaces/ChoppedCheese/lag-policy-engine` (`main` branch).
5. **Readiness Verification:**
   - Polls `https://choppedcheese-lag-policy-engine.hf.space/api/health` until HTTP 200 OK with `{"status": "ok"}` is returned (with configurable timeout), returning deployment metadata (`space_id`, `space_url`, `runtime_url`, `health_status`).

---

## 4. Verification Criteria

- `Dockerfile` and `requirements.txt` exist and contain zero secret values.
- `https://huggingface.co/spaces/ChoppedCheese/lag-policy-engine` is created and configured with `sdk: docker` and `app_port: 7860`.
- `https://choppedcheese-lag-policy-engine.hf.space/api/health`, `/api/graph/topology`, `/api/entities/POLICY-LTA`, and `/api/graphrag/query` respond over HTTPS with CORS headers permitting `https://luisp1028.github.io`.
