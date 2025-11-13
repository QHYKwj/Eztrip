// src/config/axios.js
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api', // 👈 对应 vite.config.mjs 的 proxy 配置
  timeout: 5000,
})

// 请求拦截器（可选）
api.interceptors.request.use(
  config => {
    // 例如自动添加 token
    // const token = localStorage.getItem('token')
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  error => Promise.reject(error),
)

// 响应拦截器（可选）
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  },
)

export default api
