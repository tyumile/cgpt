import { CabinetSession } from "@/src/shared/types";

const SESSION_STORAGE_KEY = "cabinet_session_v1";
const PUBLIC_BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/gpt";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? PUBLIC_BASE_PATH;

function canUseBrowserStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function loadCabinetSession(): CabinetSession | null {
  if (!canUseBrowserStorage()) {
    return null;
  }

  const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as CabinetSession;
    if (
      typeof parsed.token !== "string" ||
      typeof parsed.email !== "string" ||
      typeof parsed.full_name !== "string" ||
      typeof parsed.expires_at !== "number"
    ) {
      window.localStorage.removeItem(SESSION_STORAGE_KEY);
      return null;
    }

    if (parsed.expires_at <= Date.now()) {
      window.localStorage.removeItem(SESSION_STORAGE_KEY);
      return null;
    }

    return parsed;
  } catch {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  }
}

export function saveCabinetSession(session: CabinetSession): CabinetSession {
  if (canUseBrowserStorage()) {
    window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  }

  return session;
}

export async function authorizeCabinet(email: string, fullName: string): Promise<CabinetSession> {
  const response = await fetch(`${API_BASE}/api/cabinet/auth`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
    body: JSON.stringify({
      email,
      full_name: fullName,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Auth failed: ${response.status}`);
  }

  const data = (await response.json()) as {
    session_token: string;
    email: string;
    full_name: string;
    expires_at: string;
  };
  const expiresAtMs = Date.parse(data.expires_at);
  if (!Number.isFinite(expiresAtMs)) {
    throw new Error("Invalid session expiry from server.");
  }

  return saveCabinetSession({
    token: data.session_token,
    email: data.email,
    full_name: data.full_name,
    expires_at: expiresAtMs,
  });
}

export function clearCabinetSession(): void {
  if (!canUseBrowserStorage()) {
    return;
  }
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function getCabinetSessionToken(): string | null {
  return loadCabinetSession()?.token ?? null;
}
