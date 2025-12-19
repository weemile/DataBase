// ecommerce-frontend/src/api/auth.js
import { api } from '@/utils/request'

export const authApi = {
  // 用户登录
  login: async (username, password) => {
    console.log('🔐 登录请求:', { username, password: '***' })
    try {
      const response = await api.post('/auth/login', { username, password })
      console.log('✅ 登录响应完整对象:', response)
      
      // 🔧 修改：返回 response.data，不是整个response
      const data = response.data
      console.log('✅ 登录响应数据:', data)
      
      // 保存token（根据你的后端响应格式调整）
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token)
        console.log('🔐 Token已保存:', data.access_token.substring(0, 20) + '...')
      }
      
      // 🔧 修改：返回数据，不是响应对象
      return data
      
    } catch (error) {
      console.error('❌ 登录失败:', error)
      throw error
    }
  },
  
  // 用户注册
  register: async (userData) => {
    console.log('📝 注册请求:', userData)
    try {
      const response = await api.post('/auth/register', userData)
      console.log('✅ 注册响应:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 注册失败:', error)
      throw error
    }
  },
  
  // 获取当前用户信息
  getCurrentUser: async () => {
    console.log('👤 获取用户信息请求')
    try {
      const response = await api.get('/auth/me')
      console.log('✅ 用户信息:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ 获取用户信息失败:', error)
      throw error
    }
  }
}

export default authApi