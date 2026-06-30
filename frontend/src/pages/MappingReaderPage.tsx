import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import FileUploadRoundedIcon from "@mui/icons-material/FileUploadRounded";
import InsertDriveFileRoundedIcon from "@mui/icons-material/InsertDriveFileRounded";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useMemo, useRef, useState } from "react";

type SupportedFileKind = "excel" | "word" | "pdf" | "unknown";

interface MappingRow {
  sourceField: string;
  targetField: string;
  dataType: string;
  rule: string;
}

interface ValidationCase {
  id: string;
  title: string;
  category: string;
  severity: "low" | "medium" | "high";
  description: string;
}

const sampleMappingRows: MappingRow[] = [
  { sourceField: "src.customer_id", targetField: "tgt.customer_id", dataType: "string", rule: "Primary Key" },
  { sourceField: "src.full_name", targetField: "tgt.customer_name", dataType: "string", rule: "Trim + case-insensitive compare" },
  { sourceField: "src.email", targetField: "tgt.email", dataType: "string", rule: "Regex email format" },
  { sourceField: "src.created_at", targetField: "tgt.created_date", dataType: "timestamp", rule: "Date normalization" },
  { sourceField: "src.credit_limit", targetField: "tgt.credit_limit", dataType: "decimal(12,2)", rule: "Precision/scale validation" },
];

function detectFileKind(fileName: string): SupportedFileKind {
  const ext = fileName.toLowerCase().split(".").pop() ?? "";
  if (["xlsx", "xls", "xlsm"].includes(ext)) {
    return "excel";
  }
  if (["doc", "docx"].includes(ext)) {
    return "word";
  }
  if (ext === "pdf") {
    return "pdf";
  }
  return "unknown";
}

function generateValidationCases(kind: SupportedFileKind, rows: MappingRow[]): ValidationCase[] {
  const cases: ValidationCase[] = [
    {
      id: "VC-001",
      title: "Primary key uniqueness and null check",
      category: "Integrity",
      severity: "high",
      description: "Validate mapped primary key fields for uniqueness and non-null constraints.",
    },
    {
      id: "VC-002",
      title: "Source-target row count reconciliation",
      category: "Completeness",
      severity: "high",
      description: "Compare total record counts between mapped source and target entities.",
    },
    {
      id: "VC-003",
      title: "Data type conformance across mapped fields",
      category: "Schema",
      severity: "medium",
      description: "Validate data type compatibility for all mapped columns.",
    },
  ];

  const hasDecimal = rows.some((row) => row.dataType.includes("decimal"));
  if (hasDecimal) {
    cases.push({
      id: "VC-004",
      title: "Numeric precision and scale validation",
      category: "Quality",
      severity: "high",
      description: "Verify decimal precision and scale consistency for financial fields.",
    });
  }

  if (kind === "excel") {
    cases.push({
      id: "VC-005",
      title: "Workbook sheet mapping integrity",
      category: "Mapping",
      severity: "medium",
      description: "Ensure all expected worksheet mappings are present and parsed correctly.",
    });
  }

  if (kind === "word") {
    cases.push({
      id: "VC-006",
      title: "Narrative rule extraction consistency",
      category: "NLP",
      severity: "medium",
      description: "Validate parser extraction of business rules from unstructured text sections.",
    });
  }

  if (kind === "pdf") {
    cases.push({
      id: "VC-007",
      title: "OCR/table extraction confidence threshold",
      category: "Parsing",
      severity: "high",
      description: "Validate extracted mappings meet minimum confidence threshold before execution.",
    });
  }

  return cases;
}

function severityColor(severity: ValidationCase["severity"]): "error" | "warning" | "success" {
  if (severity === "high") {
    return "error";
  }
  if (severity === "medium") {
    return "warning";
  }
  return "success";
}

export function MappingReaderPage(): React.JSX.Element {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [fileKind, setFileKind] = useState<SupportedFileKind>("unknown");
  const [mappingRows, setMappingRows] = useState<MappingRow[]>([]);

  const validationCases = useMemo(() => generateValidationCases(fileKind, mappingRows), [fileKind, mappingRows]);

  const handleOpenPicker = (): void => {
    inputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    const detected = detectFileKind(file.name);
    setFileName(file.name);
    setFileKind(detected);
    setMappingRows(detected === "unknown" ? [] : sampleMappingRows);
  };

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Source-to-Target Mapping Reader</Typography>
      <Typography variant="body2" color="text.secondary">
        Upload Excel, Word, or PDF mapping documents and auto-generate validation cases.
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={1.4} alignItems={{ xs: "stretch", md: "center" }}>
            <input
              ref={inputRef}
              type="file"
              accept=".xlsx,.xls,.xlsm,.doc,.docx,.pdf"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
            <Button variant="contained" startIcon={<FileUploadRoundedIcon />} onClick={handleOpenPicker}>
              Upload Mapping File
            </Button>
            <Chip
              icon={<InsertDriveFileRoundedIcon />}
              label={fileName ? `Selected: ${fileName}` : "No file selected"}
              variant="outlined"
            />
            <Chip
              icon={<AutoAwesomeRoundedIcon />}
              label={`Format: ${fileKind.toUpperCase()}`}
              color={fileKind === "unknown" ? "default" : "secondary"}
              variant="filled"
            />
          </Stack>
          <Box sx={{ mt: 1.4 }}>
            {fileName && fileKind === "unknown" ? (
              <Alert severity="warning">Unsupported file type. Please upload Excel, Word, or PDF.</Alert>
            ) : (
              <Alert severity="info">
                Reader supports enterprise mapping extraction with rule inference and validation-case generation.
              </Alert>
            )}
          </Box>
        </CardContent>
      </Card>

      <Stack direction={{ xs: "column", lg: "row" }} spacing={2} alignItems="stretch">
        <Card sx={{ flex: 1.2 }}>
          <CardContent>
            <Typography variant="h6">Extracted Mapping Preview</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.2 }}>
              Parsed source-target mappings from uploaded document.
            </Typography>
            <Divider sx={{ mb: 1.2 }} />

            {mappingRows.length ? (
              <Table size="small" aria-label="mapping preview table">
                <TableHead>
                  <TableRow>
                    <TableCell>Source Field</TableCell>
                    <TableCell>Target Field</TableCell>
                    <TableCell>Data Type</TableCell>
                    <TableCell>Rule</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mappingRows.map((row) => (
                    <TableRow key={`${row.sourceField}-${row.targetField}`}>
                      <TableCell>{row.sourceField}</TableCell>
                      <TableCell>{row.targetField}</TableCell>
                      <TableCell>{row.dataType}</TableCell>
                      <TableCell>{row.rule}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Alert severity="info">Upload a supported mapping document to preview extracted mappings.</Alert>
            )}
          </CardContent>
        </Card>

        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography variant="h6">Auto-Generated Validation Cases</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.2 }}>
              Validation suite generated from mapping metadata and inferred business rules.
            </Typography>
            <Divider sx={{ mb: 1.2 }} />

            <Stack spacing={1.1}>
              {validationCases.map((item) => (
                <Box key={item.id} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.2 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.6 }}>
                    <Typography variant="subtitle2">{item.id} - {item.title}</Typography>
                    <Chip label={item.severity.toUpperCase()} color={severityColor(item.severity)} size="small" />
                  </Stack>
                  <Typography variant="caption" color="text.secondary">
                    {item.category}
                  </Typography>
                  <Typography variant="body2">{item.description}</Typography>
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Stack>
  );
}
