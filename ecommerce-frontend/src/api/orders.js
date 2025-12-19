import { api } from '@/utils/request'

// 获取订单列表
export function getOrders(params = {}) {
  return api.get('/orders/', { params })
}

// 创建订单
export function createOrder(orderData) {
  return api.post('/orders/', orderData)
}

// 获取订单详情
export function getOrderDetail(orderId) {
  return api.get(`/orders/${orderId}`)
}

// 支付订单
export function payOrder(orderId) {
  return api.post(`/orders/${orderId}/pay`)
}

// 取消订单 - 添加这个
export function cancelOrder(orderId) {
  return api.delete(`/orders/${orderId}`)
}

// 订单状态处理
export const formatOrderStatus = (status) => {
  const map = {
    0: { text: '待支付', type: 'warning' },
    1: { text: '已支付', type: 'info' },
    2: { text: '已发货', type: '' },
    3: { text: '已完成', type: 'success' },
    4: { text: '已取消', type: 'danger' },
    5: { text: '退款中', type: 'warning' }
  }
  return map[status] || { text: `状态${status}`, type: 'info' }
}