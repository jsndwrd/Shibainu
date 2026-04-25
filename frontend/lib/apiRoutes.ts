export const API_ROUTES = {
  root: "/",
  health: "/health",

  auth: {
    login: "/api/auth/login",
    logout: "/api/auth/logout",
    me: "/api/auth/me",
  },

  aspirations: {
    create: "/api/aspirations/",
    list: "/api/aspirations/",
    mine: "/api/aspirations/mine",
    detail: (aspirationId: string) => `/api/aspirations/${aspirationId}`,
    updateStatus: (aspirationId: string, status: string) =>
      `/api/aspirations/${aspirationId}/status?status=${encodeURIComponent(status)}`,
  },

  reference: {
    provinces: "/api/ref/provinces",
    regencies: (province: string) =>
      `/api/ref/regencies/${encodeURIComponent(province)}`,
    categories: "/api/ref/categories",
  },

  clusters: {
    list: "/api/clusters/",
    detail: (clusterId: string) => `/api/clusters/${clusterId}`,
    recompute: "/api/clusters/recompute",
  },

  scores: {
    list: "/api/scores/",
    top: "/api/scores/top",
    regional: (province: string) =>
      `/api/scores/regional/${encodeURIComponent(province)}`,
    recompute: "/api/scores/recompute",
  },

  briefs: {
    generate: "/api/briefs/generate",
    list: "/api/briefs/",
    detail: (briefId: string) => `/api/briefs/${briefId}`,
  },
};
