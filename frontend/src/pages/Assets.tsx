import React, { useMemo, useState, useEffect } from 'react';
import { Search, Globe, Server, Shield, Loader2, AlertCircle, CheckCircle2, RotateCcw, Eye, X } from 'lucide-react';
import { assetApi } from '../api';
import { toast } from 'sonner';

export const Assets = () => {
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any | null>(null);
  const [historyScans, setHistoryScans] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedScan, setSelectedScan] = useState<any | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const assetRows = useMemo(() => {
    if (!results) return [];

    const rawRows = Array.isArray(results.assets)
      ? results.assets
      : Array.isArray(results.ports)
      ? results.ports
      : [];

    return rawRows.map((item: any) => ({
      port: item.port,
      protocol: item.protocol || item.fingerprint || item.service || 'unknown',
      service: item.service || item.fingerprint || 'unknown',
      version: item.version || item.banner || item.fingerprint || '未知',
    }));
  }, [results]);

  const vulnerabilityCount = useMemo(() => {
    if (!results) return 0;
    if (Array.isArray(results.vulnerabilities)) return results.vulnerabilities.length;
    if (typeof results.vulnerability_count === 'number') return results.vulnerability_count;
    return 0;
  }, [results]);

  const fetchHistoryScans = async () => {
    try {
      const res = await assetApi.getAssetScans();
      setHistoryScans(Array.isArray(res.data.scans) ? res.data.scans : []);
    } catch (err) {
      toast.error('获取历史扫描记录失败');
    }
  };

  const fetchScanDetails = async (scanId: number) => {
    setDetailsLoading(true);
    try {
      const res = await assetApi.getAssetScanById(scanId);
      setSelectedScan(res.data);
      setShowDetails(true);
    } catch (err) {
      toast.error('获取扫描详情失败');
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return toast.error('请输入扫描目标');

    setLoading(true);
    setResults(null);
    try {
      const res = await assetApi.scanAssets(target);
      setResults(res.data);
      toast.success('资产扫描完成');
      // 扫描完成后刷新历史记录
      fetchHistoryScans();
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.[0]?.msg || err.response?.data?.detail || '扫描失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistoryScans();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold">资产识别</h2>
        <p className="text-muted-foreground mt-1">weakpass</p>
      </div>

      {/* 历史记录按钮 */}
      <div className="flex justify-between items-center">
        <div />
        <button 
          onClick={() => {
            setShowHistory(!showHistory);
            if (!showHistory) {
              fetchHistoryScans();
            }
          }}
          className="flex items-center gap-2 bg-secondary hover:bg-secondary/80 text-secondary-foreground px-4 py-2 rounded-lg transition-all"
        >
          <Eye size={18} />
          {showHistory ? '隐藏历史' : '查看历史'} ({historyScans.length})
        </button>
      </div>

      <div className="bg-card border border-border rounded-2xl p-8 shadow-xl max-w-3xl mx-auto">
        <form onSubmit={handleScan} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
            <input
              type="text"
              value={target}
              onChange={e => setTarget(e.target.value)}
              placeholder="输入 IP、域名或网段，例如 192.168.1.1 或 example.com"
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
                {assetRows.length} <span className="text-sm font-normal text-muted-foreground">个活跃端口</span>
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
                {vulnerabilityCount} <span className="text-sm font-normal text-muted-foreground">个潜在风险</span>
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
                    <th className="px-6 py-4 font-medium">指纹/版本</th>
                    <th className="px-6 py-4 font-medium">状态</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {assetRows.map((row: any, idx: number) => (
                    <tr key={idx} className="hover:bg-muted/30 transition-colors">
                      <td className="px-6 py-4 font-mono font-bold text-primary">{row.port}</td>
                      <td className="px-6 py-4 text-sm uppercase">{row.protocol}</td>
                      <td className="px-6 py-4 text-sm font-medium">{row.service}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.version}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded-full text-[10px] font-bold uppercase">Open</span>
                      </td>
                    </tr>
                  ))}
                  {assetRows.length === 0 && (
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
          <p className="text-muted-foreground">输入目标并开始扫描，以查看资产识别结果</p>
        </div>
      )}

      {/* 历史记录面板 */}
      {showHistory && (
        <div className="bg-card border border-border rounded-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="p-6 border-b border-border flex items-center justify-between">
            <h3 className="font-bold text-lg">资产扫描历史</h3>
            <button onClick={() => setShowHistory(false)} className="text-muted-foreground hover:text-foreground">
              <X size={20} />
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-muted/50 text-muted-foreground text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-medium">扫描ID</th>
                  <th className="px-6 py-4 font-medium">目标</th>
                  <th className="px-6 py-4 font-medium">资产数量</th>
                  <th className="px-6 py-4 font-medium">扫描时间</th>
                  <th className="px-6 py-4 font-medium text-right">状态</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {historyScans.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-muted-foreground">
                      暂无历史扫描记录
                    </td>
                  </tr>
                ) : (
                  historyScans.map((scan: any) => (
                    <tr 
                      key={scan.id} 
                      className="hover:bg-muted/30 transition-colors cursor-pointer"
                      onClick={() => fetchScanDetails(scan.id)}
                    >
                      <td className="px-6 py-4 font-mono text-xs text-muted-foreground">{scan.id}</td>
                      <td className="px-6 py-4">{scan.target}</td>
                      <td className="px-6 py-4">{scan.asset_count || 0}</td>
                      <td className="px-6 py-4">{new Date(scan.scan_time).toLocaleString()}</td>
                      <td className="px-6 py-4 text-right">
                        <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded-full text-xs font-medium">
                          {scan.status === 'completed' ? '已完成' : scan.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 扫描详情弹窗 */}
      {showDetails && selectedScan && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-2xl w-full max-w-4xl max-h-[80vh] overflow-y-auto shadow-2xl">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <h3 className="text-xl font-bold">扫描详情</h3>
              <button onClick={() => setShowDetails(false)} className="text-muted-foreground hover:text-foreground">
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {detailsLoading ? (
                <div className="flex items-center justify-center py-10">
                  <Loader2 className="animate-spin text-primary" size={32} />
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-muted rounded-lg p-4">
                      <p className="text-sm text-muted-foreground mb-1">扫描ID</p>
                      <p className="font-medium">{selectedScan.scan?.id}</p>
                    </div>
                    <div className="bg-muted rounded-lg p-4">
                      <p className="text-sm text-muted-foreground mb-1">目标</p>
                      <p className="font-medium">{selectedScan.scan?.target}</p>
                    </div>
                    <div className="bg-muted rounded-lg p-4">
                      <p className="text-sm text-muted-foreground mb-1">资产数量</p>
                      <p className="font-medium">{selectedScan.scan?.asset_count || 0}</p>
                    </div>
                    <div className="bg-muted rounded-lg p-4">
                      <p className="text-sm text-muted-foreground mb-1">扫描时间</p>
                      <p className="font-medium">{selectedScan.scan?.scan_time ? new Date(selectedScan.scan.scan_time).toLocaleString() : 'N/A'}</p>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-3">端口与服务详情</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border border-border rounded-lg">
                        <thead>
                          <tr className="bg-muted/50 text-muted-foreground text-xs uppercase tracking-wider">
                            <th className="px-4 py-3 font-medium">端口</th>
                            <th className="px-4 py-3 font-medium">服务</th>
                            <th className="px-4 py-3 font-medium">指纹/版本</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {selectedScan.assets && selectedScan.assets.length > 0 ? (
                            selectedScan.assets.map((asset: any, idx: number) => (
                              <tr key={idx} className="hover:bg-muted/30 transition-colors">
                                <td className="px-4 py-3 font-mono font-bold text-primary">{asset.port}</td>
                                <td className="px-4 py-3 text-sm font-medium">{asset.service}</td>
                                <td className="px-4 py-3 text-sm text-muted-foreground">{asset.fingerprint || '未知'}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan={3} className="px-4 py-6 text-center text-muted-foreground">
                                未发现开放端口
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};