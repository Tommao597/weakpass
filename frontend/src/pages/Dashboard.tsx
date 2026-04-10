import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Activity,
  Database,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
  Clock,
  Zap,
  Plus,
  FileText,
  Loader2,
} from 'lucide-react';
import { detectorApi, dictApi } from '../api';
import { toast } from 'sonner';
import { normalizeTasks } from '../utils/task';

const StatCard = ({ title, value, change, icon: Icon, color, onClick }: any) => (
  <div
    onClick={onClick}
    className={`bg-card border border-border p-6 rounded-2xl transition-all ${onClick ? 'cursor-pointer hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5' : ''}`}
  >
    <div className="flex justify-between items-start mb-4">
      <div className={`p-3 rounded-xl ${color} bg-opacity-10`}>
        <Icon className={color.replace('bg-', 'text-')} size={24} />
      </div>
      {change && (
        <span className="flex items-center gap-1 text-green-500 text-xs font-bold">
          <TrendingUp size={12} /> {change}
        </span>
      )}
    </div>
    <p className="text-muted-foreground text-sm font-medium">{title}</p>
    <h3 className="text-3xl font-bold mt-1">{value}</h3>
  </div>
);

export const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTargets: 0,
    weakPasswords: 0,
    dictCount: 0,
    health: 98,
    recentTasks: [] as any[],
  });

  const fetchData = async () => {
    try {
      const [tasksRes, dictsRes] = await Promise.all([
        detectorApi.listTasks(),
        dictApi.listDicts(),
      ]);

      const rawTasks = Array.isArray(tasksRes.data) ? tasksRes.data : (tasksRes.data?.tasks || []);
      const tasks = normalizeTasks(rawTasks);
      const dicts = Array.isArray(dictsRes.data) ? dictsRes.data : (dictsRes.data?.dicts || []);

      const totalTargets = tasks.reduce((acc: number, task: any) => acc + (task.targets?.length || 0), 0);
      const weakPasswords = tasks.reduce((acc: number, task: any) => acc + (task.vulnerabilitiesCount || 0), 0);
      const completedTasks = tasks.filter((task: any) => task.status === 'completed');
      const failedTasks = tasks.filter((task: any) => task.status === 'failed');
      const health = tasks.length > 0
        ? Math.round((completedTasks.length / (completedTasks.length + failedTasks.length || 1)) * 100)
        : 100;

      setStats({
        totalTargets,
        weakPasswords,
        dictCount: dicts.length,
        health: Math.min(100, Math.max(0, health)),
        recentTasks: tasks.slice(0, 5),
      });
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err);
      toast.error('获取系统概况失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="h-[60vh] flex items-center justify-center">
        <Loader2 className="animate-spin text-primary" size={48} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold">系统总览</h2>
          <p className="text-muted-foreground mt-1">这里展示当前检测任务、弱口令发现和字典库概况</p>
        </div>
        <div className="flex items-center gap-2 bg-card border border-border px-4 py-2 rounded-xl text-sm text-muted-foreground">
          <Clock size={16} />
          上次更新: {new Date().toLocaleString()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="累计检测目标"
          value={stats.totalTargets.toLocaleString()}
          icon={Activity}
          color="bg-primary"
          onClick={() => navigate('/detector')}
        />
        <StatCard
          title="已发现弱口令"
          value={stats.weakPasswords.toLocaleString()}
          icon={AlertTriangle}
          color="bg-red-500"
          onClick={() => navigate('/reports')}
        />
        <StatCard
          title="字典库数量"
          value={stats.dictCount}
          icon={Database}
          color="bg-indigo-500"
          onClick={() => navigate('/dictionary')}
        />
        <StatCard
          title="系统健康度"
          value={`${stats.health}%`}
          icon={ShieldCheck}
          color="bg-green-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-card border border-border rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-border flex items-center justify-between">
            <h3 className="font-bold text-lg">最近检测活动</h3>
            <button
              onClick={() => navigate('/reports')}
              className="text-primary text-sm font-bold flex items-center gap-1 hover:underline"
            >
              查看全部 <ArrowUpRight size={14} />
            </button>
          </div>
          <div className="divide-y divide-border">
            {stats.recentTasks.length === 0 ? (
              <div className="p-10 text-center text-muted-foreground">
                暂无检测活动
              </div>
            ) : (
              stats.recentTasks.map((task, i) => (
                <div
                  key={task.id || i}
                  className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors cursor-pointer"
                  onClick={() => navigate('/reports')}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${
                      task.status === 'running' ? 'bg-primary animate-pulse' :
                      task.status === 'completed' ? 'bg-green-500' :
                      task.status === 'failed' ? 'bg-red-500' : 'bg-muted-foreground/30'
                    }`} />
                    <div>
                      <p className="font-medium text-sm truncate max-w-[200px]">{task.targets?.join(', ')}</p>
                      <p className="text-xs text-muted-foreground">
                        {task.protocols?.join('/')} · {new Date(task.createdAt || Date.now()).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      task.vulnerabilitiesCount > 0 ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'
                    }`}>
                      {task.vulnerabilitiesCount > 0 ? '发现风险' : '安全'}
                    </span>
                    <span className="text-xs text-muted-foreground font-medium capitalize">{task.status}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-card border border-border rounded-2xl p-6 space-y-6">
          <h3 className="font-bold text-lg">快速操作</h3>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/detector')}
              className="w-full flex items-center gap-3 p-4 bg-primary text-primary-foreground hover:opacity-90 rounded-xl transition-all group"
            >
              <Zap className="group-hover:scale-110 transition-transform" size={20} />
              <span className="font-bold">发起检测任务</span>
            </button>
            <button
              onClick={() => navigate('/dictionary')}
              className="w-full flex items-center gap-3 p-4 bg-muted hover:bg-muted/80 rounded-xl transition-all border border-border"
            >
              <Plus size={20} />
              <span className="font-bold">导入新字典</span>
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="w-full flex items-center gap-3 p-4 bg-muted hover:bg-muted/80 rounded-xl transition-all border border-border"
            >
              <FileText size={20} />
              <span className="font-bold">查看检测报告</span>
            </button>
          </div>

          <div className="pt-6 border-t border-border">
            <div className="bg-primary/10 border border-primary/20 rounded-xl p-4">
              <p className="text-xs text-primary font-bold mb-1 uppercase tracking-wider">系统提示</p>
              <p className="text-sm text-foreground/80">建议定期更新常用弱口令字典，以保持检测结果的有效性。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
