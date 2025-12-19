import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { cartApi } from '@/api/cart'
import { ElMessage } from 'element-plus'

export const useCartStore = defineStore('cart', () => {
  // 购物车商品列表
  const cartItems = ref([])
  
  // 购物车商品总数
  const totalItems = computed(() => 
    cartItems.value.reduce((total, item) => total + item.quantity, 0)
  )
  
  // 购物车总金额
  const totalAmount = computed(() =>
    cartItems.value.reduce((total, item) => 
      total + (item.price * item.quantity), 0
    ).toFixed(2)
  )
  
  // 选中的商品数量
  const selectedItems = computed(() =>
    cartItems.value.filter(item => item.selected)
  )
  
  // 选中的商品总金额
  const selectedAmount = computed(() =>
    selectedItems.value.reduce((total, item) =>
      total + (item.price * item.quantity), 0
    ).toFixed(2)
  )

  // 从后端获取购物车数据
  const fetchCart = async () => {
    try {
      const response = await cartApi.getCart()
      
      if (response.data.code === 200) {
        const cartData = response.data.data
        cartItems.value = cartData.items.map(item => ({
          cart_id: item.cart_id,
          product_id: item.product_id,
          product_name: item.product_name,
          price: item.price || item.unit_price,
          image_url: item.image_url,
          stock_quantity: item.stock_quantity,
          quantity: item.quantity,
          selected: item.selected !== undefined ? item.selected : true
        }))
        return true
      }
      return false
    } catch (error) {
      console.error('获取购物车失败:', error)
      return false
    }
  }

  // 初始化购物车（替换initFromStorage）
  const initCart = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        cartItems.value = []
        return
      }
      await fetchCart()
    } catch (error) {
      console.error('初始化购物车失败:', error)
      cartItems.value = []
    }
  }

  // 添加商品到购物车
  const addToCart = async (product, quantity = 1) => {
    try {
      const response = await cartApi.addToCart(product.product_id, quantity)
      
      if (response.data.code === 200) {
        // 添加成功后，重新获取购物车数据
        await fetchCart()
        
        ElMessage.success('添加购物车成功')
        return true
      } else {
        ElMessage.error(response.data.message || '添加失败')
        return false
      }
    } catch (error) {
      console.error('添加购物车失败:', error)
      ElMessage.error('添加购物车失败')
      return false
    }
  }

  // 更新商品数量
  const updateQuantity = async (productId, quantity) => {
    try {
      if (quantity <= 0) {
        await removeFromCart(productId)
        return
      }
      
      const response = await cartApi.updateQuantity(productId, quantity)
      
      if (response.data.code === 200) {
        await fetchCart() // 更新本地数据
        ElMessage.success('更新数量成功')
        return true
      } else {
        ElMessage.error(response.data.message || '更新失败')
        return false
      }
    } catch (error) {
      console.error('更新数量失败:', error)
      ElMessage.error('更新数量失败')
      return false
    }
  }

  // 切换选中状态
  const toggleSelect = (productId) => {
    const item = cartItems.value.find(item => item.product_id === productId)
    if (item) {
      item.selected = !item.selected
      // 注意：这里不调用后端，只在getSelectedItems时使用
    }
  }

  // 全选/全不选
  const toggleSelectAll = (selected) => {
    cartItems.value.forEach(item => {
      item.selected = selected
    })
  }

  // 移除商品
  const removeFromCart = async (productId) => {
    try {
      const response = await cartApi.removeFromCart(productId)
      
      if (response.data.code === 200) {
        await fetchCart() // 更新本地数据
        ElMessage.success('移除成功')
        return true
      } else {
        ElMessage.error(response.data.message || '移除失败')
        return false
      }
    } catch (error) {
      console.error('移除商品失败:', error)
      ElMessage.error('移除商品失败')
      return false
    }
  }

  // 清空购物车
  const clearCart = async () => {
    try {
      const response = await cartApi.clearCart()
      
      if (response.data.code === 200) {
        cartItems.value = []
        ElMessage.success('购物车已清空')
        return true
      } else {
        ElMessage.error(response.data.message || '清空失败')
        return false
      }
    } catch (error) {
      console.error('清空购物车失败:', error)
      ElMessage.error('清空购物车失败')
      return false
    }
  }

  // 获取选中的商品（用于下单）
  const getSelectedItems = () => {
    return selectedItems.value.map(item => ({
      cart_id: item.cart_id,
      product_id: item.product_id,
      quantity: item.quantity
    }))
  }

  // 删除已下单的商品
  const removeSelectedItems = async () => {
    try {
      const selectedIds = selectedItems.value.map(item => item.product_id)
      
      // 批量删除选中的商品
      const promises = selectedIds.map(id => cartApi.removeFromCart(id))
      await Promise.all(promises)
      
      await fetchCart() // 更新本地数据
      return true
    } catch (error) {
      console.error('删除选中商品失败:', error)
      ElMessage.error('删除选中商品失败')
      return false
    }
  }

  return {
    cartItems,
    totalItems,
    totalAmount,
    selectedItems,
    selectedAmount,
    addToCart,
    updateQuantity,
    toggleSelect,
    toggleSelectAll,
    removeFromCart,
    clearCart,
    fetchCart,        // 新增
    initCart,         // 替换 initFromStorage
    getSelectedItems,
    removeSelectedItems
  }
})