import { create } from "zustand";
import { API_ROUTES } from "@/lib/apiRoutes";
import { apiFetch } from "@/lib/apiClient";

import type { AspirasiData } from "@/schemas/aspirasiSchema";
import type {
  LoginRequest,
  LoginResponse,
  MeResponse,
  AspirationCreatePayload,
  AspirationResponse,
  AspirationListItem,
} from "@/lib/apiContract";

interface AspirasiStoreState {
  step: number;
  formData: Partial<AspirasiData>;

  accessToken: string | null;
  citizenId: string | null;
  user: MeResponse | null;

  aspirations: AspirationListItem[];
  createdAspiration: AspirationResponse | null;

  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;

  hydrateAuthFromStorage: () => void;

  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateData: (data: Partial<AspirasiData>) => void;
  resetForm: () => void;
  clearError: () => void;

  login: (payload: LoginRequest) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<MeResponse>;

  fetchAspirations: () => Promise<AspirationListItem[]>;
  fetchMyAspirations: () => Promise<AspirationListItem[]>;
  fetchAspirationsByCitizenId: (
    citizenId: string,
  ) => Promise<AspirationListItem[]>;

  submitAspirasi: () => Promise<AspirationResponse>;

  updateAspirationStatus: (
    aspirationId: string,
    status: string,
  ) => Promise<AspirationResponse>;
}

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;

  return (
    localStorage.getItem("token") ||
    localStorage.getItem("access_token") ||
    null
  );
}

function saveToken(token: string) {
  if (typeof window === "undefined") return;

  localStorage.setItem("token", token);
  localStorage.setItem("access_token", token);
}

function removeToken() {
  if (typeof window === "undefined") return;

  localStorage.removeItem("token");
  localStorage.removeItem("access_token");
}

function normalizeUrgency(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;

  if (typeof value === "number") {
    return Math.min(5, Math.max(1, value));
  }

  const urgencyMap: Record<string, number> = {
    "Sangat Rendah": 1,
    Rendah: 2,
    Sedang: 3,
    Tinggi: 4,
    Kritis: 5,
  };

  return urgencyMap[String(value)] ?? null;
}

function buildDescription(data: Record<string, any>): string {
  const title = data.judulLaporan ?? "";
  const description =
    data.deskripsi ?? data.deskripsiLaporan ?? data.description ?? "";

  return `${title}\n\n${description}`.trim();
}

function mapFormToPayload(
  formData: Partial<AspirasiData>,
): AspirationCreatePayload {
  const data = formData as Record<string, any>;

  return {
    description: data.description ?? buildDescription(data),
    category: data.category ?? data.kategoriAspirasi ?? data.kategori ?? null,
    province: data.province ?? data.provinsi ?? "",
    regency: data.regency ?? data.kota ?? data.kabupatenKota ?? "",
    impact_scope: data.impact_scope ?? data.skalaDampak ?? "local",
    target_level:
      data.target_level ?? data.targetLevel ?? data.instansiTujuan ?? "daerah",
  };
}

function validateAspirationPayload(payload: AspirationCreatePayload) {
  const requiredFields: Array<keyof AspirationCreatePayload> = [
    "description",
    "province",
    "regency",
    "impact_scope",
    "target_level",
  ];

  const emptyFields = requiredFields.filter((field) => {
    const value = payload[field];

    return typeof value !== "string" || value.trim() === "";
  });

  if (emptyFields.length > 0) {
    throw new Error(`Field wajib belum lengkap: ${emptyFields.join(", ")}`);
  }

  if (payload.description.length < 15) {
    throw new Error("Deskripsi minimal 15 karakter.");
  }

  if (payload.description.length > 500) {
    throw new Error("Deskripsi maksimal 500 karakter.");
  }
}

export const useAspirasiStore = create<AspirasiStoreState>((set, get) => ({
  step: 1,
  formData: {},

  accessToken: null,
  citizenId: null,
  user: null,

  aspirations: [],
  createdAspiration: null,

  isLoading: false,
  isSubmitting: false,
  error: null,

  hydrateAuthFromStorage: () => {
    const token = getStoredToken();

    if (token) {
      set({ accessToken: token });
    }
  },

  setStep: (step) => set({ step }),

  nextStep: () =>
    set((state) => ({
      step: Math.min(4, state.step + 1),
    })),

  prevStep: () =>
    set((state) => ({
      step: Math.max(1, state.step - 1),
    })),

  updateData: (data) =>
    set((state) => ({
      formData: {
        ...state.formData,
        ...data,
      },
    })),

  resetForm: () =>
    set({
      step: 1,
      formData: {},
      createdAspiration: null,
      error: null,
    }),

  clearError: () => set({ error: null }),

  login: async (payload) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<LoginResponse>(API_ROUTES.auth.login, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      saveToken(response.access_token);

      set({
        accessToken: response.access_token,
        citizenId: response.citizen_id,
        isLoading: false,
      });

      return response;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Gagal login.";

      set({
        error: message,
        isLoading: false,
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
      removeToken();

      set({
        accessToken: null,
        citizenId: null,
        user: null,
        aspirations: [],
        createdAspiration: null,
        step: 1,
        formData: {},
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

      set({
        user: response,
        citizenId: response.id,
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

  fetchAspirations: async () => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<AspirationListItem[]>(
        API_ROUTES.aspirations.list,
        {
          method: "GET",
          token: get().accessToken,
        },
      );

      set({
        aspirations: response,
        isLoading: false,
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Gagal mengambil data aspirasi.";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },

  fetchMyAspirations: async () => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<AspirationListItem[]>(
        API_ROUTES.aspirations.mine,
        {
          method: "GET",
          token: get().accessToken,
        },
      );

      set({
        aspirations: response,
        isLoading: false,
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Gagal mengambil aspirasi milik user.";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },

  fetchAspirationsByCitizenId: async (citizenId) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<AspirationListItem[]>(
        API_ROUTES.aspirations.citizen(citizenId),
        {
          method: "GET",
          token: get().accessToken,
        },
      );

      set({
        aspirations: response,
        isLoading: false,
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Gagal mengambil aspirasi berdasarkan citizen id.";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },

  submitAspirasi: async () => {
    try {
      set({ isSubmitting: true, error: null });

      const payload = mapFormToPayload(get().formData);

      validateAspirationPayload(payload);

      const response = await apiFetch<AspirationResponse>(
        API_ROUTES.aspirations.create,
        {
          method: "POST",
          token: get().accessToken,
          body: JSON.stringify(payload),
        },
      );

      set({
        createdAspiration: response,
        isSubmitting: false,
        step: 1,
        formData: {},
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Gagal mengirim aspirasi.";

      set({
        error: message,
        isSubmitting: false,
      });

      throw error;
    }
  },

  updateAspirationStatus: async (aspirationId, status) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiFetch<AspirationResponse>(
        API_ROUTES.aspirations.updateStatus(aspirationId, status),
        {
          method: "PATCH",
          token: get().accessToken,
        },
      );

      set({ isLoading: false });

      return response;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Gagal memperbarui status aspirasi.";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },
}));
