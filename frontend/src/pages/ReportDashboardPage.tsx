import DownloadRoundedIcon from "@mui/icons-material/DownloadRounded";
import EmailRoundedIcon from "@mui/icons-material/EmailRounded";
import IosShareRoundedIcon from "@mui/icons-material/IosShareRounded";
import PictureAsPdfRoundedIcon from "@mui/icons-material/PictureAsPdfRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ReportItem {
  id: string;
  name: string;
  month: string;
  type: "executive_summary" | "detailed_report" | "comparison_report" | "trend_report";
  format: "html" | "pdf" | "excel" | "csv" | "json";
  status: "ready" | "queued" | "failed";
  passRate: number;
  failureRate: number;
  executions: number;
}

const reports: ReportItem[] = [
  {
    id: "r-101",
    name: "AMEX Migration Weekly",
    month: "Jan",
    type: "comparison_report",
    format: "pdf",
    status: "ready",
    passRate: 97.8,
    failureRate: 2.2,
    executions: 62,
  },
  {
    id: "r-102",
    name: "Snowflake Quality Pulse",
    month: "Feb",
    type: "trend_report",
    format: "html",
    status: "ready",
    passRate: 96.4,
    failureRate: 3.6,
    executions: 57,
  },
  {
    id: "r-103",
    name: "Revenue Controls Daily",
    month: "Mar",
    type: "detailed_report",
    format: "excel",
    status: "queued",
    passRate: 95.9,
    failureRate: 4.1,
    executions: 70,
  },
  {
    id: "r-104",
    name: "Platform Executive Digest",
    month: "Apr",
    type: "executive_summary",
    format: "pdf",
    status: "ready",
    passRate: 98.2,
    failureRate: 1.8,
    executions: 54,
  },
  {
    id: "r-105",
    name: "Legacy Sunset Audit",
    month: "May",
    type: "comparison_report",
    format: "json",
    status: "failed",
    passRate: 92.7,
    failureRate: 7.3,
    executions: 41,
  },
  {
    id: "r-106",
    name: "Quarter End Stability",
    month: "Jun",
    type: "trend_report",
    format: "csv",
    status: "ready",
    passRate: 97.2,
    failureRate: 2.8,
    executions: 66,
  },
];

const statusColors: Record<ReportItem["status"], string> = {
  ready: "#2e7d32",
  queued: "#ed6c02",
  failed: "#d32f2f",
};

const typeLabel: Record<ReportItem["type"], string> = {
  executive_summary: "Executive Summary",
  detailed_report: "Detailed Report",
  comparison_report: "Comparison Report",
  trend_report: "Trend Report",
};

export function ReportDashboardPage(): React.JSX.Element {
  const [selectedType, setSelectedType] = useState<"all" | ReportItem["type"]>("all");
  const [selectedStatus, setSelectedStatus] = useState<"all" | ReportItem["status"]>("all");
  const [selectedFormat, setSelectedFormat] = useState<"all" | ReportItem["format"]>("all");
  const [selectedId, setSelectedId] = useState<string>(reports[0].id);
  const [toast, setToast] = useState<string>("");

  const filtered = useMemo(
    () =>
      reports.filter((item) => {
        const typeMatch = selectedType === "all" || item.type === selectedType;
        const statusMatch = selectedStatus === "all" || item.status === selectedStatus;
        const formatMatch = selectedFormat === "all" || item.format === selectedFormat;
        return typeMatch && statusMatch && formatMatch;
      }),
    [selectedFormat, selectedStatus, selectedType]
  );

  const selectedReport = useMemo(
    () => filtered.find((item) => item.id === selectedId) ?? filtered[0] ?? reports[0],
    [filtered, selectedId]
  );

  const trendData = filtered.map((item) => ({
    month: item.month,
    passRate: item.passRate,
    failureRate: item.failureRate,
  }));

  const executionData = filtered.map((item) => ({
    report: item.name.split(" ")[0],
    executions: item.executions,
  }));

  const statusDistribution = Object.entries(
    filtered.reduce<Record<ReportItem["status"], number>>(
      (acc, item) => {
        acc[item.status] += 1;
        return acc;
      },
      { ready: 0, queued: 0, failed: 0 }
    )
  ).map(([status, count]) => ({ status, count }));

  const runAction = (action: "Export" | "Share" | "Email" | "PDF") => {
    setToast(`${action} triggered for ${selectedReport.name}`);
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Report Dashboard</Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", lg: "row" }} spacing={1.2}>
            <FormControl size="small" sx={{ minWidth: 210 }}>
              <InputLabel id="report-type-label">Report Type</InputLabel>
              <Select
                labelId="report-type-label"
                value={selectedType}
                label="Report Type"
                onChange={(event) => setSelectedType(event.target.value as "all" | ReportItem["type"])}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="executive_summary">Executive Summary</MenuItem>
                <MenuItem value="detailed_report">Detailed Report</MenuItem>
                <MenuItem value="comparison_report">Comparison Report</MenuItem>
                <MenuItem value="trend_report">Trend Report</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel id="report-status-label">Status</InputLabel>
              <Select
                labelId="report-status-label"
                value={selectedStatus}
                label="Status"
                onChange={(event) => setSelectedStatus(event.target.value as "all" | ReportItem["status"])}
              >
                <MenuItem value="all">All Statuses</MenuItem>
                <MenuItem value="ready">Ready</MenuItem>
                <MenuItem value="queued">Queued</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel id="report-format-label">Format</InputLabel>
              <Select
                labelId="report-format-label"
                value={selectedFormat}
                label="Format"
                onChange={(event) => setSelectedFormat(event.target.value as "all" | ReportItem["format"])}
              >
                <MenuItem value="all">All Formats</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="excel">Excel</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="json">JSON</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 260, flexGrow: 1 }}>
              <InputLabel id="selected-report-label">Selected Report</InputLabel>
              <Select
                labelId="selected-report-label"
                value={selectedReport.id}
                label="Selected Report"
                onChange={(event) => setSelectedId(event.target.value)}
              >
                {filtered.map((item) => (
                  <MenuItem key={item.id} value={item.id}>
                    {item.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      <Grid container spacing={2.2}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Interactive Validation Trend
              </Typography>
              <Box sx={{ width: "100%", height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis domain={[88, 100]} />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="passRate"
                      name="Pass %"
                      stroke="#2e7d32"
                      strokeWidth={3}
                      activeDot={{ r: 8 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="failureRate"
                      name="Failure %"
                      stroke="#d32f2f"
                      strokeWidth={3}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Status Distribution
              </Typography>
              <Box sx={{ width: "100%", height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={statusDistribution} dataKey="count" nameKey="status" outerRadius={90}>
                      {statusDistribution.map((entry) => (
                        <Cell key={entry.status} fill={statusColors[entry.status as ReportItem["status"]]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.2}>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Executions by Report
              </Typography>
              <Box sx={{ width: "100%", height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={executionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="report" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="executions" fill="#1976d2" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 5 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.4}>
                <Typography variant="h6">Report Actions</Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedReport.name} • {typeLabel[selectedReport.type]} • {selectedReport.format.toUpperCase()}
                </Typography>

                <Stack direction={{ xs: "column", sm: "row" }} spacing={1} flexWrap="wrap" useFlexGap>
                  <Button variant="outlined" startIcon={<DownloadRoundedIcon />} onClick={() => runAction("Export")}>
                    Export
                  </Button>
                  <Button variant="outlined" startIcon={<IosShareRoundedIcon />} onClick={() => runAction("Share")}>
                    Share
                  </Button>
                  <Button variant="outlined" startIcon={<EmailRoundedIcon />} onClick={() => runAction("Email")}>
                    Email
                  </Button>
                  <Button variant="contained" startIcon={<PictureAsPdfRoundedIcon />} onClick={() => runAction("PDF")}>
                    PDF
                  </Button>
                </Stack>

                <Alert severity={selectedReport.status === "ready" ? "success" : selectedReport.status === "queued" ? "warning" : "error"}>
                  Current status: {selectedReport.status.toUpperCase()}.
                </Alert>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar open={Boolean(toast)} autoHideDuration={2500} onClose={() => setToast("")}> 
        <Alert severity="info" onClose={() => setToast("")}>
          {toast}
        </Alert>
      </Snackbar>
    </Stack>
  );
}
