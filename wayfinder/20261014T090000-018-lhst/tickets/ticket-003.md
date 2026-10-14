# Ticket 003: Frontend Dynamic HTTPS Endpoint Resolution (`?api_url=` & UI Control) and Host-Offline Fail-Fast Recovery

- **Ticket ID:** `ticket-003`
- **Title:** Frontend Dynamic HTTPS Endpoint Resolution (`?api_url=` & UI Control) and Host-Offline Fail-Fast Recovery
- **Type:** `wayfinder:task`
- **Status:** Resolved
- **Claimed by:** `antigravity-wayfinder`
- **Blocked By:** [`ticket-001.md`](ticket-001.md)
- **Governing Specification:** [`functional_specification_018.md`](file:///Users/diesel/desktop/lag/functional_specification_018.md) (§5.1, §5.2, §6.3)

---

## 1. Question

How must the React/TypeScript frontend (`src/frontend/src/utils/apiConfig.ts`, `src/frontend/src/components/FilterToolbar.tsx`, `src/frontend/src/App.tsx`) resolve the live backend HTTPS endpoint and handle host-offline or tunnel-rotation scenarios while strictly obeying fail-fast telemetry rules?

---

## 2. Resolution

1. **Dynamic Endpoint Resolution (`src/frontend/src/utils/apiConfig.ts`):**
   - Implemented `getApiBaseUrl()`, `setRuntimeApiBaseUrl(url)`, and `getRuntimeApiBaseUrl()` supporting:
     1. Runtime URL query parameter `?api_url=https://...` (or `?backend_url=https://...`) parsed from `window.location.search`;
     2. Interactive UI runtime endpoint override stored in memory and `sessionStorage`;
     3. Build-time `import.meta.env.VITE_API_BASE_URL` injected during GitHub Pages static bundle compilation;
     4. `DEFAULT_PUBLIC_INGRESS_URL` fallback when served from `*.github.io`;
     5. Relative `""` on local development (`localhost` / `127.0.0.1`).
2. **Interactive Endpoint Control & Offline Fail-Fast Recovery (`FilterToolbar.tsx` & `App.tsx`):**
   - Updated `SOURCE` selector label in `FilterToolbar.tsx` to `Live Container API (Public HTTPS)`.
   - Added an interactive `API URL` configuration popover/bar (`data-testid="api-url-config-btn"`, `data-testid="api-url-input"`, `data-testid="api-url-apply-btn"`) allowing operators or external visitors to inspect or update the active public HTTPS tunnel URL at runtime and immediately re-probe `/api/health` and reload topology.
   - Enhanced the fail-fast error banner (`data-testid="backend-error-banner"`) in `App.tsx` so that whenever the host machine or local container is unreachable, the status badge immediately transitions to `▲ EXECUTION ERROR` (zero silent fallback) and provides explicit user recovery buttons:
     - `Retry Live API` (`data-testid="retry-backend-btn"`)
     - `Load Pre-computed LTA Snapshot` (`data-testid="load-precomputed-lta-btn"`)
     - `Load Pre-computed IVIG Snapshot` (`data-testid="load-precomputed-ivig-btn"`)
