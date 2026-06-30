import React, { createContext, useContext, useMemo, useState } from "react";

export type Locale = "en" | "es" | "fr";

export type TranslationKey =
  | "nav.dashboard"
  | "nav.validations"
  | "nav.projects"
  | "nav.execution"
  | "nav.reports"
  | "nav.connections"
  | "nav.aiChatbot"
  | "nav.mappingReader"
  | "nav.sqlGenerator"
  | "nav.testCaseGenerator"
  | "nav.aiReportExplainer"
  | "nav.settings"
  | "nav.admin"
  | "nav.accessibility"
  | "layout.enterpriseConsole"
  | "layout.role"
  | "layout.language"
  | "layout.welcome"
  | "layout.skipToContent"
  | "layout.shortcutHint";

const translations: Record<Locale, Record<TranslationKey, string>> = {
  en: {
    "nav.dashboard": "Dashboard",
    "nav.validations": "Validations",
    "nav.projects": "Projects",
    "nav.execution": "Execution",
    "nav.reports": "Reports",
    "nav.connections": "Connections",
    "nav.aiChatbot": "AI Chatbot",
    "nav.mappingReader": "Mapping Reader",
    "nav.sqlGenerator": "SQL Generator",
    "nav.testCaseGenerator": "Test Case Generator",
    "nav.aiReportExplainer": "AI Report Explainer",
    "nav.settings": "Settings",
    "nav.admin": "Administration",
    "nav.accessibility": "Accessibility",
    "layout.enterpriseConsole": "Enterprise Console",
    "layout.role": "Role",
    "layout.language": "Language",
    "layout.welcome": "Welcome",
    "layout.skipToContent": "Skip to main content",
    "layout.shortcutHint": "Keyboard shortcuts: Alt+1 Dashboard, Alt+2 Validations, Alt+3 Projects",
  },
  es: {
    "nav.dashboard": "Panel",
    "nav.validations": "Validaciones",
    "nav.projects": "Proyectos",
    "nav.execution": "Ejecucion",
    "nav.reports": "Informes",
    "nav.connections": "Conexiones",
    "nav.aiChatbot": "Chatbot IA",
    "nav.mappingReader": "Lector STM",
    "nav.sqlGenerator": "Generador SQL",
    "nav.testCaseGenerator": "Generador de Casos",
    "nav.aiReportExplainer": "Explicador de Reportes IA",
    "nav.settings": "Configuracion",
    "nav.admin": "Administracion",
    "nav.accessibility": "Accesibilidad",
    "layout.enterpriseConsole": "Consola Empresarial",
    "layout.role": "Rol",
    "layout.language": "Idioma",
    "layout.welcome": "Bienvenido",
    "layout.skipToContent": "Saltar al contenido principal",
    "layout.shortcutHint": "Atajos: Alt+1 Panel, Alt+2 Validaciones, Alt+3 Proyectos",
  },
  fr: {
    "nav.dashboard": "Tableau de bord",
    "nav.validations": "Validations",
    "nav.projects": "Projets",
    "nav.execution": "Execution",
    "nav.reports": "Rapports",
    "nav.connections": "Connexions",
    "nav.aiChatbot": "Chatbot IA",
    "nav.mappingReader": "Lecteur STM",
    "nav.sqlGenerator": "Generateur SQL",
    "nav.testCaseGenerator": "Generateur de Cas de Test",
    "nav.aiReportExplainer": "Explicateur de Rapports IA",
    "nav.settings": "Parametres",
    "nav.admin": "Administration",
    "nav.accessibility": "Accessibilite",
    "layout.enterpriseConsole": "Console Entreprise",
    "layout.role": "Role",
    "layout.language": "Langue",
    "layout.welcome": "Bienvenue",
    "layout.skipToContent": "Aller au contenu principal",
    "layout.shortcutHint": "Raccourcis: Alt+1 Tableau de bord, Alt+2 Validations, Alt+3 Projets",
  },
};

interface LocalizationContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TranslationKey) => string;
}

const LocalizationContext = createContext<LocalizationContextValue | null>(null);

export function LocalizationProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [locale, setLocale] = useState<Locale>("en");

  const value = useMemo(
    () => ({
      locale,
      setLocale,
      t: (key: TranslationKey) => translations[locale][key],
    }),
    [locale]
  );

  return <LocalizationContext.Provider value={value}>{children}</LocalizationContext.Provider>;
}

export function useLocalization(): LocalizationContextValue {
  const ctx = useContext(LocalizationContext);
  if (!ctx) {
    throw new Error("useLocalization must be used within LocalizationProvider");
  }
  return ctx;
}
