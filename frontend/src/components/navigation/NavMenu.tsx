import { List, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import { NavLink } from "react-router-dom";

import { navItems } from "../../config/navigation";
import { useAuth } from "../../context/AuthContext";
import { useLocalization } from "../../context/LocalizationContext";

export function NavMenu({ onNavigate }: { onNavigate?: () => void }): React.JSX.Element {
  const {
    user: { role },
  } = useAuth();
  const { t } = useLocalization();

  const allowedItems = navItems.filter((item) => item.roles.includes(role));

  return (
    <List sx={{ pt: 1 }}>
      {allowedItems.map((item) => {
        const Icon = item.icon;
        return (
          <ListItemButton
            key={item.id}
            component={NavLink}
            to={item.path}
            onClick={onNavigate}
            sx={{
              borderRadius: 2,
              mx: 1,
              mb: 0.4,
              "&.active": {
                bgcolor: "primary.main",
                color: "primary.contrastText",
                "& .MuiListItemIcon-root": {
                  color: "primary.contrastText",
                },
              },
            }}
          >
            <ListItemIcon>
              <Icon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary={item.labelKey ? t(item.labelKey) : item.label} />
          </ListItemButton>
        );
      })}
    </List>
  );
}