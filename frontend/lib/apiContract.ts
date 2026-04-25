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

export interface AspirationCreatePayload {
  description: string;
  category?: string | null;
  urgency?: number | null;
  province: string;
  regency: string;
  impact_scope: string;
  target_level: string;
}

export interface AspirationResponse {
  id: UUID;
  citizen_id: UUID;
  description: string;
  cleaned_description: string;
  predicted_category: string;
  predicted_urgency: number;
  cluster_id: UUID;
  priority_score: number;
  status: string;
  submitted_at: ISODateTime;
}

export interface AspirationListItem {
  id: UUID;
  category: string;
  urgency: number;
  cluster_id: UUID;
  submitted_at: ISODateTime;
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
