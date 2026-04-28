import type { AuthResponse, UserProfile } from "../types";
import { apiRequest } from "./http";

export function register(payload: {
  username: string;
  email: string;
  password: string;
}): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: payload
  });
}

export function login(payload: { username: string; password: string }): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: payload
  });
}

export function me(token: string): Promise<UserProfile> {
  return apiRequest<UserProfile>("/api/auth/me", {
    token
  });
}
