import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";
import {
  AppBar,
  Avatar,
  Box,
  Drawer,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Toolbar,
  Typography,
  useMediaQuery,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { Locale, useLocalization } from "../../context/LocalizationContext";
import { useColorMode } from "../../theme";
import type { UserRole } from "../../types/rbac";
import { NavMenu } from "../navigation/NavMenu";

const drawerWidth = 272;

const roleLabels: Record<UserRole, string> = {
  platform_admin: "Platform Admin",
  organization_admin: "Organization Admin",
  architect: "Architect",
  qa_lead: "QA Lead",
  qa_engineer: "QA Engineer",
  viewer: "Viewer",
  guest: "Guest",
};

export function DashboardLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [mobileOpen, setMobileOpen] = useState(false);
  const materialTheme = useTheme();
  const isDesktop = useMediaQuery(materialTheme.breakpoints.up("md"));
  const { mode, toggleMode } = useColorMode();
  const { user, setRole } = useAuth();
  const { locale, setLocale, t } = useLocalization();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const inInput =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.getAttribute("contenteditable") === "true";
      if (inInput || !event.altKey) {
        return;
      }

      if (event.key === "1") {
        event.preventDefault();
        navigate("/");
      }
      if (event.key === "2") {
        event.preventDefault();
        navigate("/validations");
      }
      if (event.key === "3") {
        event.preventDefault();
        navigate("/projects");
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [navigate]);

  const drawerContent = useMemo(
    () => (
      <Box sx={{ p: 1.5 }}>
        <Typography variant="h6" sx={{ px: 1.5, py: 1 }}>
          TKK Validator
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ px: 1.5 }}>
          {t("layout.enterpriseConsole")}
        </Typography>
        <NavMenu onNavigate={() => setMobileOpen(false)} />
      </Box>
    ),
    [t]
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <a href="#main-content" className="skip-link">
        {t("layout.skipToContent")}
      </a>
      <AppBar
        position="fixed"
        color="transparent"
        elevation={0}
        sx={{
          backdropFilter: "blur(14px)",
          borderBottom: "1px solid",
          borderColor: "divider",
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ gap: 1.2 }}>
          {!isDesktop && (
            <IconButton color="inherit" onClick={() => setMobileOpen((prev) => !prev)} aria-label="Toggle navigation menu">
              <MenuRoundedIcon />
            </IconButton>
          )}
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {t("layout.welcome")}, {user.name}
          </Typography>
          <FormControl size="small" sx={{ minWidth: 190 }}>
            <InputLabel id="role-select-label">{t("layout.role")}</InputLabel>
            <Select
              labelId="role-select-label"
              value={user.role}
              label={t("layout.role")}
              onChange={(event) => setRole(event.target.value as UserRole)}
            >
              {Object.entries(roleLabels).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 130 }}>
            <InputLabel id="lang-select-label">{t("layout.language")}</InputLabel>
            <Select
              labelId="lang-select-label"
              value={locale}
              label={t("layout.language")}
              onChange={(event) => setLocale(event.target.value as Locale)}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="es">Espanol</MenuItem>
              <MenuItem value="fr">Francais</MenuItem>
            </Select>
          </FormControl>
          <IconButton color="inherit" onClick={toggleMode} aria-label="Toggle color theme">
            {mode === "dark" ? <LightModeRoundedIcon /> : <DarkModeRoundedIcon />}
          </IconButton>
          <Stack direction="row" spacing={1} alignItems="center">
            <Avatar sx={{ bgcolor: "secondary.main", width: 34, height: 34 }}>{user.name[0]}</Avatar>
            <Typography variant="body2" sx={{ display: { xs: "none", sm: "block" } }}>
              {roleLabels[user.role]}
            </Typography>
          </Stack>
        </Toolbar>
        <Typography variant="caption" sx={{ px: 2, pb: 0.8, color: "text.secondary", display: { xs: "none", md: "block" } }}>
          {t("layout.shortcutHint")}
        </Typography>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { md: drawerWidth },
          flexShrink: { md: 0 },
        }}
      >
        <Drawer
          variant={isDesktop ? "permanent" : "temporary"}
          open={isDesktop ? true : mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: "block",
            "& .MuiDrawer-paper": {
              width: drawerWidth,
              boxSizing: "border-box",
              borderRight: "1px solid",
              borderColor: "divider",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        id="main-content"
        tabIndex={-1}
        sx={{
          flexGrow: 1,
          p: { xs: 2, md: 3 },
          width: { md: `calc(100% - ${drawerWidth}px)` },
          background: (theme) =>
            theme.palette.mode === "dark"
              ? "radial-gradient(circle at top right, rgba(39,211,182,0.12), transparent 48%), radial-gradient(circle at bottom left, rgba(255,180,84,0.1), transparent 40%)"
              : "radial-gradient(circle at top right, rgba(0,121,107,0.1), transparent 48%), radial-gradient(circle at bottom left, rgba(239,108,0,0.08), transparent 40%)",
        }}
      >
        <Box className="sr-only" aria-live="polite" aria-atomic="true">
          Current page: {location.pathname}
        </Box>
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}