import React, { createContext, useContext, useMemo, useState } from "react";

import { DEV_ACCOUNTS, isNonProductionEnvironment } from "../config/devAuth";
import type { AuthUser, UserRole } from "../types/rbac";

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isDemoModeAvailable: boolean;
  login: (identifier: string, password: string) => boolean;
  logout: () => void;
  setRole: (role: UserRole) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [user, setUser] = useState<AuthUser | null>(null);

  const login = (identifier: string, password: string): boolean => {
    const normalizedIdentifier = identifier.trim().toLowerCase();
    const account = DEV_ACCOUNTS.find(
      (candidate) =>
        (candidate.username === normalizedIdentifier || candidate.email.toLowerCase() === normalizedIdentifier) &&
        candidate.password === password
    );

    if (!account) {
      return false;
    }

    setUser({
      id: `dev-user-${account.username}`,
      username: account.username,
      name: account.label,
      email: account.email,
      role: account.role,
    });
    return true;
  };

  const logout = (): void => {
    setUser(null);
  };

  const setRole = (role: UserRole): void => {
    setUser((current) => {
      if (!current) {
        return current;
      }
      return { ...current, role };
    });
  };

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isDemoModeAvailable: isNonProductionEnvironment(),
      login,
      logout,
      setRole,
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}