import AutoFixHighRoundedIcon from "@mui/icons-material/AutoFixHighRounded";
import BoltRoundedIcon from "@mui/icons-material/BoltRounded";
import LightbulbRoundedIcon from "@mui/icons-material/LightbulbRounded";
import PlayArrowRoundedIcon from "@mui/icons-material/PlayArrowRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
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

type SqlDialect = "postgres" | "snowflake" | "databricks";
type ExplanationLine = { step: string; detail: string };

function toDialectIdentifier(identifier: string, dialect: SqlDialect): string {
  if (dialect === "snowflake") {
    return `"${identifier}"`;
  }
  if (dialect === "databricks") {
    return `\`${identifier}\``;
  }
  return identifier;
}

function generateSqlFromEnglish(prompt: string, dialect: SqlDialect): string {
  const text = prompt.toLowerCase();
  const table = text.includes("orders")
    ? "orders"
    : text.includes("customers")
      ? "customers"
      : text.includes("invoice")
        ? "invoice"
        : "dataset";

  const tableName = toDialectIdentifier(table, dialect);
  const dateCol = toDialectIdentifier("created_at", dialect);
  const amountCol = toDialectIdentifier("amount", dialect);

  if (text.includes("top") || text.includes("highest") || text.includes("largest")) {
    return [
      `SELECT ${toDialectIdentifier("customer_id", dialect)}, SUM(${amountCol}) AS total_amount`,
      `FROM ${tableName}`,
      `WHERE ${dateCol} >= CURRENT_DATE - INTERVAL '30 days'`,
      `GROUP BY ${toDialectIdentifier("customer_id", dialect)}`,
      "ORDER BY total_amount DESC",
      "LIMIT 10;",
    ].join("\n");
  }

  if (text.includes("duplicate")) {
    return [
      `SELECT ${toDialectIdentifier("primary_key", dialect)}, COUNT(*) AS duplicate_count`,
      `FROM ${tableName}`,
      `GROUP BY ${toDialectIdentifier("primary_key", dialect)}`,
      "HAVING COUNT(*) > 1",
      "ORDER BY duplicate_count DESC;",
    ].join("\n");
  }

  if (text.includes("null") || text.includes("missing")) {
    return [
      `SELECT COUNT(*) AS null_records`,
      `FROM ${tableName}`,
      `WHERE ${toDialectIdentifier("customer_id", dialect)} IS NULL`,
      `   OR ${toDialectIdentifier("email", dialect)} IS NULL;`,
    ].join("\n");
  }

  return [
    `SELECT ${toDialectIdentifier("customer_id", dialect)}, ${toDialectIdentifier("status", dialect)}, ${amountCol}`,
    `FROM ${tableName}`,
    `WHERE ${dateCol} >= CURRENT_DATE - INTERVAL '7 days'`,
    "ORDER BY created_at DESC",
    "LIMIT 100;",
  ].join("\n");
}

function optimizeSql(sql: string): string {
  const normalized = sql.replace(/SELECT \*/gi, "SELECT customer_id, status, amount");
  const hasLimit = /\bLIMIT\b/i.test(normalized);
  const optimized = hasLimit ? normalized : `${normalized}\nLIMIT 500;`;

  return [
    "-- Optimization notes:",
    "-- 1) Reduced wildcard projection",
    "-- 2) Ensured bounded result set",
    "-- 3) Preserved filter predicates for pushdown",
    optimized,
  ].join("\n");
}

function explainSql(sql: string): ExplanationLine[] {
  const lines: ExplanationLine[] = [
    { step: "Projection", detail: "Selects only needed columns for downstream validation or reporting." },
    { step: "Source", detail: "Reads from the mapped source/target table inferred from your English prompt." },
    { step: "Filtering", detail: "Applies date or quality filters early to reduce scanned data volume." },
    { step: "Ordering", detail: "Sorts data for deterministic inspection when needed." },
  ];

  if (/group by/i.test(sql)) {
    lines.push({ step: "Aggregation", detail: "Groups rows to compute rollups used for reconciliation checks." });
  }
  if (/having/i.test(sql)) {
    lines.push({ step: "Post-aggregation filter", detail: "Keeps only aggregated records that violate expected thresholds." });
  }
  if (/limit/i.test(sql)) {
    lines.push({ step: "Row limiting", detail: "Constrains output size for faster execution and safer previews." });
  }

  return lines;
}

export function SQLGeneratorPage(): React.JSX.Element {
  const [dialect, setDialect] = useState<SqlDialect>("postgres");
  const [englishPrompt, setEnglishPrompt] = useState("");
  const [generatedSql, setGeneratedSql] = useState("");
  const [activeTab, setActiveTab] = useState(0);

  const optimizedSql = useMemo(() => (generatedSql ? optimizeSql(generatedSql) : ""), [generatedSql]);
  const explanation = useMemo(() => (generatedSql ? explainSql(generatedSql) : []), [generatedSql]);

  const runGeneration = (): void => {
    const sql = generateSqlFromEnglish(englishPrompt.trim(), dialect);
    setGeneratedSql(sql);
    setActiveTab(0);
  };

  const samplePrompt =
    "Show top 10 customers by order amount in last 30 days and include only active records.";

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">SQL Generator</Typography>
      <Typography variant="body2" color="text.secondary">
        Generate SQL from English, optimize query plans, and explain SQL behavior for validation workflows.
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", lg: "row" }} spacing={1.3}>
            <TextField
              fullWidth
              multiline
              minRows={4}
              label="English request"
              placeholder={samplePrompt}
              value={englishPrompt}
              onChange={(event) => setEnglishPrompt(event.target.value)}
            />
            <Stack spacing={1.1} sx={{ minWidth: { xs: "100%", lg: 250 } }}>
              <FormControl fullWidth>
                <InputLabel id="sql-dialect-label">Dialect</InputLabel>
                <Select
                  labelId="sql-dialect-label"
                  value={dialect}
                  label="Dialect"
                  onChange={(event) => setDialect(event.target.value as SqlDialect)}
                >
                  <MenuItem value="postgres">PostgreSQL</MenuItem>
                  <MenuItem value="snowflake">Snowflake</MenuItem>
                  <MenuItem value="databricks">Databricks SQL</MenuItem>
                </Select>
              </FormControl>
              <Button
                variant="contained"
                startIcon={<PlayArrowRoundedIcon />}
                onClick={runGeneration}
                disabled={!englishPrompt.trim()}
              >
                Generate SQL
              </Button>
              <Button variant="outlined" onClick={() => setEnglishPrompt(samplePrompt)}>
                Use Sample Prompt
              </Button>
              <Chip label={`Dialect: ${dialect.toUpperCase()}`} color="secondary" variant="filled" />
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {generatedSql ? (
        <Card>
          <CardContent>
            <Tabs value={activeTab} onChange={(_, value: number) => setActiveTab(value)}>
              <Tab icon={<BoltRoundedIcon />} iconPosition="start" label="Generated SQL" />
              <Tab icon={<AutoFixHighRoundedIcon />} iconPosition="start" label="Optimized SQL" />
              <Tab icon={<LightbulbRoundedIcon />} iconPosition="start" label="Explanation" />
            </Tabs>

            <Box sx={{ mt: 1.4 }}>
              {activeTab === 0 && (
                <Box sx={{ bgcolor: "action.hover", borderRadius: 2, p: 1.4 }}>
                  <Typography component="pre" sx={{ m: 0, whiteSpace: "pre-wrap", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                    {generatedSql}
                  </Typography>
                </Box>
              )}

              {activeTab === 1 && (
                <Box sx={{ bgcolor: "action.hover", borderRadius: 2, p: 1.4 }}>
                  <Typography component="pre" sx={{ m: 0, whiteSpace: "pre-wrap", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                    {optimizedSql}
                  </Typography>
                </Box>
              )}

              {activeTab === 2 && (
                <Stack spacing={1.1}>
                  {explanation.map((row) => (
                    <Alert key={row.step} severity="info">
                      <strong>{row.step}:</strong> {row.detail}
                    </Alert>
                  ))}
                </Stack>
              )}
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Alert severity="info">Provide an English request to generate and explain SQL.</Alert>
      )}
    </Stack>
  );
}
