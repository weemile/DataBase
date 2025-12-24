<template>
  <div class="order-detail-page" v-if="order">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/orders' }">我的订单</el-breadcrumb-item>
        <el-breadcrumb-item>订单详情</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 订单状态卡片 -->
    <div class="order-status-card">
      <div class="status-left">
        <h2>订单号：{{ order.order_no }}</h2>
        <div class="order-time">下单时间：{{ formatDateTime(order.create_time) }}</div>
      </div>
      <div class="status-right">
        <el-tag :type="getStatusTagType(order.order_status)" size="large">
          {{ getStatusText(order.order_status) }}
        </el-tag>
        <div v-if="order.pay_time" class="pay-time">支付时间：{{ formatDateTime(order.pay_time) }}</div>
      </div>
    </div>

    <!-- 收货地址 -->
    <div class="address-card">
      <div class="address-header">
        <el-icon><Location /></el-icon>
        <span class="title">收货信息</span>
      </div>
      <div class="address-content">
        <div class="receiver">
          <span class="name">{{ order.receiver_name }}</span>
          <span class="phone">{{ order.receiver_phone }}</span>
        </div>
        <div class="address">{{ order.province }}{{ order.city }}{{ order.district }}{{ order.detail_address }}</div>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="order-items-card">
      <div class="card-header">
        <h3>商品信息</h3>
      </div>
      <div class="order-items">
        <div class="order-header">
          <div class="header-left">商品</div>
          <div class="header-right">
            <div class="header-column">单价</div>
            <div class="header-column">数量</div>
            <div class="header-column">小计</div>
          </div>
        </div>
        
        <div
          v-for="item in order.items"
          :key="item.item_id"
          class="order-item"
        >
          <div class="item-left">
            <img :src="item.product_image" :alt="item.product_name" class="product-image" />
            <div class="item-info">
              <h4>{{ item.product_name }}</h4>
              <div class="item-spec" v-if="item.specification">规格：{{ item.specification }}</div>
            </div>
          </div>
          
          <div class="item-right">
            <div class="item-column price">¥{{ item.unit_price.toFixed(2) }}</div>
            <div class="item-column quantity">×{{ item.quantity }}</div>
            <div class="item-column subtotal">¥{{ item.subtotal.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单金额汇总 -->
    <div class="order-summary-card">
      <div class="card-header">
        <h3>订单金额</h3>
      </div>
      <div class="summary-content">
        <div class="summary-row">
          <span>商品金额：</span>
          <span>¥{{ order.total_amount.toFixed(2) }}</span>
        </div>
        <div class="summary-row" v-if="order.discount_amount > 0">
          <span>优惠金额：</span>
          <span class="discount">- ¥{{ order.discount_amount.toFixed(2) }}</span>
        </div>
        <div class="summary-row">
          <span>运费：</span>
          <span v-if="order.shipping_fee === 0">包邮</span>
          <span v-else>¥{{ order.shipping_fee.toFixed(2) }}</span>
        </div>
        <div class="summary-row total">
          <span>实付金额：</span>
          <span class="total-amount">¥{{ order.final_amount.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- 订单操作 -->
    <div class="order-actions" v-if="order.order_status === 0">
      <el-button type="primary" @click="payOrder">立即支付</el-button>
      <el-button @click="cancelOrder">取消订单</el-button>
    </div>
    
    <div class="order-actions" v-else-if="order.order_status === 1">
      <el-button type="success" @click="confirmReceive">确认收货</el-button>
      <el-button @click="viewLogistics">查看物流</el-button>
    </div>
  </div>

  <!-- 加载中 -->
  <div v-else class="loading">
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Location } from '@element-plus/icons-vue'
import { getOrderDetail, payOrder as apiPayOrder, cancelOrder as apiCancelOrder } from '@/api/orders'

const route = useRoute()
const router = useRouter()

const order = ref(null)
const loading = ref(true)

// 获取订单详情
const fetchOrderDetail = async () => {
  try {
    const orderId = route.params.id
    const response = await getOrderDetail(orderId)
    
    if (response.data.code === 200) {
      order.value = response.data.data
      console.log('订单详情:', order.value)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
    ElMessage.error('获取订单详情失败')
  } finally {
    loading.value = false
  }
}

// 支付订单
const payOrder = async () => {
  try {
    ElMessageBox.confirm('确认支付该订单吗？', '支付确认', {
      confirmButtonText: '确认支付',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      const response = await apiPayOrder(order.value.order_id)
      
      if (response.data && response.data.code === 200) {
        ElMessage.success('支付成功')
        // 刷新订单详情，让用户在详情页查看支付结果
        await fetchOrderDetail()
      } else {
        ElMessage.error(response.data?.message || '支付失败')
      }
    })
  } catch (error) {
    console.error('支付失败:', error)
    ElMessage.error('支付失败')
  }
}

// 取消订单
const cancelOrder = async () => {
  try {
    ElMessageBox.confirm('确认取消该订单吗？', '取消确认', {
      confirmButtonText: '确认取消',
      cancelButtonText: '再想想',
      type: 'warning'
    }).then(async () => {
      const response = await apiCancelOrder(order.value.order_id)
      
      if (response.data.code === 200) {
        ElMessage.success('订单已取消')
        await fetchOrderDetail()
      } else {
        ElMessage.error(response.data.message || '取消失败')
      }
    })
  } catch (error) {
    console.error('取消订单失败:', error)
    ElMessage.error('取消失败')
  }
}

// 确认收货
const confirmReceive = () => {
  ElMessage.warning('确认收货功能暂未实现')
}

// 查看物流
const viewLogistics = () => {
  ElMessage.warning('查看物流功能暂未实现')
}

// 状态映射
const getStatusText = (status) => {
  const statusMap = {
    0: '待支付',
    1: '待发货',
    2: '已发货',
    3: '已完成',
    4: '已取消'
  }
  return statusMap[status] || '未知状态'
}

const getStatusTagType = (status) => {
  const typeMap = {
    0: 'warning',
    1: 'primary',
    2: 'info',
    3: 'success',
    4: 'danger'
  }
  return typeMap[status] || 'info'
}

// 时间格式化
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 初始化
onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.order-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.order-status-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.status-left h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.order-time {
  color: #909399;
  font-size: 14px;
}

.status-right {
  text-align: right;
}

.pay-time {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}

.address-card,
.order-items-card,
.order-summary-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.address-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.address-header .el-icon {
  margin-right: 8px;
  color: #409EFF;
}

.address-header .title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.receiver {
  margin-bottom: 8px;
}

.receiver .name {
  font-size: 16px;
  font-weight: 500;
  margin-right: 15px;
}

.receiver .phone {
  color: #606266;
}

.address {
  color: #606266;
  line-height: 1.6;
}

.card-header {
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
  color: #909399;
  font-size: 14px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  width: 300px;
}

.header-column {
  flex: 1;
  text-align: center;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.item-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.product-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 15px;
}

.item-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.item-spec {
  color: #909399;
  font-size: 12px;
}

.item-right {
  display: flex;
  width: 300px;
}

.item-column {
  flex: 1;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.price, .subtotal {
  color: #303133;
  font-weight: 500;
}

.quantity {
  color: #606266;
}

.summary-content {
  padding: 0 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.summary-row.total {
  border-bottom: none;
  margin-top: 10px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.discount {
  color: #67C23A;
}

.total-amount {
  color: #F56C6C;
  font-size: 24px;
}

.order-actions {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: right;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.order-actions .el-button {
  margin-left: 10px;
}

.loading {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>