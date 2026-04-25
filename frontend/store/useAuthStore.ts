import { create } from "zustand";

interface AuthState {
    isAuthenticated: boolean;
    user: { nik: string; dob: string } | null;
    login: (nik: string, dob: string) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    isAuthenticated: false,
    user: null,
    login: (nik, dob) => set({ isAuthenticated: true, user: { nik, dob } }),
    logout: () => set({ isAuthenticated: false, user: null }),
}));
