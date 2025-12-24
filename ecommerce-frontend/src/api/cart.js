// src/api/cart.js - 购物车API封装
import { api } from '@/utils/request'

export const cartApi = {
  // 获取购物车列表
  getCart() {
    return api.get('/cart/')
  },
  
  // 添加商品到购物车
  addToCart(product, quantity = 1) {
    // Get product_id based on the type of product parameter
    let productId;
    if (typeof product === 'object' && product !== null) {
      productId = product.product_id || product.id;
    } else {
      productId = product;
    }
    
    // Create request data with only the required fields
    // Ensure they are valid integers
    const requestData = {
      product_id: Number.isNaN(parseInt(productId)) ? 0 : parseInt(productId),
      quantity: Number.isNaN(parseInt(quantity)) ? 1 : parseInt(quantity)
    };
    
    // Log the request data for debugging
    console.log('📤 发送到后端的购物车请求:', requestData);
    
    return api.post('/cart/add', requestData);
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
  },
  
  // 批量删除购物车商品
  batchRemoveFromCart(product_ids) {
    return api.delete('/cart/batch', {
      data: product_ids
    })
  }
}

export default cartApi