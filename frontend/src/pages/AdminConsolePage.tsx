import AdminPanelSettingsRoundedIcon from "@mui/icons-material/AdminPanelSettingsRounded";
import ApartmentRoundedIcon from "@mui/icons-material/ApartmentRounded";
import GavelRoundedIcon from "@mui/icons-material/GavelRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import KeyRoundedIcon from "@mui/icons-material/KeyRounded";
import ManageAccountsRoundedIcon from "@mui/icons-material/ManageAccountsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

interface OrgRow {
  id: string;
  name: string;
  status: "active" | "trial" | "suspended";
  users: number;
  teams: number;
}

interface UserRow {
  name: string;
  email: string;
  role: string;
  status: "active" | "invited" | "disabled";
}

interface TeamRow {
  team: string;
  owner: string;
  projects: number;
  members: number;
}

interface LicenseRow {
  item: string;
  used: number;
  total: number;
}

const organizations: OrgRow[] = [
  { id: "TKK-ORG-001", name: "TKK Technologies Pvt Ltd", status: "active", users: 84, teams: 7 },
  { id: "TKK-ORG-002", name: "TKK Data Labs", status: "trial", users: 12, teams: 2 },
  { id: "TKK-ORG-003", name: "TKK Analytics Europe", status: "suspended", users: 18, teams: 3 },
];

const users: UserRow[] = [
  { name: "Krishna", email: "admin@tkkvalidator.local", role: "Platform Admin", status: "active" },
  { name: "Ananya", email: "orgadmin@tkkvalidator.local", role: "Organization Admin", status: "active" },
  { name: "Rahul", email: "architect@tkkvalidator.local", role: "Architect", status: "active" },
  { name: "Mira", email: "qalead@tkkvalidator.local", role: "QA Lead", status: "invited" },
  { name: "Vikram", email: "viewer@tkkvalidator.local", role: "Viewer", status: "disabled" },
];

const teams: TeamRow[] = [
  { team: "Data Engineering Team", owner: "Rahul", projects: 4, members: 15 },
  { team: "Quality Automation", owner: "Mira", projects: 6, members: 11 },
  { team: "Platform Reliability", owner: "Krishna", projects: 3, members: 8 },
];

const permissionRows = [
  { feature: "Manage Organizations", platformAdmin: "yes", orgAdmin: "no", architect: "no", qaLead: "no" },
  { feature: "Manage Users", platformAdmin: "yes", orgAdmin: "yes", architect: "no", qaLead: "no" },
  { feature: "Manage Secrets", platformAdmin: "yes", orgAdmin: "yes", architect: "yes", qaLead: "no" },
  { feature: "Create Validation Jobs", platformAdmin: "yes", orgAdmin: "yes", architect: "yes", qaLead: "yes" },
  { feature: "Configure Schedulers", platformAdmin: "yes", orgAdmin: "yes", architect: "yes", qaLead: "no" },
];

const licenseRows: LicenseRow[] = [
  { item: "Named Users", used: 96, total: 150 },
  { item: "Execution Workers", used: 14, total: 20 },
  { item: "AI Provider Calls / Day", used: 18200, total: 50000 },
  { item: "Report Exports / Day", used: 410, total: 1000 },
];

const auditEvents = [
  "[2026-06-30 10:02:11] Admin role granted to orgadmin@tkkvalidator.local",
  "[2026-06-30 09:48:53] SMTP configuration updated by admin@tkkvalidator.local",
  "[2026-06-30 09:11:22] New team created: Platform Reliability",
  "[2026-06-30 08:56:44] Permission matrix changed: Configure Schedulers",
  "[2026-06-30 08:31:29] License usage threshold alert triggered (70%)",
];

export function AdminConsolePage(): React.JSX.Element {
  const [tab, setTab] = useState(0);

  const orgSummary = useMemo(
    () => ({
      active: organizations.filter((item) => item.status === "active").length,
      trial: organizations.filter((item) => item.status === "trial").length,
      suspended: organizations.filter((item) => item.status === "suspended").length,
    }),
    []
  );

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Administration Console</Typography>

      <Grid container spacing={1.2}>
        <Grid size={{ xs: 12, sm: 4 }}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Active Organizations
                  </Typography>
                  <Typography variant="h4">{orgSummary.active}</Typography>
                </Box>
                <ApartmentRoundedIcon color="primary" />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Trial Organizations
                  </Typography>
                  <Typography variant="h4">{orgSummary.trial}</Typography>
                </Box>
                <VerifiedRoundedIcon color="warning" />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Suspended Organizations
                  </Typography>
                  <Typography variant="h4">{orgSummary.suspended}</Typography>
                </Box>
                <GavelRoundedIcon color="error" />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Tabs value={tab} onChange={(_event, value) => setTab(value)} variant="scrollable" allowScrollButtonsMobile>
            <Tab icon={<ApartmentRoundedIcon />} iconPosition="start" label="Organizations" />
            <Tab icon={<ManageAccountsRoundedIcon />} iconPosition="start" label="Users" />
            <Tab icon={<GroupsRoundedIcon />} iconPosition="start" label="Teams" />
            <Tab icon={<KeyRoundedIcon />} iconPosition="start" label="Permissions" />
            <Tab icon={<VerifiedRoundedIcon />} iconPosition="start" label="License" />
            <Tab icon={<AdminPanelSettingsRoundedIcon />} iconPosition="start" label="Audit" />
          </Tabs>
          <Divider sx={{ my: 1.2 }} />

          {tab === 0 && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Organization ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Users</TableCell>
                  <TableCell align="right">Teams</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {organizations.map((org) => (
                  <TableRow key={org.id}>
                    <TableCell>{org.id}</TableCell>
                    <TableCell>{org.name}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={org.status}
                        color={org.status === "active" ? "success" : org.status === "trial" ? "warning" : "error"}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">{org.users}</TableCell>
                    <TableCell align="right">{org.teams}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {tab === 1 && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.email}>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.role}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={user.status}
                        color={user.status === "active" ? "success" : user.status === "invited" ? "warning" : "default"}
                        variant="outlined"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {tab === 2 && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Team</TableCell>
                  <TableCell>Owner</TableCell>
                  <TableCell align="right">Projects</TableCell>
                  <TableCell align="right">Members</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {teams.map((team) => (
                  <TableRow key={team.team}>
                    <TableCell>{team.team}</TableCell>
                    <TableCell>{team.owner}</TableCell>
                    <TableCell align="right">{team.projects}</TableCell>
                    <TableCell align="right">{team.members}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {tab === 3 && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Feature</TableCell>
                  <TableCell>Platform Admin</TableCell>
                  <TableCell>Org Admin</TableCell>
                  <TableCell>Architect</TableCell>
                  <TableCell>QA Lead</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {permissionRows.map((row) => (
                  <TableRow key={row.feature}>
                    <TableCell>{row.feature}</TableCell>
                    <TableCell>{row.platformAdmin}</TableCell>
                    <TableCell>{row.orgAdmin}</TableCell>
                    <TableCell>{row.architect}</TableCell>
                    <TableCell>{row.qaLead}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {tab === 4 && (
            <Stack spacing={1.2}>
              {licenseRows.map((item) => {
                const percentage = Math.round((item.used / item.total) * 100);
                return (
                  <Box key={item.item} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.1 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2" fontWeight={700}>
                        {item.item}
                      </Typography>
                      <Chip size="small" label={`${item.used}/${item.total}`} />
                    </Stack>
                    <Typography variant="caption" color="text.secondary">
                      Utilization: {percentage}%
                    </Typography>
                  </Box>
                );
              })}
            </Stack>
          )}

          {tab === 5 && (
            <List dense disablePadding>
              {auditEvents.map((event) => (
                <ListItem key={event} sx={{ borderBottom: "1px solid", borderColor: "divider" }}>
                  <ListItemIcon>
                    <AdminPanelSettingsRoundedIcon fontSize="small" color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={event} />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}
