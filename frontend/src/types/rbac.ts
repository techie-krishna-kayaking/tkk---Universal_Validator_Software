export type UserRole =
  | "platform_admin"
  | "organization_admin"
  | "architect"
  | "qa_lead"
  | "qa_engineer"
  | "viewer"
  | "guest";

export type ThemeMode = "light" | "dark";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}