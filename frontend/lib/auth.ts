import { apiFetch } from "./api";

export type AuthUser = {
  id: number;
  email: string;
  role: "user" | "admin";
};

export type AuthToken = {
  access_token: string;
  token_type: "bearer";
};

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

export function logout() {
  return apiFetch<{ message: string }>("/auth/logout", {
    method: "POST",
  });
}

export function getMe(accessToken: string) {
  return apiFetch<AuthUser>("/auth/me", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}
