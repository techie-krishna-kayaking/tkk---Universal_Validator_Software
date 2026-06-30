import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import CloudDoneRoundedIcon from "@mui/icons-material/CloudDoneRounded";
import DataObjectRoundedIcon from "@mui/icons-material/DataObjectRounded";
import ErrorRoundedIcon from "@mui/icons-material/ErrorRounded";
import HubRoundedIcon from "@mui/icons-material/HubRounded";
import LinkRoundedIcon from "@mui/icons-material/LinkRounded";
import ManageSearchRoundedIcon from "@mui/icons-material/ManageSearchRounded";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

interface ConnectorDefinition {
  id: string;
  name: string;
  category: "files" | "databases" | "cloud" | "big_data" | "apis";
  protocol: string;
  authModes: string[];
}

interface MetadataItem {
  objectName: string;
  objectType: string;
  columns: string;
  sampleRows: number;
}

interface ConnectionFormState {
  endpoint: string;
  port: string;
  databaseOrPath: string;
  username: string;
  password: string;
  token: string;
}

const connectors: ConnectorDefinition[] = [
  { id: "csv", name: "CSV", category: "files", protocol: "file", authModes: ["none"] },
  { id: "tsv", name: "TSV", category: "files", protocol: "file", authModes: ["none"] },
  { id: "txt", name: "TXT", category: "files", protocol: "file", authModes: ["none"] },
  { id: "excel", name: "Excel", category: "files", protocol: "file", authModes: ["none"] },
  { id: "json", name: "JSON", category: "files", protocol: "file", authModes: ["none"] },
  { id: "xml", name: "XML", category: "files", protocol: "file", authModes: ["none"] },
  { id: "parquet", name: "Parquet", category: "files", protocol: "file", authModes: ["none"] },
  { id: "avro", name: "Avro", category: "files", protocol: "file", authModes: ["none"] },
  { id: "orc", name: "ORC", category: "files", protocol: "file", authModes: ["none"] },
  { id: "feather", name: "Feather", category: "files", protocol: "file", authModes: ["none"] },
  { id: "arrow", name: "Arrow", category: "files", protocol: "file", authModes: ["none"] },
  { id: "delta", name: "Delta", category: "files", protocol: "file", authModes: ["none"] },
  { id: "iceberg", name: "Iceberg", category: "files", protocol: "file", authModes: ["none"] },
  { id: "hudi", name: "Hudi", category: "files", protocol: "file", authModes: ["none"] },
  { id: "twbx", name: "Tableau TWBX", category: "files", protocol: "file", authModes: ["none"] },
  { id: "oracle", name: "Oracle", category: "databases", protocol: "jdbc", authModes: ["basic", "token"] },
  { id: "sqlserver", name: "SQL Server", category: "databases", protocol: "jdbc", authModes: ["basic"] },
  { id: "postgres", name: "PostgreSQL", category: "databases", protocol: "jdbc", authModes: ["basic"] },
  { id: "mysql", name: "MySQL", category: "databases", protocol: "jdbc", authModes: ["basic"] },
  { id: "snowflake", name: "Snowflake", category: "databases", protocol: "jdbc", authModes: ["basic", "token"] },
  { id: "redshift", name: "Redshift", category: "databases", protocol: "jdbc", authModes: ["basic"] },
  { id: "bigquery", name: "BigQuery", category: "databases", protocol: "http", authModes: ["token"] },
  { id: "duckdb", name: "DuckDB", category: "databases", protocol: "file", authModes: ["none"] },
  { id: "s3", name: "Amazon S3", category: "cloud", protocol: "https", authModes: ["token"] },
  { id: "azureblob", name: "Azure Blob", category: "cloud", protocol: "https", authModes: ["token"] },
  { id: "adls", name: "Azure Data Lake", category: "cloud", protocol: "https", authModes: ["token"] },
  { id: "gcs", name: "Google Cloud Storage", category: "cloud", protocol: "https", authModes: ["token"] },
  { id: "onedrive", name: "OneDrive", category: "cloud", protocol: "https", authModes: ["token"] },
  { id: "sharepoint", name: "SharePoint", category: "cloud", protocol: "https", authModes: ["token"] },
  { id: "spark", name: "Spark", category: "big_data", protocol: "thrift", authModes: ["basic", "token"] },
  { id: "hive", name: "Hive", category: "big_data", protocol: "thrift", authModes: ["basic"] },
  { id: "kafka", name: "Kafka", category: "big_data", protocol: "tcp", authModes: ["basic", "token"] },
  { id: "rest", name: "REST API", category: "apis", protocol: "https", authModes: ["token", "basic"] },
  { id: "soap", name: "SOAP API", category: "apis", protocol: "https", authModes: ["token", "basic"] },
  { id: "graphql", name: "GraphQL", category: "apis", protocol: "https", authModes: ["token"] },
  { id: "openapi", name: "OpenAPI", category: "apis", protocol: "https", authModes: ["token"] },
];

const categoryLabels: Record<ConnectorDefinition["category"], string> = {
  files: "Files",
  databases: "Databases",
  cloud: "Cloud Storage",
  big_data: "Big Data",
  apis: "APIs",
};

function buildMetadataPreview(connector: ConnectorDefinition): MetadataItem[] {
  if (connector.category === "databases") {
    return [
      { objectName: "public.customers", objectType: "table", columns: "id,name,status,created_at", sampleRows: 5000 },
      { objectName: "public.orders", objectType: "table", columns: "order_id,customer_id,amount,order_date", sampleRows: 22000 },
      { objectName: "analytics.monthly_kpis", objectType: "view", columns: "month,pass_rate,failure_rate", sampleRows: 24 },
    ];
  }
  if (connector.category === "files") {
    return [
      { objectName: "landing/source_snapshot.parquet", objectType: "file", columns: "id,name,amount,status", sampleRows: 120000 },
      { objectName: "landing/target_snapshot.parquet", objectType: "file", columns: "id,name,amount,status", sampleRows: 119980 },
      { objectName: "archive/reports.json", objectType: "file", columns: "workflow_id,result,score,created_at", sampleRows: 428 },
    ];
  }
  if (connector.category === "cloud") {
    return [
      { objectName: "bucket://raw/amex/", objectType: "prefix", columns: "object_key,size,last_modified", sampleRows: 820 },
      { objectName: "bucket://curated/snow/", objectType: "prefix", columns: "object_key,size,last_modified", sampleRows: 410 },
      { objectName: "bucket://reports/", objectType: "prefix", columns: "object_key,size,last_modified", sampleRows: 207 },
    ];
  }
  if (connector.category === "big_data") {
    return [
      { objectName: "hive.prod.transactions", objectType: "table", columns: "txn_id,tenant_id,amount,event_ts", sampleRows: 2500000 },
      { objectName: "hive.prod.validations", objectType: "table", columns: "run_id,status,score,run_at", sampleRows: 760000 },
      { objectName: "kafka.validation.events", objectType: "topic", columns: "event_id,event_type,payload,created_at", sampleRows: 180000 },
    ];
  }
  return [
    { objectName: "/v1/validations/runs", objectType: "endpoint", columns: "run_id,status,started_at,ended_at", sampleRows: 1200 },
    { objectName: "/v1/projects", objectType: "endpoint", columns: "project_id,name,owner,active", sampleRows: 83 },
    { objectName: "/v1/reports", objectType: "endpoint", columns: "report_id,type,format,created_at", sampleRows: 428 },
  ];
}

const initialForm: ConnectionFormState = {
  endpoint: "",
  port: "",
  databaseOrPath: "",
  username: "",
  password: "",
  token: "",
};

export function ConnectionManagementPage(): React.JSX.Element {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<"all" | ConnectorDefinition["category"]>("all");
  const [selectedConnector, setSelectedConnector] = useState<ConnectorDefinition>(connectors[0]);
  const [activeTab, setActiveTab] = useState(0);
  const [form, setForm] = useState<ConnectionFormState>(initialForm);
  const [credentialResult, setCredentialResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [connectionResult, setConnectionResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [metadataRows, setMetadataRows] = useState<MetadataItem[]>([]);

  const filteredConnectors = useMemo(() => {
    return connectors.filter((connector) => {
      const categoryMatch = selectedCategory === "all" || connector.category === selectedCategory;
      const searchMatch =
        connector.name.toLowerCase().includes(search.toLowerCase()) ||
        connector.protocol.toLowerCase().includes(search.toLowerCase());
      return categoryMatch && searchMatch;
    });
  }, [search, selectedCategory]);

  const connectorStats = useMemo(() => {
    return {
      total: connectors.length,
      files: connectors.filter((item) => item.category === "files").length,
      databases: connectors.filter((item) => item.category === "databases").length,
      cloud: connectors.filter((item) => item.category === "cloud").length,
      apis: connectors.filter((item) => item.category === "apis").length,
    };
  }, []);

  const updateField = (key: keyof ConnectionFormState, value: string) => {
    setForm((previous) => ({ ...previous, [key]: value }));
  };

  const validateCredentials = () => {
    const needsBasic = selectedConnector.authModes.includes("basic");
    const needsToken = selectedConnector.authModes.includes("token");

    if (!form.endpoint.trim()) {
      setCredentialResult({ ok: false, message: "Endpoint/Host is required." });
      return;
    }

    if (needsBasic && (!form.username.trim() || !form.password.trim())) {
      setCredentialResult({ ok: false, message: "Username and password are required for this connector." });
      return;
    }

    if (needsToken && !form.token.trim()) {
      setCredentialResult({ ok: false, message: "Token/Key is required for this connector." });
      return;
    }

    setCredentialResult({ ok: true, message: "Credentials validated successfully." });
  };

  const testConnection = () => {
    if (!credentialResult?.ok) {
      setConnectionResult({ ok: false, message: "Please validate credentials before running a connection test." });
      return;
    }

    const simulatedLatencyMs = 80 + Math.floor(Math.random() * 320);
    setConnectionResult({
      ok: true,
      message: `Connection successful via ${selectedConnector.protocol.toUpperCase()} in ${simulatedLatencyMs} ms.`,
    });
  };

  const previewMetadata = () => {
    if (!connectionResult?.ok) {
      setMetadataRows([]);
      return;
    }
    setMetadataRows(buildMetadataPreview(selectedConnector));
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Connection Management</Typography>

      <Grid container spacing={1.2}>
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                All Connectors
              </Typography>
              <Typography variant="h5">{connectorStats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Files
              </Typography>
              <Typography variant="h5">{connectorStats.files}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Databases
              </Typography>
              <Typography variant="h5">{connectorStats.databases}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Cloud Storage
              </Typography>
              <Typography variant="h5">{connectorStats.cloud}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                APIs
              </Typography>
              <Typography variant="h5">{connectorStats.apis}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.2}>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.6}>
                <Stack direction={{ xs: "column", md: "row" }} spacing={1.2}>
                  <TextField
                    size="small"
                    placeholder="Search connectors"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    fullWidth
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <ManageSearchRoundedIcon fontSize="small" />
                        </InputAdornment>
                      ),
                    }}
                  />
                  <FormControl size="small" sx={{ minWidth: 190 }}>
                    <InputLabel id="category-filter-label">Category</InputLabel>
                    <Select
                      labelId="category-filter-label"
                      value={selectedCategory}
                      label="Category"
                      onChange={(event) =>
                        setSelectedCategory(event.target.value as "all" | ConnectorDefinition["category"])
                      }
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="files">Files</MenuItem>
                      <MenuItem value="databases">Databases</MenuItem>
                      <MenuItem value="cloud">Cloud Storage</MenuItem>
                      <MenuItem value="big_data">Big Data</MenuItem>
                      <MenuItem value="apis">APIs</MenuItem>
                    </Select>
                  </FormControl>
                </Stack>

                <Typography variant="h6">All Connectors</Typography>
                <Grid container spacing={1}>
                  {filteredConnectors.map((connector) => {
                    const selected = selectedConnector.id === connector.id;
                    return (
                      <Grid key={connector.id} size={{ xs: 12, sm: 6, xl: 4 }}>
                        <Box
                          onClick={() => {
                            setSelectedConnector(connector);
                            setCredentialResult(null);
                            setConnectionResult(null);
                            setMetadataRows([]);
                          }}
                          sx={{
                            p: 1.2,
                            borderRadius: 2,
                            border: "1px solid",
                            borderColor: selected ? "primary.main" : "divider",
                            bgcolor: selected ? "action.hover" : "transparent",
                            cursor: "pointer",
                          }}
                        >
                          <Stack direction="row" alignItems="center" justifyContent="space-between">
                            <Typography variant="body2" fontWeight={700}>
                              {connector.name}
                            </Typography>
                            <Chip size="small" label={categoryLabels[connector.category]} />
                          </Stack>
                          <Typography variant="caption" color="text.secondary">
                            Protocol: {connector.protocol}
                          </Typography>
                        </Box>
                      </Grid>
                    );
                  })}
                </Grid>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 5 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.6}>
                <Stack spacing={0.3}>
                  <Typography variant="h6">{selectedConnector.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {categoryLabels[selectedConnector.category]} connector • Auth modes: {selectedConnector.authModes.join(", ")}
                  </Typography>
                </Stack>

                <Tabs value={activeTab} onChange={(_event, next) => setActiveTab(next)} variant="fullWidth">
                  <Tab icon={<LinkRoundedIcon />} iconPosition="start" label="Test" />
                  <Tab icon={<StorageRoundedIcon />} iconPosition="start" label="Credentials" />
                  <Tab icon={<DataObjectRoundedIcon />} iconPosition="start" label="Metadata" />
                </Tabs>

                {(activeTab === 0 || activeTab === 1) && (
                  <Stack spacing={1.1}>
                    <TextField
                      size="small"
                      label="Endpoint / Host"
                      value={form.endpoint}
                      onChange={(event) => updateField("endpoint", event.target.value)}
                    />
                    <Grid container spacing={1}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          size="small"
                          label="Port"
                          value={form.port}
                          onChange={(event) => updateField("port", event.target.value)}
                          fullWidth
                        />
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          size="small"
                          label="Database / Path"
                          value={form.databaseOrPath}
                          onChange={(event) => updateField("databaseOrPath", event.target.value)}
                          fullWidth
                        />
                      </Grid>
                    </Grid>

                    {selectedConnector.authModes.includes("basic") && (
                      <Grid container spacing={1}>
                        <Grid size={{ xs: 12, sm: 6 }}>
                          <TextField
                            size="small"
                            label="Username"
                            value={form.username}
                            onChange={(event) => updateField("username", event.target.value)}
                            fullWidth
                          />
                        </Grid>
                        <Grid size={{ xs: 12, sm: 6 }}>
                          <TextField
                            size="small"
                            type="password"
                            label="Password"
                            value={form.password}
                            onChange={(event) => updateField("password", event.target.value)}
                            fullWidth
                          />
                        </Grid>
                      </Grid>
                    )}

                    {selectedConnector.authModes.includes("token") && (
                      <TextField
                        size="small"
                        label="Token / API Key"
                        value={form.token}
                        onChange={(event) => updateField("token", event.target.value)}
                        type="password"
                        fullWidth
                      />
                    )}
                  </Stack>
                )}

                {activeTab === 1 && (
                  <Stack spacing={1.2}>
                    <Button variant="contained" startIcon={<CheckCircleRoundedIcon />} onClick={validateCredentials}>
                      Validate Credentials
                    </Button>
                    {credentialResult && (
                      <Alert severity={credentialResult.ok ? "success" : "error"}>{credentialResult.message}</Alert>
                    )}
                  </Stack>
                )}

                {activeTab === 0 && (
                  <Stack spacing={1.2}>
                    <Button variant="contained" startIcon={<CloudDoneRoundedIcon />} onClick={testConnection}>
                      Test Connection
                    </Button>
                    {connectionResult && (
                      <Alert severity={connectionResult.ok ? "success" : "error"}>{connectionResult.message}</Alert>
                    )}
                  </Stack>
                )}

                {activeTab === 2 && (
                  <Stack spacing={1.2}>
                    <Button variant="contained" startIcon={<HubRoundedIcon />} onClick={previewMetadata}>
                      Metadata Preview
                    </Button>
                    {!connectionResult?.ok && (
                      <Alert severity="warning" icon={<ErrorRoundedIcon />}>
                        Run credential validation and connection test before previewing metadata.
                      </Alert>
                    )}
                    {metadataRows.length > 0 && (
                      <>
                        <Divider />
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Object</TableCell>
                              <TableCell>Type</TableCell>
                              <TableCell>Columns</TableCell>
                              <TableCell align="right">Sample Rows</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {metadataRows.map((row) => (
                              <TableRow key={row.objectName}>
                                <TableCell>{row.objectName}</TableCell>
                                <TableCell>{row.objectType}</TableCell>
                                <TableCell>{row.columns}</TableCell>
                                <TableCell align="right">{row.sampleRows.toLocaleString()}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </>
                    )}
                  </Stack>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
