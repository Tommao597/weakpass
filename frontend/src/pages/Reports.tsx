import React, { useEffect, useState } from 'react';
import {
  FileText,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { detectorApi, reportApi } from '../api';
import { toast } from 'sonner';
import { normalizeDetectionResults, normalizeTasks } from '../utils/task';

export const Reports = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState<any | null>(null);
  const [results, setResults] = useState<any[]>([]);

  const fetchTasks = async () => {
    try {
      const res = await detectorApi.listTasks();
      const rawData = Array.isArray(res.data) ? res.data : (res.data?.tasks || []);
      const completedTasks = normalizeTasks(rawData).filter((task: any) => task.status === 'completed');
      setTasks(completedTasks);
    } catch (err) {
      toast.error('获取任务列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const viewResults = async (task: any) => {
    setSelectedTask(task);
    try {
      const res = await detectorApi.getResult(task.id);
      setResults(normalizeDetectionResults(res.data));
    } catch (err) {
      setResults([]);
      toast.error('获取检测结果失败');
    }
  };

  const handleExport = async (taskId: string, type: 'pdf' | 'excel') => {
    try {
      const res = type === 'pdf'
        ? await reportApi.exportPdf(taskId)
        : await reportApi.exportExcel(taskId);

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${taskId}.${type === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('导出成功');
    } catch (err) {
      toast.error('导出失败');
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold">检测报告</h2>
        <p className="text-muted-foreground mt-1">查看已完成任务的检测结果，并导出详细报告</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-4">
          <h3 className="font-semibold text-muted-foreground uppercase text-xs tracking-widest px-2">已完成任务</h3>
          <div className="space-y-3">
            {loading ? (
              Array(3).fill(0).map((_, i) => (
                <div key={i} className="h-24 bg-card border border-border rounded-xl animate-pulse" />
              ))
            ) : tasks.length === 0 ? (
              <div className="p-8 text-center bg-card/50 border border-border rounded-xl text-muted-foreground text-sm">
                暂无可导出的已完成任务
              </div>
            ) : (
              tasks.map((task) => (
                <button
                  key={task.id}
                  onClick={() => viewResults(task)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    selectedTask?.id === task.id
                      ? 'bg-primary/10 border-primary shadow-lg shadow-primary/5'
                      : 'bg-card border-border hover:border-border/80'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono text-[10px] text-muted-foreground">{task.id.slice(0, 8)}</span>
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Clock size={10} /> {new Date(task.createdAt || Date.now()).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="font-medium text-sm truncate mb-1">{task.targets?.join(', ')}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] px-1.5 py-0.5 bg-muted rounded text-muted-foreground">
                      {task.protocols?.join('/')}
                    </span>
                    <span className="text-[10px] text-primary font-medium">
                      发现 {task.vulnerabilitiesCount || 0} 个弱口令
                    </span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          {!selectedTask ? (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-card/30 border border-border rounded-2xl text-muted-foreground">
              <FileText size={48} className="mb-4 opacity-20" />
              <p>请从左侧选择一个已完成任务查看详情</p>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-2xl overflow-hidden animate-in fade-in duration-300">
              <div className="p-6 border-b border-border flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-lg">任务详情: {selectedTask.id.slice(0, 8)}</h3>
                  <p className="text-sm text-muted-foreground">
                    完成时间 {new Date(selectedTask.completedAt || Date.now()).toLocaleString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExport(selectedTask.id, 'pdf')}
                    className="flex items-center gap-2 px-3 py-1.5 bg-muted hover:bg-muted/80 rounded-lg text-sm font-medium transition-all"
                  >
                    <FileText size={16} className="text-red-500" /> PDF
                  </button>
                  <button
                    onClick={() => handleExport(selectedTask.id, 'excel')}
                    className="flex items-center gap-2 px-3 py-1.5 bg-muted hover:bg-muted/80 rounded-lg text-sm font-medium transition-all"
                  >
                    <FileSpreadsheet size={16} className="text-green-500" /> Excel
                  </button>
                </div>
              </div>

              <div className="p-6">
                <div className="grid grid-cols-3 gap-4 mb-8">
                  <div className="p-4 bg-muted/50 rounded-xl border border-border">
                    <p className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">扫描目标</p>
                    <p className="text-xl font-bold">{selectedTask.targets?.length || 0}</p>
                  </div>
                  <div className="p-4 bg-muted/50 rounded-xl border border-border">
                    <p className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">检测协议</p>
                    <p className="text-xl font-bold">{selectedTask.protocols?.length || 0}</p>
                  </div>
                  <div className="p-4 bg-red-500/10 rounded-xl border border-red-500/20">
                    <p className="text-xs text-red-500/70 uppercase font-bold tracking-wider mb-1">风险发现</p>
                    <p className="text-xl font-bold text-red-500">{results.length}</p>
                  </div>
                </div>

                <h4 className="font-bold mb-4 flex items-center gap-2">
                  <AlertCircle size={18} className="text-red-500" /> 弱口令详情
                </h4>

                <div className="space-y-3">
                  {results.length === 0 ? (
                    <div className="py-10 text-center bg-muted/20 rounded-xl border border-border">
                      <CheckCircle2 className="mx-auto text-green-500 mb-2" size={32} />
                      <p className="text-muted-foreground">未发现弱口令风险</p>
                    </div>
                  ) : (
                    results.map((result, idx) => (
                      <div key={idx} className="p-4 bg-muted/50 border border-border rounded-xl flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center text-red-500">
                            <XCircle size={20} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold">{result.target}</span>
                              <span className="text-[10px] px-1.5 py-0.5 bg-muted rounded text-muted-foreground uppercase">
                                {result.protocol}
                              </span>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              账号: <span className="text-foreground font-mono">{result.username}</span> |
                              密码: <span className="text-red-500 font-mono"> {result.password}</span>
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] text-muted-foreground block mb-1">检测状态</span>
                          <span className="text-xs text-muted-foreground">{result.status || 'weak'}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
