import { create } from "zustand";
import { API_ROUTES } from "@/lib/apiRoutes";
import { apiFetch } from "@/lib/apiClient";

import type {
  CategoryOption,
  ProvinceResponse,
  RawCategoryResponse,
  RegencyResponse,
} from "@/lib/apiContract";

interface ReferenceStoreState {
  categories: CategoryOption[];
  provinces: ProvinceResponse[];
  regencies: RegencyResponse[];

  isLoadingCategories: boolean;
  isLoadingProvinces: boolean;
  isLoadingRegencies: boolean;

  error: string | null;

  fetchCategories: () => Promise<CategoryOption[]>;
  fetchProvinces: () => Promise<ProvinceResponse[]>;
  fetchRegencies: (province: string) => Promise<RegencyResponse[]>;

  resetRegencies: () => void;
  clearError: () => void;
}

function normalizeCategories(data: RawCategoryResponse[]): CategoryOption[] {
  return data.map((item) => {
    if (typeof item === "string") {
      return {
        label: item,
        value: item,
      };
    }

    const label = item.label ?? item.name ?? item.value ?? item.code ?? "";

    return {
      label,
      value: item.value ?? item.code ?? label,
    };
  });
}

export const useReferenceStore = create<ReferenceStoreState>((set) => ({
  categories: [],
  provinces: [],
  regencies: [],

  isLoadingCategories: false,
  isLoadingProvinces: false,
  isLoadingRegencies: false,

  error: null,

  fetchCategories: async () => {
    try {
      set({ isLoadingCategories: true, error: null });

      const response = await apiFetch<RawCategoryResponse[]>(
        API_ROUTES.reference.categories,
        {
          method: "GET",
        },
      );

      const categories = normalizeCategories(response);

      set({
        categories,
        isLoadingCategories: false,
      });

      return categories;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Gagal mengambil kategori.";

      set({
        error: message,
        isLoadingCategories: false,
      });

      throw error;
    }
  },

  fetchProvinces: async () => {
    try {
      set({ isLoadingProvinces: true, error: null });

      const response = await apiFetch<ProvinceResponse[]>(
        API_ROUTES.reference.provinces,
        {
          method: "GET",
        },
      );

      set({
        provinces: response,
        isLoadingProvinces: false,
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Gagal mengambil provinsi.";

      set({
        error: message,
        isLoadingProvinces: false,
      });

      throw error;
    }
  },

  fetchRegencies: async (province) => {
    try {
      set({ isLoadingRegencies: true, error: null });

      const response = await apiFetch<RegencyResponse[]>(
        API_ROUTES.reference.regencies(province),
        {
          method: "GET",
        },
      );

      set({
        regencies: response,
        isLoadingRegencies: false,
      });

      return response;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Gagal mengambil kota/kabupaten.";

      set({
        error: message,
        isLoadingRegencies: false,
      });

      throw error;
    }
  },

  resetRegencies: () => set({ regencies: [] }),

  clearError: () => set({ error: null }),
}));
