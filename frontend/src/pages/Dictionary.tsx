import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  Download, 
  Trash2, 
  FileText, 
  Search, 
  Plus,
  Tag,
  Calendar,
  HardDrive,
  Eye,
  Loader2,
  X,
  AlertTriangle
} from 'lucide-react';
import { dictApi } from '../api';
import { toast } from 'sonner';

export const Dictionary = () => {
  const [dicts, setDicts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [previewData, setPreviewData] = useState<{ name: string; content: string } | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  
  const [uploadForm, setUploadForm] = useState({
    name: '',
    description: '',
    tags: '',
    file: null as File | null
  });

  const fetchDicts = async () => {
    try {
      const res = await dictApi.listDicts();
      const data = Array.isArray(res.data) ? res.data : (res.data?.dicts || []);
      setDicts(data);
    } catch (err) {
      toast.error('获取字典列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDicts();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadForm.file) return toast.error('请选择文件');
    
    try {
      await dictApi.createDict(
        uploadForm.file,
        uploadForm.name,
        uploadForm.description,
        uploadForm.tags
      );
      toast.success('字典上传成功');
      setIsUploading(false);
      setUploadForm({ name: '', description: '', tags: '', file: null });
      fetchDicts();
    } catch (err) {
      toast.error('上传失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await dictApi.deleteDict(id);
      toast.success('已删除');
      setDeleteId(null);
      fetchDicts();
    } catch (err) {
      toast.error('删除失败');
    }
  };

  const handleDownload = async (dict: any) => {
    try {
      const res = await dictApi.exportDict(dict.id);
      const filename = `${dict.name}.txt`;
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('开始下载');
    } catch (err) {
      toast.error('下载失败');
    }
  };
  const handlePreview = async (dict: any) => {
    setIsPreviewing(true);
    try {
      const res = await dictApi.previewDict(dict.id);
      setPreviewData({
        name: dict.name,
        content: res.data.preview.join("\n")
      });
    } catch (err) {
      toast.error('预览失败');
      setIsPreviewing(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">字典管理</h2>
          <p className="text-muted-foreground mt-1">上传并组织您的密码字典库</p>
        </div>
        <button 
          onClick={() => setIsUploading(true)}
          className="bg-primary hover:opacity-90 text-primary-foreground px-4 py-2 rounded-lg flex items-center gap-2 transition-all shadow-lg shadow-primary/20"
        >
          <Upload size={20} />
          上传字典文件
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          Array(3).fill(0).map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-2xl p-6 animate-pulse">
              <div className="w-12 h-12 bg-muted rounded-xl mb-4" />
              <div className="h-6 bg-muted rounded w-2/3 mb-2" />
              <div className="h-4 bg-muted rounded w-full mb-4" />
              <div className="flex gap-2">
                <div className="h-6 bg-muted rounded w-16" />
                <div className="h-6 bg-muted rounded w-16" />
              </div>
            </div>
          ))
        ) : !Array.isArray(dicts) || dicts.length === 0 ? (
          <div className="col-span-full py-20 text-center bg-card/50 border border-dashed border-border rounded-2xl">
            <FileText className="mx-auto text-muted-foreground/30 mb-4" size={48} />
            <p className="text-muted-foreground">暂无字典，点击上方按钮上传</p>
          </div>
        ) : (
          dicts.map((dict) => (
            <div key={dict.id} className="bg-card border border-border rounded-2xl p-6 hover:border-primary/50 transition-all group relative">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                  <FileText size={24} />
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => handlePreview(dict)}
                    className="p-2 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground"
                    title="预览"
                  >
                    <Eye size={18} />
                  </button>
                  <button 
                    onClick={() => handleDownload(dict)}
                    className="p-2 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground"
                    title="下载"
                  >
                    <Download size={18} />
                  </button>
                  <button 
                    onClick={() => setDeleteId(dict.id)}
                    className="p-2 hover:bg-red-500/10 rounded-lg text-muted-foreground hover:text-red-500"
                    title="删除"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              
              <h3 className="text-lg font-bold mb-1 truncate">{dict.name}</h3>
              <p className="text-sm text-muted-foreground line-clamp-2 mb-4 h-10">{dict.description || '暂无描述'}</p>
              
              <div className="flex flex-wrap gap-2 mb-4">
                {(() => {
                  const tags = dict.tags;
                  const tagList = typeof tags === 'string' 
                    ? tags.split(',').filter(Boolean) 
                    : Array.isArray(tags) 
                      ? tags 
                      : [];
                  
                  return tagList.map((tag: string) => (
                    <span key={tag} className="px-2 py-0.5 bg-muted text-muted-foreground rounded text-[10px] uppercase font-semibold tracking-wider">
                      {tag.trim()}
                    </span>
                  ));
                })()}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-border text-[11px] text-muted-foreground">
                <div className="flex items-center gap-1">
                  <HardDrive size={12} />
                  {dict.size || '未知大小'}
                </div>
                <div className="flex items-center gap-1">
                  <Calendar size={12} />
                  {dict.created_at ? new Date(dict.created_at).toLocaleDateString() : '未知时间'}
                </div>
              </div>

              {deleteId === dict.id && (
                <div className="absolute inset-0 bg-card/95 backdrop-blur-sm rounded-2xl flex flex-col items-center justify-center p-6 text-center z-10">
                  <AlertTriangle className="text-red-500 mb-2" size={32} />
                  <p className="font-bold mb-4">确定要删除该字典吗？</p>
                  <div className="flex gap-2 w-full">
                    <button 
                      onClick={() => setDeleteId(null)}
                      className="flex-1 bg-muted hover:bg-muted/80 py-2 rounded-lg text-sm font-bold"
                    >
                      取消
                    </button>
                    <button 
                      onClick={() => handleDelete(dict.id)}
                      className="flex-1 bg-red-500 hover:bg-red-600 text-white py-2 rounded-lg text-sm font-bold"
                    >
                      确认删除
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Preview Modal */}
      {isPreviewing && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{previewData?.name || '预览中...'}</h3>
                <p className="text-xs text-muted-foreground">仅显示前 20 行内容</p>
              </div>
              <button onClick={() => { setIsPreviewing(false); setPreviewData(null); }} className="text-muted-foreground hover:text-foreground">
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto bg-muted/30 font-mono text-sm">
              {!previewData ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                  <Loader2 className="animate-spin text-primary" size={32} />
                  <p className="text-muted-foreground">正在加载预览内容...</p>
                </div>
              ) : (
                <pre className="whitespace-pre-wrap break-all">
                  {previewData.content}
                </pre>
              )}
            </div>
            
            <div className="p-4 border-t border-border bg-card flex justify-end">
              <button 
                onClick={() => { setIsPreviewing(false); setPreviewData(null); }}
                className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-bold"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {isUploading && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-2xl w-full max-w-md shadow-2xl">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <h3 className="text-xl font-bold">上传字典</h3>
              <button onClick={() => setIsUploading(false)} className="text-muted-foreground hover:text-foreground">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleUpload} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">字典名称</label>
                <input 
                  required
                  type="text"
                  value={uploadForm.name}
                  onChange={e => setUploadForm({...uploadForm, name: e.target.value})}
                  className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">描述</label>
                <textarea 
                  value={uploadForm.description}
                  onChange={e => setUploadForm({...uploadForm, description: e.target.value})}
                  className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none h-20 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">标签 (逗号分隔)</label>
                <input 
                  type="text"
                  value={uploadForm.tags}
                  onChange={e => setUploadForm({...uploadForm, tags: e.target.value})}
                  placeholder="例如: 常用, 弱口令, 2024"
                  className="w-full bg-muted border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1.5">选择文件 (.txt, .dic)</label>
                <div className="relative group">
                  <input 
                    required
                    type="file"
                    onChange={e => setUploadForm({...uploadForm, file: e.target.files?.[0] || null})}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div className="w-full bg-muted border-2 border-dashed border-border rounded-lg p-6 text-center group-hover:border-primary transition-all">
                    <Upload className="mx-auto text-muted-foreground/50 mb-2" size={24} />
                    <p className="text-sm text-muted-foreground">
                      {uploadForm.file ? uploadForm.file.name : '点击或拖拽文件到此处'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <button 
                  type="button"
                  onClick={() => setIsUploading(false)}
                  className="flex-1 bg-muted hover:bg-muted/80 text-foreground font-semibold py-2.5 rounded-lg transition-all"
                >
                  取消
                </button>
                <button 
                  type="submit"
                  className="flex-1 bg-primary hover:opacity-90 text-primary-foreground font-semibold py-2.5 rounded-lg transition-all shadow-lg shadow-primary/20"
                >
                  开始上传
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};