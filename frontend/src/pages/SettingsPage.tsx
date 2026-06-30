import SecurityRoundedIcon from "@mui/icons-material/SecurityRounded";
import SmartToyRoundedIcon from "@mui/icons-material/SmartToyRounded";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import SyncRoundedIcon from "@mui/icons-material/SyncRounded";
import TuneRoundedIcon from "@mui/icons-material/TuneRounded";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

export function SettingsPage(): React.JSX.Element {
  const [tab, setTab] = useState(0);

  const [secretsMasked, setSecretsMasked] = useState(true);
  const [smtpTls, setSmtpTls] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [slackAlerts, setSlackAlerts] = useState(false);
  const [teamsAlerts, setTeamsAlerts] = useState(true);

  const [themeMode, setThemeMode] = useState("dark");
  const [storageProvider, setStorageProvider] = useState("local");
  const [aiProvider, setAiProvider] = useState("openai");

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Settings</Typography>

      <Card>
        <CardContent>
          <Tabs value={tab} onChange={(_event, value) => setTab(value)} variant="scrollable" allowScrollButtonsMobile>
            <Tab icon={<SecurityRoundedIcon />} iconPosition="start" label="Secrets" />
            <Tab icon={<TuneRoundedIcon />} iconPosition="start" label="Themes" />
            <Tab icon={<SyncRoundedIcon />} iconPosition="start" label="Notifications" />
            <Tab icon={<StorageRoundedIcon />} iconPosition="start" label="Storage" />
            <Tab icon={<SyncRoundedIcon />} iconPosition="start" label="SMTP" />
            <Tab icon={<SmartToyRoundedIcon />} iconPosition="start" label="AI Providers" />
          </Tabs>
          <Divider sx={{ my: 1.2 }} />

          {tab === 0 && (
            <Grid container spacing={1.2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  size="small"
                  label="Encryption Key Alias"
                  value="uv-secrets-kms-key"
                  InputProps={{ readOnly: true }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth size="small" label="Vault Namespace" value="tkk/prod/validation" />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <FormControlLabel
                  control={<Switch checked={secretsMasked} onChange={(event) => setSecretsMasked(event.target.checked)} />}
                  label="Mask secret values in UI and logs"
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Alert severity="info">
                  Secrets are encrypted at rest. Rotation hooks are enabled with a 30-day interval.
                </Alert>
              </Grid>
            </Grid>
          )}

          {tab === 1 && (
            <Grid container spacing={1.2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth size="small">
                  <InputLabel id="theme-mode-label">Theme Mode</InputLabel>
                  <Select
                    labelId="theme-mode-label"
                    label="Theme Mode"
                    value={themeMode}
                    onChange={(event) => setThemeMode(event.target.value)}
                  >
                    <MenuItem value="dark">Dark</MenuItem>
                    <MenuItem value="light">Light</MenuItem>
                    <MenuItem value="system">System</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth size="small" label="Primary Brand Color" value="#27d3b6" />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Alert severity="success">Theme settings are synchronized for all admin users in this workspace.</Alert>
              </Grid>
            </Grid>
          )}

          {tab === 2 && (
            <Grid container spacing={1.2}>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControlLabel
                  control={<Switch checked={emailAlerts} onChange={(event) => setEmailAlerts(event.target.checked)} />}
                  label="Email Alerts"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControlLabel
                  control={<Switch checked={slackAlerts} onChange={(event) => setSlackAlerts(event.target.checked)} />}
                  label="Slack Alerts"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControlLabel
                  control={<Switch checked={teamsAlerts} onChange={(event) => setTeamsAlerts(event.target.checked)} />}
                  label="Microsoft Teams Alerts"
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField fullWidth size="small" label="Alert Recipients" value="qa-lead@tkkvalidator.local,admin@tkkvalidator.local" />
              </Grid>
            </Grid>
          )}

          {tab === 3 && (
            <Grid container spacing={1.2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth size="small">
                  <InputLabel id="storage-provider-label">Storage Provider</InputLabel>
                  <Select
                    labelId="storage-provider-label"
                    label="Storage Provider"
                    value={storageProvider}
                    onChange={(event) => setStorageProvider(event.target.value)}
                  >
                    <MenuItem value="local">Local</MenuItem>
                    <MenuItem value="s3">Amazon S3</MenuItem>
                    <MenuItem value="azure_blob">Azure Blob</MenuItem>
                    <MenuItem value="gcs">Google Cloud Storage</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth size="small" label="Result Archive Path" value="/results/archive" />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Alert severity="info">Retention policy: 30 days. Automatic archival is enabled.</Alert>
              </Grid>
            </Grid>
          )}

          {tab === 4 && (
            <Grid container spacing={1.2}>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth size="small" label="SMTP Host" value="smtp.office365.com" />
              </Grid>
              <Grid size={{ xs: 12, md: 2 }}>
                <TextField fullWidth size="small" label="Port" value="587" />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <TextField fullWidth size="small" label="Username" value="noreply@tkkvalidator.local" />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <TextField fullWidth size="small" type="password" label="Password" value="********" />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <FormControlLabel
                  control={<Switch checked={smtpTls} onChange={(event) => setSmtpTls(event.target.checked)} />}
                  label="Use TLS"
                />
              </Grid>
            </Grid>
          )}

          {tab === 5 && (
            <Grid container spacing={1.2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth size="small">
                  <InputLabel id="ai-provider-label">Default AI Provider</InputLabel>
                  <Select
                    labelId="ai-provider-label"
                    label="Default AI Provider"
                    value={aiProvider}
                    onChange={(event) => setAiProvider(event.target.value)}
                  >
                    <MenuItem value="openai">OpenAI</MenuItem>
                    <MenuItem value="azure_openai">Azure OpenAI</MenuItem>
                    <MenuItem value="ollama">Ollama</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth size="small" label="Model" value="gpt-5.3-codex" />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Box sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                  <Typography variant="body2" fontWeight={700}>
                    Provider Health
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    OpenAI: Operational • Azure OpenAI: Operational • Ollama: Standby
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}
