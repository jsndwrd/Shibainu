import { create } from "zustand";
import { API_ROUTES } from "@/lib/apiRoutes";
import { apiFetch } from "@/lib/apiClient";

import type {
  LoginRequest,
  LoginResponse,
  MeResponse,
  UserRole,
} from "@/lib/apiContract";

interface AuthStoreState {
  accessToken: string | null;
  citizenId: string | null;
  user: MeResponse | null;
  role: UserRole | null;

  isAuthenticated: boolean;
  isAdmin: boolean;
  isUser: boolean;

  isLoading: boolean;
  error: string | null;

  hydrateAuth: () => void;
  login: (payload: LoginRequest) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<MeResponse>;

  getDashboardPath: () => string;
  clearError: () => void;
}

const TOKEN_KEY = "access_token";
const CITIZEN_ID_KEY = "citizen_id";
const ROLE_KEY = "role";

function getStorageItem(key: string): string | null {
  if (typeof window === "undefined") return null;

  return localStorage.getItem(key);
}

function setStorageItem(key: string, value: string) {
  if (typeof window === "undefined") return;

  localStorage.setItem(key, value);
}

function removeAuthStorage() {
  if (typeof window === "undefined") return;

  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(CITIZEN_ID_KEY);
  localStorage.removeItem(ROLE_KEY);
}

function resolveRole(role?: string | null): UserRole {
  return role === "admin" ? "admin" : "user";
}

export const useAuthStore = create<AuthStoreState>((set, get) => ({
  accessToken: null,
  citizenId: null,
  user: null,
  role: null,

  isAuthenticated: false,
  isAdmin: false,
  isUser: false,

  isLoading: false,
  error: null,

  hydrateAuth: () => {
    const token = getStorageItem(TOKEN_KEY);
    const citizenId = getStorageItem(CITIZEN_ID_KEY);
    const role = resolveRole(getStorageItem(ROLE_KEY));

    if (!token) {
      set({
        accessToken: null,
        citizenId: null,
        user: null,
        role: null,
        isAuthenticated: false,
        isAdmin: false,
        isUser: false,
      });

      return;
    }

    set({
      accessToken: token,
      citizenId,
      role,
      isAuthenticated: true,
      isAdmin: role === "admin",
      isUser: role === "user",
    });
  },

  login: async (payload) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<LoginResponse>(API_ROUTES.auth.login, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      const role = resolveRole(response.role);

      setStorageItem(TOKEN_KEY, response.access_token);
      setStorageItem(CITIZEN_ID_KEY, response.citizen_id);
      setStorageItem(ROLE_KEY, role);

      set({
        accessToken: response.access_token,
        citizenId: response.citizen_id,
        role,
        isAuthenticated: true,
        isAdmin: role === "admin",
        isUser: role === "user",
        isLoading: false,
      });

      return response;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Gagal login.";

      set({
        error: message,
        isLoading: false,
        isAuthenticated: false,
        isAdmin: false,
        isUser: false,
      });

      throw error;
    }
  },

  logout: async () => {
    try {
      await apiFetch(API_ROUTES.auth.logout, {
        method: "POST",
        token: get().accessToken,
      });
    } finally {
      removeAuthStorage();

      set({
        accessToken: null,
        citizenId: null,
        user: null,
        role: null,
        isAuthenticated: false,
        isAdmin: false,
        isUser: false,
        isLoading: false,
        error: null,
      });
    }
  },

  fetchMe: async () => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<MeResponse>(API_ROUTES.auth.me, {
        method: "GET",
        token: get().accessToken,
      });

      const role = resolveRole(response.role);

      setStorageItem(CITIZEN_ID_KEY, response.id);
      setStorageItem(ROLE_KEY, role);

      set({
        user: response,
        citizenId: response.id,
        role,
        isAuthenticated: true,
        isAdmin: role === "admin",
        isUser: role === "user",
        isLoading: false,
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Gagal mengambil data user.";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },

  getDashboardPath: () => {
    const role = get().isAdmin;

    if (role) {
      return "/admin";
    }

    return "/laporan";
  },

  clearError: () => set({ error: null }),
}));
