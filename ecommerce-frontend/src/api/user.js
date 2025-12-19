// src/api/user.js - 用户相关API
import { api } from '@/utils/request'

export const userApi = {
  // ==================== 用户信息 ====================
  // 获取当前用户信息
  getCurrentUser: () => api.get('/auth/me'),
  
  // 更新用户信息
  updateProfile: (userData) => api.put('/auth/profile', userData),
  
  // ==================== 地址管理 ====================
  // 获取地址列表
  getAddresses: () => api.get('/user/addresses'),
  
  // 添加地址
  addAddress: (addressData) => api.post('/user/addresses', addressData),
  
  // 修改地址
  updateAddress: (addressId, addressData) => 
    api.put(`/user/addresses/${addressId}`, addressData),
  
  // 删除地址
  deleteAddress: (addressId) => api.delete(`/user/addresses/${addressId}`),
  
  // 设置默认地址
  setDefaultAddress: (addressId) => api.put(`/user/addresses/${addressId}/default`)
}

export default userApi