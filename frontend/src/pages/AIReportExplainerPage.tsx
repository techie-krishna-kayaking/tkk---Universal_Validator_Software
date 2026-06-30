import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import BugReportRoundedIcon from "@mui/icons-material/BugReportRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import RecommendRoundedIcon from "@mui/icons-material/RecommendRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

type Severity = "critical" | "high" | "medium" | "low";

interface FailureSummaryItem {
  area: string;
  failedChecks: number;
  failureRate: string;
  severity: Severity;
}

interface AnomalyExplanation {
  signal: string;
  impact: string;
  probableCause: string;
}

interface FixRecommendation {
  priority: "P1" | "P2" | "P3";
  action: string;
  owner: string;
  eta: string;
}

const mockRuns = [
  { id: "RUN-20260630-001", label: "AMEX-DM nightly migration" },
  { id: "RUN-20260630-002", label: "SNOW-VAL incremental sync" },
  { id: "RUN-20260630-003", label: "Customer-360 weekly full load" },
];

function severityColor(severity: Severity): "error" | "warning" | "info" | "success" {
  if (severity === "critical" || severity === "high") {
    return "error";
  }
  if (severity === "medium") {
    return "warning";
  }
  if (severity === "low") {
    return "info";
  }
  return "success";
}

function buildInsights(runId: string): {
  failureSummary: FailureSummaryItem[];
  anomalies: AnomalyExplanation[];
  recommendations: FixRecommendation[];
  executiveSummary: string;
} {
  const flavor = runId.includes("002") ? "incremental" : runId.includes("003") ? "full load" : "migration";

  return {
    executiveSummary:
      `AI review indicates concentrated failures in key integrity checks during ${flavor} execution. ` +
      "Anomaly patterns suggest schema drift and transformation inconsistencies as primary drivers.",
    failureSummary: [
      { area: "Primary Key Integrity", failedChecks: 4, failureRate: "12.4%", severity: "critical" },
      { area: "Null & Missing Values", failedChecks: 6, failureRate: "9.1%", severity: "high" },
      { area: "Precision/Scale", failedChecks: 3, failureRate: "4.8%", severity: "medium" },
      { area: "Special Characters", failedChecks: 1, failureRate: "1.3%", severity: "low" },
    ],
    anomalies: [
      {
        signal: "Sudden 8x spike in duplicate keys for customer_id",
        impact: "Downstream dashboard aggregates may overcount active accounts.",
        probableCause: "Incremental merge condition excludes a newly added composite key component.",
      },
      {
        signal: "Numeric truncation observed in credit_limit values",
        impact: "Financial reconciliation variance exceeds SLA threshold.",
        probableCause: "Target column scale changed from (12,2) to (12,0) in latest release.",
      },
      {
        signal: "Unexpected NULL increase in source email column",
        impact: "Notification workflows are at risk of skipped recipients.",
        probableCause: "Source API contract introduced optional email payload without fallback mapping.",
      },
    ],
    recommendations: [
      {
        priority: "P1",
        action: "Patch merge predicate to include full business key and rerun duplicate validation.",
        owner: "Data Engineering",
        eta: "4 hours",
      },
      {
        priority: "P1",
        action: "Restore target decimal scale and backfill affected records from source snapshot.",
        owner: "Platform DBA",
        eta: "Same day",
      },
      {
        priority: "P2",
        action: "Add API payload guardrail: enforce required email or default enrichment rule.",
        owner: "Integration Team",
        eta: "1 sprint",
      },
      {
        priority: "P3",
        action: "Enable anomaly alert threshold tuning for duplicate and null spikes.",
        owner: "QA Lead",
        eta: "Next release",
      },
    ],
  };
}

export function AIReportExplainerPage(): React.JSX.Element {
  const [selectedRun, setSelectedRun] = useState(mockRuns[0].id);
  const [customContext, setCustomContext] = useState("");
  const [activeTab, setActiveTab] = useState(0);
  const [analyzeRequested, setAnalyzeRequested] = useState(false);

  const insights = useMemo(() => buildInsights(selectedRun), [selectedRun]);

  const analyze = (): void => {
    setAnalyzeRequested(true);
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">AI Report Explainer</Typography>
      <Typography variant="body2" color="text.secondary">
        Summarize failures, explain anomalies, and recommend fixes for validation report runs.
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", lg: "row" }} spacing={1.3}>
            <TextField
              select
              fullWidth
              label="Validation run"
              value={selectedRun}
              onChange={(event) => setSelectedRun(event.target.value)}
            >
              {mockRuns.map((run) => (
                <MenuItem key={run.id} value={run.id}>
                  {run.id} - {run.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              label="Optional context"
              placeholder="Example: prioritize financial-impact findings and customer-facing risks."
              value={customContext}
              onChange={(event) => setCustomContext(event.target.value)}
            />
            <Button variant="contained" startIcon={<AutoAwesomeRoundedIcon />} onClick={analyze}>
              Explain Report
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {analyzeRequested ? (
        <Card>
          <CardContent>
            <Alert severity="info" sx={{ mb: 1.2 }}>
              {insights.executiveSummary}
            </Alert>

            {customContext.trim() ? (
              <Alert severity="success" sx={{ mb: 1.2 }}>
                Context applied: {customContext.trim()}
              </Alert>
            ) : null}

            <Tabs value={activeTab} onChange={(_, value: number) => setActiveTab(value)}>
              <Tab icon={<BugReportRoundedIcon />} iconPosition="start" label="Failure Summary" />
              <Tab icon={<InsightsRoundedIcon />} iconPosition="start" label="Anomaly Explanation" />
              <Tab icon={<RecommendRoundedIcon />} iconPosition="start" label="Recommended Fixes" />
            </Tabs>

            <Box sx={{ mt: 1.4 }}>
              {activeTab === 0 && (
                <Stack spacing={1.1}>
                  {insights.failureSummary.map((item) => (
                    <Box key={item.area} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.6 }}>
                        <Typography variant="subtitle2">{item.area}</Typography>
                        <Chip label={item.severity.toUpperCase()} color={severityColor(item.severity)} size="small" />
                      </Stack>
                      <Typography variant="body2">Failed checks: {item.failedChecks}</Typography>
                      <Typography variant="body2">Failure rate: {item.failureRate}</Typography>
                    </Box>
                  ))}
                </Stack>
              )}

              {activeTab === 1 && (
                <Stack spacing={1.1}>
                  {insights.anomalies.map((item) => (
                    <Box key={item.signal} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 0.4 }}>{item.signal}</Typography>
                      <Typography variant="body2"><strong>Impact:</strong> {item.impact}</Typography>
                      <Typography variant="body2"><strong>Probable cause:</strong> {item.probableCause}</Typography>
                    </Box>
                  ))}
                </Stack>
              )}

              {activeTab === 2 && (
                <Stack spacing={1.1}>
                  {insights.recommendations.map((item, index) => (
                    <Box key={`${item.priority}-${index}`} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                      <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.4 }}>
                        <Chip label={item.priority} color={item.priority === "P1" ? "error" : item.priority === "P2" ? "warning" : "info"} size="small" />
                        <Typography variant="caption" color="text.secondary">ETA: {item.eta}</Typography>
                      </Stack>
                      <Typography variant="body2" sx={{ mb: 0.4 }}>{item.action}</Typography>
                      <Typography variant="caption" color="text.secondary">Owner: {item.owner}</Typography>
                    </Box>
                  ))}
                </Stack>
              )}
            </Box>

            <Divider sx={{ my: 1.2 }} />
            <Typography variant="caption" color="text.secondary">
              AI-generated explanations are advisory. Confirm recommendations with domain owners before production changes.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Alert severity="info">Select a run and click Explain Report to generate insights.</Alert>
      )}
    </Stack>
  );
}
