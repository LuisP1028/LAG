# Ticket 002: Zero-Cost Public HTTPS Ingress Tunnel Provisioning & Health/CORS Verification

- **Ticket ID:** `ticket-002`
- **Title:** Zero-Cost Public HTTPS Ingress Tunnel Provisioning & Health/CORS Verification
- **Type:** `wayfinder:task`
- **Status:** Resolved
- **Claimed by:** `antigravity-wayfinder`
- **Blocked By:** [`ticket-001.md`](ticket-001.md)
- **Governing Specification:** [`functional_specification_018.md`](file:///Users/diesel/desktop/lag/functional_specification_018.md) (§4.1, §4.2, §6.2)

---

## 1. Question

How must the local Docker container (`lag-policy-engine-local`) be exposed to the public internet over standard TLS (HTTPS port 443) at zero recurring cost so that any external browser visiting `https://luisp1028.github.io/lag-policy-engine-showcase/` can execute cross-origin `fetch` calls without Mixed-Content blocks, VPN clients, or custom certificates?

---

## 2. Resolution

1. **Docker Network & Companion Cloudflare Quick Tunnel (`src/deploy/deploy_local_container.py` & `docker-compose.yml`):**
   - Created an isolated Docker bridge network `lag-net`.
   - Attached `lag-policy-engine-local` (listening on port `7860`, also mapped to `127.0.0.1:7860` on the host) to `lag-net`.
   - Launched companion container `lag-policy-engine-tunnel` (`cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://lag-policy-engine-local:7860`) on `lag-net`.
   - Extracted the generated `https://<subdomain>.trycloudflare.com` public HTTPS ingress URL deterministically from `docker logs lag-policy-engine-tunnel` and verified public DNS + HTTPS readiness across `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/PLAW-117-328`, `/api/graphrag/query`, and `OPTIONS` preflight with `Origin: https://luisp1028.github.io`.
