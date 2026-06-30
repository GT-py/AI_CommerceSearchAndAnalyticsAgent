export type UserRole = "user" | "admin";

export type AuthUser = {
  id: number;
  email: string;
  role: UserRole;
};

export type AuthToken = {
  access_token: string;
  token_type: "bearer";
};
