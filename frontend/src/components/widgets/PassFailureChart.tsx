import { Box, Stack, Typography, useTheme } from "@mui/material";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

interface PassFailureChartProps {
  pass: number;
  failure: number;
}

export function PassFailureChart({ pass, failure }: PassFailureChartProps): React.JSX.Element {
  const theme = useTheme();
  const data = [
    { name: "Pass", value: pass, color: theme.palette.primary.main },
    { name: "Failure", value: failure, color: theme.palette.error.main },
  ];

  return (
    <Box sx={{ width: "100%", height: 300 }}>
      <Typography variant="h6" sx={{ mb: 1.2 }}>
        Pass % / Failure %
      </Typography>
      <ResponsiveContainer width="100%" height="78%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={86} innerRadius={56}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => {
              const numeric = typeof value === "number" ? value : Number(value ?? 0);
              return `${numeric.toFixed(1)}%`;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <Stack direction="row" justifyContent="center" spacing={2}>
        <Typography variant="body2" color="text.secondary">
          Pass: {pass.toFixed(1)}%
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Failure: {failure.toFixed(1)}%
        </Typography>
      </Stack>
    </Box>
  );
}
