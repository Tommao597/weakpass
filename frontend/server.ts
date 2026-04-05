import express from 'express';
import path from 'path';
import fs from 'fs';
import { createServer as createViteServer } from 'vite';
import { v4 as uuidv4 } from 'uuid';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // 模拟数据库存储
  const tasks: any[] = [];
  const dicts: any[] = [
    { id: 'default-1', name: '系统默认字典', description: '包含 10,000 条最常用的弱口令', tags: '基础, 推荐', created_at: new Date().toISOString(), size: '1.2 MB', filename: 'default.txt' }
  ];

  // --- API 路由 ---

  // 弱口令检测接口
  app.post('/api/detector/detect', (req, res) => {
    const config = req.body;
    const taskId = uuidv4();
    const newTask = {
      id: taskId,
      status: 'running',
      progress: 0,
      targets: config.targets,
      protocols: config['协议'],
      created_at: new Date().toISOString(),
      vulnerabilities_count: 0
    };
    tasks.push(newTask);
    
    // 模拟检测进度
    const interval = setInterval(() => {
      const task = tasks.find(t => t.id === taskId);
      if (task && task.status === 'running') {
        task.progress += 10;
        if (task.progress >= 100) {
          task.progress = 100;
          task.status = 'completed';
          task.vulnerabilities_count = Math.floor(Math.random() * 5);
          clearInterval(interval);
        }
      } else {
        clearInterval(interval);
      }
    }, 3000);

    res.json({ task_id: taskId, message: '检测任务已启动' });
  });

  app.get('/api/detector/tasks', (req, res) => {
    res.json(tasks);
  });

  app.get('/api/detector/result/:task_id', (req, res) => {
    // 模拟返回一些弱口令结果
    res.json([
      { target: '192.168.1.1', protocol: 'ssh', username: 'admin', password: 'password123' },
      { target: '192.168.1.1', protocol: 'ssh', username: 'root', password: '123456' }
    ]);
  });

  app.post('/api/detector/pause/:task_id', (req, res) => {
    const task = tasks.find(t => t.id === req.params.task_id);
    if (task) task.status = 'paused';
    res.json({ message: '任务已暂停' });
  });

  app.post('/api/detector/resume/:task_id', (req, res) => {
    const task = tasks.find(t => t.id === req.params.task_id);
    if (task) task.status = 'running';
    res.json({ message: '任务已恢复' });
  });

  app.post('/api/detector/stop/:task_id', (req, res) => {
    const task = tasks.find(t => t.id === req.params.task_id);
    if (task) task.status = 'stopped';
    res.json({ message: '任务已停止' });
  });

  // 字典管理接口
  app.get('/api/dict/dicts', (req, res) => {
    res.json(dicts);
  });

  app.post('/api/dict/dicts', (req, res) => {
    const { name, description, tags, sourceFilename } = req.query as any;
    const filename = sourceFilename || `dict_${Date.now()}.txt`;
    const newDict = {
      id: uuidv4(),
      name: name || '未命名字典',
      description: description || '',
      tags: tags || '',
      created_at: new Date().toISOString(),
      size: '15 KB',
      filename: filename
    };
    dicts.push(newDict);
    res.json(newDict);
  });

  app.get('/api/dict/dicts/:dict_id/preview', (req, res) => {
    const dict = dicts.find(d => d.id === req.params.dict_id);
    if (!dict) return res.status(404).json({ message: '字典不存在' });
    
    // 优先从临时存储中获取内容（针对刚生成的智能字典）
    let content = (app as any)._tempDicts?.[dict.filename] || (dict as any)._mockContent;
    
    if (!content) {
      // 默认模拟内容
      content = Array(20).fill(0).map((_, i) => `password_sample_${i + 1}`).join('\n');
    }
    
    res.json({ content });
  });

  app.delete('/api/dict/dicts/:dict_id', (req, res) => {
    const index = dicts.findIndex(d => d.id === req.params.dict_id);
    if (index !== -1) dicts.splice(index, 1);
    res.json({ message: '删除成功' });
  });

  // 智能字典生成接口 (增强版逻辑)
  app.post('/api/smart_dict/generate', (req, res) => {
    const { name, 生日, 电话, 电子邮件, 公司 } = req.body;
    
    const results = new Set<string>();
    const years = 生日 ? [生日.slice(0, 4), 生日.slice(-4), 生日.slice(-2)] : ['2023', '2024', '2025'];
    const phoneSuffix = 电话 ? [电话.slice(-4), 电话.slice(-6)] : [];
    const specials = ['@', '!', '#', '_', ''];

    // 1. 基础组合
    if (name) {
      const capitalized = name.charAt(0).toUpperCase() + name.slice(1);
      const upper = name.toUpperCase();
      
      [name, capitalized, upper].forEach(n => {
        results.add(n);
        results.add(n + '123');
        results.add(n + '888');
        results.add(n + '666');
        
        years.forEach(y => {
          specials.forEach(s => {
            results.add(n + s + y);
            results.add(y + s + n);
          });
        });
      });
    }

    // 2. 企业模式
    if (公司) {
      const c = 公司.toLowerCase();
      const capC = c.charAt(0).toUpperCase() + c.slice(1);
      specials.forEach(s => {
        results.add(capC + s + 'Admin');
        results.add('Admin' + s + capC);
        results.add(c + '2024');
        results.add(capC + '@123');
      });
    }

    // 3. 电话与生日
    if (phoneSuffix.length > 0) {
      phoneSuffix.forEach(p => {
        results.add('pw' + p);
        if (name) results.add(name + p);
      });
    }

    // 4. 数字替换 (简单 Leet Speak)
    if (name && name.includes('a')) results.add(name.replace(/a/g, '4') + '123');
    if (name && name.includes('e')) results.add(name.replace(/e/g, '3') + '888');

    const content = Array.from(results).join('\n');
    const filename = `smart_dict_${Date.now()}.txt`;
    
    // 模拟存储生成的内容，以便预览和下载
    (app as any)._tempDicts = (app as any)._tempDicts || {};
    (app as any)._tempDicts[filename] = content;

    res.json({ filename, message: '智能字典生成成功', count: results.size });
  });

  app.get('/api/dict/download/:filename', (req, res) => {
    const content = (app as any)._tempDicts?.[req.params.filename] || '模拟字典文件内容: \nadmin123\nroot123\npassword\n123456';
    res.send(content);
  });

  // --- Vite 托管 ---
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
