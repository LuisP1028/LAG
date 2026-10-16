/**
 * API Base URL and Bundled Pre-Computed Policy Run Artifact Resolver.
 *
 * Implements `functional_specification_018.md` §5.1 and `functional_specification_805.md` §4.2:
 * 1. Resolves runtime `?api_url=https://...` (or `?backend_url=https://...`) URL query parameter
 *    so explicit overrides take highest priority.
 * 2. Resolves interactive UI runtime endpoint override (`setRuntimeApiBaseUrl`).
 * 3. Preserves local development origin priority (`localhost` / `127.0.0.1`) when no explicit override is set.
 * 4. Dynamically fetches cache-busted `./tunnel.json?t=...` at page initialization (`initRuntimeTunnelConfig`)
 *    so Cloudflare Quick Tunnel rotations propagate without a frontend bundle rebuild.
 * 5. Falls back to build-time `VITE_API_BASE_URL` or `DEFAULT_PUBLIC_INGRESS_URL`.
 */

export const DEFAULT_PUBLIC_INGRESS_URL = 'https://harbor-armed-reporting-assurance.trycloudflare.com';
export const DEFAULT_HF_SPACE_URL = DEFAULT_PUBLIC_INGRESS_URL;

const STORAGE_KEY = 'lag_runtime_api_url';
let runtimeApiUrlOverride: string | null = null;
let publishedTunnelUrl: string | null = null;

function normalizeApiUrl(raw: string): string {
  return raw.trim().replace(/\/+$/, '');
}

function isLocalhostOrigin(): boolean {
  if (typeof window === 'undefined' || !window.location || !window.location.hostname) {
    return false;
  }
  const host = window.location.hostname.toLowerCase();
  return host === 'localhost' || host === '127.0.0.1';
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

export async function initRuntimeTunnelConfig(): Promise<string> {
  // Preserve highest precedence for explicit query parameter or local dev origins
  const fromQuery = readQueryParamApiUrl();
  if (fromQuery) {
    return fromQuery;
  }
  if (isLocalhostOrigin()) {
    return getApiBaseUrl();
  }

  try {
    const rawBase = import.meta.env?.BASE_URL || './';
    const normalizedBase = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
    const res = await fetch(`${normalizedBase}tunnel.json?t=${Date.now()}`, {
      cache: 'no-store',
      headers: { 'Cache-Control': 'no-cache' },
    });
    if (res.ok) {
      const data = await res.json();
      const candidate = data?.url || data?.backend_url || data?.public_https_url;
      if (typeof candidate === 'string' && /^https?:\/\//i.test(candidate.trim())) {
        publishedTunnelUrl = normalizeApiUrl(candidate);
      }
    }
  } catch {
    // Fall back gracefully to build-time or default ingress URL
  }

  return getApiBaseUrl();
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
  // 1. Check interactive runtime override (set via setRuntimeApiBaseUrl or prior query param seed)
  if (runtimeApiUrlOverride && runtimeApiUrlOverride.length > 0) {
    return runtimeApiUrlOverride;
  }

  // 2. Check URL query parameter (?api_url=https://... or ?backend_url=https://...) on initial resolution
  const fromQuery = readQueryParamApiUrl();
  if (fromQuery) {
    return fromQuery;
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

  // 3. Dynamically discovered runtime tunnel metadata (tunnel.json) takes priority over static build-time URL
  if (publishedTunnelUrl && publishedTunnelUrl.length > 0) {
    return publishedTunnelUrl;
  }

  // 4. Check build-time configured public HTTPS ingress URL
  const envUrl = import.meta.env?.VITE_API_BASE_URL;
  if (typeof envUrl === 'string' && envUrl.trim().length > 0) {
    return normalizeApiUrl(envUrl);
  }

  // 5. Default public HTTPS ingress when hosted on GitHub Pages
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const host = window.location.hostname.toLowerCase();
    if (host.endsWith('github.io')) {
      return DEFAULT_PUBLIC_INGRESS_URL;
    }
  }

  // 6. Local development proxy
  return '';
}

export function getPrecomputedRunUrl(policy: 'LTA' | 'IVIG'): string {
  const rawBase = import.meta.env?.BASE_URL || './';
  const normalizedBase = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
  const fileName = policy === 'IVIG' ? 'ivig_knowledge_graph.json' : 'lta_knowledge_graph.json';
  return `${normalizedBase}runs/${fileName}`;
}
