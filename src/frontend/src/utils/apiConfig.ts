/**
 * API Base URL and Bundled Pre-Computed Policy Run Artifact Resolver.
 *
 * Implements `functional_specification_018.md` §5.1:
 * 1. Resolves runtime `?api_url=https://...` (or `?backend_url=https://...`) URL query parameter
 *    so ephemeral public HTTPS tunnel URLs can be connected immediately on GitHub Pages.
 * 2. Resolves interactive UI runtime endpoint override (`setRuntimeApiBaseUrl`).
 * 3. Resolves build-time `VITE_API_BASE_URL` pointing to the active public HTTPS ingress tunnel
 *    of the operator's local Docker container.
 * 4. Falls back to `DEFAULT_PUBLIC_INGRESS_URL` on `*.github.io`, or `""` on local dev (`localhost`).
 */

export const DEFAULT_PUBLIC_INGRESS_URL = 'https://evident-consolidation-dod-seo.trycloudflare.com';
export const DEFAULT_HF_SPACE_URL = DEFAULT_PUBLIC_INGRESS_URL;

const STORAGE_KEY = 'lag_runtime_api_url';
let runtimeApiUrlOverride: string | null = null;

function normalizeApiUrl(raw: string): string {
  return raw.trim().replace(/\/+$/, '');
}

function readQueryParamApiUrl(): string | null {
  if (typeof window === 'undefined' || !window.location) {
    return null;
  }
  try {
    const params = new URLSearchParams(window.location.search);
    const candidate = params.get('api_url') || params.get('backend_url');
    if (candidate && /^https?:\/\//i.test(candidate.trim())) {
      const clean = normalizeApiUrl(candidate);
      runtimeApiUrlOverride = clean;
      try {
        window.sessionStorage?.setItem(STORAGE_KEY, clean);
      } catch {
        // Ignore storage errors in restricted environments
      }
      return clean;
    }
  } catch {
    // Ignore malformed query string
  }
  return null;
}

export function setRuntimeApiBaseUrl(url: string): void {
  const clean = normalizeApiUrl(url);
  runtimeApiUrlOverride = clean || null;
  if (typeof window !== 'undefined') {
    try {
      if (clean) {
        window.sessionStorage?.setItem(STORAGE_KEY, clean);
      } else {
        window.sessionStorage?.removeItem(STORAGE_KEY);
      }
    } catch {
      // Ignore storage errors
    }
  }
}

export function getRuntimeApiBaseUrl(): string {
  return getApiBaseUrl();
}

export function getApiBaseUrl(): string {
  // 1. Check URL query parameter (?api_url=https://...)
  const fromQuery = readQueryParamApiUrl();
  if (fromQuery) {
    return fromQuery;
  }

  // 2. Check interactive runtime override (in-memory or sessionStorage)
  if (runtimeApiUrlOverride && runtimeApiUrlOverride.length > 0) {
    return runtimeApiUrlOverride;
  }
  if (typeof window !== 'undefined') {
    try {
      const stored = window.sessionStorage?.getItem(STORAGE_KEY);
      if (stored && /^https?:\/\//i.test(stored.trim())) {
        runtimeApiUrlOverride = normalizeApiUrl(stored);
        return runtimeApiUrlOverride;
      }
    } catch {
      // Ignore storage errors
    }
  }

  // 3. Check build-time configured public HTTPS ingress URL
  const envUrl = import.meta.env?.VITE_API_BASE_URL;
  if (typeof envUrl === 'string' && envUrl.trim().length > 0) {
    return normalizeApiUrl(envUrl);
  }

  // 4. Default public HTTPS ingress when hosted on GitHub Pages
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const host = window.location.hostname.toLowerCase();
    if (host.endsWith('github.io')) {
      return DEFAULT_PUBLIC_INGRESS_URL;
    }
  }

  // 5. Local development proxy
  return '';
}

export function getPrecomputedRunUrl(policy: 'LTA' | 'IVIG'): string {
  const rawBase = import.meta.env?.BASE_URL || './';
  const normalizedBase = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
  const fileName = policy === 'IVIG' ? 'ivig_knowledge_graph.json' : 'lta_knowledge_graph.json';
  return `${normalizedBase}runs/${fileName}`;
}
