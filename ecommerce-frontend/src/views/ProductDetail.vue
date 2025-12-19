<template>
  <div class="product-detail-page" v-if="product">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/products' }">商品中心</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: `/products?category=${product.category}` }">
          {{ getCategoryName(product.category) }}
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ product.name }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 商品信息区域 -->
    <div class="product-container">
      <!-- 左侧商品图片 -->
      <div class="product-images">
        <div class="main-image">
          <img :src="currentImage || product.mainImage" :alt="product.name" />
          <div v-if="product.promotion" class="promotion-badge">
            {{ product.promotion }}
          </div>
        </div>
        <div class="thumbnail-list">
          <div
            v-for="(image, index) in product.images"
            :key="index"
            class="thumbnail"
            :class="{ active: currentImageIndex === index }"
            @click="changeImage(index)"
          >
            <img :src="image" :alt="`${product.name}-${index + 1}`" />
          </div>
        </div>
      </div>

      <!-- 右侧商品信息 -->
      <div class="product-info">
        <h1 class="product-title">{{ product.name }}</h1>
        
        <div class="product-meta">
          <div class="product-code">商品编号：{{ product.code }}</div>
          <div class="product-sales">销量：{{ product.sales }} 件</div>
          <div class="product-stock" :class="{ 'low-stock': product.stock <= 10 }">
            库存：{{ product.stock > 0 ? `${product.stock} 件` : '缺货' }}
          </div>
        </div>

        <!-- 数据测试 -->
        <div v-if="product" style="background: #e8f4ff; padding: 10px; margin: 10px 0; border-left: 4px solid #409eff;">
          <h4 style="margin: 0 0 8px 0; color: #409eff;">数据测试:</h4>
          <div style="display: flex; gap: 15px; font-size: 14px;">
            <div><strong>has_discount:</strong> {{ product.has_discount }}</div>
            <div><strong>discounted_price:</strong> {{ product.discounted_price }}</div>
            <div><strong>original_price:</strong> {{ product.original_price }}</div>
            <div><strong>price:</strong> {{ product.price }}</div>
          </div>
        </div>

        <!-- 价格展示区域 -->
        <div class="price-section">
          <div class="current-price">
            <!-- 如果有促销 -->
            <template v-if="product.has_discount">
              <span class="price-label">促销价：</span>
              <span class="price">¥{{ formatPrice(product.discounted_price) }}</span>
              <span class="original-price">¥{{ formatPrice(product.original_price) }}</span>
              
              <!-- 促销标签 -->
              <el-tag type="danger" class="discount-tag">
                {{ product.discount_label }}
              </el-tag>
              
              <!-- 促销名称 -->
              <el-tag v-if="product.best_promotion" type="warning" class="promotion-tag">
                {{ product.best_promotion.promotion_name }}
              </el-tag>
            </template>
            
            <!-- 如果没有促销 -->
            <template v-else>
              <span class="price-label">售价：</span>
              <span class="price">¥{{ formatPrice(product.price) }}</span>
            </template>
          </div>
          
          <!-- 促销描述 -->
          <div v-if="product.best_promotion" class="promotion-info">
            <el-icon><InfoFilled /></el-icon>
            <span class="promotion-desc">{{ product.best_promotion.promotion_description }}</span>
            <span class="promotion-time">
              活动时间：{{ formatDate(product.best_promotion.start_time) }} 至 {{ formatDate(product.best_promotion.end_time) }}
            </span>
          </div>
          
          <!-- 节省金额提示 -->
          <div v-if="product.has_discount" class="saving-hint">
            <el-icon><Discount /></el-icon>
            <span>立即节省：¥{{ formatPrice(product.discount_amount) }}</span>
          </div>
        </div>

        <!-- 商品规格 -->
        <div class="specifications" v-if="product.specifications.length">
          <h3>规格选择</h3>
          <div class="spec-list">
            <div
              v-for="spec in product.specifications"
              :key="spec.id"
              class="spec-item"
              :class="{ selected: selectedSpecId === spec.id }"
              @click="selectSpec(spec)"
            >
              {{ spec.name }}
              <span v-if="spec.priceDiff" class="price-diff">
                {{ spec.priceDiff > 0 ? '+' : '' }}¥{{ spec.priceDiff }}
              </span>
            </div>
          </div>
        </div>

        <!-- 购买数量 -->
        <div class="quantity-section">
          <h3>购买数量</h3>
          <div class="quantity-control">
            <el-input-number
              v-model="quantity"
              :min="1"
              :max="product.stock"
              :disabled="product.stock <= 0"
              controls-position="right"
            />
            <span class="stock-tip">最多可购买 {{ product.stock }} 件</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            :icon="ShoppingCart"
            :disabled="product.stock <= 0"
            @click="addToCart"
            class="cart-btn"
          >
            加入购物车
          </el-button>
          <el-button
            type="danger"
            size="large"
            :disabled="product.stock <= 0"
            @click="buyNow"
            class="buy-btn"
          >
            立即购买
          </el-button>
          <el-button
            type="info"
            size="large"
            :icon="Star"
            @click="toggleFavorite"
            class="favorite-btn"
            :class="{ favorited: isFavorited }"
          >
            {{ isFavorited ? '已收藏' : '收藏' }}
          </el-button>
        </div>

        <!-- 服务承诺 -->
        <div class="service-promise">
          <div class="service-item">
            <el-icon><CircleCheck /></el-icon>
            <span>正品保证</span>
          </div>
          <div class="service-item">
            <el-icon><CircleCheck /></el-icon>
            <span>七天退换</span>
          </div>
          <div class="service-item">
            <el-icon><CircleCheck /></el-icon>
            <span>极速发货</span>
          </div>
          <div class="service-item">
            <el-icon><CircleCheck /></el-icon>
            <span>售后无忧</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 商品详情标签页 -->
    <div class="product-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商品详情" name="detail">
          <div class="product-description" v-html="product.description"></div>
          <div class="detail-images">
            <img
              v-for="(img, index) in product.detailImages"
              :key="index"
              :src="img"
              :alt="`${product.name}-详情-${index + 1}`"
            />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="规格参数" name="specs">
          <div class="specs-table">
            <div class="specs-row" v-for="spec in product.parameters" :key="spec.name">
              <div class="specs-name">{{ spec.name }}</div>
              <div class="specs-value">{{ spec.value }}</div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="商品评价" name="reviews">
          <div class="reviews-section">
            <div class="reviews-summary">
              <div class="rating-overview">
                <div class="rating-score">{{ product.rating }}</div>
                <div class="rating-stars">
                  <el-rate v-model="product.rating" disabled />
                </div>
                <div class="rating-count">{{ product.reviewCount }} 条评价</div>
              </div>
              <div class="rating-distribution">
                <div
                  v-for="item in ratingDistribution"
                  :key="item.stars"
                  class="distribution-item"
                >
                  <span class="stars">{{ item.stars }}星</span>
                  <el-progress
                    :percentage="item.percentage"
                    :color="getProgressColor(item.stars)"
                    :show-text="false"
                  />
                  <span class="percentage">{{ item.percentage }}%</span>
                </div>
              </div>
            </div>
            
            <div class="reviews-list">
              <div
                v-for="review in product.reviews.slice(0, 5)"
                :key="review.id"
                class="review-item"
              >
                <div class="review-header">
                  <el-avatar :size="40" :src="review.avatar" />
                  <div class="review-user">
                    <div class="username">{{ review.username }}</div>
                    <el-rate v-model="review.rating" disabled size="small" />
                  </div>
                  <div class="review-time">{{ review.time }}</div>
                </div>
                <div class="review-content">
                  {{ review.content }}
                </div>
                <div class="review-images" v-if="review.images">
                  <img
                    v-for="(img, index) in review.images"
                    :key="index"
                    :src="img"
                    class="review-img"
                  />
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="常见问题" name="faq">
          <div class="faq-section">
            <el-collapse v-model="activeFaq">
              <el-collapse-item
                v-for="(faq, index) in product.faqs"
                :key="index"
                :title="faq.question"
                :name="index"
              >
                {{ faq.answer }}
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 推荐商品 -->
    <div class="related-products">
      <h2 class="section-title">猜你喜欢</h2>
      <div class="related-list">
        <div
          v-for="item in relatedProducts"
          :key="item.id"
          class="related-item"
          @click="goToProductDetail(item.id)"
        >
          <img :src="item.image" :alt="item.name" />
          <div class="related-info">
            <h3>{{ item.name }}</h3>
            <div class="related-price">¥{{ formatPrice(item.price) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else class="loading">
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { ElMessage } from 'element-plus'
import {
  ShoppingCart,
  Star,
  CircleCheck,
  InfoFilled,
  Discount
} from '@element-plus/icons-vue'
import { getProductDetail } from '@/api/products'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref(null)
const currentImageIndex = ref(0)
const selectedSpecId = ref(null)
const quantity = ref(1)
const isFavorited = ref(false)
const activeTab = ref('detail')
const activeFaq = ref([])

// 相关商品
const relatedProducts = ref([
  {
    id: 2,
    name: '华为 Mate 60 Pro',
    price: 6999,
    image: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200&h=200&fit=crop'
  },
  {
    id: 3,
    name: '三星 Galaxy S23 Ultra',
    price: 8999,
    image: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=200&h=200&fit=crop'
  },
  {
    id: 4,
    name: 'AirPods Pro 2',
    price: 1899,
    image: 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=200&h=200&fit=crop'
  },
  {
    id: 5,
    name: 'Apple Watch Series 9',
    price: 2999,
    image: 'https://images.unsplash.com/photo-1638913662252-70efce1e60a7?w=200&h=200&fit=crop'
  }
])

// 时间格式化
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
}

// 价格格式化（安全处理）
const formatPrice = (price) => {
  if (price === null || price === undefined) return '0.00'
  const num = Number(price)
  return isNaN(num) ? '0.00' : num.toFixed(2)
}

// 计算属性
const currentImage = computed(() => {
  if (product.value?.images?.length > 0) {
    return product.value.images[currentImageIndex.value]
  }
  return ''
})

const ratingDistribution = computed(() => {
  return [
    { stars: 5, percentage: 78 },
    { stars: 4, percentage: 15 },
    { stars: 3, percentage: 4 },
    { stars: 2, percentage: 2 },
    { stars: 1, percentage: 1 }
  ]
})

// 方法
const getCategoryName = (categoryId) => {
  const categoryMap = {
    4: '手机通讯',
    5: '电脑办公',
    6: '男装',
    7: '女装',
    8: '空调冰箱'
  }
  return categoryMap[categoryId] || '其他分类'
}

const getProgressColor = (stars) => {
  const colors = {
    5: '#67C23A',
    4: '#E6A23C',
    3: '#909399',
    2: '#F56C6C',
    1: '#F56C6C'
  }
  return colors[stars] || '#409EFF'
}

const changeImage = (index) => {
  currentImageIndex.value = index
}

const selectSpec = (spec) => {
  selectedSpecId.value = spec.id
}

const addToCart = () => {
  if (product.value.stock <= 0) {
    ElMessage.warning('商品已售罄')
    return
  }
  
  // 转换为cartStore期望的格式
  const cartProduct = {
    product_id: product.value.id,
    product_name: product.value.name,
    // 使用促销价（如果有）否则使用原价
    price: product.value.has_discount ? product.value.discounted_price : product.value.price,
    image_url: product.value.images[0] || '', // 使用第一张图片
    stock_quantity: product.value.stock
  }
  
  cartStore.addToCart(cartProduct, quantity.value)
  ElMessage.success(`已添加 ${product.value.name} 到购物车`)
}

const buyNow = () => {
  if (product.value.stock <= 0) {
    ElMessage.warning('商品已售罄')
    return
  }
  
  // 转换为cartStore期望的格式
  const cartProduct = {
    product_id: product.value.id,
    product_name: product.value.name,
    // 使用促销价（如果有）否则使用原价
    price: product.value.has_discount ? product.value.discounted_price : product.value.price,
    image_url: product.value.images[0] || '',
    stock_quantity: product.value.stock
  }
  
  cartStore.addToCart(cartProduct, quantity.value)
  router.push('/checkout')
}

const toggleFavorite = () => {
  isFavorited.value = !isFavorited.value
  ElMessage.success(isFavorited.value ? '已添加到收藏夹' : '已取消收藏')
}

const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`)
}

// 获取商品详情 - 修改后的版本
const fetchProductDetail = async () => {
  try {
    const productId = route.params.id
    const response = await getProductDetail(productId)
    
    console.log('🔄 API响应:', response.data.data)  // 调试
    
    if (response.data.code === 200) {
      const apiProduct = response.data.data
      
      product.value = {
        id: apiProduct.product_id,
        name: apiProduct.product_name,
        code: apiProduct.product_code || `PROD${apiProduct.product_id}`,
        category: apiProduct.category_id,
        // 使用真实图片或占位图
        mainImage: apiProduct.image_url || `https://placehold.co/600x600/cccccc/ffffff?text=${encodeURIComponent(apiProduct.product_name)}`,
        images: [apiProduct.image_url || `https://placehold.co/600x600/cccccc/ffffff?text=${encodeURIComponent(apiProduct.product_name)}`],
        
        // ==== 关键修改：添加促销字段 ====
        price: apiProduct.price,  // 原价
        has_discount: apiProduct.has_discount,  // 是否有折扣
        discounted_price: apiProduct.discounted_price,  // 折后价
        original_price: apiProduct.original_price,  // 原价（用于显示）
        discount_label: apiProduct.discount_label,  // 折扣标签 "7折"
        best_promotion: apiProduct.best_promotion,  // 最优促销对象
        discount_amount: apiProduct.discount_amount,  // 节省金额
        
        // 其他字段保持不变
        stock: apiProduct.stock_quantity,
        sales: apiProduct.sold_quantity,
        description: apiProduct.description || '暂无详细描述',
        parameters: [
          { name: '品牌', value: apiProduct.brand || '未指定' },
          { name: '型号', value: apiProduct.model || '未指定' },
          { name: '分类', value: apiProduct.category_name || '未分类' }
        ],
        rating: apiProduct.avg_rating || 4.5,
        reviewCount: apiProduct.review_count || 0,
        reviews: [],
        faqs: [],
        // 保持其他字段
        specifications: [],
        detailImages: [],
        promotion: null,
        coupon: null,
        discount: null,
        originalPrice: apiProduct.cost_price // 保持向后兼容
      }
      
      console.log('✅ 转换后的product促销字段:', {
        has_discount: product.value.has_discount,
        discounted_price: product.value.discounted_price,
        original_price: product.value.original_price,
        discount_label: product.value.discount_label,
        best_promotion: product.value.best_promotion,
        discount_amount: product.value.discount_amount
      })
    }
  } catch (error) {
    console.error('获取商品详情失败:', error)
    ElMessage.error('获取商品信息失败')
  }
}

// 初始化
onMounted(() => {
  fetchProductDetail()
  cartStore.initCart()
})
</script>

<style scoped>
/* 促销标签样式 */
.promotion-tag {
  margin-left: 8px;
  font-size: 12px;
  height: 24px;
  line-height: 22px;
}

/* 促销信息样式 */
.promotion-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 4px;
  font-size: 13px;
  color: #409eff;
}

.promotion-info .el-icon {
  font-size: 14px;
}

.promotion-desc {
  flex: 1;
}

.promotion-time {
  font-size: 12px;
  color: #909399;
}

/* 节省提示样式 */
.saving-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 10px;
  background: #fdf6ec;
  border-radius: 4px;
  font-size: 13px;
  color: #e6a23c;
}

.saving-hint .el-icon {
  font-size: 14px;
}

/* 原有样式保持不变 */
.product-detail-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.product-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.product-images {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-image {
  position: relative;
  width: 100%;
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.promotion-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  background: #f56c6c;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 10px 0;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.thumbnail.active {
  border-color: #409EFF;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-title {
  font-size: 24px;
  color: #303133;
  margin: 0;
  line-height: 1.3;
}

.product-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 14px;
}

.low-stock {
  color: #f56c6c;
  font-weight: 500;
}

.price-section {
  padding: 20px;
  background: #fdf6ec;
  border-radius: 8px;
}

.current-price {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.price-label {
  color: #606266;
  font-size: 14px;
}

.price {
  font-size: 32px;
  color: #f56c6c;
  font-weight: bold;
}

.original-price {
  font-size: 18px;
  color: #909399;
  text-decoration: line-through;
}

.discount-tag {
  font-size: 14px;
  height: 28px;
  line-height: 26px;
}

.coupon-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.coupon-text {
  color: #e6a23c;
  font-size: 14px;
}

.specifications h3,
.quantity-section h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 15px;
}

.spec-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.spec-item {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.spec-item:hover {
  border-color: #409EFF;
}

.spec-item.selected {
  border-color: #409EFF;
  background: #ecf5ff;
  color: #409EFF;
}

.price-diff {
  color: #f56c6c;
  font-size: 12px;
  margin-left: 5px;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stock-tip {
  color: #909399;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.cart-btn,
.buy-btn {
  flex: 1;
  height: 48px;
  font-size: 16px;
}

.favorite-btn {
  width: 120px;
}

.favorite-btn.favorited {
  color: #f56c6c;
  border-color: #f56c6c;
}

.service-promise {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-top: 20px;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.service-item .el-icon {
  color: #67c23a;
}

.product-tabs {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.product-description {
  line-height: 1.8;
  color: #606266;
}

.product-description :deep(p) {
  margin-bottom: 15px;
}

.product-description :deep(ul) {
  margin-bottom: 15px;
  padding-left: 20px;
}

.product-description :deep(li) {
  margin-bottom: 8px;
}

.detail-images {
  margin-top: 30px;
}

.detail-images img {
  width: 100%;
  margin-bottom: 20px;
  border-radius: 8px;
}

.specs-table {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.specs-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  border-bottom: 1px solid #e4e7ed;
}

.specs-row:last-child {
  border-bottom: none;
}

.specs-name,
.specs-value {
  padding: 15px 20px;
}

.specs-name {
  background: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.specs-value {
  color: #303133;
}

.reviews-section {
  padding: 20px;
}

.reviews-summary {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 40px;
  margin-bottom: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.rating-overview {
  text-align: center;
}

.rating-score {
  font-size: 48px;
  color: #f56c6c;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 10px;
}

.rating-stars {
  margin-bottom: 10px;
}

.rating-count {
  color: #909399;
  font-size: 14px;
}

.rating-distribution {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.distribution-item {
  display: grid;
  grid-template-columns: 60px 1fr 60px;
  align-items: center;
  gap: 15px;
}

.stars {
  color: #606266;
  font-size: 14px;
}

.percentage {
  color: #909399;
  font-size: 14px;
  text-align: right;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.review-user {
  flex: 1;
}

.username {
  font-weight: 500;
  margin-bottom: 5px;
}

.review-time {
  color: #909399;
  font-size: 14px;
}

.review-content {
  color: #303133;
  line-height: 1.6;
  margin-bottom: 15px;
}

.review-images {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.review-img {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  object-fit: cover;
}

.faq-section {
  padding: 20px;
}

.related-products {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}

.related-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.related-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.related-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.related-item img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.related-info {
  padding: 15px;
}

.related-info h3 {
  font-size: 14px;
  color: #303133;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-price {
  font-size: 16px;
  color: #f56c6c;
  font-weight: bold;
}

.loading {
  padding: 40px;
}

@media (max-width: 768px) {
  .product-container {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 20px;
  }
  
  .main-image {
    height: 300px;
  }
  
  .service-promise {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .reviews-summary {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .favorite-btn {
    width: auto;
  }
}
</style>