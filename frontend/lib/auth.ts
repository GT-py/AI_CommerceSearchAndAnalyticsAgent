import { apiFetch } from "./api";
import type { AuthToken, AuthUser } from "@/types/user";

export const ACCESS_TOKEN_STORAGE_KEY = "acsaa_access_token";

export function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string) {
  window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
  window.dispatchEvent(new Event("auth:changed"));
}

export function clearStoredToken() {
  window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  window.dispatchEvent(new Event("auth:changed"));
}

export function register(email: string, password: string) {
  return apiFetch<AuthUser>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(email: string, password: string) {
  return apiFetch<AuthToken>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout() {
  try {
    await apiFetch<{ message: string }>("/auth/logout", {
      method: "POST",
      token: getStoredToken(),
    });
  } finally {
    clearStoredToken();
  }
}

export function getMe(accessToken: string) {
  return apiFetch<AuthUser>("/auth/me", {
    token: accessToken,
  });
}

export async function getStoredUser() {
  const token = getStoredToken();
  if (!token) {
    return null;
  }

  try {
    return await getMe(token);
  } catch {
    clearStoredToken();
    return null;
  }
}
