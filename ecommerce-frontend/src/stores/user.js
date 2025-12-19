// ecommerce-frontend/src/stores/user.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref(null)
  
  // 是否已登录
  const isLoggedIn = computed(() => !!userInfo.value)
  
  // 用户名（方便使用）
  const username = computed(() => userInfo.value?.username || '')
  
  // 用户头像
  const avatar = computed(() => userInfo.value?.avatar_url || '')
  
  // 用户ID
  const userId = computed(() => userInfo.value?.user_id || null)
  
  // 用户类型（0:普通用户, 1:商家, 2:管理员）
  const userType = computed(() => userInfo.value?.user_type || 0)
  
  // Token（新增）
  const token = computed(() => userInfo.value?.token || localStorage.getItem('access_token'))

  // ==================== 登录相关方法 ====================
  
  // 真实登录方法（调用后端API）
  const realLogin = async (username, password) => {
    try {
      console.log('🔐 开始登录，用户名:', username)
      
      // 调用后端API
      const result = await authApi.login(username, password)
      console.log('✅ 登录API返回:', result)
      
      // 🔧 修改：result 现在就是数据对象，不是响应对象
      const userData = {
        user_id: result.user_id,          // ✅ 正确：result.user_id
        username: result.username,        // ✅ 正确：result.username
        user_type: result.user_type,      // ✅ 正确：result.user_type
        token: result.access_token        // ✅ 正确：result.access_token
      }
      
      console.log('👤 构建的用户数据:', userData)
      
      // 保存用户信息到store
      userInfo.value = userData
      
      // 保存到localStorage
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('access_token', result.access_token)
      
      // 🔧 新增：验证保存是否成功
      const savedToken = localStorage.getItem('access_token')
      const savedUser = localStorage.getItem('user')
      console.log('💾 验证保存:')
      console.log('- token:', savedToken ? savedToken.substring(0, 20) + '...' : '未找到')
      console.log('- user:', savedUser ? JSON.parse(savedUser) : '未找到')
      
      ElMessage.success('登录成功！')
      return userData
      
    } catch (error) {
      console.error('❌ 登录失败:', error)
      throw error // 让调用者处理错误
    }
  }
  
  // 兼容的登录方法（保持现有代码可用）
  const login = (userData) => {
    userInfo.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
    if (userData.token) {
      localStorage.setItem('access_token', userData.token)
    }
  }

  // 退出登录
  const logout = () => {
    userInfo.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    ElMessage.success('已退出登录')
    router.push('/login')
  }

  // 初始化时从localStorage恢复用户信息
  const initFromStorage = () => {
    const savedUser = localStorage.getItem('user')
    const savedToken = localStorage.getItem('access_token')
    
    if (savedUser) {
      try {
        userInfo.value = JSON.parse(savedUser)
        console.log('📱 从本地存储恢复用户信息:', userInfo.value)
      } catch (e) {
        console.error('解析用户信息失败', e)
        localStorage.removeItem('user')
      }
    }
    
    // 如果没有用户信息但有token，尝试获取用户信息
    if (!userInfo.value && savedToken) {
      console.log('🔍 检测到token，自动获取用户信息...')
      autoLoginWithToken(savedToken)
    }
  }
  
  // 使用token自动登录
  const autoLoginWithToken = async (token) => {
    try {
      console.log('🔄 尝试使用token自动登录...')
      // 设置临时token以获取用户信息
      localStorage.setItem('access_token', token)
      
      // 获取用户信息
      const userData = await authApi.getCurrentUser()
      console.log('✅ 获取到的用户信息:', userData)
      
      // 构建完整的用户对象
      const fullUserData = {
        ...userData,
        token: token
      }
      
      userInfo.value = fullUserData
      localStorage.setItem('user', JSON.stringify(fullUserData))
      console.log('✅ Token自动登录成功')
      
    } catch (error) {
      console.error('❌ Token自动登录失败:', error)
      // 清理无效的token
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      userInfo.value = null
    }
  }

  // 更新用户信息
  const updateUserInfo = (newInfo) => {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...newInfo }
      localStorage.setItem('user', JSON.stringify(userInfo.value))
    }
  }
  
  // 获取token（供其他模块使用）
  const getToken = () => {
    return token.value
  }

  // 🔧 新增：手动设置用户信息（用于开发调试）
  const setUserInfo = (info) => {
    userInfo.value = info
    if (info) {
      localStorage.setItem('user', JSON.stringify(info))
      if (info.token) {
        localStorage.setItem('access_token', info.token)
      }
    }
  }

  return {
    userInfo,
    isLoggedIn,
    username,
    avatar,
    userId,
    userType,
    token,
    login,          // 兼容方法
    realLogin,      // 新增：真实登录方法
    logout,
    initFromStorage,
    updateUserInfo,
    getToken,
    setUserInfo     // 新增：用于开发调试
  }
})