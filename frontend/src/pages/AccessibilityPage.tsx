import AccessibilityNewRoundedIcon from "@mui/icons-material/AccessibilityNewRounded";
import GTranslateRoundedIcon from "@mui/icons-material/GTranslateRounded";
import KeyboardRoundedIcon from "@mui/icons-material/KeyboardRounded";
import RecordVoiceOverRoundedIcon from "@mui/icons-material/RecordVoiceOverRounded";
import {
  Alert,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";

import { useLocalization } from "../context/LocalizationContext";

export function AccessibilityPage(): React.JSX.Element {
  const { locale } = useLocalization();

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Accessibility & Localization</Typography>

      <Card>
        <CardContent>
          <Stack spacing={1.2}>
            <Typography variant="h6">Accessibility</Typography>
            <Typography variant="body2" color="text.secondary">
              Keyboard-first navigation, visible focus states, skip links, and ARIA labels are enabled.
            </Typography>
            <Divider />
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <KeyboardRoundedIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary="Keyboard Support" secondary="Alt+1 Dashboard, Alt+2 Validations, Alt+3 Projects." />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <RecordVoiceOverRoundedIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary="Screen Reader" secondary="Route change announcements are provided via aria-live regions." />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <AccessibilityNewRoundedIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary="Focus Visibility" secondary="High-contrast focus rings are shown for keyboard users." />
              </ListItem>
            </List>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack spacing={1.2}>
            <Typography variant="h6">Localization</Typography>
            <Typography variant="body2" color="text.secondary">
              The interface is multi-language ready with runtime locale switching in the top bar.
            </Typography>
            <Divider />
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <GTranslateRoundedIcon color="secondary" />
                </ListItemIcon>
                <ListItemText primary="Supported Locales" secondary="English, Spanish, French" />
              </ListItem>
            </List>
            <Alert severity="info">Current locale: {locale.toUpperCase()}</Alert>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
