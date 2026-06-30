import SendRoundedIcon from "@mui/icons-material/SendRounded";
import SmartToyRoundedIcon from "@mui/icons-material/SmartToyRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

type ChatRole = "assistant" | "user";

interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
}

interface ValidationIntent {
  source: string;
  target: string;
  checks: string[];
  confidence: "high" | "medium";
  summary: string;
}

const quickPrompts = [
  "Compare source orders CSV with target Snowflake table by order_id for nulls and duplicates.",
  "Validate row count and schema between S3 parquet and Databricks Delta for customer_dim.",
  "Run data value comparison for invoice records with primary key invoice_id.",
];

function extractIntent(prompt: string): ValidationIntent {
  const lower = prompt.toLowerCase();
  const checks: string[] = [];

  if (lower.includes("row count") || lower.includes("record count")) {
    checks.push("Record Count");
  }
  if (lower.includes("schema") || lower.includes("metadata") || lower.includes("column")) {
    checks.push("Column Count", "Metadata Types");
  }
  if (lower.includes("null")) {
    checks.push("Null Analysis");
  }
  if (lower.includes("duplicate")) {
    checks.push("Duplicate Detection");
  }
  if (lower.includes("compare") || lower.includes("comparison") || lower.includes("match")) {
    checks.push("Data Value Comparison");
  }
  if (lower.includes("checksum") || lower.includes("hash")) {
    checks.push("Row Checksums");
  }
  if (lower.includes("distinct")) {
    checks.push("Distinct Values");
  }

  const source = lower.includes("csv")
    ? "Source File (CSV)"
    : lower.includes("s3")
      ? "S3 Dataset"
      : lower.includes("api")
        ? "API Endpoint"
        : "Configured Source";
  const target = lower.includes("snowflake")
    ? "Snowflake Target"
    : lower.includes("databricks") || lower.includes("delta")
      ? "Databricks Delta Target"
      : lower.includes("postgres")
        ? "PostgreSQL Target"
        : "Configured Target";

  const uniqueChecks = Array.from(new Set(checks.length ? checks : ["Record Count", "Data Value Comparison"]));
  const confidence: ValidationIntent["confidence"] = uniqueChecks.length >= 3 ? "high" : "medium";

  return {
    source,
    target,
    checks: uniqueChecks,
    confidence,
    summary: `Prepared ${uniqueChecks.length} validation checks from natural language intent.`,
  };
}

function messageId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function AIChatbotPage(): React.JSX.Element {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: messageId(),
      role: "assistant",
      content:
        "Describe source, target, keys, and checks in plain language. I will generate a natural-language validation plan for execution.",
      createdAt: new Date().toLocaleTimeString(),
    },
  ]);
  const [latestIntent, setLatestIntent] = useState<ValidationIntent | null>(null);
  const [toastOpen, setToastOpen] = useState(false);

  const canSend = input.trim().length > 0;

  const usageHint = useMemo(
    () =>
      "Example: Compare source customer CSV against Snowflake customer_dim by customer_id for row count, null analysis and duplicates.",
    []
  );

  const sendPrompt = (promptOverride?: string): void => {
    const promptText = (promptOverride ?? input).trim();
    if (!promptText) {
      return;
    }

    const userMessage: ChatMessage = {
      id: messageId(),
      role: "user",
      content: promptText,
      createdAt: new Date().toLocaleTimeString(),
    };

    const intent = extractIntent(promptText);
    const assistantMessage: ChatMessage = {
      id: messageId(),
      role: "assistant",
      content: `${intent.summary} Source: ${intent.source}. Target: ${intent.target}.`,
      createdAt: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setLatestIntent(intent);
    setInput("");
  };

  const runValidationPlan = (): void => {
    if (!latestIntent) {
      return;
    }
    setToastOpen(true);
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Enterprise AI Chatbot</Typography>
      <Typography variant="body2" color="text.secondary">
        Natural language validation for enterprise data quality workflows.
      </Typography>

      <Stack direction={{ xs: "column", lg: "row" }} spacing={2} alignItems="stretch">
        <Card sx={{ flex: 1.6, minHeight: 520 }}>
          <CardContent sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
              <SmartToyRoundedIcon color="primary" />
              <Typography variant="h6">Chat Console</Typography>
            </Stack>

            <Box
              aria-live="polite"
              sx={{
                flex: 1,
                overflowY: "auto",
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 2,
                p: 1.2,
                mb: 1.2,
              }}
            >
              <Stack spacing={1}>
                {messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                      maxWidth: "84%",
                      px: 1.3,
                      py: 0.9,
                      borderRadius: 2,
                      bgcolor: message.role === "user" ? "primary.main" : "action.hover",
                      color: message.role === "user" ? "primary.contrastText" : "text.primary",
                    }}
                  >
                    <Typography variant="body2">{message.content}</Typography>
                    <Typography variant="caption" sx={{ opacity: 0.75 }}>
                      {message.createdAt}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Box>

            <Stack spacing={1}>
              <TextField
                label="Describe validation in plain language"
                placeholder={usageHint}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                multiline
                minRows={3}
              />
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {quickPrompts.map((prompt) => (
                  <Chip key={prompt} label={prompt} onClick={() => sendPrompt(prompt)} variant="outlined" />
                ))}
              </Stack>
              <Stack direction="row" justifyContent="flex-end">
                <Button variant="contained" endIcon={<SendRoundedIcon />} onClick={() => sendPrompt()} disabled={!canSend}>
                  Send Prompt
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1, minHeight: 520 }}>
          <CardContent sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <Typography variant="h6">Generated Validation Plan</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.2 }}>
              Structured plan derived from natural language.
            </Typography>
            <Divider sx={{ mb: 1.2 }} />

            {latestIntent ? (
              <Stack spacing={1.2} sx={{ flex: 1 }}>
                <Alert severity={latestIntent.confidence === "high" ? "success" : "info"}>
                  Intent confidence: {latestIntent.confidence.toUpperCase()}
                </Alert>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Source" secondary={latestIntent.source} />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Target" secondary={latestIntent.target} />
                  </ListItem>
                </List>
                <Typography variant="subtitle2">Validation Checks</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {latestIntent.checks.map((check) => (
                    <Chip key={check} label={check} color="secondary" variant="filled" />
                  ))}
                </Stack>
                <Box sx={{ mt: "auto", pt: 1 }}>
                  <Button variant="contained" fullWidth onClick={runValidationPlan}>
                    Run Validation Plan
                  </Button>
                </Box>
              </Stack>
            ) : (
              <Alert severity="info">Send a prompt to generate a validation plan.</Alert>
            )}
          </CardContent>
        </Card>
      </Stack>

      <Snackbar
        open={toastOpen}
        autoHideDuration={2600}
        onClose={() => setToastOpen(false)}
        message="Validation run submitted to execution queue."
      />
    </Stack>
  );
}
