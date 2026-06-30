import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import FactCheckRoundedIcon from "@mui/icons-material/FactCheckRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

type TestCaseType = "manual" | "automation" | "negative" | "boundary" | "edge";
type Priority = "P1" | "P2" | "P3";

interface GeneratedTestCase {
  id: string;
  title: string;
  type: TestCaseType;
  priority: Priority;
  preconditions: string;
  steps: string[];
  expectedResult: string;
}

function normalizeInput(input: string): string {
  return input.trim().toLowerCase();
}

function generateCases(scenario: string): GeneratedTestCase[] {
  const text = normalizeInput(scenario);
  const entity = text.includes("invoice") ? "invoice" : text.includes("order") ? "order" : "record";
  const key = text.includes("customer") ? "customer_id" : "primary_key";

  return [
    {
      id: "TC-MAN-001",
      title: `Manual validation for ${entity} data reconciliation`,
      type: "manual",
      priority: "P1",
      preconditions: "Source and target connections are configured and accessible.",
      steps: [
        `Open validation builder and load ${entity} mapping configuration.`,
        `Run record count and data value comparison using ${key}.`,
        "Review generated mismatch report and sample mismatched rows.",
      ],
      expectedResult: "Validation summary should show accurate pass/fail counts and actionable mismatch details.",
    },
    {
      id: "TC-AUTO-002",
      title: `Automation regression suite for ${entity} workflow`,
      type: "automation",
      priority: "P1",
      preconditions: "CI pipeline has access to seeded test datasets.",
      steps: [
        "Trigger API-based validation run using predefined YAML suite.",
        "Assert response status, execution state transitions, and report artifact generation.",
        "Verify historical trend metrics update in dashboard datastore.",
      ],
      expectedResult: "Automated run completes successfully and all expected artifacts are produced.",
    },
    {
      id: "TC-NEG-003",
      title: `Negative validation when source schema is incompatible`,
      type: "negative",
      priority: "P1",
      preconditions: "Target dataset contains a missing mandatory column.",
      steps: [
        "Submit validation job with intentionally incompatible target schema.",
        "Capture API and UI error payloads.",
        "Verify RBAC-safe and user-friendly error messaging.",
      ],
      expectedResult: "Run fails gracefully with explicit schema mismatch error and no partial report corruption.",
    },
    {
      id: "TC-BND-004",
      title: `Boundary validation for max precision/scale columns`,
      type: "boundary",
      priority: "P2",
      preconditions: "Dataset contains numeric values at precision and scale limits.",
      steps: [
        "Execute precision/scale check on decimal fields.",
        "Validate handling at upper and lower numeric bounds.",
        "Review rounding/coercion behavior in comparison engine.",
      ],
      expectedResult: "Boundary values are evaluated correctly without overflow, truncation, or false mismatches.",
    },
    {
      id: "TC-EDG-005",
      title: `Edge case validation for unicode and leading zeros`,
      type: "edge",
      priority: "P2",
      preconditions: "Input includes multilingual text, emoji-like symbols, and zero-padded IDs.",
      steps: [
        "Run special-character integrity validation.",
        "Run leading-zero preservation validation.",
        "Compare source and target outputs at row level with checksum evidence.",
      ],
      expectedResult: "Encoding and zero-padding are preserved with no silent normalization issues.",
    },
  ];
}

function priorityColor(priority: Priority): "error" | "warning" | "success" {
  if (priority === "P1") {
    return "error";
  }
  if (priority === "P2") {
    return "warning";
  }
  return "success";
}

export function TestCaseGeneratorPage(): React.JSX.Element {
  const [scenario, setScenario] = useState("");
  const [activeType, setActiveType] = useState<TestCaseType | "all">("all");
  const [generatedCases, setGeneratedCases] = useState<GeneratedTestCase[]>([]);
  const [activeTab, setActiveTab] = useState(0);

  const filteredCases = useMemo(() => {
    if (activeType === "all") {
      return generatedCases;
    }
    return generatedCases.filter((item) => item.type === activeType);
  }, [activeType, generatedCases]);

  const runGeneration = (): void => {
    const normalized = scenario.trim();
    if (!normalized) {
      return;
    }
    setGeneratedCases(generateCases(normalized));
    setActiveTab(0);
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Test Case Generator</Typography>
      <Typography variant="body2" color="text.secondary">
        Generate manual, automation, negative, boundary, and edge test cases from natural-language validation scenarios.
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", lg: "row" }} spacing={1.3}>
            <TextField
              fullWidth
              multiline
              minRows={4}
              label="Scenario description"
              placeholder="Example: Validate invoice migration from Snowflake to Databricks for nulls, duplicates, and precision mismatches."
              value={scenario}
              onChange={(event) => setScenario(event.target.value)}
            />
            <Stack spacing={1.1} sx={{ minWidth: { xs: "100%", lg: 260 } }}>
              <Button
                variant="contained"
                startIcon={<AutoAwesomeRoundedIcon />}
                onClick={runGeneration}
                disabled={!scenario.trim()}
              >
                Generate Test Cases
              </Button>
              <Button
                variant="outlined"
                onClick={() =>
                  setScenario("Validate customer order migration from Oracle to Snowflake with duplicate, null, and case-sensitivity checks.")
                }
              >
                Use Sample Scenario
              </Button>
              <FormControl fullWidth>
                <InputLabel id="case-filter-label">Type Filter</InputLabel>
                <Select
                  labelId="case-filter-label"
                  value={activeType}
                  label="Type Filter"
                  onChange={(event) => setActiveType(event.target.value as TestCaseType | "all")}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="manual">Manual</MenuItem>
                  <MenuItem value="automation">Automation</MenuItem>
                  <MenuItem value="negative">Negative</MenuItem>
                  <MenuItem value="boundary">Boundary</MenuItem>
                  <MenuItem value="edge">Edge</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {generatedCases.length > 0 ? (
        <Card>
          <CardContent>
            <Tabs value={activeTab} onChange={(_, value: number) => setActiveTab(value)}>
              <Tab label="Generated Cases" icon={<FactCheckRoundedIcon />} iconPosition="start" />
              <Tab label="Coverage" icon={<AutoAwesomeRoundedIcon />} iconPosition="start" />
            </Tabs>

            <Box sx={{ mt: 1.5 }}>
              {activeTab === 0 && (
                <Stack spacing={1.2}>
                  {filteredCases.map((testCase) => (
                    <Box key={testCase.id} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.8, flexWrap: "wrap" }}>
                        <Typography variant="subtitle2">{testCase.id} - {testCase.title}</Typography>
                        <Chip label={testCase.type.toUpperCase()} color="secondary" size="small" />
                        <Chip label={testCase.priority} color={priorityColor(testCase.priority)} size="small" />
                      </Stack>
                      <Typography variant="caption" color="text.secondary">Preconditions</Typography>
                      <Typography variant="body2" sx={{ mb: 0.8 }}>{testCase.preconditions}</Typography>
                      <Typography variant="caption" color="text.secondary">Steps</Typography>
                      <ol style={{ marginTop: 6, marginBottom: 8 }}>
                        {testCase.steps.map((step) => (
                          <li key={step}>
                            <Typography variant="body2">{step}</Typography>
                          </li>
                        ))}
                      </ol>
                      <Typography variant="caption" color="text.secondary">Expected Result</Typography>
                      <Typography variant="body2">{testCase.expectedResult}</Typography>
                    </Box>
                  ))}
                </Stack>
              )}

              {activeTab === 1 && (
                <Stack spacing={1.1}>
                  <Alert severity="success">Manual: {generatedCases.filter((item) => item.type === "manual").length}</Alert>
                  <Alert severity="success">Automation: {generatedCases.filter((item) => item.type === "automation").length}</Alert>
                  <Alert severity="warning">Negative: {generatedCases.filter((item) => item.type === "negative").length}</Alert>
                  <Alert severity="warning">Boundary: {generatedCases.filter((item) => item.type === "boundary").length}</Alert>
                  <Alert severity="info">Edge: {generatedCases.filter((item) => item.type === "edge").length}</Alert>
                </Stack>
              )}
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Alert severity="info">Provide a scenario and generate test cases.</Alert>
      )}

      <Divider />
      <Typography variant="caption" color="text.secondary">
        Generated cases can be exported and integrated with manual QA runs or automation pipelines in upcoming modules.
      </Typography>
    </Stack>
  );
}
