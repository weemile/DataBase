<template>
  <div class="orders-page">
    <div class="page-header">
      <h2>我的订单</h2>
    </div>
    
    <el-tabs v-model="activeTab" class="order-tabs">
      <el-tab-pane label="全部" name="all"></el-tab-pane>
      <el-tab-pane label="待支付" name="pending"></el-tab-pane>
      <el-tab-pane label="待发货" name="unshipped"></el-tab-pane>
      <el-tab-pane label="待收货" name="shipped"></el-tab-pane>
      <el-tab-pane label="已完成" name="completed"></el-tab-pane>
    </el-tabs>

    <div class="order-list" v-if="orders.length > 0">
      <el-card v-for="order in orders" :key="order.id" class="order-card">
        <!-- 订单头部 -->
        <div class="order-header">
          <div class="order-info">
            <span class="order-no">订单号：{{ order.order_no }}</span>
            <span class="order-time">下单时间：{{ formatTime(order.create_time) }}</span>
          </div>
          <div class="order-status">
            <el-tag :type="getStatusType(order.order_status)">
              {{ getStatusText(order.order_status) }}
            </el-tag>
          </div>
        </div>

        <!-- 商品数量 -->
        <div class="product-count">
          商品数量：{{ getProductCount(order) }}件
        </div>

        <!-- 订单金额 -->
        <div class="order-summary">
          <div class="summary-item">
            <span>商品总价：</span>
            <span>¥{{ (order.total_amount || 0).toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span>运费：</span>
            <span>¥{{ (order.shipping_fee || 0).toFixed(2) }}</span>
          </div>
          <div class="summary-item total">
            <span>实付金额：</span>
            <span class="final-amount">¥{{ (order.final_amount || order.total_amount || 0).toFixed(2) }}</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="order-actions">
          <el-button v-if="order.order_status === 0" type="primary" @click="payOrder(order)">
            立即支付
          </el-button>
          <el-button v-if="order.order_status === 0" @click="cancelOrder(order)">
            取消订单
          </el-button>
          <el-button v-if="order.order_status === 2" type="success" @click="confirmReceipt(order)">
            确认收货
          </el-button>
          <el-button @click="viewOrderDetail(order)">
            查看详情
          </el-button>
          <el-button v-if="order.order_status === 3" type="info" @click="addReview(order)">
            评价
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="暂无订单" class="empty-state">
      <el-button type="primary" @click="$router.push('/products')">去购物</el-button>
    </el-empty>

    <!-- 分页 -->
    <div class="pagination" v-if="orders.length > 0">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrders, payOrder as apiPayOrder } from '@/api/orders'

const router = useRouter()
const activeTab = ref('all')
const orders = ref([])
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)

// 订单状态映射
const statusMap = {
  0: { text: '待支付', type: 'warning' },
  1: { text: '已支付', type: 'primary' },
  2: { text: '已发货', type: 'success' },
  3: { text: '已完成', type: 'info' },
  4: { text: '已取消', type: 'danger' },
  5: { text: '退款中', type: 'warning' }
}

const getStatusText = (status) => statusMap[status]?.text || '未知状态'
const getStatusType = (status) => statusMap[status]?.type || 'info'

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString()
}

// 计算商品数量
const getProductCount = (order) => {
  if (!order) return 0
  
  // 优先使用item_count字段（后端已计算）
  if (order.item_count !== undefined) {
    return order.item_count
  }
  
  // 如果没有item_count，则从items数组计算
  if (!order.items) return 0
  
  if (Array.isArray(order.items)) {
    // 如果是数组，计算总数量
    return order.items.reduce((sum, item) => sum + (item.quantity || 0), 0)
  } else if (typeof order.items === 'object') {
    // 如果是对象，检查是否有quantity属性
    return order.items.quantity || 0
  }
  return 0
}

// 加载订单
const loadOrders = async () => {
  try {
    console.log('开始获取订单列表...')
    
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 状态筛选
    if (activeTab.value !== 'all') {
      const tabStatusMap = {
        'pending': 0,
        'unshipped': 1,
        'shipped': 2,
        'completed': 3
      }
      if (tabStatusMap[activeTab.value] !== undefined) {
        params.status = tabStatusMap[activeTab.value]
      }
    }
    
    console.log('请求参数:', params)
    
    const response = await getOrders(params)
    console.log('API响应:', response)
    
    if (response.data.code === 200) {
      console.log('获取到的订单数据:', response.data.data)
      
      // 处理items字段
      let items = response.data.data.items || response.data.data || []
      
      // 确保是数组
      if (items && !Array.isArray(items)) {
        items = [items]
      }
      
      orders.value = items
      total.value = response.data.data.total || items.length
      
      console.log('处理后的订单数量:', orders.value.length)
      console.log('处理后的订单:', orders.value)
    } else {
      console.log('API返回错误:', response.data.message)
      orders.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取订单失败:', error)
    ElMessage.error('获取订单失败')
    orders.value = []
    total.value = 0
  }
}

// 分页处理
const handlePageChange = (page) => {
  currentPage.value = page
  loadOrders()
}

// 支付订单
const payOrder = async (order) => {
  try {
    console.log('支付订单:', order.order_id)
    
    // 调用支付API
    const response = await apiPayOrder(order.order_id)
    if (response.data && response.data.code === 200) {
      ElMessage.success('支付成功！')
      // 重新加载订单以更新状态
      loadOrders()
    } else {
      ElMessage.error('支付失败: ' + (response.data?.message || '请稍后重试'))
    }
  } catch (error) {
    console.error('支付失败:', error)
    ElMessage.error('支付失败')
  }
}

const cancelOrder = (order) => {
  ElMessage.warning(`取消订单 ${order.order_no}`)
  // 实际应调用API
}

const confirmReceipt = (order) => {
  ElMessage.success(`确认收货 ${order.order_no}`)
  // 实际应调用API
}

const viewOrderDetail = (order) => {
  router.push(`/order/${order.order_id}`)
}

const addReview = (order) => {
  ElMessage.info(`评价订单 ${order.order_no}`)
  // 实际应跳转到评价页面
}

// 监听标签切换
watch(activeTab, () => {
  currentPage.value = 1
  loadOrders()
})

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 24px;
  color: #333;
  font-weight: 600;
}

.order-tabs {
  margin-bottom: 20px;
}

.order-card {
  margin-bottom: 20px;
  border: 1px solid #e8e8e8;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 20px;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.order-no {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.order-time {
  font-size: 14px;
  color: #666;
}

.order-status {
  min-width: 80px;
}

.product-count {
  padding: 15px 0;
  font-size: 14px;
  color: #666;
  border-bottom: 1px solid #f5f5f5;
}

.order-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-bottom: 20px;
  padding-top: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  width: 300px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.summary-item.total {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #e8e8e8;
}

.final-amount {
  font-size: 20px;
  color: #e53935;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.empty-state {
  margin: 50px 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>