export type TaskRecord = Record<string, any>;

const toArray = (value: unknown): any[] => {
  if (Array.isArray(value)) return value;
  return [];
};

const toNumber = (value: unknown): number | null => {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
};

export const getTaskId = (task: TaskRecord): string =>
  String(task?.id ?? task?.task_id ?? '');

export const normalizeTask = (task: TaskRecord) => {
  const targets = toArray(task?.targets ?? task?.config?.targets).map(String);
  const protocols = toArray(task?.protocols ?? task?.config?.protocols).map(String);
  const result = toArray(task?.result);
  const statistics = task?.statistics ?? {};
  const progress =
    toNumber(task?.percent) ??
    toNumber(task?.progress) ??
    0;
  const vulnerabilitiesCount =
    toNumber(task?.vulnerabilities_count) ??
    toNumber(task?.vulnerability_count) ??
    toNumber(statistics?.total) ??
    result.length;

  return {
    ...task,
    id: getTaskId(task),
    targets,
    protocols,
    progress,
    result,
    statistics,
    vulnerabilitiesCount,
    createdAt: task?.created_at ?? task?.start_time ?? null,
    completedAt: task?.completed_at ?? null,
  };
};

export const normalizeTasks = (tasks: unknown) =>
  toArray(tasks)
    .map((task) => normalizeTask(task as TaskRecord))
    .filter((task) => task.id);

export const normalizeDetectionResults = (payload: unknown) => {
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === 'object' && Array.isArray((payload as TaskRecord).result)) {
    return (payload as TaskRecord).result;
  }
  return [];
};
