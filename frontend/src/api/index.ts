import axios from 'axios';
import request from './request'

const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_URL || '/',
  headers: {
    'Content-Type': 'application/json',
  },
});


// ================= Detector APIs =================
export const detectorApi = {

  startDetect: (config: any) => {
    const payload = {
      targets: config.targets,
      ports: config.ports || null,
      usernames: config.usernames,
      protocols: config.protocols,
      thread_count: config.thread_count || 10,
      timeout: config.timeout || 5,
      dict_id: config.dict_id || null
    };

    return api.post('/api/detector/detect', payload);
  },

  getTaskStatus: (taskId: string) =>
    api.get(`/api/detector/task/${taskId}`),

  listTasks: () =>
    api.get('/api/detector/tasks'),

  getResult: (taskId: string) =>
    api.get(`/api/detector/result/${taskId}`),

  getProgress: (taskId: string) =>
    api.get(`/api/detector/progress/${taskId}`),

  pauseTask: (taskId: string) =>
    api.post(`/api/detector/pause/${taskId}`),

  resumeTask: (taskId: string) =>
    api.post(`/api/detector/resume/${taskId}`),

  stopTask: (taskId: string) =>
    api.post(`/api/detector/stop/${taskId}`),
};



// ================= Asset APIs =================
export const assetApi = {

  scanAssets: (target: string) =>
    api.post('/api/asset/assets/scan', null, { params: { target } }),

};



// ================= Dictionary APIs =================
export const dictApi = {

  // 上传字典
  createDict: (file: File, name: string, description: string, tags: string) => {

    const formData = new FormData();
    formData.append('file', file);

    return api.post('/api/dict/dicts', formData, {
      params: { name, description, tags },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },


  // 获取字典列表
  listDicts: () =>
    api.get('/api/dict/dicts'),


  // 获取单个字典
  getDict: (dictId: string) =>
    api.get(`/api/dict/dicts/${dictId}`),


  // 删除字典
  deleteDict: (dictId: string) =>
    api.delete(`/api/dict/dicts/${dictId}`),


  // 导出字典
  exportDict: (dictId: string) =>
    api.post(`/api/dict/dicts/${dictId}/export`),


  // 下载生成的字典
  downloadDict: (filename: string) =>
    api.get(`/api/dict/download/${filename}`, {
      responseType: 'blob'
    }),


  // 预览字典
  previewDict: (dictId: string) =>
    api.get(`/api/dict/dicts/${dictId}/preview`),

  saveGeneratedDict(filename: string) {
  return request.post('/api/dict/dicts/save_generated', null, {
    params: { filename }
  })
}


};



// ================= AI Password Dictionary APIs =================
export const passwordApi = {

  generateDict: (data: any) =>
    api.post('/api/password/generate_dict', data),

};



// ================= Smart Dictionary APIs =================
export const smartDictApi = {

  generate: (data: any) =>
    api.post('/api/smart_dict/generate', data),

};



// ================= Report APIs =================
export const reportApi = {

  exportPdf: (taskId: string) =>
    api.get(`/api/report/export/${taskId}/pdf`, {
      responseType: 'blob'
    }),

  exportExcel: (taskId: string) =>
    api.get(`/api/report/export/${taskId}/excel`, {
      responseType: 'blob'
    }),

};



export default api;