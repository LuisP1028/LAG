# Ticket 005: Independent GitHub Repository Creation & GitHub Pages Static Deployment (`LuisP1028/lag-policy-engine-showcase`)

- **Ticket ID:** `ticket-005`
- **Title:** Independent GitHub Repository Creation & GitHub Pages Static Deployment (`LuisP1028/lag-policy-engine-showcase`)
- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked By:** `ticket-002`, `ticket-003`, `ticket-004`
- **Governing Specification:** `functional_specification_016.md` (§2.1 Independent GitHub Repository Creation, §5.1.1 GitHub Pages Accessibility, §5.1.3 Interactive Showcase Verification)

---

## 1. Decision Question

How must the standalone frontend showcase repository be isolated, built, verified free of sensitive credentials, pushed to an independent GitHub repository, and published via GitHub Pages so that any external user visiting `https://luisp1028.github.io/lag-policy-engine-showcase/` over HTTPS can interact with the full 8-hop legislative/healthcare engine connected to the live Hugging Face Space runtime (`https://choppedcheese-lag-policy-engine.hf.space`)?

---

## 2. Empirical Platform & Repository Qualification

1. **Authenticated GitHub Account (`gh auth status`):**
   - Account: `LuisP1028` (`https://github.com/LuisP1028`).
   - Token scopes verified: `'gist'`, `'read:org'`, `'repo'`, `'workflow'`.
2. **Dedicated Showcase Repository Identifier & Public URL:**
   - Repository Name: `LuisP1028/lag-policy-engine-showcase` (separate from root development repo `LuisP1028/LAG`).
   - GitHub Repository URL: `https://github.com/LuisP1028/lag-policy-engine-showcase`
   - Public GitHub Pages HTTPS URL: `https://luisp1028.github.io/lag-policy-engine-showcase/`
3. **Static Asset Base Path Alignment (`src/frontend/vite.config.ts`):**
   - Because GitHub Pages project repositories serve assets under `/<repo-name>/` (`/lag-policy-engine-showcase/`), `src/frontend/vite.config.ts` must configure `base: process.env.VITE_BASE_PATH || './'` so all compiled JS/CSS bundles and static assets resolve relatively on both `https://luisp1028.github.io/lag-policy-engine-showcase/` and `http://localhost:5173/`.

---

## 3. Locked Architectural Decision

### 3.1 Vite Build Configuration (`src/frontend/vite.config.ts`)
Update `src/frontend/vite.config.ts` (lines 5–16) to set `base: process.env.VITE_BASE_PATH || './'`:
```typescript
export default defineConfig({
  base: process.env.VITE_BASE_PATH || './',
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 3.2 Automated GitHub Repository & GitHub Pages Deployment Module (`src/deploy/deploy_github_pages.py`)
Create `src/deploy/deploy_github_pages.py` exposing `deploy_frontend_to_github_pages(repo_full_name: str = "LuisP1028/lag-policy-engine-showcase", backend_url: str = "https://choppedcheese-lag-policy-engine.hf.space") -> Dict[str, Any]`:
1. **Frontend Production Build:**
   - Ensures `src/frontend/public/runs/lta_knowledge_graph.json` and `src/frontend/public/runs/ivig_knowledge_graph.json` are synced from `exports/`.
   - Runs `npm run build` in `src/frontend` with `VITE_API_BASE_URL=https://choppedcheese-lag-policy-engine.hf.space` and `VITE_BASE_PATH=./`.
   - Verifies that `src/frontend/dist/index.html`, compiled JS/CSS bundles in `src/frontend/dist/assets/`, and `src/frontend/dist/runs/lta_knowledge_graph.json` exist.
2. **Secret & Credential Sanitization Gate (§2.1 Constraints):**
   - Scans every file to be committed to `LuisP1028/lag-policy-engine-showcase` (both source and `dist/`) to verify:
     - Zero `.env` files exist.
     - Zero secret token patterns (`gho_`, `ghp_`, `hf_`, private Neo4j passwords, or values from `/Users/diesel/Desktop/LAG/.env`) appear anywhere in any file.
   - Raises `RuntimeError` immediately if any forbidden pattern is detected.
3. **Independent Git Repository Initialization & Push (`LuisP1028/lag-policy-engine-showcase`):**
   - Creates `LuisP1028/lag-policy-engine-showcase` via `gh repo create LuisP1028/lag-policy-engine-showcase --public` (if not already created).
   - Initializes a standalone Git repository in an isolated temporary staging directory with its own clean Git history:
     - Populates `main` branch with the standalone frontend source (`package.json`, `vite.config.ts`, `tsconfig*.json`, `index.html`, `public/`, `src/`, `README.md`, `.nojekyll`, `.github/workflows/deploy-pages.yml`) plus the compiled static site at the repository root (and on `gh-pages` branch with `dist/*` + `.nojekyll` + `404.html` SPA fallback) so GitHub Pages serves `index.html` directly from the branch root.
     - Pushes both `main` and `gh-pages` branches to `https://github.com/LuisP1028/lag-policy-engine-showcase.git`.
4. **GitHub Pages Activation & Live HTTPS Verification:**
   - Enables GitHub Pages on `LuisP1028/lag-policy-engine-showcase` via GitHub REST API (`gh api repos/LuisP1028/lag-policy-engine-showcase/pages -X POST -f source[branch]=gh-pages -f source[path]=/` or `PUT` if already enabled).
   - Polls `https://luisp1028.github.io/lag-policy-engine-showcase/` until HTTP 200 OK is returned and verifies that the served HTML references the compiled interactive showcase bundle.

### 3.3 Unified Dual-Platform Deployment & Verification Orchestrator (`src/deploy/deploy_all.py`)
Create `src/deploy/deploy_all.py` that orchestrates:
1. `deploy_backend_to_hf_space("ChoppedCheese/lag-policy-engine")`
2. `deploy_frontend_to_github_pages("LuisP1028/lag-policy-engine-showcase", backend_url="https://choppedcheese-lag-policy-engine.hf.space")`
3. End-to-end live verification across both public HTTPS URLs (`https://luisp1028.github.io/lag-policy-engine-showcase/` and `https://choppedcheese-lag-policy-engine.hf.space/api/health`, `/api/graph/topology`, `/api/entities/STAT-117-328-SEC-4133`, `/api/graphrag/query`), writing the verified deployment manifest to `src/deploy/deployment_manifest.json`.

---

## 4. Verification Criteria

- `https://github.com/LuisP1028/lag-policy-engine-showcase` exists as an independent public GitHub repository with zero committed secrets.
- `https://luisp1028.github.io/lag-policy-engine-showcase/` returns HTTP 200 OK over HTTPS without authentication and serves the compiled interactive showcase.
- `https://choppedcheese-lag-policy-engine.hf.space/api/health`, `/api/graph/topology?state_filter=GU`, `/api/entities/STAT-117-328-SEC-4133`, and `/api/graphrag/query` return HTTP 200 OK over HTTPS with CORS headers allowing `https://luisp1028.github.io`.
