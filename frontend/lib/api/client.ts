/**
 * Shared backend client. Every `lib/api` call goes through here so the base URL,
 * credentials, and error handling live in one place.
 *
 * The FastAPI backend authenticates via a session cookie set at login, so all
 * requests send credentials. Set `NEXT_PUBLIC_API_BASE_URL` to point at the
 * backend (defaults to the local FastAPI dev server).
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** Absolute URL for a backend path — used for full-page redirects (e.g. OAuth). */
export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

/** Thrown when the backend responds with a non-2xx status. */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Fetch JSON from the backend with the session cookie attached. */
export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(apiUrl(path), { credentials: "include", ...init });

  if (!res.ok) {
    throw new ApiError(res.status, `Request to ${path} failed (${res.status})`);
  }

  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}
