import type { UserRole } from "../types/rbac";

export interface DevAccount {
  label: string;
  username: string;
  email: string;
  password: string;
  role: UserRole;
}

export const DEV_ORGANIZATION = {
  id: "TKK-ORG-001",
  name: "TKK Technologies Pvt Ltd",
};

export const DEV_TEAM = {
  id: "TEAM-DE-001",
  name: "Data Engineering Team",
};

export const DEV_PROJECTS = [
  {
    code: "AMEX-DM-001",
    name: "American Express Data Migration",
  },
  {
    code: "SNOW-VAL-001",
    name: "Snowflake Migration Validation",
  },
] as const;

export const DEV_ACCOUNTS: DevAccount[] = [
  {
    label: "Platform Admin",
    username: "admin",
    email: "admin@tkkvalidator.local",
    password: "Admin@123",
    role: "platform_admin",
  },
  {
    label: "Organization Admin",
    username: "orgadmin",
    email: "orgadmin@tkkvalidator.local",
    password: "Admin@123",
    role: "organization_admin",
  },
  {
    label: "Architect",
    username: "architect",
    email: "architect@tkkvalidator.local",
    password: "Architect@123",
    role: "architect",
  },
  {
    label: "QA Lead",
    username: "qalead",
    email: "qalead@tkkvalidator.local",
    password: "QALead@123",
    role: "qa_lead",
  },
  {
    label: "QA Engineer",
    username: "tester",
    email: "tester@tkkvalidator.local",
    password: "Tester@123",
    role: "qa_engineer",
  },
  {
    label: "Data Engineer",
    username: "dataengineer",
    email: "dataengineer@tkkvalidator.local",
    password: "Data@123",
    role: "data_engineer",
  },
  {
    label: "Viewer",
    username: "viewer",
    email: "viewer@tkkvalidator.local",
    password: "Viewer@123",
    role: "viewer",
  },
  {
    label: "Guest",
    username: "guest",
    email: "guest@tkkvalidator.local",
    password: "Guest@123",
    role: "guest",
  },
];

export const isNonProductionEnvironment = (): boolean => {
  const appEnv = ((import.meta.env.VITE_APP_ENV as string | undefined) ?? "").toLowerCase();

  if (appEnv === "prod" || appEnv === "production" || appEnv === "stage" || appEnv === "staging") {
    return false;
  }

  return import.meta.env.MODE !== "production";
};

export const DEMO_MODE_ACCOUNTS: DevAccount[] = DEV_ACCOUNTS.filter((account) =>
  ["admin", "tester", "viewer"].includes(account.username)
);
