// src/api/cart.js - 购物车API封装
import { api } from '@/utils/request'

export const cartApi = {
  // 获取购物车列表
  getCart() {
    return api.get('/cart/')
  },
  
  // 添加商品到购物车
  addToCart(product_id, quantity = 1) {
    return api.post('/cart/add', {
      product_id,
      quantity
    })
  },
  
  // 更新购物车商品数量
  updateQuantity(product_id, quantity) {
    return api.put(`/cart/${product_id}`, {
      product_id,
      quantity
    })
  },
  
  // 从购物车移除商品
  removeFromCart(product_id) {
    return api.delete(`/cart/${product_id}`)
  },
  
  // 清空购物车
  clearCart() {
    return api.delete('/cart/')
  }
}

export default cartApi