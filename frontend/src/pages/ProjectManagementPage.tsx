import FolderOpenRoundedIcon from "@mui/icons-material/FolderOpenRounded";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import StarBorderRoundedIcon from "@mui/icons-material/StarBorderRounded";
import StarRoundedIcon from "@mui/icons-material/StarRounded";
import TaskRoundedIcon from "@mui/icons-material/TaskRounded";
import ViewModuleRoundedIcon from "@mui/icons-material/ViewModuleRounded";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  IconButton,
  InputAdornment,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

interface ProjectItem {
  id: string;
  name: string;
  code: string;
  folders: number;
  suites: number;
  templates: number;
  favorite: boolean;
}

interface SuiteItem {
  id: string;
  name: string;
  projectCode: string;
  folder: string;
  status: "draft" | "active" | "archived";
}

interface TemplateItem {
  id: string;
  name: string;
  type: string;
  updatedBy: string;
  favorite: boolean;
}

const initialProjects: ProjectItem[] = [
  {
    id: "p1",
    name: "American Express Data Migration",
    code: "AMEX-DM-001",
    folders: 6,
    suites: 12,
    templates: 8,
    favorite: true,
  },
  {
    id: "p2",
    name: "Snowflake Migration Validation",
    code: "SNOW-VAL-001",
    folders: 4,
    suites: 9,
    templates: 5,
    favorite: false,
  },
  {
    id: "p3",
    name: "Revenue Integrity Controls",
    code: "REV-CTL-009",
    folders: 8,
    suites: 15,
    templates: 11,
    favorite: true,
  },
];

const suites: SuiteItem[] = [
  { id: "s1", name: "Daily Core Reconciliation", projectCode: "AMEX-DM-001", folder: "Daily", status: "active" },
  { id: "s2", name: "Monthly Financial Close", projectCode: "REV-CTL-009", folder: "Finance", status: "active" },
  { id: "s3", name: "Schema Drift Watch", projectCode: "SNOW-VAL-001", folder: "Schema", status: "draft" },
  { id: "s4", name: "Legacy Sunset Verification", projectCode: "AMEX-DM-001", folder: "Cutover", status: "archived" },
];

const templates: TemplateItem[] = [
  { id: "t1", name: "Warehouse to Lakehouse Baseline", type: "Data Comparison", updatedBy: "architect", favorite: true },
  { id: "t2", name: "API to Table Contract Validation", type: "Schema + Null", updatedBy: "qalead", favorite: false },
  { id: "t3", name: "Financial Precision Guardrail", type: "Precision/Scale", updatedBy: "admin", favorite: true },
];

const folders = ["Daily", "Finance", "Schema", "Cutover", "Adhoc", "Critical"];

export function ProjectManagementPage(): React.JSX.Element {
  const [searchText, setSearchText] = useState("");
  const [projects, setProjects] = useState(initialProjects);
  const [activeTab, setActiveTab] = useState(0);

  const normalizedSearch = searchText.trim().toLowerCase();

  const filteredProjects = useMemo(
    () =>
      projects.filter(
        (project) =>
          project.name.toLowerCase().includes(normalizedSearch) ||
          project.code.toLowerCase().includes(normalizedSearch)
      ),
    [projects, normalizedSearch]
  );

  const filteredSuites = useMemo(
    () =>
      suites.filter(
        (suite) =>
          suite.name.toLowerCase().includes(normalizedSearch) ||
          suite.projectCode.toLowerCase().includes(normalizedSearch) ||
          suite.folder.toLowerCase().includes(normalizedSearch)
      ),
    [normalizedSearch]
  );

  const filteredTemplates = useMemo(
    () =>
      templates.filter(
        (template) =>
          template.name.toLowerCase().includes(normalizedSearch) ||
          template.type.toLowerCase().includes(normalizedSearch)
      ),
    [normalizedSearch]
  );

  const favorites = useMemo(
    () => [
      ...projects.filter((item) => item.favorite).map((item) => ({ type: "Project", name: item.name, id: item.id })),
      ...templates.filter((item) => item.favorite).map((item) => ({ type: "Template", name: item.name, id: item.id })),
    ],
    [projects]
  );

  const toggleProjectFavorite = (id: string) => {
    setProjects((previous) =>
      previous.map((project) =>
        project.id === id ? { ...project, favorite: !project.favorite } : project
      )
    );
  };

  return (
    <Stack spacing={2.2}>
      <Stack direction={{ xs: "column", md: "row" }} spacing={1.2} alignItems={{ xs: "stretch", md: "center" }}>
        <Typography variant="h4" sx={{ flexGrow: 1 }}>
          Project Management
        </Typography>
        <TextField
          size="small"
          placeholder="Search projects, folders, suites, templates"
          value={searchText}
          onChange={(event) => setSearchText(event.target.value)}
          sx={{ minWidth: { xs: "100%", md: 420 } }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchRoundedIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
      </Stack>

      <Tabs
        value={activeTab}
        onChange={(_event, next) => setActiveTab(next)}
        variant="scrollable"
        allowScrollButtonsMobile
      >
        <Tab icon={<ViewModuleRoundedIcon />} iconPosition="start" label="Projects" />
        <Tab icon={<FolderOpenRoundedIcon />} iconPosition="start" label="Folders" />
        <Tab icon={<TaskRoundedIcon />} iconPosition="start" label="Validation Suites" />
        <Tab icon={<ViewModuleRoundedIcon />} iconPosition="start" label="Templates" />
        <Tab icon={<StarRoundedIcon />} iconPosition="start" label="Favorites" />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={2}>
          {filteredProjects.map((project) => (
            <Grid key={project.id} size={{ xs: 12, md: 6, xl: 4 }}>
              <Card>
                <CardContent>
                  <Stack spacing={1.2}>
                    <Stack direction="row" alignItems="center" justifyContent="space-between">
                      <Typography variant="h6">{project.name}</Typography>
                      <IconButton size="small" onClick={() => toggleProjectFavorite(project.id)}>
                        {project.favorite ? <StarRoundedIcon color="warning" /> : <StarBorderRoundedIcon />}
                      </IconButton>
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      {project.code}
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      <Chip size="small" label={`${project.folders} folders`} />
                      <Chip size="small" label={`${project.suites} suites`} />
                      <Chip size="small" label={`${project.templates} templates`} />
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Stack spacing={1.2}>
              <Typography variant="h6">Folders</Typography>
              <Typography variant="body2" color="text.secondary">
                Organize suites by business domain, cadence, or criticality.
              </Typography>
              <Divider />
              <Grid container spacing={1.2}>
                {folders
                  .filter((folder) => folder.toLowerCase().includes(normalizedSearch))
                  .map((folder) => (
                    <Grid key={folder} size={{ xs: 12, sm: 6, lg: 4 }}>
                      <Box
                        sx={{
                          border: "1px solid",
                          borderColor: "divider",
                          borderRadius: 2,
                          p: 1.2,
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                        }}
                      >
                        <FolderOpenRoundedIcon color="primary" fontSize="small" />
                        <Typography variant="body2" fontWeight={600}>
                          {folder}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
              </Grid>
            </Stack>
          </CardContent>
        </Card>
      )}

      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Stack spacing={1.2}>
              <Typography variant="h6">Validation Suites</Typography>
              <Divider />
              <Stack spacing={1}>
                {filteredSuites.map((suite) => (
                  <Box
                    key={suite.id}
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      p: 1.2,
                      borderRadius: 2,
                      border: "1px solid",
                      borderColor: "divider",
                      gap: 1,
                    }}
                  >
                    <Stack>
                      <Typography variant="body2" fontWeight={700}>
                        {suite.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {suite.projectCode} • {suite.folder}
                      </Typography>
                    </Stack>
                    <Chip
                      size="small"
                      label={suite.status}
                      color={suite.status === "active" ? "success" : suite.status === "draft" ? "warning" : "default"}
                      variant="outlined"
                    />
                  </Box>
                ))}
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      )}

      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Stack spacing={1.2}>
              <Typography variant="h6">Templates</Typography>
              <Divider />
              <Grid container spacing={1.2}>
                {filteredTemplates.map((template) => (
                  <Grid key={template.id} size={{ xs: 12, md: 6 }}>
                    <Box sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
                        <Stack>
                          <Typography variant="body2" fontWeight={700}>
                            {template.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {template.type} • Updated by {template.updatedBy}
                          </Typography>
                        </Stack>
                        {template.favorite ? <StarRoundedIcon color="warning" fontSize="small" /> : <StarBorderRoundedIcon fontSize="small" />}
                      </Stack>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Stack>
          </CardContent>
        </Card>
      )}

      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Stack spacing={1.2}>
              <Typography variant="h6">Favorites</Typography>
              <Divider />
              {favorites.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No favorites selected yet.
                </Typography>
              ) : (
                <Stack spacing={1}>
                  {favorites
                    .filter((item) => item.name.toLowerCase().includes(normalizedSearch))
                    .map((item) => (
                      <Box
                        key={item.id}
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          border: "1px solid",
                          borderColor: "divider",
                          borderRadius: 2,
                          p: 1.2,
                        }}
                      >
                        <Typography variant="body2" fontWeight={600}>
                          {item.name}
                        </Typography>
                        <Chip size="small" label={item.type} variant="outlined" />
                      </Box>
                    ))}
                </Stack>
              )}
            </Stack>
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}
