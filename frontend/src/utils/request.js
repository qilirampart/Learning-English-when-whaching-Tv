import axios from 'axios';

// 基于 API_FE_DOC.md 的描述,API 前缀为 /api
const service = axios.create({
  baseURL: '/api', // 开发环境需在 vite.config.js 配置 proxy
  timeout: 5000
});

// 请求拦截器:注入 Token
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data;
    // 假设后端返回 code 200 为成功
    if (res.code && res.code !== 200 && res.code !== 201) {
        // 处理逻辑错误
        return Promise.reject(new Error(res.message || 'Error'));
    }
    return res;
  },
  error => {
    if (error.response && error.response.status === 401) {
        // Token 失效,跳转登录
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default service;
