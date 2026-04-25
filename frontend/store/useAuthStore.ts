import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
    isAuthenticated: boolean;
    user: { nik: string; dob: string } | null;
    login: (nik: string, dob: string) => void;
    logout: () => void;
}

// Gunakan persist middleware untuk membungkus fungsi set
export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            isAuthenticated: false,
            user: null,
            login: (nik, dob) =>
                set({ isAuthenticated: true, user: { nik, dob } }),
            logout: () => set({ isAuthenticated: false, user: null }),
        }),
        {
            name: "vokara-auth-storage", // Nama key yang akan disimpan di localStorage
        },
    ),
);
