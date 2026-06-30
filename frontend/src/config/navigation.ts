import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import DataThresholdingRoundedIcon from "@mui/icons-material/DataThresholdingRounded";
import FolderRoundedIcon from "@mui/icons-material/FolderRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import ManageAccountsRoundedIcon from "@mui/icons-material/ManageAccountsRounded";
import MonitorHeartRoundedIcon from "@mui/icons-material/MonitorHeartRounded";
import AccessibilityRoundedIcon from "@mui/icons-material/AccessibilityRounded";
import SmartToyRoundedIcon from "@mui/icons-material/SmartToyRounded";
import DescriptionRoundedIcon from "@mui/icons-material/DescriptionRounded";
import TerminalRoundedIcon from "@mui/icons-material/TerminalRounded";
import RuleRoundedIcon from "@mui/icons-material/RuleRounded";
import PsychologyAltRoundedIcon from "@mui/icons-material/PsychologyAltRounded";
import SettingsSuggestRoundedIcon from "@mui/icons-material/SettingsSuggestRounded";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import type { SvgIconComponent } from "@mui/icons-material";

import type { TranslationKey } from "../context/LocalizationContext";
import type { UserRole } from "../types/rbac";

export interface NavItem {
  id: string;
  label: string;
  labelKey?: TranslationKey;
  path: string;
  icon: SvgIconComponent;
  roles: UserRole[];
}

export const navItems: NavItem[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    path: "/",
    icon: DashboardRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer", "viewer", "guest"],
  },
  {
    id: "validations",
    label: "Validations",
    path: "/validations",
    icon: DataThresholdingRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer"],
  },
  {
    id: "projects",
    label: "Projects",
    path: "/projects",
    icon: FolderRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer"],
  },
  {
    id: "execution",
    label: "Execution",
    path: "/execution",
    icon: MonitorHeartRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer", "viewer"],
  },
  {
    id: "reports",
    label: "Reports",
    path: "/reports",
    icon: InsightsRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer", "viewer"],
  },
  {
    id: "connections",
    label: "Connections",
    path: "/connections",
    icon: StorageRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead"],
  },
  {
    id: "ai-chatbot",
    label: "AI Chatbot",
    labelKey: "nav.aiChatbot",
    path: "/ai-chatbot",
    icon: SmartToyRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer"],
  },
  {
    id: "mapping-reader",
    label: "Mapping Reader",
    labelKey: "nav.mappingReader",
    path: "/mapping-reader",
    icon: DescriptionRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer"],
  },
  {
    id: "sql-generator",
    label: "SQL Generator",
    labelKey: "nav.sqlGenerator",
    path: "/sql-generator",
    icon: TerminalRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer"],
  },
  {
    id: "test-case-generator",
    label: "Test Case Generator",
    labelKey: "nav.testCaseGenerator",
    path: "/test-case-generator",
    icon: RuleRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer"],
  },
  {
    id: "ai-report-explainer",
    label: "AI Report Explainer",
    labelKey: "nav.aiReportExplainer",
    path: "/ai-report-explainer",
    icon: PsychologyAltRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect", "qa_lead", "qa_engineer", "viewer"],
  },
  {
    id: "settings",
    label: "Settings",
    labelKey: "nav.settings",
    path: "/settings",
    icon: SettingsSuggestRoundedIcon,
    roles: ["platform_admin", "organization_admin", "architect"],
  },
  {
    id: "accessibility",
    label: "Accessibility",
    labelKey: "nav.accessibility",
    path: "/accessibility",
    icon: AccessibilityRoundedIcon,
    roles: [
      "platform_admin",
      "organization_admin",
      "architect",
      "qa_lead",
      "qa_engineer",
      "viewer",
      "guest",
    ],
  },
  {
    id: "admin",
    label: "Administration",
    path: "/admin",
    icon: ManageAccountsRoundedIcon,
    roles: ["platform_admin", "organization_admin"],
  },
];