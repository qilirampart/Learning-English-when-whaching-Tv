import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // API 基础 URL
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

  // 初始化 - 从 token 获取用户信息
  const initialize = async () => {
    if (!token.value) {
      return
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })
      user.value = response.data.user
    } catch (error) {
      console.error('初始化用户信息失败:', error)
      // Token 无效，清除
      logout()
    }
  }

  // 注册
  const register = async (username, email, password) => {
    loading.value = true
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
        username,
        email,
        password
      })

      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', response.data.token)

      return { success: true, message: response.data.message }
    } catch (error) {
      const message = error.response?.data?.message || '注册失败，请重试'
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  // 登录
  const login = async (username, password) => {
    loading.value = true
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        username,
        password
      })

      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', response.data.token)

      return { success: true, message: response.data.message }
    } catch (error) {
      const message = error.response?.data?.message || '登录失败，请重试'
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  // 退出登录
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  // 刷新 token
  const refreshToken = async () => {
    if (!token.value) {
      return { success: false }
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/auth/refresh`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
      )

      token.value = response.data.token
      localStorage.setItem('token', response.data.token)

      return { success: true }
    } catch (error) {
      console.error('刷新 token 失败:', error)
      logout()
      return { success: false }
    }
  }

  return {
    // 状态
    token,
    user,
    loading,
    isAuthenticated,

    // 方法
    initialize,
    register,
    login,
    logout,
    refreshToken
  }
})
