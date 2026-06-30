import DeleteOutlineRoundedIcon from "@mui/icons-material/DeleteOutlineRounded";
import DragIndicatorRoundedIcon from "@mui/icons-material/DragIndicatorRounded";
import PlayArrowRoundedIcon from "@mui/icons-material/PlayArrowRounded";
import PreviewRoundedIcon from "@mui/icons-material/PreviewRounded";
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
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";

interface ValidationRule {
  id: string;
  name: string;
  description: string;
}

const allRules: ValidationRule[] = [
  { id: "record_count", name: "Record Count", description: "Validate source vs target row counts." },
  { id: "column_count", name: "Column Count", description: "Detect extra or missing columns." },
  { id: "metadata", name: "Metadata Types", description: "Validate datatype compatibility." },
  { id: "duplicate", name: "Duplicate Detection", description: "Find duplicates across primary keys." },
  { id: "null_analysis", name: "Null Analysis", description: "Measure unexpected null values." },
  { id: "data_comparison", name: "Data Comparison", description: "Compare row/column values by key." },
  { id: "column_order", name: "Column Order", description: "Detect column order mismatches." },
  { id: "precision_scale", name: "Precision/Scale", description: "Detect numeric precision corruption." },
  { id: "distinct_values", name: "Distinct Values", description: "Compare unique value cardinality." },
  { id: "row_checksum", name: "Row Checksums", description: "Detect silent data corruption." },
  { id: "great_expectations", name: "Great Expectations", description: "Run expectation suites." },
  { id: "isolation_forest", name: "Isolation Forest", description: "Detect outliers/anomalies." },
];

const sources = [
  "Source - Oracle (Finance)",
  "Source - S3 (landing/amex)",
  "Source - API (Salesforce)",
  "Source - Snowflake (raw)",
];

const targets = [
  "Target - Snowflake (curated)",
  "Target - PostgreSQL (reporting)",
  "Target - Databricks Delta",
  "Target - BigQuery (analytics)",
];

const keySuggestions = ["id", "customer_id", "order_id", "account_id", "transaction_id"];

export function ValidationBuilderPage(): React.JSX.Element {
  const [builderName, setBuilderName] = useState("AMEX Daily Validation Suite");
  const [source, setSource] = useState(sources[0]);
  const [target, setTarget] = useState(targets[0]);
  const [primaryKeys, setPrimaryKeys] = useState("id");
  const [search, setSearch] = useState("");
  const [selectedRules, setSelectedRules] = useState<ValidationRule[]>([]);
  const [draggingRuleId, setDraggingRuleId] = useState<string | null>(null);
  const [previewPayload, setPreviewPayload] = useState<string>("");
  const [runState, setRunState] = useState<"idle" | "running" | "done">("idle");
  const [runSummary, setRunSummary] = useState<string>("");

  useEffect(() => {
    if (runState !== "running") {
      return;
    }

    const timer = window.setTimeout(() => {
      setRunState("done");
      setRunSummary(
        `Run completed for ${builderName} with ${selectedRules.length} rule(s). Source: ${source} -> Target: ${target}.`
      );
    }, 1400);

    return () => window.clearTimeout(timer);
  }, [builderName, runState, selectedRules.length, source, target]);

  const availableRules = useMemo(
    () =>
      allRules.filter(
        (rule) =>
          !selectedRules.some((selected) => selected.id === rule.id) &&
          (rule.name.toLowerCase().includes(search.toLowerCase()) ||
            rule.description.toLowerCase().includes(search.toLowerCase()))
      ),
    [search, selectedRules]
  );

  const addRule = (rule: ValidationRule) => {
    setSelectedRules((previous) => [...previous, rule]);
  };

  const removeRule = (ruleId: string) => {
    setSelectedRules((previous) => previous.filter((rule) => rule.id !== ruleId));
  };

  const moveRule = (ruleId: string, targetIndex: number) => {
    setSelectedRules((previous) => {
      const currentIndex = previous.findIndex((item) => item.id === ruleId);
      if (currentIndex < 0 || currentIndex === targetIndex) {
        return previous;
      }
      const reordered = [...previous];
      const [moved] = reordered.splice(currentIndex, 1);
      reordered.splice(targetIndex, 0, moved);
      return reordered;
    });
  };

  const handleDropToBuilder = () => {
    if (!draggingRuleId) {
      return;
    }
    const rule = allRules.find((item) => item.id === draggingRuleId);
    if (!rule) {
      return;
    }
    if (selectedRules.some((item) => item.id === rule.id)) {
      return;
    }
    addRule(rule);
  };

  const handlePreview = () => {
    const payload = {
      suite_name: builderName,
      source,
      target,
      primary_keys: primaryKeys
        .split(",")
        .map((key) => key.trim())
        .filter(Boolean),
      validation_rules: selectedRules.map((rule, index) => ({
        order: index + 1,
        rule_id: rule.id,
        rule_name: rule.name,
      })),
      run_options: {
        preview_mode: true,
        generated_at: new Date().toISOString(),
      },
    };
    setPreviewPayload(JSON.stringify(payload, null, 2));
  };

  const handleRun = () => {
    if (selectedRules.length === 0) {
      setRunSummary("Add at least one validation rule before running.");
      return;
    }
    setRunSummary("");
    setRunState("running");
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Validation Builder</Typography>

      <Grid container spacing={2.2}>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.4}>
                <Typography variant="h6">Configure Validation Suite</Typography>
                <TextField
                  label="Suite Name"
                  size="small"
                  value={builderName}
                  onChange={(event) => setBuilderName(event.target.value)}
                />

                <Grid container spacing={1.2}>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <FormControl size="small" fullWidth>
                      <InputLabel id="source-select-label">Source</InputLabel>
                      <Select
                        labelId="source-select-label"
                        label="Source"
                        value={source}
                        onChange={(event) => setSource(event.target.value)}
                      >
                        {sources.map((item) => (
                          <MenuItem key={item} value={item}>
                            {item}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <FormControl size="small" fullWidth>
                      <InputLabel id="target-select-label">Target</InputLabel>
                      <Select
                        labelId="target-select-label"
                        label="Target"
                        value={target}
                        onChange={(event) => setTarget(event.target.value)}
                      >
                        {targets.map((item) => (
                          <MenuItem key={item} value={item}>
                            {item}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                <TextField
                  size="small"
                  label="Primary Keys"
                  value={primaryKeys}
                  onChange={(event) => setPrimaryKeys(event.target.value)}
                  helperText="Comma-separated keys, for example: id,customer_id"
                />
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {keySuggestions.map((key) => (
                    <Chip
                      key={key}
                      size="small"
                      label={key}
                      onClick={() => {
                        if (!primaryKeys.split(",").map((item) => item.trim()).includes(key)) {
                          setPrimaryKeys((prev) => `${prev},${key}`.replace(/^,/, ""));
                        }
                      }}
                    />
                  ))}
                </Stack>
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2.2 }}>
            <CardContent>
              <Stack spacing={1.2}>
                <Typography variant="h6">Validation Rules (Drag-and-Drop)</Typography>
                <TextField
                  size="small"
                  placeholder="Search validation rules"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />

                <Grid container spacing={1}>
                  {availableRules.map((rule) => (
                    <Grid key={rule.id} size={{ xs: 12, md: 6 }}>
                      <Box
                        draggable
                        onDragStart={() => setDraggingRuleId(rule.id)}
                        onDragEnd={() => setDraggingRuleId(null)}
                        sx={{
                          border: "1px dashed",
                          borderColor: "divider",
                          borderRadius: 2,
                          p: 1.1,
                          bgcolor: "background.default",
                          cursor: "grab",
                        }}
                      >
                        <Stack direction="row" spacing={1} alignItems="center">
                          <DragIndicatorRoundedIcon fontSize="small" color="action" />
                          <Box>
                            <Typography variant="body2" fontWeight={700}>
                              {rule.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {rule.description}
                            </Typography>
                          </Box>
                        </Stack>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 5 }}>
          <Card
            onDragOver={(event) => event.preventDefault()}
            onDrop={handleDropToBuilder}
            sx={{ minHeight: 240 }}
          >
            <CardContent>
              <Stack spacing={1.2}>
                <Typography variant="h6">Builder Canvas</Typography>
                <Typography variant="body2" color="text.secondary">
                  Drop rules here and reorder execution steps.
                </Typography>
                <Divider />

                {selectedRules.length === 0 ? (
                  <Alert severity="info">No rules selected yet. Drag rules into this canvas.</Alert>
                ) : (
                  <Stack spacing={1}>
                    {selectedRules.map((rule, index) => (
                      <Box
                        key={rule.id}
                        draggable
                        onDragStart={() => setDraggingRuleId(rule.id)}
                        onDragEnd={() => setDraggingRuleId(null)}
                        onDragOver={(event) => event.preventDefault()}
                        onDrop={() => moveRule(draggingRuleId ?? "", index)}
                        sx={{
                          border: "1px solid",
                          borderColor: "divider",
                          borderRadius: 2,
                          p: 1,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: 1,
                        }}
                      >
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <Chip size="small" label={index + 1} />
                          <Typography variant="body2" fontWeight={600}>
                            {rule.name}
                          </Typography>
                        </Stack>
                        <Stack direction="row" spacing={0.4}>
                          <Button
                            size="small"
                            onClick={() => moveRule(rule.id, Math.max(0, index - 1))}
                            disabled={index === 0}
                          >
                            Up
                          </Button>
                          <Button
                            size="small"
                            onClick={() => moveRule(rule.id, Math.min(selectedRules.length - 1, index + 1))}
                            disabled={index === selectedRules.length - 1}
                          >
                            Down
                          </Button>
                          <Button
                            size="small"
                            color="error"
                            startIcon={<DeleteOutlineRoundedIcon />}
                            onClick={() => removeRule(rule.id)}
                          >
                            Remove
                          </Button>
                        </Stack>
                      </Box>
                    ))}
                  </Stack>
                )}

                <Divider />
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button variant="outlined" startIcon={<PreviewRoundedIcon />} onClick={handlePreview}>
                    Preview
                  </Button>
                  <Button variant="contained" startIcon={<PlayArrowRoundedIcon />} onClick={handleRun}>
                    Run
                  </Button>
                </Stack>

                {runState === "running" && (
                  <Stack spacing={0.7}>
                    <Typography variant="body2">Running validation pipeline...</Typography>
                    <LinearProgress />
                  </Stack>
                )}

                {runSummary && <Alert severity={runState === "done" ? "success" : "warning"}>{runSummary}</Alert>}
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2.2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Pipeline Preview
              </Typography>
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 1.2,
                  borderRadius: 2,
                  border: "1px solid",
                  borderColor: "divider",
                  bgcolor: "background.default",
                  minHeight: 180,
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  fontSize: 12,
                }}
              >
                {previewPayload || "Click Preview to generate payload."}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
