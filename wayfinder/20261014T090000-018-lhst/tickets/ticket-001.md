# Ticket 001: Self-Hosted Local Docker Container Runtime, Runtime Secret Injection & Exact CORS Echo Policy

- **Ticket ID:** `ticket-001`
- **Title:** Self-Hosted Local Docker Container Runtime, Runtime Secret Injection & Exact CORS Echo Policy
- **Type:** `wayfinder:task`
- **Status:** Resolved
- **Claimed by:** `antigravity-wayfinder`
- **Blocked By:** None
- **Governing Specification:** [`functional_specification_018.md`](file:///Users/diesel/desktop/lag/functional_specification_018.md) (§3.1, §3.2, §4.2, §6.1)

---

## 1. Question

How must the containerized FastAPI backend (`Dockerfile`, `docker-compose.yml`, `src/api/server.py`, and `src/deploy/deploy_local_container.py`) be configured and launched so that:
1. It executes inside an isolated local Docker container (`lag-policy-engine-local`) on the operator's host machine at zero recurring cost;
2. It loads the complete 8-hop knowledge graph (`3,875` nodes across 17 categories, `7,593` edges across 18 relationship types) via `NEO4J_URI="embedded://exports/lta_knowledge_graph.json"` without requiring an external database daemon inside the container;
3. It injects `HF_TOKEN`, `HUGGINGFACE_API_KEY` (preserving the `ACT-KG-` token for live GraphRAG LLM synthesis), and `CONGRESS_API_KEY` exclusively at container startup with zero secrets in image layers or tracked files; and
4. Its `CORSMiddleware` returns `access-control-allow-origin: https://luisp1028.github.io` on preflight `OPTIONS` requests originating from `https://luisp1028.github.io`?

---

## 2. Resolution

1. **Exact CORS Origin Echo (`src/api/server.py`):**
   - Removed `"*"` from `allow_origins` in `CORSMiddleware` (which caused Starlette to emit `access-control-allow-origin: *` instead of echoing the requesting origin).
   - Configured explicit `allow_origins` (`https://luisp1028.github.io`, `http://localhost:3000`, `http://localhost:5173`, `http://127.0.0.1:3000`, `http://127.0.0.1:5173`) and `allow_origin_regex=r"https://.*\.github\.io|https://.*\.trycloudflare\.com|https://.*\.hf\.space|http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?"`, `allow_methods=["GET", "POST", "OPTIONS"]`, `allow_headers=["Content-Type", "Authorization", "*"]`.
2. **Self-Contained Local Container Runtime (`Dockerfile`, `docker-compose.yml`, `src/deploy/deploy_local_container.py`):**
   - Built `lag-policy-engine:local` from `Dockerfile` (Python 3.11-slim, non-root user, port `7860`, `NEO4J_URI="embedded://exports/lta_knowledge_graph.json"`).
   - Passed `HF_TOKEN`, `HUGGINGFACE_API_KEY`, and `CONGRESS_API_KEY` solely via runtime environment variables read from `.env` at container launch while explicitly setting `NEO4J_URI="embedded://exports/lta_knowledge_graph.json"` so the container never attempts to connect to the host's `bolt://localhost:7687` loopback.
