/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Detector } from './pages/Detector';
import { Assets } from './pages/Assets';
import { Dictionary } from './pages/Dictionary';
import { SmartDict } from './pages/SmartDict';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { ThemeProvider } from './context/ThemeContext';

export default function App() {
  return (
    <ThemeProvider>
      <Router>
        <Toaster position="top-right" theme="dark" richColors />
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/detector" element={<Detector />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/dictionary" element={<Dictionary />} />
            <Route path="/smart-dict" element={<SmartDict />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}
