<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>用户登录</h2>
        <p>欢迎回到电商商城</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item>
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" :underline="false" @click="goToForgotPassword">
              忘记密码？
            </el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span>还没有账号？</span>
          <el-link type="primary" :underline="false" @click="goToRegister">
            立即注册
          </el-link>
        </div>

        <div class="divider">
          <span>其他登录方式</span>
        </div>

        <div class="social-login">
          <el-button class="social-btn wechat" circle>
            <el-icon :size="24"><ChatDotRound /></el-icon>
          </el-button>
          <el-button class="social-btn qq" circle>
            <el-icon :size="24"><Iphone /></el-icon>
          </el-button>
          <el-button class="social-btn weibo" circle>
            <el-icon :size="24"><Comment /></el-icon>
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock, ChatDotRound, Iphone, Comment } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref()
const loading = ref(false)
const rememberMe = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 验证表单
    await loginFormRef.value.validate()
    loading.value = true
    
    console.log('🔄 开始登录，数据:', { 
      username: loginForm.username, 
      password: '***' // 不记录真实密码
    })
    
    // 调用真实登录方法
    await userStore.realLogin(loginForm.username, loginForm.password)
    
    loading.value = false
    
    // 跳转到原页面或首页
    const redirect = route.query.redirect || '/'
    console.log(`↪️ 跳转到: ${redirect}`)
    router.push(redirect)
    
  } catch (error) {
    console.error('❌ 登录失败:', error)
    loading.value = false
    
    // 根据错误类型显示不同消息
    if (error.response) {
      if (error.response.status === 401) {
        ElMessage.error('用户名或密码错误')
      } else if (error.response.status === 422) {
        ElMessage.error('请输入有效的用户名和密码')
      } else {
        ElMessage.error('登录失败: ' + (error.response.data?.detail || '服务器错误'))
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查后端服务是否运行')
    } else {
      ElMessage.error('登录失败: ' + error.message)
    }
  }
}

// 导航函数
const goToRegister = () => {
  router.push('/register')
}

const goToForgotPassword = () => {
  ElMessage.info('请联系管理员重置密码')
}

// 组件挂载时初始化
onMounted(() => {
  console.log('🔧 Login.vue 已挂载')
  
  // 测试API连接（可选）
  // testApiConnection()
})

// 测试API连接
const testApiConnection = async () => {
  try {
    const response = await fetch('http://localhost:8000/')
    const data = await response.json()
    console.log('✅ 后端连接正常:', data)
  } catch (error) {
    console.error('❌ 后端连接失败:', error)
    ElMessage.warning('后端服务可能未启动，请运行: python main.py')
  }
}
</script>


<style scoped>
.login-container {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  margin-top: 10px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: #606266;
  font-size: 14px;
}

.login-footer span {
  margin-right: 8px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 30px 0;
  color: #909399;
  font-size: 14px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e4e7ed;
}

.divider span {
  padding: 0 15px;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.social-btn {
  width: 50px;
  height: 50px;
  border: none;
  transition: all 0.3s;
}

.social-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.social-btn.wechat {
  background: #07C160;
  color: white;
}

.social-btn.qq {
  background: #12B7F5;
  color: white;
}

.social-btn.weibo {
  background: #E6162D;
  color: white;
}

.social-btn .el-icon {
  margin: 0;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
}
</style>