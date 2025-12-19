import { api } from '@/utils/request'

// 获取商品列表
export function getProducts(params = {}) {
  // 合并默认参数
  const requestParams = {
    page: 1,
    page_size: 6,
    ...params
  }
  return api.get('/products/', requestParams)
}

// 获取商品详情
export function getProductDetail(productId) {
  return api.get(`/products/${productId}`)
}

// 获取商品分类
export function getCategories() {
  return api.get('/products/categories')
}

// 获取商品列表（支持搜索、筛选、排序）
export function searchProducts(params = {}) {
  // 默认参数
  const defaultParams = {
    page: 1,
    page_size: 12,
    ...params
  }
  return api.get('/products/', defaultParams)
}