import { useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  FormControlLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";

import { DEMO_MODE_ACCOUNTS, DEV_ACCOUNTS, DEV_ORGANIZATION, isNonProductionEnvironment } from "../config/devAuth";
import { useAuth } from "../context/AuthContext";

const LOGIN_BANNER = [
  "===============================================",
  "     TKK Universal Validator - DEV MODE",
  "===============================================",
  "Environment : Development",
  "Version     : v1.0.0-dev",
  `Organization: ${DEV_ORGANIZATION.name}`,
  "",
  "Use one of the following accounts:",
  "",
  "Platform Admin",
  "admin / Admin@123",
  "",
  "Architect",
  "architect / Architect@123",
  "",
  "QA Lead",
  "qalead / QALead@123",
  "",
  "QA Engineer",
  "tester / Tester@123",
  "",
  "Viewer",
  "viewer / Viewer@123",
  "===============================================",
].join("\n");

export function LoginPage(): React.JSX.Element {
  const { login, isDemoModeAvailable } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [demoModeEnabled, setDemoModeEnabled] = useState(false);
  const [demoAccountUsername, setDemoAccountUsername] = useState(DEMO_MODE_ACCOUNTS[0]?.username ?? "admin");

  const selectedDemoAccount = useMemo(
    () => DEMO_MODE_ACCOUNTS.find((account) => account.username === demoAccountUsername) ?? DEMO_MODE_ACCOUNTS[0],
    [demoAccountUsername]
  );

  const applyDemoAutofill = (): void => {
    if (!selectedDemoAccount) {
      return;
    }

    setIdentifier(selectedDemoAccount.username);
    setPassword(selectedDemoAccount.password);
    setError(null);
  };

  const onSubmit = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const ok = login(identifier, password);
    if (!ok) {
      setError("Invalid credentials. Use one of the predefined development accounts.");
      return;
    }
    setError(null);
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        p: 2,
        background:
          "radial-gradient(circle at 15% 20%, rgba(0,121,107,0.18), transparent 40%), radial-gradient(circle at 85% 10%, rgba(255,167,38,0.18), transparent 38%), linear-gradient(120deg, #f8fbf8 0%, #eef5ff 100%)",
      }}
    >
      <Card sx={{ width: "100%", maxWidth: 640, borderRadius: 3, boxShadow: "0 20px 60px rgba(0,0,0,0.12)" }}>
        <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            TKK Universal Validator
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Sign in to continue to the enterprise console.
          </Typography>

          {isNonProductionEnvironment() && (
            <Alert severity="info" sx={{ mt: 2, mb: 2, whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 12 }}>
              {LOGIN_BANNER}
            </Alert>
          )}

          <Box component="form" onSubmit={onSubmit} sx={{ mt: 1 }}>
            <Stack spacing={1.5}>
              <TextField
                label="Username or Email"
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                autoComplete="username"
                required
              />
              <TextField
                type="password"
                label="Password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />

              {isDemoModeAvailable && (
                <>
                  <Divider sx={{ my: 0.5 }} />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={demoModeEnabled}
                        onChange={(event) => setDemoModeEnabled(event.target.checked)}
                        color="secondary"
                      />
                    }
                    label="Demo Mode (Non-production only)"
                  />

                  {demoModeEnabled && (
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                      <Select
                        size="small"
                        value={demoAccountUsername}
                        onChange={(event) => setDemoAccountUsername(event.target.value)}
                        sx={{ minWidth: 220 }}
                      >
                        {DEMO_MODE_ACCOUNTS.map((account) => (
                          <MenuItem key={account.username} value={account.username}>
                            {account.label} ({account.username})
                          </MenuItem>
                        ))}
                      </Select>
                      <Button variant="outlined" onClick={applyDemoAutofill}>
                        Autofill Credentials
                      </Button>
                    </Stack>
                  )}
                </>
              )}

              {error && <Alert severity="error">{error}</Alert>}

              <Button type="submit" variant="contained" size="large">
                Sign In
              </Button>

              <Typography variant="caption" color="text.secondary">
                Organization: {DEV_ORGANIZATION.name} ({DEV_ORGANIZATION.id})
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Team: Data Engineering Team (TEAM-DE-001)
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Available accounts: {DEV_ACCOUNTS.map((account) => account.username).join(", ")}
              </Typography>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
