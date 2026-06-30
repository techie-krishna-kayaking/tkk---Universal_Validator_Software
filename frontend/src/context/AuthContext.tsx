import React, { createContext, useContext, useMemo, useState } from "react";

import type { AuthUser, UserRole } from "../types/rbac";

interface AuthContextValue {
  user: AuthUser;
  setRole: (role: UserRole) => void;
}

const demoUser: AuthUser = {
  id: "user-demo-1",
  name: "Krishna",
  email: "architect@tkkvalidator.local",
  role: "architect",
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [role, setRole] = useState<UserRole>(demoUser.role);

  const value = useMemo(
    () => ({
      user: { ...demoUser, role },
      setRole,
    }),
    [role]
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