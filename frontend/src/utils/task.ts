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
  // 处理后端返回的target（字符串）转换为targets（数组）
  const targets = toArray(task?.targets ?? task?.config?.targets).map(String);
  if (!targets.length && task?.target) {
    // 如果没有targets但有target字段，将其按逗号分割为数组
    targets.push(...task.target.split(',').map((t: string) => t.trim()));
  }
  
  // 处理后端返回的protocol（字符串）转换为protocols（数组）
  const protocols = toArray(task?.protocols ?? task?.config?.protocols).map(String);
  if (!protocols.length && task?.protocol) {
    // 如果没有protocols但有protocol字段，将其按逗号分割为数组
    protocols.push(...task.protocol.split(',').map((p: string) => p.trim()));
  }
  
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