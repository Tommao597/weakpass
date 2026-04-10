import React, { useState } from 'react';
import {
  BrainCircuit,
  Sparkles,
  Download,
  Save,
  Loader2,
  Zap,
} from 'lucide-react';
import { smartDictApi, passwordApi, dictApi } from '../api';
import { toast } from 'sonner';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const SmartDict = () => {
  const [activeTab, setActiveTab] = useState<'smart' | 'ai'>('smart');
  const [loading, setLoading] = useState(false);
  const [generatedFile, setGeneratedFile] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    birthday: '',
    phone: '',
    email: '',
    company: '',
    limit: 500,
  });

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();

    const hasValue = [
      formData.name,
      formData.birthday,
      formData.phone,
      formData.email,
      formData.company,
    ].some((val) => val.trim() !== '');

    if (!hasValue) {
      toast.error('请至少填写一项信息后再生成字典');
      return;
    }

    setLoading(true);

    try {
      const basePayload = {
        name: formData.name.trim() || null,
        birthday: formData.birthday.trim() || null,
        phone: formData.phone.trim() || null,
        email: formData.email.trim() || null,
        company: formData.company.trim() || null,
      };

      const res = activeTab === 'smart'
        ? await smartDictApi.generate(basePayload)
        : await passwordApi.generateDict({
            ...basePayload,
            use_rule: false,
            use_ai: true,
            limit: formData.limit,
          });

      if (res.data?.filename) {
        setGeneratedFile(res.data.filename);
        setIsSaved(false);
        toast.success(`${activeTab === 'smart' ? '智能' : 'AI'} 字典生成成功`);
      } else {
        throw new Error('未获取到生成文件名');
      }
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail?.[0]?.msg ||
        err.response?.data?.detail ||
        err.response?.data?.message ||
        '生成失败';

      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!generatedFile) return;

    try {
      const res = await dictApi.downloadDict(generatedFile);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', generatedFile);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      toast.error('下载失败');
    }
  };

  const handleSaveToLibrary = async () => {
    if (!generatedFile || isSaved) return;

    setSaving(true);

    try {
      await dictApi.saveGeneratedDict(generatedFile);
      setIsSaved(true);
      toast.success('已成功保存到字典库');
    } catch {
      toast.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <div className="w-16 h-16 bg-primary/20 text-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
          <BrainCircuit size={32} />
        </div>

        <h2 className="text-3xl font-bold">定制化字典生成</h2>
        <p className="text-muted-foreground">
          根据个人或企业信息生成更贴近场景的密码字典
        </p>
      </div>

      <div className="flex justify-center p-1 bg-muted rounded-xl max-w-md mx-auto">
        <button
          onClick={() => setActiveTab('smart')}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold',
            activeTab === 'smart'
              ? 'bg-card shadow-sm'
              : 'text-muted-foreground'
          )}
        >
          <Zap size={16} /> 智能生成
        </button>

        <button
          onClick={() => setActiveTab('ai')}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold',
            activeTab === 'ai'
              ? 'bg-card shadow-sm'
              : 'text-muted-foreground'
          )}
        >
          <Sparkles size={16} /> AI增强
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-7 bg-card border rounded-2xl p-8">
          <form onSubmit={handleGenerate} className="space-y-6">
            <input
              placeholder="姓名或拼音"
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              className="w-full border rounded-xl px-4 py-3"
            />

            <input
              placeholder="生日，例如 19900101"
              value={formData.birthday}
              onChange={e => setFormData({ ...formData, birthday: e.target.value })}
              className="w-full border rounded-xl px-4 py-3"
            />

            <input
              placeholder="手机号"
              value={formData.phone}
              onChange={e => setFormData({ ...formData, phone: e.target.value })}
              className="w-full border rounded-xl px-4 py-3"
            />

            <input
              placeholder="邮箱"
              value={formData.email}
              onChange={e => setFormData({ ...formData, email: e.target.value })}
              className="w-full border rounded-xl px-4 py-3"
            />

            <input
              placeholder="公司"
              value={formData.company}
              onChange={e => setFormData({ ...formData, company: e.target.value })}
              className="w-full border rounded-xl px-4 py-3"
            />

            <button
              disabled={loading}
              className="w-full bg-primary text-white py-4 rounded-xl flex justify-center gap-2"
            >
              {loading
                ? <Loader2 className="animate-spin" />
                : activeTab === 'smart'
                ? <Zap />
                : <Sparkles />
              }
              {loading ? '生成中...' : '开始生成字典'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-5 space-y-6">
          {generatedFile && (
            <div className="border rounded-2xl p-6 space-y-4">
              <p className="text-sm text-green-500">字典生成成功</p>
              <p className="text-xs truncate">{generatedFile}</p>

              <div className="flex gap-2">
                <button
                  onClick={handleSaveToLibrary}
                  disabled={isSaved || saving}
                  className="flex-1 bg-primary text-white py-2 rounded-lg flex justify-center gap-2"
                >
                  {saving ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
                  {isSaved ? '已保存' : '保存到库'}
                </button>

                <button
                  onClick={handleDownload}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg flex justify-center gap-2"
                >
                  <Download size={14} />
                  下载
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
