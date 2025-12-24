<template>
  <div class="profile-page">
    <!-- 🔧 新增：加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-skeleton :rows="5" animated />
    </div>
    
    <!-- 🔧 新增：空状态提示 -->
    <div v-else-if="!loading && !userInfo.user_id" class="empty-state">
      <el-empty description="获取用户信息失败" />
      <el-button type="primary" @click="fetchUserInfo">重试</el-button>
    </div>
    
    <!-- 个人中心头部 -->
    <el-card class="profile-header" v-if="!loading && userInfo.user_id">
      <div class="header-content">
        <!-- 用户头像和信息 -->
        <div class="user-info">
          <el-avatar :size="80" :src="userInfo.avatar_url" class="user-avatar">
            {{ userInfo.username?.charAt(0) }}
          </el-avatar>
          <div class="user-details">
            <h2 class="username">{{ userInfo.username }}</h2>
            <div class="user-meta">
              <el-tag type="info" size="small">{{ getUserType() }}</el-tag>
              <span class="user-id">ID: {{ userInfo.user_id }}</span>
              <span class="register-time">注册时间：{{ formatTime(userInfo.register_time) }}</span>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-label">订单总数</span>
                <span class="stat-value">{{ stats.orderCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">收藏商品</span>
                <span class="stat-value">{{ stats.favoriteCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">优惠券</span>
                <span class="stat-value">{{ stats.couponCount }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户余额和积分 -->
        <div class="account-info">
          <div class="balance-card">
            <div class="balance-title">账户余额</div>
            <div class="balance-amount">¥ {{ userInfo.balance?.toFixed(2) || '0.00' }}</div>
            <el-button type="primary" size="small" @click="showRecharge = true">充值</el-button>
          </div>
          <div class="points-card">
            <div class="points-title">我的积分</div>
            <div class="points-amount">{{ userInfo.points || 0 }}</div>
            <el-button type="info" size="small" @click="$router.push('/points')">查看</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 主要内容区域 -->
    <div class="profile-content" v-if="!loading && userInfo.user_id">
      <!-- 左侧导航菜单 -->
      <el-card class="profile-sidebar">
        <el-menu :default-active="activeMenu" class="profile-menu">
          <el-menu-item index="orders" @click="activeMenu = 'orders'">
            <el-icon><Tickets /></el-icon>
            <span>我的订单</span>
          </el-menu-item>
          <el-menu-item index="address" @click="activeMenu = 'address'">
            <el-icon><Location /></el-icon>
            <span>收货地址</span>
          </el-menu-item>

          <el-menu-item index="security" @click="activeMenu = 'security'">
            <el-icon><Lock /></el-icon>
            <span>账户安全</span>
          </el-menu-item>
          <el-menu-item index="settings" @click="activeMenu = 'settings'">
            <el-icon><Setting /></el-icon>
            <span>个人设置</span>
          </el-menu-item>
          <el-menu-item index="logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-card>

      <!-- 右侧内容区 -->
      <div class="profile-main">
        <!-- 订单管理 -->
        <div v-if="activeMenu === 'orders'" class="tab-content">
          <div class="tab-header">
            <h3>我的订单</h3>
            <el-button type="primary" @click="$router.push('/orders')">查看全部订单</el-button>
          </div>
          <el-tabs v-model="orderTab" class="order-tabs">
            <el-tab-pane label="最近订单" name="recent">
              <el-table :data="recentOrders" style="width: 100%">
                <el-table-column prop="order_no" label="订单号" width="180" />
                <el-table-column label="商品信息" width="300">
                  <template #default="{ row }">
                    <div class="product-info-cell">
                      <img :src="row.items[0]?.image_url" alt="" class="product-img">
                      <span>{{ row.items[0]?.product_name }}</span>
                      <span v-if="row.items.length > 1" class="more-items">等{{ row.items.length }}件商品</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="final_amount" label="实付金额" width="120">
                  <template #default="{ row }">¥{{ row.final_amount.toFixed(2) }}</template>
                </el-table-column>
                <el-table-column label="订单状态" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.order_status)" size="small">
                      {{ getStatusText(row.order_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="{ row }">
                    <el-button type="text" @click="$router.push(`/order/${row.order_id}`)">查看详情</el-button>
                    <el-button v-if="row.order_status === 0" type="text" @click="payOrder(row)">立即支付</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="待评价" name="review">
              <el-empty description="暂无待评价订单" v-if="reviewOrders.length === 0" />
              <div v-else class="review-list">
                <div v-for="order in reviewOrders" :key="order.order_id" class="review-item">
                  <div class="review-product">
                    <img :src="order.items[0]?.image_url" alt="" class="product-img">
                    <div class="product-details">
                      <h4>{{ order.items[0]?.product_name }}</h4>
                      <p class="order-info">订单号：{{ order.order_no }}</p>
                    </div>
                  </div>
                  <el-button type="primary" size="small" @click="goToReview(order)">立即评价</el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 收货地址管理 -->
<div v-else-if="activeMenu === 'address'" class="tab-content">
  <div class="tab-header">
    <h3>收货地址</h3>
    <el-button type="primary" @click="openAddAddress">添加新地址</el-button>
  </div>
  
  <!-- 加载状态 -->
  <div v-if="loadingAddresses" class="loading-addresses">
    <el-skeleton :rows="3" animated />
  </div>
  
  <!-- 空状态 -->
  <el-empty v-else-if="addresses.length === 0" description="暂无收货地址">
    <el-button type="primary" @click="showAddressDialog = true">添加第一个地址</el-button>
  </el-empty>
  
  <!-- 地址列表 -->
  <div v-else class="address-list">
    <el-card v-for="addr in addresses" :key="addr.address_id" class="address-card" 
             :class="{ 'default-address': addr.is_default === 1 }">
      <div class="address-header">
        <div class="address-title">
          <span class="receiver">{{ addr.receiver_name }}</span>
          <span class="phone">{{ addr.receiver_phone }}</span>
          <el-tag v-if="addr.is_default === 1" type="success" size="small">默认</el-tag>
        </div>
        <div class="address-actions">
          <el-button type="text" @click="editAddress(addr)">编辑</el-button>
          <el-button type="text" @click="setDefaultAddress(addr)" v-if="addr.is_default !== 1">设为默认</el-button>
          <el-button type="text" @click="deleteAddress(addr)" style="color: #f56c6c">删除</el-button>
        </div>
      </div>
      <div class="address-content">
        {{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.detail_address }}
        <span v-if="addr.postal_code" class="postal-code">邮编：{{ addr.postal_code }}</span>
      </div>
    </el-card>
  </div>
</div>



        <!-- 账户安全 -->
        <div v-else-if="activeMenu === 'security'" class="tab-content">
          <div class="tab-header">
            <h3>账户安全</h3>
          </div>
          <el-card class="security-list">
            <div class="security-item">
              <div class="security-info">
                <el-icon class="security-icon"><User /></el-icon>
                <div>
                  <h4>登录密码</h4>
                  <p>定期修改密码有助于保护账户安全</p>
                </div>
              </div>
              <el-button type="text" @click="showPasswordDialog = true">修改</el-button>
            </div>
            <div class="security-item">
              <div class="security-info">
                <el-icon class="security-icon"><Phone /></el-icon>
                <div>
                  <h4>绑定手机</h4>
                  <p>已绑定手机：{{ userInfo.phone || '未绑定' }}</p>
                </div>
              </div>
              <el-button type="text" @click="showPhoneDialog = true">
                {{ userInfo.phone ? '更换' : '绑定' }}
              </el-button>
            </div>

          </el-card>
        </div>

        <!-- 个人设置 -->
        <div v-else-if="activeMenu === 'settings'" class="tab-content">
          <div class="tab-header">
            <h3>个人设置</h3>
            <el-button v-if="!isEditing" type="primary" @click="startEditing">编辑信息</el-button>
          </div>
          
          <el-form 
            ref="settingsFormRef"
            :model="editForm" 
            :rules="settingsRules"
            label-width="120px" 
            class="settings-form"
          >
            <el-form-item label="用户名" prop="username">
              <el-input 
                v-model="editForm.username" 
                placeholder="请输入用户名"
                :disabled="!isEditing"
              />
            </el-form-item>
            
            <el-form-item label="手机号" prop="phone">
              <el-input 
                v-model="editForm.phone" 
                placeholder="请输入手机号"
                :disabled="!isEditing"
              />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input 
                v-model="editForm.email" 
                placeholder="请输入邮箱"
                :disabled="!isEditing"
              />
            </el-form-item>
            
            <el-form-item v-if="isEditing">
              <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
              <el-button @click="cancelEditing">取消</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 各种对话框 -->
    <!-- 充值对话框 -->
    <el-dialog v-model="showRecharge" title="账户充值" width="400px">
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="10" :max="10000" :step="100" />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="rechargeForm.payment_method">
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="wechat">微信支付</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecharge = false">取消</el-button>
        <el-button type="primary" @click="confirmRecharge">确认充值</el-button>
      </template>
    </el-dialog>

    <!-- 地址编辑对话框 -->
    <el-dialog v-model="showAddressDialog" :title="editingAddress ? '编辑地址' : '添加地址'" width="500px">
      <AddressForm 
        v-if="showAddressDialog"
        :address="editingAddress"
        @save="handleSaveAddress"
        @cancel="showAddressDialog = false"
      />
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <PasswordForm @save="handleChangePassword" @cancel="showPasswordDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tickets, Location, Lock, Setting,
  SwitchButton, User, Phone
} from '@element-plus/icons-vue'
import AddressForm from '@/components/AddressForm.vue'
import PasswordForm from '@/components/PasswordForm.vue'

// 🔧 新增：导入用户API
import userApi from '@/api/user'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

// 状态管理
const activeMenu = ref('orders')
const orderTab = ref('recent')
const showRecharge = ref(false)
const showAddressDialog = ref(false)
const showPasswordDialog = ref(false)
const editingAddress = ref(null)

// 🔧 新增：加载状态
const loading = ref(false)

// 表单数据
const rechargeForm = ref({
  amount: 100,
  payment_method: 'alipay'
})

// 个人设置相关状态
const settingsFormRef = ref()
const isEditing = ref(false)
const saving = ref(false)

// 编辑表单数据
const editForm = reactive({
  username: '',
  phone: '',
  email: ''
})

// 验证规则
const settingsRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

// 🔧 修改：清空模拟数据，使用空对象
const userInfo = ref({})
const stats = ref({
  orderCount: 0,
  favoriteCount: 0,
  couponCount: 0
})

// 模拟数据（其他部分保持不变）
const recentOrders = ref([
  {
    order_id: 1001,
    order_no: 'ORD202412150001',
    final_amount: 10497.00,
    order_status: 1,
    items: [
      { product_name: 'iPhone 15 Pro Max', image_url: 'iphone15.jpg' },
      { product_name: '男士商务衬衫', image_url: 'shirt.jpg' }
    ]
  },
  {
    order_id: 1002,
    order_no: 'ORD202412140002',
    final_amount: 6949.00,
    order_status: 2,
    items: [
      { product_name: '华为 Mate 60 Pro', image_url: 'mate60.jpg' }
    ]
  }
])

const reviewOrders = ref([])

// 真实数据
const addresses = ref([])
const loadingAddresses = ref(false)

// 获取地址列表函数
const fetchAddresses = async () => {
  loadingAddresses.value = true
  try {
    console.log('🔍 获取地址列表...')
    const response = await userApi.getAddresses()
    console.log('✅ 地址列表响应:', response)

    // 统一处理响应：后端可能返回 { code: 200, data: [...] } 或 直接返回数组
    const data = response.data
    if (data && data.code === 200) {
      addresses.value = data.data || []
      console.log(`📋 加载了 ${addresses.value.length} 个地址 (from data.data)`)
    } else if (response.status === 200 && Array.isArray(response.data)) {
      addresses.value = response.data
      console.log(`📋 加载了 ${addresses.value.length} 个地址 (直接数组响应)`)
    } else {
      console.error('❌ 获取地址列表失败:', data?.message || response.status)
      ElMessage.error('获取地址列表失败: ' + (data?.message || '未知错误'))
    }
  } catch (error) {
    console.error('❌ 获取地址列表异常:', error)
    ElMessage.error('获取地址列表失败: ' + (error.message || '网络错误'))
  } finally {
    loadingAddresses.value = false
  }
}

const favorites = ref([
  {
    favorite_id: 1,
    product_id: 1,
    product_name: 'iPhone 15 Pro Max',
    price: 9999.00,
    original_price: 10999.00,
    image_url: 'iphone15.jpg',
    sold_quantity: 1200,
    stock_quantity: 100
  },
  {
    favorite_id: 2,
    product_id: 3,
    product_name: 'MacBook Pro 16寸',
    price: 18999.00,
    image_url: 'macbook.jpg',
    sold_quantity: 450,
    stock_quantity: 50
  }
])

const availableCoupons = ref([
  {
    id: 1,
    name: '新人专享券',
    amount: 50,
    type: '满减券',
    min_amount: 200,
    end_time: '2024-12-31'
  },
  {
    id: 2,
    name: '双十一折扣券',
    amount: 100,
    type: '折扣券',
    min_amount: 1000,
    end_time: '2024-11-30'
  }
])

const usedCoupons = ref([])
const expiredCoupons = ref([])

// 🔧 修改：修复fetchUserInfo函数，正确处理API响应结构
const fetchUserInfo = async () => {
  loading.value = true
  try {
    console.log('🔍 开始获取用户信息...')
    
    // 调用API - 返回的是响应对象
    const response = await userApi.getCurrentUser()
    console.log('📦 API返回的完整响应:', response)
    
    // 🔧 修改：response.data 才是实际的数据
    const data = response.data
    console.log('📦 实际的数据:', data)
    
    if (data.code === 200 && data.data) {
      userInfo.value = data.data
      console.log('✅ 用户信息获取成功:', userInfo.value)
      
      // 如果用户有avatar_url，使用它
      if (!userInfo.value.avatar_url) {
        userInfo.value.avatar_url = ''
      }
    } else {
      console.error('❌ 用户信息获取失败（业务逻辑）:', data)
      ElMessage.error(data.message || '获取用户信息失败')
    }
  } catch (error) {
    console.error('❌ 获取用户信息异常:', error)
    ElMessage.error('获取用户信息失败：' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

// 个人设置相关方法
const startEditing = () => {
  isEditing.value = true
  // 复制当前用户信息到编辑表单
  editForm.username = userInfo.value.username || ''
  editForm.phone = userInfo.value.phone || ''
  editForm.email = userInfo.value.email || ''
}

const cancelEditing = () => {
  isEditing.value = false
  settingsFormRef.value?.resetFields()
}

const saveProfile = async () => {
  if (!settingsFormRef.value) return
  
  try {
    await settingsFormRef.value.validate()
    saving.value = true
    
    // 准备更新数据（只提交有变化的字段）
    const updateData = {}
    if (editForm.username !== userInfo.value.username) {
      updateData.username = editForm.username
    }
    if (editForm.phone !== userInfo.value.phone) {
      updateData.phone = editForm.phone
    }
    if (editForm.email !== userInfo.value.email) {
      updateData.email = editForm.email
    }
    
    // 如果没有变化，直接返回
    if (Object.keys(updateData).length === 0) {
      ElMessage.info('没有修改任何信息')
      isEditing.value = false
      return
    }
    
    console.log('📝 提交更新数据:', updateData)
    
    // 调用API
    const response = await userApi.updateProfile(updateData)
    console.log('✅ 更新成功:', response)
    
    // 更新本地数据
    Object.assign(userInfo.value, updateData)
    
    // 更新store
    userStore.updateUserInfo(updateData)
    
    ElMessage.success('个人信息更新成功')
    isEditing.value = false
    
  } catch (error) {
    console.error('❌ 更新失败:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '更新失败')
  } finally {
    saving.value = false
  }
}

// 工具函数
const getUserType = () => {
  const types = { 0: '普通用户', 1: '商家', 2: '管理员' }
  return types[userInfo.value.user_type] || '未知'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return dateStr.split(' ')[0]
}

const getStatusText = (status) => {
  const statusMap = {
    0: '待支付', 1: '已支付', 2: '已发货', 3: '已完成', 4: '已取消'
  }
  return statusMap[status] || '未知'
}

const getStatusType = (status) => {
  const typeMap = {
    0: 'warning', 1: 'primary', 2: 'success', 3: 'info', 4: 'danger'
  }
  return typeMap[status] || 'info'
}

// 操作方法
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  })
}

const payOrder = (order) => {
  router.push(`/checkout?order_id=${order.order_id}`)
}

const goToReview = (order) => {
  ElMessage.info('跳转到评价页面')
  // router.push(`/review/${order.order_id}`)
}

const openAddAddress = () => {
  // 清空编辑地址，确保打开的是“新增”对话框而非残留的编辑数据
  editingAddress.value = null
  showAddressDialog.value = true
}

const editAddress = (addr) => {
  editingAddress.value = { ...addr }
  showAddressDialog.value = true
}


const setDefaultAddress = async (addr) => {
  try {
    console.log(`⭐ 设置默认地址: ${addr.address_id}`)
    const response = await userApi.setDefaultAddress(addr.address_id)
    
    if (response.code === 200) {
      ElMessage.success('已设为默认地址')
      // 刷新地址列表
      await fetchAddresses()
    } else {
      ElMessage.error(response.message || '设置默认地址失败')
    }
  } catch (error) {
    console.error('❌ 设置默认地址失败:', error)
    ElMessage.error('设置默认地址失败: ' + (error.message || '网络错误'))
  }
}

const deleteAddress = async (addr) => {
  try {
    await ElMessageBox.confirm('确定要删除这个地址吗？', '删除地址', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    console.log(`🗑️ 删除地址: ${addr.address_id}`)
    const response = await userApi.deleteAddress(addr.address_id)
    
    if (response.code === 200) {
      ElMessage.success('地址已删除')
      // 刷新地址列表
      await fetchAddresses()
    } else {
      ElMessage.error(response.message || '删除地址失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('❌ 删除地址失败:', error)
      ElMessage.error('删除地址失败: ' + (error.message || '网络错误'))
    }
  }
}

const handleSaveAddress = async (addressData) => {
  try {
    console.log('💾 保存地址数据:', addressData)
    
    let response
    const isEdit = !!(editingAddress.value && editingAddress.value.address_id)
    if (isEdit) {
      // 更新地址
      response = await userApi.updateAddress(editingAddress.value.address_id, addressData)
    } else {
      // 添加新地址
      response = await userApi.addAddress(addressData)
    }
    
    console.log('✅ 保存地址响应:', response)
    const res = response.data
    // 兼容后端两种返回：{ code: 200 } 或 直接 status 200
    if ((res && res.code === 200) || response.status === 200) {
      ElMessage.success('地址保存成功')
      // 刷新地址列表
      await fetchAddresses()
      showAddressDialog.value = false
      editingAddress.value = null
    } else {
      ElMessage.error(res?.message || '地址保存失败')
    }
  } catch (error) {
    console.error('❌ 保存地址失败:', error)
    ElMessage.error('保存地址失败: ' + (error.message || '网络错误'))
  }
}

const addToCart = (product) => {
  cartStore.addToCart({
    product_id: product.product_id,
    product_name: product.product_name,
    price: product.price,
    image_url: product.image_url,
    stock_quantity: product.stock_quantity
  }, 1)
  ElMessage.success('已加入购物车')
}

const goToCouponCenter = () => {
  ElMessage.info('跳转到领券中心')
  // router.push('/coupons')
}

const confirmRecharge = () => {
  ElMessage.success(`充值${rechargeForm.value.amount}元成功`)
  userInfo.value.balance += rechargeForm.value.amount
  showRecharge.value = false
}

const handleChangePassword = async (passwordData) => {
  try {
    // 调用后端API来修改密码
    console.log('修改密码数据:', passwordData)
    const response = await userApi.changePassword({
      currentPassword: passwordData.currentPassword,
      newPassword: passwordData.newPassword
    })
    console.log('密码修改成功:', response)
    ElMessage.success('密码修改成功')
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败: ' + (error.response?.data?.detail || error.message || '网络错误'))
  } finally {
    showPasswordDialog.value = false
  }
}

onMounted(() => {
  // 从localStorage加载用户信息
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    try {
      const parsedUser = JSON.parse(savedUser)
      userInfo.value = { ...userInfo.value, ...parsedUser }
    } catch (e) {
      console.error('加载用户信息失败', e)
    }
  }
  
  // 🔧 新增：当切换到地址标签时加载地址
  // 或者可以在组件挂载时预加载
})
</script>

<style scoped>
.profile-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* 🔧 新增：加载状态样式 */
.loading-overlay {
  padding: 40px;
}

.empty-state {
  text-align: center;
  padding: 100px 0;
}

.profile-header {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.profile-header :deep(.el-card__body) {
  padding: 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 25px;
}

.user-avatar {
  background: white;
  color: #764ba2;
  font-size: 32px;
  font-weight: bold;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.username {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
  color: white;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-id, .register-time {
  font-size: 14px;
  opacity: 0.9;
}

.user-stats {
  display: flex;
  gap: 30px;
  margin-top: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

.account-info {
  display: flex;
  gap: 20px;
}

.balance-card, .points-card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 20px;
  min-width: 150px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.balance-title, .points-title {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.balance-amount {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 15px;
}

.points-amount {
  font-size: 24px;
  font-weight: 600;
  color: #ffd700;
  margin-bottom: 15px;
}

.profile-content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
}

.profile-sidebar {
  height: fit-content;
}

.profile-menu {
  border: none;
}

.profile-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 5px 0;
  border-radius: 6px;
}

.profile-menu :deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
}

.profile-main {
  min-height: 600px;
}

.tab-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

.tab-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.product-info-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-img {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}

.more-items {
  font-size: 12px;
  color: #999;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  background: #f9f9f9;
}

.review-product {
  display: flex;
  align-items: center;
  gap: 15px;
}

.product-details h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.order-info {
  font-size: 12px;
  color: #999;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.address-card {
  transition: all 0.3s;
}

.address-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.default-address {
  border: 2px solid #67c23a;
}

.address-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.address-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.receiver {
  font-weight: 600;
  font-size: 16px;
}

.phone {
  color: #666;
}

.address-content {
  color: #333;
  line-height: 1.6;
}

.postal-code {
  display: block;
  margin-top: 5px;
  color: #999;
  font-size: 14px;
}

.favorites-list {
  margin-top: 20px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.favorite-item {
  position: relative;
}

.favorite-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-5px)
}

.product-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px 4px 0 0;
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.current-price {
  font-size: 18px;
  color: #e53935;
  font-weight: 600;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.product-actions {
  display: flex;
  justify-content: space-between;
  padding: 0 15px 15px;
}

.coupon-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.coupon-card {
  border: 2px dashed #e8e8e8;
  background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
}

.coupon-card.usable {
  border-color: #67c23a;
}

.coupon-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.coupon-amount {
  text-align: center;
  min-width: 100px;
}

.coupon-amount .amount {
  font-size: 32px;
  font-weight: 600;
  color: #e53935;
  display: block;
}

.coupon-amount .type {
  font-size: 12px;
  color: #666;
}

.coupon-info {
  flex: 1;
  padding: 0 20px;
}

.coupon-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.condition, .validity {
  margin: 5px 0;
  font-size: 13px;
  color: #666;
}

.security-list {
  border: none;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.security-item:last-child {
  border-bottom: none;
}

.security-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.security-icon {
  font-size: 24px;
  color: #409eff;
}

.security-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.security-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.settings-form {
  max-width: 600px;
  margin-top: 20px;
}
</style>