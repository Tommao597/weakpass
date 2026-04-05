import React, { useState } from 'react';
import { Search, Globe, Server, Shield, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { assetApi } from '../api';
import { toast } from 'sonner';

export const Assets = () => {
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any | null>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return toast.error('请输入扫描目标');

    setLoading(true);
    setResults(null);
    try {
      const res = await assetApi.scanAssets(target);
      setResults(res.data);
      toast.success('资产扫描完成');
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.[0]?.msg || '扫描失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold">资产识别</h2>
        <p className="text-muted-foreground mt-1">自动发现并识别目标系统的开放端口、服务及操作系统信息</p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-8 shadow-xl max-w-3xl mx-auto">
        <form onSubmit={handleScan} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
            <input 
              type="text"
              value={target}
              onChange={e => setTarget(e.target.value)}
              placeholder="输入 IP 地址、域名或网段 (如: 192.168.1.1, example.com)"
              className="w-full bg-muted border border-border rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary outline-none transition-all"
            />
          </div>
          <button 
            type="submit"
            disabled={loading}
            className="bg-primary hover:opacity-90 disabled:opacity-50 text-primary-foreground font-bold px-8 rounded-xl transition-all shadow-lg shadow-primary/20 flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
            {loading ? '扫描中...' : '开始扫描'}
          </button>
        </form>
      </div>

      {results && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-card border border-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center text-blue-500">
                  <Globe size={20} />
                </div>
                <h3 className="font-bold">基本信息</h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">目标:</span>
                  <span className="font-medium">{results.target}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">状态:</span>
                  <span className="text-green-500 font-medium flex items-center gap-1">
                    <CheckCircle2 size={14} /> 在线
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-indigo-500/10 rounded-lg flex items-center justify-center text-indigo-500">
                  <Server size={20} />
                </div>
                <h3 className="font-bold">开放端口</h3>
              </div>
              <div className="text-2xl font-bold text-indigo-500">
                {results.ports?.length || 0} <span className="text-sm font-normal text-muted-foreground">个活跃端口</span>
              </div>
            </div>

            <div className="bg-card border border-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center text-red-500">
                  <Shield size={20} />
                </div>
                <h3 className="font-bold">风险评估</h3>
              </div>
              <div className="text-2xl font-bold text-red-500">
                {results.vulnerabilities?.length || 0} <span className="text-sm font-normal text-muted-foreground">个潜在风险</span>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-2xl overflow-hidden">
            <div className="p-6 border-b border-border">
              <h3 className="font-bold text-lg">端口与服务详情</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-muted/50 text-muted-foreground text-xs uppercase tracking-wider">
                    <th className="px-6 py-4 font-medium">端口</th>
                    <th className="px-6 py-4 font-medium">协议</th>
                    <th className="px-6 py-4 font-medium">服务</th>
                    <th className="px-6 py-4 font-medium">版本</th>
                    <th className="px-6 py-4 font-medium">状态</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {results.ports?.map((port: any, idx: number) => (
                    <tr key={idx} className="hover:bg-muted/30 transition-colors">
                      <td className="px-6 py-4 font-mono font-bold text-primary">{port.port}</td>
                      <td className="px-6 py-4 text-sm uppercase">{port.protocol}</td>
                      <td className="px-6 py-4 text-sm font-medium">{port.service}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{port.version || '未知'}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded-full text-[10px] font-bold uppercase">Open</span>
                      </td>
                    </tr>
                  ))}
                  {(!results.ports || results.ports.length === 0) && (
                    <tr>
                      <td colSpan={5} className="px-6 py-10 text-center text-muted-foreground">
                        未发现开放端口
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {!results && !loading && (
        <div className="py-20 text-center bg-card/30 border border-dashed border-border rounded-2xl max-w-3xl mx-auto">
          <AlertCircle className="mx-auto text-muted-foreground/30 mb-4" size={48} />
          <p className="text-muted-foreground">输入目标并点击扫描以开始资产识别</p>
        </div>
      )}
    </div>
  );
};
