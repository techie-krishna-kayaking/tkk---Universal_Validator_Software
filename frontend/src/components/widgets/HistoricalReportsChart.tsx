import { Box, Typography, useTheme } from "@mui/material";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface HistoricalReportPoint {
  month: string;
  reports: number;
}

export function HistoricalReportsChart({ data }: { data: HistoricalReportPoint[] }): React.JSX.Element {
  const theme = useTheme();

  return (
    <Box sx={{ width: "100%", height: 300 }}>
      <Typography variant="h6" sx={{ mb: 1.2 }}>
        Historical Reports
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: 0, right: 16, top: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis dataKey="month" stroke={theme.palette.text.secondary} />
          <YAxis stroke={theme.palette.text.secondary} />
          <Tooltip />
          <Bar dataKey="reports" fill={theme.palette.secondary.main} radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
