import { Navigate, Route, Routes } from "react-router-dom";

import { DashboardLayout } from "./components/layout/DashboardLayout";
import { navItems } from "./config/navigation";
import { useAuth } from "./context/AuthContext";
import { OverviewPage } from "./pages/OverviewPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { ConnectionManagementPage } from "./pages/ConnectionManagementPage";
import { AdminConsolePage } from "./pages/AdminConsolePage";
import { LoginPage } from "./pages/LoginPage";
import { AccessibilityPage } from "./pages/AccessibilityPage";
import { AIChatbotPage } from "./pages/AIChatbotPage";
import { AIReportExplainerPage } from "./pages/AIReportExplainerPage";
import { ExecutionMonitoringPage } from "./pages/ExecutionMonitoringPage";
import { MappingReaderPage } from "./pages/MappingReaderPage";
import { ProjectManagementPage } from "./pages/ProjectManagementPage";
import { ReportDashboardPage } from "./pages/ReportDashboardPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SQLGeneratorPage } from "./pages/SQLGeneratorPage";
import { TestCaseGeneratorPage } from "./pages/TestCaseGeneratorPage";
import { ValidationBuilderPage } from "./pages/ValidationBuilderPage";

function ProtectedRoute({
  allowedRoles,
  children,
}: {
  allowedRoles: string[];
  children: React.ReactNode;
}): React.JSX.Element {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

export function App(): React.JSX.Element {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        {navItems
          .filter((item) => item.path !== "/")
          .map((item) => (
            <Route
              key={item.id}
              path={item.path}
              element={
                <ProtectedRoute allowedRoles={item.roles}>
                  {item.path === "/projects" ? (
                    <ProjectManagementPage />
                  ) : item.path === "/validations" ? (
                    <ValidationBuilderPage />
                  ) : item.path === "/execution" ? (
                    <ExecutionMonitoringPage />
                  ) : item.path === "/reports" ? (
                    <ReportDashboardPage />
                  ) : item.path === "/admin" ? (
                    <AdminConsolePage />
                  ) : item.path === "/settings" ? (
                    <SettingsPage />
                  ) : item.path === "/ai-chatbot" ? (
                    <AIChatbotPage />
                  ) : item.path === "/mapping-reader" ? (
                    <MappingReaderPage />
                  ) : item.path === "/sql-generator" ? (
                    <SQLGeneratorPage />
                  ) : item.path === "/test-case-generator" ? (
                    <TestCaseGeneratorPage />
                  ) : item.path === "/ai-report-explainer" ? (
                    <AIReportExplainerPage />
                  ) : item.path === "/accessibility" ? (
                    <AccessibilityPage />
                  ) : item.path === "/connections" ? (
                    <ConnectionManagementPage />
                  ) : (
                    <PlaceholderPage title={item.label} subtitle={`${item.label} module shell is ready for Prompt 24+ expansion.`} />
                  )}
                </ProtectedRoute>
              }
            />
          ))}
      </Routes>
    </DashboardLayout>
  );
}