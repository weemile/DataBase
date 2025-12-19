// ecommerce-frontend/src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://localhost:8000/api', // 后端API地址（确保是8000端口！）
  timeout: 10000, // 10秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token') || localStorage.getItem('token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log(`🔐 请求携带Token: ${token.substring(0, 20)}...`)
    }
    
    console.log(`🚀 请求: ${config.method?.toUpperCase() || 'GET'} ${config.url}`, config.data || '')
    return config
  },
  (error) => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理响应
request.interceptors.response.use(
  (response) => {
    console.log(`✅ 响应成功: ${response.status} ${response.config.url}`, response.data)
    
    // 返回完整响应，让调用处处理业务逻辑
    return response
  },
  (error) => {
    console.error('❌ 请求错误:', error)
    
    if (error.response) {
      const { status, data } = error.response
      console.error(`服务器错误 ${status}:`, data)
      
      switch (status) {
        case 400:
          ElMessage.error(data.detail || data.message || '请求参数错误')
          break
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          // 清除用户信息
          const userStore = useUserStore()
          userStore.logout()
          localStorage.removeItem('access_token')
          localStorage.removeItem('token')
          // 跳转到登录页
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有访问权限')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422:
          ElMessage.error('数据验证失败：' + (data.detail || '请检查输入'))
          break
        case 500:
          ElMessage.error(data.detail || data.message || '服务器内部错误')
          break
        default:
          ElMessage.error(`请求失败: ${status}`)
      }
    } else if (error.request) {
      console.error('网络错误，无响应:', error.request)
      ElMessage.error('网络连接失败，请检查网络或后端服务是否运行')
    } else {
      console.error('请求配置错误:', error.message)
      ElMessage.error('请求配置错误: ' + error.message)
    }
    
    return Promise.reject(error)
  }
)

// 导出常用的请求方法
export const api = {
  get: (url, params) => request.get(url, { params }),
  post: (url, data) => request.post(url, data),
  put: (url, data) => request.put(url, data),
  delete: (url) => request.delete(url),
  patch: (url, data) => request.patch(url, data)
}

export default request