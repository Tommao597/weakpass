import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Search, 
  Plus, 
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  X
} from 'lucide-react';
import { detectorApi, dictApi } from '../api';
import { toast } from 'sonner';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const ProtocolBadge = ({ protocol }: { protocol: string; key?: string }) => {
  const colors: Record<string, string> = {
    ssh: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    ftp: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    mysql: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    redis: 'bg-red-500/10 text-red-400 border-red-500/20',
    rdp: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${colors[protocol] || 'bg-slate-500/10 text-slate-400 border-slate-500/20'}`}>
      {protocol.toUpperCase()}
    </span>
  );
};

export const Detector = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [dicts, setDicts] = useState<any[]>([]);

  const [formData, setFormData] = useState({
    targets: '',
    usernames: 'root,admin',
    protocols: ['ssh'],
    threads: 10,
    timeout: 5,
    dict_id: ''
  });

  const fetchTasks = async () => {
    try {
      const res = await detectorApi.listTasks();
      const data = Array.isArray(res.data) ? res.data : (res.data?.tasks || []);
      setTasks(data);
    } catch (err) {
      toast.error('获取任务列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchDicts = async () => {
    try {
      const res = await dictApi.listDicts();
      const data = Array.isArray(res.data) ? res.data : (res.data?.dicts || []);
      setDicts(data);
    } catch (err) {}
  };

  useEffect(() => {
    fetchTasks();
    fetchDicts();
    const timer = setInterval(fetchTasks, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleStartDetect = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const config = {
        targets: formData.targets.split(',').map(t => t.trim()),
        usernames: formData.usernames.split(',').map(u => u.trim()),
        protocols: formData.protocols,
        thread_count: formData.threads,
        timeout: formData.timeout,
        dict_id: formData.dict_id || null
      };
      await detectorApi.startDetect(config);
      toast.success('检测任务已启动');
      setIsCreating(false);
      fetchTasks();
    } catch (err) {
      toast.error('启动任务失败');
    }
  };

  const handleAction = async (taskId: string, action: 'pause' | 'resume' | 'stop') => {
    try {
      if (action === 'pause') await detectorApi.pauseTask(taskId);
      if (action === 'resume') await detectorApi.resumeTask(taskId);
      if (action === 'stop') await detectorApi.stopTask(taskId);
      toast.success('操作成功');
      fetchTasks();
    } catch (err) {
      toast.error('操作失败');
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">弱口令检测</h2>
          <p className="text-muted-foreground mt-1">配置并管理您的自动化安全检测任务</p>
        </div>
        <button 
          onClick={() => setIsCreating(true)}
          className="bg-primary hover:opacity-90 text-primary-foreground px-4 py-2 rounded-lg flex items-center gap-2 transition-all shadow-lg shadow-primary/20"
        >
          <Plus size={20} />
          新建检测任务
        </button>
      </div>

      {/* Task List */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-border flex items-center justify-between">
          <h3 className="font-semibold text-lg">任务列表</h3>
          <button onClick={fetchTasks} className="text-muted-foreground hover:text-foreground transition-colors">
            <RotateCcw size={18} />
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-muted/50 text-muted-foreground text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-medium">任务 ID</th>
                <th className="px-6 py-4 font-medium">目标</th>
                <th className="px-6 py-4 font-medium">协议</th>
                <th className="px-6 py-4 font-medium">进度</th>
                <th className="px-6 py-4 font-medium">状态</th>
                <th className="px-6 py-4 font-medium text-right">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-muted-foreground">
                    <Loader2 className="animate-spin mx-auto mb-2 text-primary" size={24} />
                    加载中...
                  </td>
                </tr>
              ) : !Array.isArray(tasks) || tasks.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-muted-foreground">
                    暂无活跃任务
                  </td>
                </tr>
              ) : (
                tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-muted-foreground">{task.id.slice(0, 8)}...</td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {task.targets?.slice(0, 2).map((t: string) => (
                          <span key={t} className="text-sm">{t}</span>
                        ))}
                        {task.targets?.length > 2 && <span className="text-xs text-muted-foreground">+{task.targets.length - 2}</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1">
                        {task.protocols?.map((p: string) => <ProtocolBadge key={p} protocol={p} />)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="w-full max-w-[100px] bg-muted h-1.5 rounded-full overflow-hidden">
                        <div 
                          className="bg-primary h-full transition-all duration-500" 
                          style={{ width: `${task.progress || 0}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-muted-foreground mt-1 block">{task.progress || 0}%</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium",
                        task.status === 'running' ? "bg-green-500/10 text-green-500" :
                        task.status === 'paused' ? "bg-yellow-500/10 text-yellow-500" :
                        task.status === 'stopped' ? "bg-red-500/10 text-red-500" :
                        "bg-muted text-muted-foreground"
                      )}>
                        <span className={cn("w-1.5 h-1.5 rounded-full", 
                          task.status === 'running' ? "bg-green-500 animate-pulse" : 
                          task.status === 'paused' ? "bg-yellow-500" : 
                          "bg-red-500"
                        )} />
                        {task.status === 'running' ? '运行中' : 
                         task.status === 'paused' ? '已暂停' : 
                         task.status === 'completed' ? '已完成' : '已停止'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        {task.status === 'running' && (
                          <button onClick={() => handleAction(task.id, 'pause')} className="p-1.5 hover:bg-muted rounded text-yellow-500" title="暂停">
                            <Pause size={16} />
                          </button>
                        )}
                        {task.status === 'paused' && (
                          <button onClick={() => handleAction(task.id, 'resume')} className="p-1.5 hover:bg-muted rounded text-green-500" title="恢复">
                            <Play size={16} />
                          </button>
                        )}
                        {(task.status === 'running' || task.status === 'paused') && (
                          <button onClick={() => handleAction(task.id, 'stop')} className="p-1.5 hover:bg-muted rounded text-red-500" title="停止">
                            <Square size={16} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Task Modal */}
      {isCreating && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-2xl w-full max-w-lg shadow-2xl">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <h3 className="text-xl font-bold">新建检测任务</h3>
              <button onClick={() => setIsCreating(false)} className="text-muted-foreground hover:text-foreground">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleStartDetect} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">检测目标 (逗号分隔)</label>
                <textarea 
                  required
                  value={formData.targets}
                  onChange={e => setFormData({...formData, targets: e.target.value})}
                  placeholder="例如: 192.168.1.1, example.com"
                  className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all h-24 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-1.5">用户名 (逗号分隔)</label>
                  <input 
                    type="text"
                    value={formData.usernames}
                    onChange={e => setFormData({...formData, usernames: e.target.value})}
                    className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-1.5">线程数</label>
                  <input 
                    type="number"
                    min="1" max="1000"
                    value={formData.threads}
                    onChange={e => setFormData({...formData, threads: parseInt(e.target.value)})}
                    className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">检测协议</label>
                <div className="flex flex-wrap gap-2">
                  {['ssh', 'ftp', 'mysql', 'redis', 'rdp', 'telnet', 'smb'].map(p => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => {
                        const newProtocols = formData.protocols.includes(p)
                          ? formData.protocols.filter(item => item !== p)
                          : [...formData.protocols, p];
                        setFormData({...formData, protocols: newProtocols});
                      }}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-sm font-medium border transition-all",
                        formData.protocols.includes(p)
                          ? "bg-primary border-primary text-primary-foreground"
                          : "bg-muted border-border text-muted-foreground hover:border-primary/50"
                      )}
                    >
                      {p.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">选择字典 (可选)</label>
                <select 
                  value={formData.dict_id}
                  onChange={e => setFormData({...formData, dict_id: e.target.value})}
                  className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none"
                >
                  <option value="">使用系统默认字典</option>
                  {Array.isArray(dicts) && dicts.map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>

              <div className="pt-4 flex gap-3">
                <button 
                  type="button"
                  onClick={() => setIsCreating(false)}
                  className="flex-1 bg-muted hover:bg-muted/80 text-foreground font-semibold py-2.5 rounded-lg transition-all"
                >
                  取消
                </button>
                <button 
                  type="submit"
                  className="flex-1 bg-primary hover:opacity-90 text-primary-foreground font-semibold py-2.5 rounded-lg transition-all shadow-lg shadow-primary/20"
                >
                  立即启动
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
