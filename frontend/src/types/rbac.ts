export type UserRole =
  | "platform_admin"
  | "organization_admin"
  | "architect"
  | "developer"
  | "data_engineer"
  | "qa_lead"
  | "qa_engineer"
  | "viewer"
  | "guest";

export type ThemeMode = "light" | "dark";

export interface AuthUser {
  id: string;
  username: string;
  name: string;
  email: string;
  role: UserRole;
}