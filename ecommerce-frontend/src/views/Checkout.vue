<template>
  <div class="checkout-page">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/cart' }">购物车</el-breadcrumb-item>
        <el-breadcrumb-item>结算订单</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 结算步骤 -->
    <div class="checkout-steps">
      <el-steps :active="activeStep" finish-status="success">
        <el-step title="确认订单" description="核对商品信息" />
        <el-step title="选择地址" description="选择收货地址" />
        <el-step title="支付方式" description="选择支付方式" />
        <el-step title="完成支付" description="完成订单支付" />
      </el-steps>
    </div>

    <!-- 步骤1：确认订单 -->
    <div v-if="activeStep === 1" class="checkout-step">
      <h2 class="step-title">1. 确认订单信息</h2>
      
      <!-- 商品列表 -->
      <div class="order-items">
        <div class="order-header">
          <div class="header-left">商品信息</div>
          <div class="header-right">
            <div class="header-column">单价</div>
            <div class="header-column">数量</div>
            <div class="header-column">小计</div>
          </div>
        </div>
        
        <div
          v-for="item in selectedItems"
          :key="item.product_id"
          class="order-item"
        >
          <div class="item-left">
            <img :src="item.image_url || defaultImage" :alt="item.product_name" />
            <div class="item-info">
              <h3>{{ item.product_name }}</h3>
              <div v-if="item.spec" class="item-spec">{{ item.spec }}</div>
              <div class="item-stock">库存：{{ item.stock_quantity }} 件</div>
            </div>
          </div>
          
          <div class="item-right">
            <div class="item-column">
              <div class="price">¥{{ item.price.toFixed(2) }}</div>
              <div v-if="item.original_price" class="original-price">
                ¥{{ item.original_price.toFixed(2) }}
              </div>
            </div>
            <div class="item-column quantity">
              ×{{ item.quantity }}
            </div>
            <div class="item-column subtotal">
              ¥{{ (item.price * item.quantity).toFixed(2) }}
            </div>
          </div>
        </div>
        
        <div class="order-summary">
          <div class="summary-item">
            <span>商品合计：</span>
            <span>¥{{ cartStore.selectedAmount }}</span>
          </div>
          <div class="summary-item">
            <span>运费：</span>
            <span v-if="shippingFee === 0">包邮</span>
            <span v-else>+ ¥{{ shippingFee.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span>优惠券：</span>
            <span class="discount">- ¥{{ couponDiscount.toFixed(2) }}</span>
          </div>
          <div class="summary-item total">
            <span>应付总额：</span>
            <span class="total-price">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
        </div>
      </div>
      
      <div class="step-actions">
        <el-button @click="goBackToCart">返回购物车</el-button>
        <el-button type="primary" @click="nextStep">下一步：选择地址</el-button>
      </div>
    </div>

    <!-- 步骤2：选择地址 -->
    <div v-else-if="activeStep === 2" class="checkout-step">
      <h2 class="step-title">2. 选择收货地址</h2>
      
      <div class="address-section">
        <div class="address-list">
          <div
            v-for="address in addresses"
            :key="address.address_id"
            class="address-card"
            :class="{ selected: selectedAddressId === address.address_id }"
            @click="selectAddress(address.address_id)"
          >
            <div class="address-header">
              <span class="receiver">{{ address.receiver_name }}</span>
              <span class="phone">{{ address.receiver_phone }}</span>
              <el-tag v-if="address.is_default" type="primary" size="small">默认</el-tag>
            </div>
            <div class="address-content">
              {{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail_address }}
            </div>
            <div class="address-actions">
              <el-button type="primary" link @click.stop="editAddress(address)">编辑</el-button>
              <el-button type="danger" link @click.stop="deleteAddress(address.address_id)">删除</el-button>
            </div>
          </div>
          
          <div class="add-address" @click="addNewAddress">
            <el-icon :size="40" color="#409EFF"><Plus /></el-icon>
            <div>添加新地址</div>
          </div>
        </div>
      </div>
      
      <!-- 地址表单对话框 -->
      <el-dialog
        v-model="addressDialogVisible"
        :title="isEditingAddress ? '编辑地址' : '新增地址'"
        width="500px"
      >
        <el-form
          ref="addressFormRef"
          :model="addressForm"
          :rules="addressRules"
          label-width="80px"
        >
          <el-form-item label="收货人" prop="receiver_name">
            <el-input v-model="addressForm.receiver_name" />
          </el-form-item>
          <el-form-item label="手机号" prop="receiver_phone">
            <el-input v-model="addressForm.receiver_phone" />
          </el-form-item>
          <el-form-item label="所在地区" prop="region">
            <el-cascader
              v-model="addressForm.region"
              :options="regionOptions"
              placeholder="请选择省/市/区"
            />
          </el-form-item>
          <el-form-item label="详细地址" prop="detail_address">
            <el-input
              v-model="addressForm.detail_address"
              type="textarea"
              rows="2"
              placeholder="请输入详细地址，如街道、小区、楼栋号、单元室等"
            />
          </el-form-item>
          <el-form-item label="邮政编码" prop="postal_code">
            <el-input v-model="addressForm.postal_code" />
          </el-form-item>
          <el-form-item label="设为默认">
            <el-switch v-model="addressForm.is_default" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="addressDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAddress">保存</el-button>
        </template>
      </el-dialog>
      
      <div class="step-actions">
        <el-button @click="prevStep">上一步</el-button>
        <el-button type="primary" :disabled="!selectedAddressId" @click="nextStep">
          下一步：支付方式
        </el-button>
      </div>
    </div>

    <!-- 步骤3：支付方式 -->
    <div v-else-if="activeStep === 3" class="checkout-step">
      <h2 class="step-title">3. 选择支付方式</h2>
      
      <div class="payment-section">
        <div class="payment-methods">
          <div
            v-for="method in paymentMethods"
            :key="method.id"
            class="payment-method"
            :class="{ selected: selectedPaymentMethod === method.id }"
            @click="selectPaymentMethod(method.id)"
          >
            <div class="method-icon">
              <el-icon :size="30" :color="method.color">
                <component :is="method.icon" />
              </el-icon>
            </div>
            <div class="method-info">
              <h3>{{ method.name }}</h3>
              <p>{{ method.description }}</p>
            </div>
            <div class="method-check">
              <el-radio :model-value="selectedPaymentMethod" :label="method.id" />
            </div>
          </div>
        </div>
        
        <div class="order-summary-card">
          <h3>订单信息</h3>
          <div class="summary-content">
            <div class="summary-row">
              <span>商品金额：</span>
              <span>¥{{ cartStore.selectedAmount }}</span>
            </div>
            <div class="summary-row">
              <span>运费：</span>
              <span v-if="shippingFee === 0">包邮</span>
              <span v-else>¥{{ shippingFee.toFixed(2) }}</span>
            </div>
            <div class="summary-row">
              <span>优惠：</span>
              <span class="discount">- ¥{{ couponDiscount.toFixed(2) }}</span>
            </div>
            <div class="summary-row total">
              <span>应付总额：</span>
              <span class="total-price">¥{{ totalAmount.toFixed(2) }}</span>
            </div>
          </div>
          
          <div class="agreement">
            <el-checkbox v-model="agreeAgreement">
              我已阅读并同意
              <el-link type="primary" :underline="false">《用户购买协议》</el-link>
            </el-checkbox>
          </div>
          
          <el-button
            type="danger"
            size="large"
            :disabled="!agreeAgreement || !selectedPaymentMethod"
            @click="submitOrder"
            class="submit-order-btn"
          >
            提交订单
          </el-button>
        </div>
      </div>
      
      <div class="step-actions">
        <el-button @click="prevStep">上一步</el-button>
        <el-button type="info" @click="saveOrderAsDraft">保存为草稿</el-button>
      </div>
    </div>

    <!-- 步骤4：支付完成 -->
    <div v-else class="checkout-step">
      <h2 class="step-title">4. 支付完成</h2>
      
      <div class="success-section">
        <div class="success-icon">
          <el-icon :size="80" color="#67C23A"><CircleCheck /></el-icon>
        </div>
        <h2>支付成功！</h2>
        <p class="order-number">订单号：{{ orderInfo.order_no }}</p>
        <p class="order-amount">支付金额：<span class="amount">¥{{ (orderInfo.total_amount || orderInfo.final_amount || orderInfo.amount || 0).toFixed(2) }}</span></p>
        <p class="success-tip">我们将在24小时内为您发货，请保持手机畅通</p>
        
        <div class="success-actions">
          <el-button @click="viewOrderDetail">查看订单详情</el-button>
          <el-button type="primary" @click="goToHome">继续购物</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  CircleCheck,
  CreditCard,
  Wallet,
  Coin,
  Platform
} from '@element-plus/icons-vue'

// 导入API
import { createOrder, payOrder } from '@/api/orders'
import userApi from '@/api/user'

const router = useRouter()
const cartStore = useCartStore()

const activeStep = ref(1)
const shippingFee = ref(0)
const couponDiscount = ref(0)
const selectedAddressId = ref(null)
const selectedPaymentMethod = ref('')
const agreeAgreement = ref(false)
const addressDialogVisible = ref(false)
const isEditingAddress = ref(false)

const defaultImage = 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w-300&h=300&fit=crop'

// 订单信息
const orderInfo = ref({
  order_no: '',
  amount: 0,
  create_time: new Date().toISOString()
})

// 地址数据
const addresses = ref([])

// 地址表单
const addressForm = ref({
  receiver_name: '',
  receiver_phone: '',
  region: [],
  detail_address: '',
  postal_code: '',
  is_default: false
})

const addressFormRef = ref()

const addressRules = {
  receiver_name: [
    { required: true, message: '请输入收货人姓名', trigger: 'blur' }
  ],
  receiver_phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  region: [
    { required: true, message: '请选择所在地区', trigger: 'change' }
  ],
  detail_address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' },
    { min: 5, message: '地址至少5个字符', trigger: 'blur' }
  ]
}

const regionOptions = [
  {
    value: 'beijing',
    label: '北京市',
    children: [
      { value: 'chaoyang', label: '朝阳区' },
      { value: 'haidian', label: '海淀区' },
      { value: 'dongcheng', label: '东城区' }
    ]
  },
  {
    value: 'shanghai',
    label: '上海市',
    children: [
      { value: 'pudong', label: '浦东新区' },
      { value: 'huangpu', label: '黄浦区' },
      { value: 'xuhui', label: '徐汇区' }
    ]
  }
]

// 支付方式
const paymentMethods = ref([
  {
    id: 'alipay',
    name: '支付宝',
    icon: Platform,  // 使用 Platform 图标替代
    color: '#1677FF',
    description: '推荐支付宝用户使用'
  },
  {
    id: 'wechat',
    name: '微信支付',
    icon: Coin,      // 使用 Coin 图标替代
    color: '#07C160',
    description: '推荐微信用户使用'
  },
  {
    id: 'bankcard',
    name: '银行卡支付',
    icon: CreditCard,
    color: '#722ED1',
    description: '支持储蓄卡/信用卡'
  },
  {
    id: 'balance',
    name: '余额支付',
    icon: Wallet,    // 使用 Wallet 图标替代
    color: '#FA8C16',
    description: '使用账户余额支付'
  }
])

// 计算属性
const selectedItems = computed(() => cartStore.selectedItems)
const totalAmount = computed(() => {
  return parseFloat(cartStore.selectedAmount) + shippingFee.value - couponDiscount.value
})

// 方法
const goBackToCart = () => {
  router.push('/cart')
}

const nextStep = () => {
  if (activeStep.value < 4) {
    activeStep.value++
    
    // 如果是最后一步，计算订单信息
    if (activeStep.value === 4) {
      orderInfo.value.amount = totalAmount.value
    }
  }
}

const prevStep = () => {
  if (activeStep.value > 1) {
    activeStep.value--
  }
}

const selectAddress = (addressId) => {
  selectedAddressId.value = addressId
}

const addNewAddress = () => {
  isEditingAddress.value = false
  addressForm.value = {
    receiver_name: '',
    receiver_phone: '',
    region: [],
    detail_address: '',
    postal_code: '',
    is_default: addresses.value.length === 0
  }
  addressDialogVisible.value = true
}

const editAddress = (address) => {
  isEditingAddress.value = true
  addressForm.value = {
    receiver_name: address.receiver_name,
    receiver_phone: address.receiver_phone,
    region: [address.province, address.city, address.district],
    detail_address: address.detail_address,
    postal_code: address.postal_code,
    is_default: address.is_default
  }
  addressDialogVisible.value = true
}

const deleteAddress = (addressId) => {
  ElMessageBox.confirm('确定要删除这个地址吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    addresses.value = addresses.value.filter(addr => addr.address_id !== addressId)
    ElMessage.success('删除成功')
    
    // 如果删除的是当前选中的地址，清空选择
    if (selectedAddressId.value === addressId) {
      selectedAddressId.value = null
    }
  }).catch(() => {})
}

const saveAddress = async () => {
  if (!addressFormRef.value) return
  
  try {
    await addressFormRef.value.validate()
    
    if (isEditingAddress.value) {
      // 更新地址
      ElMessage.success('地址更新成功')
    } else {
      // 新增地址
      const newAddress = {
        address_id: Date.now(),
        ...addressForm.value,
        province: addressForm.value.region[0] || '',
        city: addressForm.value.region[1] || '',
        district: addressForm.value.region[2] || ''
      }
      
      addresses.value.push(newAddress)
      ElMessage.success('地址添加成功')
      
      // 如果是第一个地址或设为默认，自动选中
      if (newAddress.is_default || addresses.value.length === 1) {
        selectedAddressId.value = newAddress.address_id
      }
    }
    
    addressDialogVisible.value = false
  } catch (error) {
    console.error('地址验证失败:', error)
  }
}

const selectPaymentMethod = (methodId) => {
  selectedPaymentMethod.value = methodId
}

// 获取地址列表
const fetchAddresses = async () => {
  try {
    const response = await userApi.getAddresses()
    if (response.data.code === 200) {
      addresses.value = response.data.data
      console.log('API返回的地址列表:', addresses.value)
      
      // 设置默认地址
      const defaultAddress = addresses.value.find(addr => addr.is_default)
      if (defaultAddress) {
        selectedAddressId.value = defaultAddress.address_id
        console.log('默认地址ID:', selectedAddressId.value)
      }
    }
  } catch (error) {
    console.error('获取地址失败:', error)
  }
}

// 提交订单
const submitOrder = async () => {
  console.log('=== submitOrder 开始 ===')
  console.log('selectedAddressId:', selectedAddressId.value)
  console.log('selectedPaymentMethod:', selectedPaymentMethod.value)
  console.log('agreeAgreement:', agreeAgreement.value)
  console.log('selectedItems:', selectedItems.value)
  
  if (!selectedAddressId.value) {
    ElMessage.error('请选择收货地址')
    return
  }
  
  if (!selectedPaymentMethod.value) {
    ElMessage.error('请选择支付方式')
    return
  }
  
  ElMessageBox.confirm('确认提交订单吗？', '提示', {
    confirmButtonText: '确认支付',
    cancelButtonText: '再想想',
    type: 'warning'
  }).then(async () => {
    console.log('用户确认提交订单 - 进入then回调')
    console.log('开始执行创建订单逻辑')
    
    let loadingMessage = null  // 在这里声明
    
    try {
      // 使用简单的信息提示代替loading
      loadingMessage = ElMessage({
        message: '订单创建中...',
        type: 'info',
        duration: 0 // 不自动关闭
      })
      
      console.log('准备订单数据...')
      // 准备订单数据
      const orderData = {
        address_id: parseInt(selectedAddressId.value),
        cart_ids: cartStore.selectedItems.map(item => parseInt(item.cart_id)),
        shipping_fee: shippingFee.value,
        remark: ""
      }
      
      console.log('订单数据:', orderData)
      console.log('调用 createOrder API...')
      
      // 调用API创建订单
      const response = await createOrder(orderData)
      
      console.log('API响应:', response)
      console.log('响应数据:', response.data)
      console.log('响应状态码:', response.data.code)
      
      if (response.data.code === 200) {
        console.log('订单创建成功')
        
        // 设置订单信息（包含金额）
        const orderData = response.data.data
        orderInfo.value = {
          ...orderData,
          amount: totalAmount.value  // 使用前端计算的金额
        }
        
        console.log('订单信息:', orderInfo.value)
        console.log('订单号:', orderInfo.value.order_no)
        console.log('订单金额:', orderInfo.value.amount)
        
        try {
          // 订单创建成功后，立即调用支付接口
          console.log('开始调用支付接口...')
          
          // 更新loading提示
          if (loadingMessage && typeof loadingMessage.close === 'function') {
            loadingMessage.close()
          }
          
          loadingMessage = ElMessage({
            message: '正在处理支付...',
            type: 'info',
            duration: 0 // 不自动关闭
          })
          
          const payResponse = await payOrder(orderInfo.value.order_id)
          console.log('支付接口响应:', payResponse)
          
          if (payResponse.data && payResponse.data.code === 200) {
            console.log('支付成功')
            
            // 关闭loading提示
            if (loadingMessage && typeof loadingMessage.close === 'function') {
              loadingMessage.close()
            }
            
            // 跳转到完成页面
            nextStep()
            
            ElMessage.success('支付成功！')
          } else {
            console.log('支付失败', payResponse.data?.message)
            
            // 关闭loading提示
            if (loadingMessage && typeof loadingMessage.close === 'function') {
              loadingMessage.close()
            }
            
            ElMessage.error('支付失败：' + (payResponse.data?.message || '请稍后重试'))
            
            // 跳转到订单详情页面，让用户可以重新支付
            router.push(`/orders/${orderInfo.value.order_id}`)
          }
        } catch (payError) {
          console.error('支付过程中出错:', payError)
          
          // 关闭loading提示
          if (loadingMessage && typeof loadingMessage.close === 'function') {
            loadingMessage.close()
          }
          
          ElMessage.error('支付失败，请稍后重试')
          
          // 跳转到订单详情页面，让用户可以重新支付
          router.push(`/orders/${orderInfo.value.order_id}`)
        }
      } else {
        console.log('订单创建失败，响应码:', response.data.code)
        console.log('错误信息:', response.data.message)
        
        // 关闭loading提示
        if (loadingMessage && typeof loadingMessage.close === 'function') {
          loadingMessage.close()
        }
        ElMessage.error('订单创建失败：' + response.data.message)
      }
    } catch (error) {
      console.error('创建订单过程中出错:', error)
      console.error('错误类型:', error.name)
      console.error('错误消息:', error.message)
      console.error('错误堆栈:', error.stack)
      
      // 现在 loadingMessage 在作用域内
      if (loadingMessage && typeof loadingMessage.close === 'function') {
        loadingMessage.close()
      }
      
      ElMessage.error('订单创建失败，请重试')
    }
  }).catch((reason) => {
    console.log('用户取消提交订单，原因:', reason)
  })
}

// 查看订单详情
const viewOrderDetail = () => {
  if (orderInfo.value && orderInfo.value.order_id) {
    router.push(`/orders/${orderInfo.value.order_id}`)
  } else {
    // 如果没有order_id，跳转到订单列表
    router.push('/orders')
  }
}

// 返回首页
const goToHome = () => {
  router.push('/')
}

// 返回订单列表
const goToOrders = () => {
  router.push('/orders')
}

// 保存为草稿（模板中有引用）
const saveOrderAsDraft = () => {
  ElMessage.warning('暂不支持保存草稿功能')
}

// 初始化
onMounted(() => {
  cartStore.initCart()
  fetchAddresses()
  
  // 如果没有选中的商品，跳回购物车
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要购买的商品')
    router.push('/cart')
  }
})
</script>

<style scoped>
.checkout-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.checkout-steps {
  margin-bottom: 40px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.checkout-step {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.step-title {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.order-items {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.order-header {
  display: grid;
  grid-template-columns: 2fr 1fr;
  background: #f5f7fa;
  padding: 15px 20px;
  font-weight: 500;
  color: #606266;
}

.header-right {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  text-align: center;
}

.order-item {
  display: grid;
  grid-template-columns: 2fr 1fr;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.order-item:last-child {
  border-bottom: none;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.item-left img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.item-spec {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.item-stock {
  color: #606266;
  font-size: 14px;
}

.item-right {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: center;
  text-align: center;
}

.item-column {
  padding: 0 10px;
}

.price {
  font-size: 16px;
  color: #f56c6c;
  font-weight: 500;
  margin-bottom: 5px;
}

.original-price {
  font-size: 14px;
  color: #909399;
  text-decoration: line-through;
}

.quantity {
  font-size: 16px;
  color: #606266;
}

.subtotal {
  font-size: 18px;
  color: #303133;
  font-weight: 500;
}

.order-summary {
  padding: 20px;
  background: #fafafa;
  border-top: 1px solid #e4e7ed;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #606266;
}

.summary-item.total {
  font-size: 18px;
  color: #303133;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}

.total-price {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}

.discount {
  color: #67c23a;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.address-section {
  padding: 20px 0;
}

.address-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.address-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.address-card:hover {
  border-color: #409EFF;
}

.address-card.selected {
  border-color: #409EFF;
  background: #ecf5ff;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.receiver {
  font-weight: 500;
  color: #303133;
}

.phone {
  color: #606266;
}

.address-content {
  color: #606266;
  line-height: 1.5;
  margin-bottom: 15px;
  min-height: 40px;
}

.address-actions {
  display: flex;
  gap: 15px;
  opacity: 0;
  transition: opacity 0.3s;
}

.address-card:hover .address-actions {
  opacity: 1;
}

.add-address {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  padding: 40px 20px;
  color: #909399;
}

.add-address:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.add-address div {
  margin-top: 10px;
}

.payment-section {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 40px;
}

.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.payment-method {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.payment-method:hover {
  border-color: #409EFF;
}

.payment-method.selected {
  border-color: #409EFF;
  background: #ecf5ff;
}

.method-info h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 5px;
}

.method-info p {
  color: #909399;
  font-size: 14px;
}

.order-summary-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  position: sticky;
  top: 20px;
}

.order-summary-card h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.summary-content {
  margin-bottom: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #606266;
}

.summary-row.total {
  font-size: 18px;
  color: #303133;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}

.agreement {
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.submit-order-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
}

.success-section {
  text-align: center;
  padding: 60px 20px;
}

.success-icon {
  margin-bottom: 30px;
}

.success-section h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 20px;
}

.order-number {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.order-amount {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
}

.amount {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}

.success-tip {
  color: #909399;
  margin-bottom: 40px;
}

.success-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

@media (max-width: 768px) {
  .payment-section {
    grid-template-columns: 1fr;
  }
  
  .order-item {
    grid-template-columns: 1fr;
  }
  
  .item-right {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px dashed #e4e7ed;
  }
  
  .order-header {
    display: none;
  }
  
  .success-actions {
    flex-direction: column;
  }
}
</style>