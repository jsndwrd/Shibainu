export type UUID = string;
export type ISODate = string;
export type ISODateTime = string;
export type UserRole = "user" | "admin";

export interface LoginRequest {
  nik: string;
  dob: ISODate;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  citizen_id: UUID;
  role: UserRole;
}

export interface MeResponse {
  id: string;
  nik: string;
  province: string | null;
  full_name: string | null;
  role?: "user" | "admin";
}

export type PolicyLevel = "strategic" | "operational";

export interface AspirationCreatePayload {
  description: string;
  category?: string | null;
  province: string;
  regency: string;
  impact_scope: string;
  target_level: string;
}

export interface AspirationResponse {
  id: string;
  citizen_id: string;
  description: string;
  cleaned_description?: string | null;

  category_user_input?: string | null;
  predicted_category?: string | null;
  category_confidence?: number | null;

  predicted_asta_cita?: string | null;
  asta_confidence?: number | null;

  policy_level?: "strategic" | "operational" | string | null;
  policy_level_confidence?: number | null;
  policy_level_reason?: string | null;
  routing_target?: string | null;

  province?: string | null;
  regency?: string | null;
  impact_scope?: string | null;
  target_level?: string | null;

  cluster_id?: string | null;
  priority_score?: number | null;

  status: string;
  submitted_at: string;
}

export interface AspirationListItem {
  id: string;

  category_user_input?: string | null;
  predicted_category?: string | null;

  policy_level?: "strategic" | "operational" | string | null;
  policy_level_confidence?: number | null;
  routing_target?: string | null;

  cluster_id?: string | null;
  priority_score?: number | null;

  status?: string | null;
  submitted_at: string;
}

export interface ProvinceResponse {
  code: string;
  name: string;
}

export interface RegencyResponse {
  code: string;
  name: string;
  province_code: string;
}

export interface CategoryOption {
  label: string;
  value: string;
}

export type RawCategoryResponse =
  | string
  | {
      name?: string;
      label?: string;
      value?: string;
      code?: string;
    };

export interface ClusterResponse {
  id: UUID;
  label: string;
  category: string;
  member_count: number;
  avg_urgency: number;
  top_provinces: string[];
  priority_score: number;
  created_at: ISODateTime;
  last_updated: ISODateTime;
}

export interface ClusterDetailResponse extends ClusterResponse {
  sub_topics: string[];
  urgency_dist: Record<string, number>;
}

export interface ScoreResponse {
  cluster_id: UUID;
  volume_score: number;
  urgency_score: number;
  geo_score: number;
  impact_score: number;
  total_score: number;
  computed_at: ISODateTime;
}

export interface BriefGenerateRequest {
  cluster_ids: UUID[];
}

export interface BriefResponse {
  id: UUID;
  cluster_id: UUID;
  content: string;
  urgency_classification: string;
  generated_by: string;
  generated_at: ISODateTime;
}

export interface MessageResponse {
  message: string;
}

export interface AdminStats {
  totalAspirations: number;
  totalClusters: number;
  totalBriefs: number;
  averagePriorityScore: number;
  criticalReports: number;
}
