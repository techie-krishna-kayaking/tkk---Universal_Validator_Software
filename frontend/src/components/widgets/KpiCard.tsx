import TrendingUpRoundedIcon from "@mui/icons-material/TrendingUpRounded";
import TrendingDownRoundedIcon from "@mui/icons-material/TrendingDownRounded";
import { Card, CardContent, Stack, Typography } from "@mui/material";

interface KpiCardProps {
  label: string;
  value: string;
  delta: string;
  trend?: "up" | "down";
}

export function KpiCard({ label, value, delta, trend = "up" }: KpiCardProps): React.JSX.Element {
  const isUp = trend === "up";

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.2}>
          <Typography variant="body2" color="text.secondary">
            {label}
          </Typography>
          <Typography variant="h5" fontWeight={700}>
            {value}
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            {isUp ? (
              <TrendingUpRoundedIcon color="primary" fontSize="small" />
            ) : (
              <TrendingDownRoundedIcon color="error" fontSize="small" />
            )}
            <Typography variant="body2" color={isUp ? "primary.main" : "error.main"} fontWeight={600}>
              {delta}
            </Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}