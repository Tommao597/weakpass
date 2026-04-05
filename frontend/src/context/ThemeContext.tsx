import React, { createContext, useContext, useEffect, useState } from 'react';

type ThemeColor = {
  name: string;
  value: string;
  foreground: string;
};

const THEME_COLORS: ThemeColor[] = [
  { name: '默认蓝', value: '#2563eb', foreground: '#ffffff' },
  { name: '赛博绿', value: '#10b981', foreground: '#ffffff' },
  { name: '深邃紫', value: '#8b5cf6', foreground: '#ffffff' },
  { name: '活力橙', value: '#f59e0b', foreground: '#ffffff' },
  { name: '极客红', value: '#ef4444', foreground: '#ffffff' },
  { name: '极简灰', value: '#475569', foreground: '#ffffff' },
];

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  primaryColor: string;
  setPrimaryColor: (color: string) => void;
  availableColors: ThemeColor[];
  themeMode: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [primaryColor, setPrimaryColor] = useState(() => {
    return localStorage.getItem('primary-color') || '#2563eb';
  });

  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    return (localStorage.getItem('theme-mode') as ThemeMode) || 'dark';
  });

  const toggleTheme = () => {
    setThemeMode(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  useEffect(() => {
    const root = document.documentElement;
    const colorObj = THEME_COLORS.find(c => c.value === primaryColor) || THEME_COLORS[0];
    root.style.setProperty('--primary-color', colorObj.value);
    root.style.setProperty('--primary-foreground', colorObj.foreground);
    localStorage.setItem('primary-color', primaryColor);
  }, [primaryColor]);

  useEffect(() => {
    const root = document.documentElement;
    if (themeMode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme-mode', themeMode);
  }, [themeMode]);

  return (
    <ThemeContext.Provider value={{ 
      primaryColor, 
      setPrimaryColor, 
      availableColors: THEME_COLORS,
      themeMode,
      toggleTheme
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
