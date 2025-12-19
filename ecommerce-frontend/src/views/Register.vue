<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h2>用户注册</h2>
        <p>加入我们，开启购物之旅</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20位字母数字）"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            size="large"
            :prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            size="large"
            :prefix-icon="Iphone"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            size="large"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="agree">
          <el-checkbox v-model="registerForm.agree">
            我已阅读并同意
            <el-link type="primary" :underline="false" @click="showAgreement">
              《用户协议》
            </el-link>
            和
            <el-link type="primary" :underline="false" @click="showPrivacy">
              《隐私政策》
            </el-link>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="register-btn"
          >
            {{ loading ? '注册中...' : '立即注册' }}
          </el-button>
        </el-form-item>

        <div class="register-footer">
          <span>已有账号？</span>
          <el-link type="primary" :underline="false" @click="goToLogin">
            立即登录
          </el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Message, Iphone, Lock } from '@element-plus/icons-vue'
import authApi from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref()
const loading = ref(false)

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agree: false
})

// 自定义验证规则（保持不变）
const validateUsername = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (value.length < 3 || value.length > 20) {
    callback(new Error('用户名长度在3-20个字符之间'))
  } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线'))
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!emailRegex.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!phoneRegex.test(value)) {
    callback(new Error('请输入有效的手机号'))
  } else {
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码至少6个字符'))
  } else {
    if (registerForm.confirmPassword) {
      registerFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgree = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议'))
  } else {
    callback()
  }
}

// 验证规则
const registerRules = {
  username: [{ validator: validateUsername, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  agree: [{ validator: validateAgree, trigger: 'change' }]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    // 验证表单
    await registerFormRef.value.validate()
    loading.value = true
    
    console.log('📝 开始注册流程...')
    
    // 准备注册数据
    const registerData = {
      username: registerForm.username,
      password: registerForm.password,
      phone: registerForm.phone,
      email: registerForm.email,
      user_type: 0  // 普通用户
    }
    
    console.log('📤 发送注册数据:', registerData)
    
    // 调用注册API
    const response = await authApi.register(registerData)
    const responseData = response.data
    
    console.log('📥 注册API响应:', responseData)
    
    // 处理不同的成功响应格式
    if (responseData.code === 200 || responseData.access_token) {
      // 注册成功
      ElMessage.success(responseData.message || '注册成功！')
      
      // 尝试自动登录获取token
      try {
        console.log('🔄 尝试自动登录...')
        const loginResponse = await authApi.login(registerForm.username, registerForm.password)
        const loginData = loginResponse.data
        
        console.log('✅ 自动登录成功:', loginData)
        
        if (loginData.access_token) {
          // 构建用户信息对象
          const userInfo = {
            user_id: loginData.user_id || responseData.data?.user_id,
            username: loginData.username || registerForm.username,
            email: registerForm.email,
            phone: registerForm.phone,
            user_type: loginData.user_type || 0,
            token: loginData.access_token,
            avatar_url: null
          }
          
          console.log('👤 用户信息:', userInfo)
          
          // 保存用户信息到store
          userStore.login(userInfo)
          console.log('💾 用户信息已保存到store')
          
          ElMessage.success('自动登录成功！')
          
          // 跳转到首页
          router.push('/')
        }
      } catch (loginError) {
        console.warn('⚠️ 自动登录失败:', loginError)
        // 自动登录失败，跳转到登录页
        ElMessage.info('注册成功，请手动登录')
        router.push('/login')
      }
      
    } else {
      // 注册失败
      console.error('❌ 注册失败，响应数据:', responseData)
      throw new Error(responseData.detail || responseData.message || '注册失败')
    }
    
  } catch (error) {
    console.error('❌ 注册过程失败:', error)
    
    // 显示详细的错误信息
    let errorMessage = '注册失败'
    
    if (error.response) {
      const errorData = error.response.data
      console.error('服务器错误详情:', errorData)
      errorMessage = errorData.detail || errorData.message || '服务器错误'
    } else if (error.request) {
      console.error('网络错误，无响应:', error.request)
      errorMessage = '网络错误，请检查后端服务是否运行在 http://localhost:8080'
    } else {
      errorMessage = error.message || '注册失败'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 导航函数
const goToLogin = () => {
  router.push('/login')
}

const showAgreement = () => {
  ElMessage.info('用户协议内容')
}

const showPrivacy = () => {
  ElMessage.info('隐私政策内容')
}
</script>

<style scoped>
.register-container {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.register-header p {
  color: #909399;
  font-size: 14px;
}

.register-form {
  margin-top: 20px;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  margin-top: 10px;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
  color: #606266;
  font-size: 14px;
}

.register-footer span {
  margin-right: 8px;
}

@media (max-width: 480px) {
  .register-card {
    padding: 30px 20px;
  }
  
  .register-header h2 {
    font-size: 24px;
  }
}
</style>