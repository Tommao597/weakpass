import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { Palette, Check, RefreshCw, Sun, Moon } from 'lucide-react';
import { motion } from 'motion/react';
import { toast } from 'sonner';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const Settings = () => {
  const { primaryColor, setPrimaryColor, availableColors, themeMode, toggleTheme } = useTheme();

  const handleReset = () => {
    setPrimaryColor('#2563eb');
    if (themeMode !== 'dark') toggleTheme();
    toast.success('已恢复默认主题设置');
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">系统设置</h2>
        <p className="text-muted-foreground">个性化您的弱口令检测系统界面</p>
      </div>

      <div className="grid gap-6">
        {/* Theme Mode Toggle */}
        <section className="bg-card border border-border rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                {themeMode === 'dark' ? <Moon className="text-primary" size={24} /> : <Sun className="text-primary" size={24} />}
              </div>
              <div>
                <h3 className="text-lg font-semibold">显示模式</h3>
                <p className="text-sm text-muted-foreground">切换白天或黑夜模式</p>
              </div>
            </div>
            <button
              onClick={toggleTheme}
              className="relative inline-flex h-8 w-14 items-center rounded-full bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            >
              <span
                className={cn(
                  "inline-block h-6 w-6 transform rounded-full bg-white transition-transform shadow-md",
                  themeMode === 'dark' ? "translate-x-7" : "translate-x-1"
                )}
              />
            </button>
          </div>
        </section>

        {/* Color Palette */}
        <section className="bg-card border border-border rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Palette className="text-primary" size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold">外观定制</h3>
              <p className="text-sm text-muted-foreground">选择系统的主题色</p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {availableColors.map((color) => (
              <button
                key={color.value}
                onClick={() => setPrimaryColor(color.value)}
                className={cn(
                  "relative group flex flex-col items-center gap-2 p-4 rounded-xl border transition-all",
                  primaryColor === color.value 
                    ? "bg-muted border-primary shadow-lg" 
                    : "bg-card border-border hover:border-primary/50 hover:bg-muted/50"
                )}
              >
                <div 
                  className="w-10 h-10 rounded-full shadow-inner flex items-center justify-center transition-transform group-hover:scale-110"
                  style={{ backgroundColor: color.value }}
                >
                  {primaryColor === color.value && (
                    <Check size={20} className="text-white drop-shadow-md" />
                  )}
                </div>
                <span className={cn(
                  "text-xs font-medium",
                  primaryColor === color.value ? "text-foreground" : "text-muted-foreground"
                )}>
                  {color.name}
                </span>
              </button>
            ))}
          </div>

          <div className="mt-8 pt-6 border-t border-border flex justify-end">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              <RefreshCw size={16} />
              恢复默认设置
            </button>
          </div>
        </section>

        <section className="bg-card border border-border rounded-2xl p-6 opacity-50 cursor-not-allowed">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-muted rounded-lg">
              <div className="w-6 h-6 bg-muted-foreground/20 rounded" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-muted-foreground">其他设置 (即将推出)</h3>
              <p className="text-sm text-muted-foreground/60">通知偏好、API 密钥管理等</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
