import PauseCircleRoundedIcon from "@mui/icons-material/PauseCircleRounded";
import PlayCircleRoundedIcon from "@mui/icons-material/PlayCircleRounded";
import QueueRoundedIcon from "@mui/icons-material/QueueRounded";
import StopCircleRoundedIcon from "@mui/icons-material/StopCircleRounded";
import TaskAltRoundedIcon from "@mui/icons-material/TaskAltRounded";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";

interface JobState {
  id: string;
  name: string;
  status: "running" | "completed" | "cancelled";
  progress: number;
  queue: "high" | "default" | "low";
}

interface QueueState {
  name: string;
  waiting: number;
  running: number;
  concurrency: string;
}

const initialJobs: JobState[] = [
  { id: "job-201", name: "AMEX Daily Validation", status: "running", progress: 22, queue: "high" },
  { id: "job-202", name: "Snowflake Migration Audit", status: "running", progress: 57, queue: "default" },
  { id: "job-203", name: "Revenue Control Reconciliation", status: "completed", progress: 100, queue: "high" },
  { id: "job-204", name: "Legacy Delta Integrity Check", status: "cancelled", progress: 34, queue: "low" },
  { id: "job-205", name: "Quarter-End Metadata Sweep", status: "completed", progress: 100, queue: "default" },
];

const queueState: QueueState[] = [
  { name: "high", waiting: 2, running: 1, concurrency: "1/3" },
  { name: "default", waiting: 4, running: 1, concurrency: "1/5" },
  { name: "low", waiting: 3, running: 0, concurrency: "0/2" },
];

const logSeed = [
  "Worker-1 started validation.record_count for job AMEX Daily Validation",
  "Worker-2 started validation.data_comparison for job Snowflake Migration Audit",
  "Loaded source rows: 1,200,345 and target rows: 1,200,118",
  "validation.record_count passed with tolerance 0.5%",
  "validation.metadata_types completed with 0 mismatches",
  "validation.row_checksums running on partition 4/10",
  "Queue heartbeat: 9 waiting jobs, 2 active jobs",
  "Persisted partial run metrics to result store",
];

export function ExecutionMonitoringPage(): React.JSX.Element {
  const [jobs, setJobs] = useState<JobState[]>(initialJobs);
  const [logs, setLogs] = useState<string[]>([
    "[10:30:01] Executor initialized with worker pool size = 6",
    "[10:30:04] Queue scanner activated for high/default/low queues",
    "[10:30:07] Dispatching AMEX Daily Validation to worker-1",
  ]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setJobs((previous) =>
        previous.map((job) => {
          if (job.status !== "running") {
            return job;
          }
          const increase = Math.floor(Math.random() * 11) + 3;
          const nextProgress = Math.min(100, job.progress + increase);
          if (nextProgress >= 100) {
            return { ...job, progress: 100, status: "completed" };
          }
          return { ...job, progress: nextProgress };
        })
      );

      const logLine = logSeed[Math.floor(Math.random() * logSeed.length)];
      const timestamp = new Date().toLocaleTimeString("en-US", { hour12: false });
      setLogs((previous) => [`[${timestamp}] ${logLine}`, ...previous].slice(0, 18));
    }, 1800);

    return () => window.clearInterval(timer);
  }, []);

  const summary = useMemo(() => {
    return {
      running: jobs.filter((job) => job.status === "running").length,
      completed: jobs.filter((job) => job.status === "completed").length,
      cancelled: jobs.filter((job) => job.status === "cancelled").length,
    };
  }, [jobs]);

  return (
    <Stack spacing={2.2}>
      <Typography variant="h4">Execution Monitoring</Typography>

      <Grid container spacing={1.2}>
        <Grid size={{ xs: 12, sm: 4 }}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Running Jobs
                  </Typography>
                  <Typography variant="h4">{summary.running}</Typography>
                </Box>
                <PlayCircleRoundedIcon color="primary" />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Completed Jobs
                  </Typography>
                  <Typography variant="h4">{summary.completed}</Typography>
                </Box>
                <TaskAltRoundedIcon color="success" />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Cancelled Jobs
                  </Typography>
                  <Typography variant="h4">{summary.cancelled}</Typography>
                </Box>
                <StopCircleRoundedIcon color="error" />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.2}>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.2}>
                <Typography variant="h6">Live Job Progress</Typography>
                <Divider />
                {jobs.map((job) => (
                  <Box key={job.id} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1.1 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" mb={0.8}>
                      <Typography variant="body2" fontWeight={700}>
                        {job.name}
                      </Typography>
                      <Stack direction="row" spacing={0.7}>
                        <Chip
                          size="small"
                          label={job.status}
                          color={job.status === "running" ? "primary" : job.status === "completed" ? "success" : "error"}
                          variant="outlined"
                        />
                        <Chip size="small" label={`${job.queue} queue`} variant="outlined" />
                      </Stack>
                    </Stack>
                    <LinearProgress
                      variant="determinate"
                      value={job.progress}
                      color={job.status === "cancelled" ? "error" : job.status === "completed" ? "success" : "primary"}
                      sx={{ height: 10, borderRadius: 99 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {job.progress}% complete
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 5 }}>
          <Stack spacing={2.2}>
            <Card>
              <CardContent>
                <Stack spacing={1.2}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <QueueRoundedIcon color="secondary" />
                    <Typography variant="h6">Queue Status</Typography>
                  </Stack>
                  <Divider />
                  {queueState.map((queue) => (
                    <Box key={queue.name} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, p: 1 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" fontWeight={700}>
                          {queue.name.toUpperCase()} Queue
                        </Typography>
                        <Chip size="small" label={`Concurrency ${queue.concurrency}`} />
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        Waiting: {queue.waiting} • Running: {queue.running}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Stack spacing={1.2}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <PauseCircleRoundedIcon color="primary" />
                    <Typography variant="h6">Live Logs</Typography>
                  </Stack>
                  <Divider />
                  <Box
                    sx={{
                      borderRadius: 2,
                      border: "1px solid",
                      borderColor: "divider",
                      p: 1,
                      bgcolor: "background.default",
                      maxHeight: 280,
                      overflowY: "auto",
                      fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                      fontSize: 12,
                    }}
                  >
                    {logs.map((line) => (
                      <Typography key={line} variant="caption" sx={{ display: "block", mb: 0.6 }}>
                        {line}
                      </Typography>
                    ))}
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
}
