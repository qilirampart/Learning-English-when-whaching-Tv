import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')

    // 如果 token 存在，添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response
  },
  (error) => {
    // 处理错误响应
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Token 无效或过期
          ElMessage.error(data.message || '登录已过期，请重新登录')

          // 清除 token
          localStorage.removeItem('token')

          // 跳转到登录页
          router.push('/login')
          break

        case 403:
          ElMessage.error(data.message || '没有权限访问')
          break

        case 404:
          ElMessage.error(data.message || '请求的资源不存在')
          break

        case 409:
          // 冲突错误（如用户名已存在），不显示通用错误提示
          // 让调用方处理
          break

        case 500:
          ElMessage.error(data.message || '服务器错误，请稍后重试')
          break

        default:
          ElMessage.error(data.message || '请求失败，请重试')
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络错误，请检查您的网络连接')
    } else {
      // 其他错误
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
