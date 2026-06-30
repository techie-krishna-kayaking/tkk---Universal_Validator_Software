import React, { createContext, useContext, useMemo, useState } from "react";
import { createTheme, Theme } from "@mui/material/styles";

import type { ThemeMode } from "./types/rbac";

interface ColorModeContextValue {
  mode: ThemeMode;
  toggleMode: () => void;
}

const ColorModeContext = createContext<ColorModeContextValue | null>(null);

export function ColorModeProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [mode, setMode] = useState<ThemeMode>("dark");

  const value = useMemo(
    () => ({
      mode,
      toggleMode: () => setMode((prev) => (prev === "dark" ? "light" : "dark")),
    }),
    [mode]
  );

  return <ColorModeContext.Provider value={value}>{children}</ColorModeContext.Provider>;
}

export function useColorMode(): ColorModeContextValue {
  const ctx = useContext(ColorModeContext);
  if (!ctx) {
    throw new Error("useColorMode must be used within ColorModeProvider");
  }
  return ctx;
}

export function useAppTheme(): Theme {
  const { mode } = useColorMode();

  return useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: mode === "dark" ? "#27d3b6" : "#00796b",
          },
          secondary: {
            main: mode === "dark" ? "#ffb454" : "#ef6c00",
          },
          background: {
            default: mode === "dark" ? "#0d141d" : "#f3f7fb",
            paper: mode === "dark" ? "#141f2b" : "#ffffff",
          },
        },
        shape: {
          borderRadius: 14,
        },
        typography: {
          fontFamily: "Space Grotesk, sans-serif",
          h4: {
            fontWeight: 700,
            letterSpacing: "0.02em",
          },
          h6: {
            fontWeight: 700,
          },
        },
        components: {
          MuiCard: {
            styleOverrides: {
              root: {
                border: mode === "dark" ? "1px solid rgba(39, 211, 182, 0.14)" : "1px solid rgba(0, 121, 107, 0.12)",
                boxShadow: mode === "dark" ? "0 12px 24px rgba(0,0,0,0.24)" : "0 8px 20px rgba(18, 38, 63, 0.08)",
              },
            },
          },
        },
      }),
    [mode]
  );
}