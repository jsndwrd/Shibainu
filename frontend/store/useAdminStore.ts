import { create } from "zustand";
import { API_ROUTES } from "@/lib/apiRoutes";
import { apiFetch } from "@/lib/apiClient";

import type {
  AdminStats,
  AspirationListItem,
  AspirationResponse,
  BriefGenerateRequest,
  BriefResponse,
  ClusterDetailResponse,
  ClusterResponse,
  MessageResponse,
  ScoreResponse,
  UUID,
} from "@/lib/apiContract";

interface AdminStoreState {
  aspirations: AspirationListItem[];
  clusters: ClusterResponse[];
  selectedCluster: ClusterDetailResponse | null;
  scores: ScoreResponse[];
  topScores: ScoreResponse[];
  briefs: BriefResponse[];
  selectedBrief: BriefResponse | null;

  stats: AdminStats;

  isLoading: boolean;
  isLoadingAspirations: boolean;
  isLoadingClusters: boolean;
  isLoadingScores: boolean;
  isLoadingBriefs: boolean;
  isGeneratingBrief: boolean;
  isUpdatingStatus: boolean;
  isRecomputing: boolean;

  error: string | null;

  fetchAdminDashboard: () => Promise<void>;

  fetchAspirations: () => Promise<AspirationListItem[]>;
  updateAspirationStatus: (
    aspirationId: UUID,
    status: string,
  ) => Promise<AspirationResponse>;

  fetchClusters: () => Promise<ClusterResponse[]>;
  fetchClusterDetail: (clusterId: UUID) => Promise<ClusterDetailResponse>;
  recomputeClusters: () => Promise<MessageResponse>;

  fetchScores: () => Promise<ScoreResponse[]>;
  fetchTopScores: () => Promise<ScoreResponse[]>;
  fetchRegionalScores: (province: string) => Promise<ScoreResponse[]>;
  recomputeScores: () => Promise<MessageResponse>;

  fetchBriefs: () => Promise<BriefResponse[]>;
  fetchBriefDetail: (briefId: UUID) => Promise<BriefResponse>;
  generateBriefs: (payload: BriefGenerateRequest) => Promise<BriefResponse[]>;

  clearSelectedBrief: () => void;
  clearSelectedCluster: () => void;
  clearError: () => void;
}

const initialStats: AdminStats = {
  totalAspirations: 0,
  totalClusters: 0,
  totalBriefs: 0,
  averagePriorityScore: 0,
  criticalReports: 0,
};

function calculateStats(params: {
  aspirations: AspirationListItem[];
  clusters: ClusterResponse[];
  briefs: BriefResponse[];
}): AdminStats {
  const { aspirations, clusters, briefs } = params;

  const totalPriority = clusters.reduce(
    (sum, cluster) => sum + Number(cluster.priority_score || 0),
    0,
  );

  const averagePriorityScore =
    clusters.length > 0 ? totalPriority / clusters.length : 0;

  const criticalReports = aspirations.filter(
    (item) => Number(item.urgency) >= 4,
  ).length;

  return {
    totalAspirations: aspirations.length,
    totalClusters: clusters.length,
    totalBriefs: briefs.length,
    averagePriorityScore,
    criticalReports,
  };
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export const useAdminStore = create<AdminStoreState>((set, get) => ({
  aspirations: [],
  clusters: [],
  selectedCluster: null,
  scores: [],
  topScores: [],
  briefs: [],
  selectedBrief: null,

  stats: initialStats,

  isLoading: false,
  isLoadingAspirations: false,
  isLoadingClusters: false,
  isLoadingScores: false,
  isLoadingBriefs: false,
  isGeneratingBrief: false,
  isUpdatingStatus: false,
  isRecomputing: false,

  error: null,

  fetchAdminDashboard: async () => {
    try {
      set({ isLoading: true, error: null });

      const [aspirations, clusters, scores, topScores, briefs] =
        await Promise.all([
          get().fetchAspirations(),
          get().fetchClusters(),
          get().fetchScores(),
          get().fetchTopScores(),
          get().fetchBriefs(),
        ]);

      set({
        aspirations,
        clusters,
        scores,
        topScores,
        briefs,
        stats: calculateStats({
          aspirations,
          clusters,
          briefs,
        }),
        isLoading: false,
      });
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal memuat dashboard admin."),
        isLoading: false,
      });

      throw error;
    }
  },

  fetchAspirations: async () => {
    try {
      set({ isLoadingAspirations: true, error: null });

      const response = await apiFetch<AspirationListItem[]>(
        API_ROUTES.aspirations.list,
        {
          method: "GET",
        },
      );

      set({
        aspirations: response,
        isLoadingAspirations: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil data aspirasi."),
        isLoadingAspirations: false,
      });

      throw error;
    }
  },

  updateAspirationStatus: async (aspirationId, status) => {
    try {
      set({ isUpdatingStatus: true, error: null });

      const response = await apiFetch<AspirationResponse>(
        API_ROUTES.aspirations.updateStatus(aspirationId, status),
        {
          method: "PATCH",
        },
      );

      await get().fetchAspirations();

      set({ isUpdatingStatus: false });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal memperbarui status aspirasi."),
        isUpdatingStatus: false,
      });

      throw error;
    }
  },

  fetchClusters: async () => {
    try {
      set({ isLoadingClusters: true, error: null });

      const response = await apiFetch<ClusterResponse[]>(
        API_ROUTES.clusters.list,
        {
          method: "GET",
        },
      );

      set({
        clusters: response,
        isLoadingClusters: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil data cluster."),
        isLoadingClusters: false,
      });

      throw error;
    }
  },

  fetchClusterDetail: async (clusterId) => {
    try {
      set({ isLoadingClusters: true, error: null });

      const response = await apiFetch<ClusterDetailResponse>(
        API_ROUTES.clusters.detail(clusterId),
        {
          method: "GET",
        },
      );

      set({
        selectedCluster: response,
        isLoadingClusters: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil detail cluster."),
        isLoadingClusters: false,
      });

      throw error;
    }
  },

  recomputeClusters: async () => {
    try {
      set({ isRecomputing: true, error: null });

      const response = await apiFetch<MessageResponse>(
        API_ROUTES.clusters.recompute,
        {
          method: "POST",
        },
      );

      await get().fetchClusters();

      set({ isRecomputing: false });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal menghitung ulang cluster."),
        isRecomputing: false,
      });

      throw error;
    }
  },

  fetchScores: async () => {
    try {
      set({ isLoadingScores: true, error: null });

      const response = await apiFetch<ScoreResponse[]>(API_ROUTES.scores.list, {
        method: "GET",
      });

      set({
        scores: response,
        isLoadingScores: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil data score."),
        isLoadingScores: false,
      });

      throw error;
    }
  },

  fetchTopScores: async () => {
    try {
      set({ isLoadingScores: true, error: null });

      const response = await apiFetch<ScoreResponse[]>(API_ROUTES.scores.top, {
        method: "GET",
      });

      set({
        topScores: response,
        isLoadingScores: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil top score."),
        isLoadingScores: false,
      });

      throw error;
    }
  },

  fetchRegionalScores: async (province) => {
    try {
      set({ isLoadingScores: true, error: null });

      const response = await apiFetch<ScoreResponse[]>(
        API_ROUTES.scores.regional(province),
        {
          method: "GET",
        },
      );

      set({
        scores: response,
        isLoadingScores: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil score regional."),
        isLoadingScores: false,
      });

      throw error;
    }
  },

  recomputeScores: async () => {
    try {
      set({ isRecomputing: true, error: null });

      const response = await apiFetch<MessageResponse>(
        API_ROUTES.scores.recompute,
        {
          method: "GET",
        },
      );

      await Promise.all([get().fetchScores(), get().fetchTopScores()]);

      set({ isRecomputing: false });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal menghitung ulang score."),
        isRecomputing: false,
      });

      throw error;
    }
  },

  fetchBriefs: async () => {
    try {
      set({ isLoadingBriefs: true, error: null });

      const response = await apiFetch<BriefResponse[]>(API_ROUTES.briefs.list, {
        method: "GET",
      });

      set({
        briefs: response,
        isLoadingBriefs: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil policy brief."),
        isLoadingBriefs: false,
      });

      throw error;
    }
  },

  fetchBriefDetail: async (briefId) => {
    try {
      set({ isLoadingBriefs: true, error: null });

      const response = await apiFetch<BriefResponse>(
        API_ROUTES.briefs.detail(briefId),
        {
          method: "GET",
        },
      );

      set({
        selectedBrief: response,
        isLoadingBriefs: false,
      });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal mengambil detail brief."),
        isLoadingBriefs: false,
      });

      throw error;
    }
  },

  generateBriefs: async (payload) => {
    try {
      set({ isGeneratingBrief: true, error: null });

      const response = await apiFetch<BriefResponse[]>(
        API_ROUTES.briefs.generate,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );

      await get().fetchBriefs();

      set({ isGeneratingBrief: false });

      return response;
    } catch (error) {
      set({
        error: getErrorMessage(error, "Gagal membuat policy brief."),
        isGeneratingBrief: false,
      });

      throw error;
    }
  },

  clearSelectedBrief: () => set({ selectedBrief: null }),

  clearSelectedCluster: () => set({ selectedCluster: null }),

  clearError: () => set({ error: null }),
}));
