import { Box, Typography, useTheme } from "@mui/material";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface TrendPoint {
  week: string;
  passRate: number;
  failures: number;
}

export function ValidationTrendChart({ data }: { data: TrendPoint[] }): React.JSX.Element {
  const theme = useTheme();

  return (
    <Box sx={{ width: "100%", height: 300 }}>
      <Typography variant="h6" sx={{ mb: 1.2 }}>
        Validation Trends
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ left: 0, right: 16, top: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis dataKey="week" stroke={theme.palette.text.secondary} />
          <YAxis yAxisId="left" stroke={theme.palette.text.secondary} domain={[88, 100]} />
          <YAxis yAxisId="right" orientation="right" stroke={theme.palette.text.secondary} />
          <Tooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="passRate"
            name="Pass %"
            stroke={theme.palette.primary.main}
            strokeWidth={2.5}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="failures"
            name="Failures"
            stroke={theme.palette.secondary.main}
            strokeWidth={2.5}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}
