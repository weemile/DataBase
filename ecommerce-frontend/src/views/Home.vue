<template>
  <div class="home">
    <!-- 轮播图 -->
    <el-carousel height="400px" class="carousel" :interval="3000" arrow="always">
      <el-carousel-item v-for="item in carouselItems" :key="item.id">
        <div class="carousel-img-container">
          <div class="carousel-img-placeholder">
            <div class="img-bg" :style="{ backgroundColor: item.bgColor }"></div>
          </div>
          <div class="carousel-text">
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
            <el-button type="primary" size="large" @click.stop="handleCarouselClick(item)">
              立即查看
            </el-button>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 商品分类 -->
    <div class="section">
      <h2 class="section-title">热门分类</h2>
      <div class="categories">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-card"
          @click="goToCategory(category.id)"
          :style="{ '--category-color': category.color }"
        >
          <div class="category-icon">
            <el-icon :size="32" :color="category.color">
              <component :is="category.icon" />
            </el-icon>
          </div>
          <h3>{{ category.name }}</h3>
          <p>{{ category.description }}</p>
          <span class="category-count">{{ category.count }}件商品</span>
        </div>
      </div>
    </div>

    <!-- 推荐商品 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">热门推荐</h2>
        <el-button type="primary" link @click="goToProducts">查看全部</el-button>
      </div>
      <div class="products">
        <el-card 
          v-for="product in featuredProducts" 
          :key="product.id"
          class="product-card"
          shadow="hover"
          @click="goToProductDetail(product.id)"
        >
          <div class="product-img-container">
            <div class="product-img-placeholder" :style="{ backgroundColor: product.bgColor }">
              <span class="product-img-text">{{ product.name.charAt(0) }}</span>
            </div>
          </div>
          <div class="product-info">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-desc">{{ product.description }}</p>
            <div class="product-footer">
              <div class="product-price">
                <span class="current-price">¥{{ product.price.toFixed(2) }}</span>
                <span class="original-price" v-if="product.originalPrice">
                  ¥{{ product.originalPrice.toFixed(2) }}
                </span>
              </div>
              <div class="product-meta">
                <el-tag size="small" type="success" v-if="product.stock > 0">
                  有货
                </el-tag>
                <el-tag size="small" type="danger" v-else>
                  缺货
                </el-tag>
                <span class="sales">销量 {{ product.sales.toLocaleString() }}</span>
              </div>
            </div>
            <div class="product-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="addToCart(product)"
                :disabled="product.stock === 0"
              >
                加入购物车
              </el-button>
              <el-button 
                type="info" 
                size="small" 
                plain 
                @click.stop="addToFavorites(product)"
              >
                收藏
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 促销活动 -->
    <div class="section promotion">
      <h2 class="section-title">限时促销</h2>
      <div class="promotions">
        <el-card v-for="promo in promotions" :key="promo.id" class="promotion-card" shadow="never">
          <div class="promotion-content">
            <div class="promotion-badge">
              <el-tag type="danger" effect="dark">{{ promo.discount }}</el-tag>
            </div>
            <h3>{{ promo.title }}</h3>
            <p class="promotion-desc">{{ promo.description }}</p>
            <div class="promotion-time">
              <el-icon><Clock /></el-icon>
              <span>截止: {{ promo.endTime }}</span>
            </div>
            <el-button type="danger" size="small" @click.stop="goToPromotion(promo)">
              立即抢购
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 特色服务 -->
    <div class="section services">
      <div class="service-item">
        <el-icon :size="32" color="#409EFF"><Van /></el-icon>
        <div class="service-info">
          <h4>全场包邮</h4>
          <p>满99元免运费</p>
        </div>
      </div>
      <div class="service-item">
        <el-icon :size="32" color="#67C23A"><Refresh /></el-icon>
        <div class="service-info">
          <h4>7天退换</h4>
          <p>无忧购物保障</p>
        </div>
      </div>
      <div class="service-item">
        <el-icon :size="32" color="#E6A23C"><Medal /></el-icon>
        <div class="service-info">
          <h4>正品保证</h4>
          <p>官方授权渠道</p>
        </div>
      </div>
      <div class="service-item">
        <el-icon :size="32" color="#909399"><Headset /></el-icon>
        <div class="service-info">
          <h4>客服支持</h4>
          <p>7x24小时在线</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useCartStore } from '@/stores/cart'
import { getProducts } from '@/api/products'

// 使用确认存在的图标（从你的列表中选择）
import { 
  Iphone,        // 手机图标 - 存在
  Monitor,       // 电脑图标 - 存在
  Goods,         // 商品图标 - 存在（代替服装）
  Refrigerator,  // 冰箱图标 - 存在
  Clock,         // 时钟图标 - 存在
  Van,           // 货车图标 - 存在
  Refresh,       // 刷新图标 - 存在
  Medal,         // 奖牌图标 - 存在
  Headset        // 耳机图标 - 存在
} from '@element-plus/icons-vue'
import { getCategories } from '@/api/products'

const router = useRouter()
const cartStore = useCartStore()

// 轮播图数据
const carouselItems = ref([
  {
    id: 1,
    title: '双十一大促',
    description: '全场商品8折起，限时抢购',
    bgColor: '#ff6b6b',
    link: '/products?promotion=1'
  },
  {
    id: 2,
    title: '新人专享礼',
    description: '新用户首单立减50元',
    bgColor: '#4ecdc4',
    link: '/register'
  },
  {
    id: 3,
    title: '品质家电',
    description: '智能家电，让生活更美好',
    bgColor: '#45b7d1',
    link: '/products?category=4'
  },
  {
    id: 4,
    title: '年终大促',
    description: '年度最低价，错过再等一年',
    bgColor: '#96ceb4',
    link: '/products'
  }
])

// 分类数据
const categories = ref([])

// 图标映射
const categoryIcons = {
  'Phones': Iphone,
  'Laptops': Monitor,
  'Electronics': Monitor,
  // 默认使用商品图标
  'default': Goods
}

// 颜色映射
const categoryColors = {
  'Phones': '#409EFF',
  'Laptops': '#67C23A',
  'Electronics': '#E6A23C',
  // 默认使用蓝色
  'default': '#409EFF'
}

// 推荐商品数据 - 清空静态数据
const featuredProducts = ref([])

// 促销活动数据
const promotions = ref([
  { 
    id: 1, 
    title: '新人专享券', 
    description: '新用户注册即送50元优惠券', 
    discount: '立减50元', 
    endTime: '2024-12-31',
    link: '/register'
  },
  { 
    id: 2, 
    title: '全场8折', 
    description: '双十一大促活动，部分商品除外', 
    discount: '8折优惠', 
    endTime: '2024-11-11',
    link: '/products?promotion=2'
  },
  { 
    id: 3, 
    title: '限时秒杀', 
    description: '每日10点开抢，限量100件', 
    discount: '7折起', 
    endTime: '今日23:59',
    link: '/products?type=flash'
  }
])

// 轮播图点击
const handleCarouselClick = (item) => {
  router.push(item.link)
}

// 导航函数
const goToCategory = (categoryId) => {
  router.push(`/products?category=${categoryId}`)
  ElMessage.success(`跳转到 ${categories.value.find(c => c.id === categoryId)?.name}`)
}

const goToProducts = () => {
  router.push('/products')
}

const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`)
}

const goToPromotion = (promo) => {
  router.push(promo.link)
  ElMessage.info(`参与活动: ${promo.title}`)
}

// 添加到购物车
const addToCart = (product) => {
  if (product.stock === 0) {
    ElMessage.warning('商品已售罄')
    return
  }
  
  const cartProduct = {
    product_id: product.id,
    product_name: product.name,
    price: product.price,
    image_url: '',  // 首页没有图片
    stock_quantity: product.stock
  }
  
  cartStore.addToCart(cartProduct, 1)
  ElMessage.success(`${product.name} 已加入购物车`)
}

// 添加到收藏
const addToFavorites = (product) => {
  ElMessage.success(`${product.name} 已加入收藏`)
  // 实际项目中这里会调用API或更新store
}

// 获取推荐商品
const fetchFeaturedProducts = async () => {
  try {
    console.log('开始获取商品...')
    const response = await getProducts({ page_size: 6 })
    console.log('API响应:', response.data)
    
    if (response.data.code === 200) {
      console.log('获取到商品数量:', response.data.data.items.length)
      console.log('商品数据:', response.data.data.items)
      
      featuredProducts.value = response.data.data.items.map(product => ({
        id: product.id,
        name: product.name,
        description: product.description,
        price: product.price,
        sales: product.sold_quantity,
        stock: product.stock,
        bgColor: getRandomColor()
      }))
      
      console.log('转换后的商品:', featuredProducts.value)
    }
  } catch (error) {
    console.error('获取商品失败:', error)
  }
}

// 获取分类数据
const fetchCategories = async () => {
  try {
    console.log('开始获取分类数据...')
    const response = await getCategories()
    console.log('分类API响应:', response.data)
    
    if (response.data.code === 200) {
      // 处理分类数据，添加图标和颜色
      const categoryData = response.data.data
      console.log('获取到分类数量:', categoryData.length)
      console.log('分类数据:', categoryData)
      
      // 转换分类数据格式，仅使用直接子分类
      categories.value = categoryData.map(category => {
        // 获取图标
        const iconName = category.category_name?.trim() || 'default'
        const icon = categoryIcons[iconName] || categoryIcons['default']
        
        // 获取颜色
        const color = categoryColors[iconName] || categoryColors['default']
        
        return {
          id: category.category_id,
          name: category.category_name?.trim() || '未知分类',
          icon: icon,
          color: color,
          description: category.category_name?.trim() + '商品',
          count: Math.floor(Math.random() * 200) + 50 // 随机生成商品数量
        }
      })
      
      console.log('转换后的分类:', categories.value)
    }
  } catch (error) {
    console.error('获取分类失败:', error)
    // 如果API调用失败，使用默认分类
    categories.value = [
      { 
        id: 11, 
        name: 'Phones', 
        icon: Iphone, 
        color: '#409EFF', 
        description: '智能手机/配件',
        count: 156
      },
      { 
        id: 12, 
        name: 'Laptops', 
        icon: Monitor, 
        color: '#67C23A', 
        description: '笔记本/台式机',
        count: 89
      }
    ]
  }
}

// 随机生成背景色（暂时替代图片）
const getRandomColor = () => {
  const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffd166', '#ef476f']
  return colors[Math.floor(Math.random() * colors.length)]
}

// 页面加载时获取数据
onMounted(() => {
  fetchFeaturedProducts()
  fetchCategories()
})
</script>

<style scoped>
.home {
  padding: 20px 0;
  background-color: #f8f9fa;
  min-height: calc(100vh - 120px);
}

/* 轮播图样式 */
.carousel {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.carousel-img-container {
  position: relative;
  height: 100%;
  width: 100%;
}

.carousel-img-placeholder {
  height: 100%;
  width: 100%;
  position: relative;
}

.img-bg {
  height: 100%;
  width: 100%;
  background: linear-gradient(135deg, var(--bg-color, #409EFF) 0%, rgba(0,0,0,0.3) 100%);
}

.carousel-text {
  position: absolute;
  bottom: 60px;
  left: 60px;
  color: white;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
  max-width: 500px;
}

.carousel-text h2 {
  font-size: 42px;
  margin-bottom: 15px;
  font-weight: 700;
}

.carousel-text p {
  font-size: 20px;
  margin-bottom: 25px;
  opacity: 0.95;
}

/* 分类区域 */
.section {
  margin-bottom: 50px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 28px;
  color: #303133;
  margin-bottom: 30px;
  font-weight: 600;
  position: relative;
  padding-bottom: 15px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 2px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

/* 分类卡片 */
.categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 25px;
}

.category-card {
  background: white;
  padding: 30px 20px;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.category-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  border-color: var(--category-color, #409EFF);
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--category-color, #409EFF);
}

.category-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  transition: transform 0.3s ease;
  background-color: rgba(var(--category-color-rgb, 64, 158, 255), 0.1);
}

.category-card:hover .category-icon {
  transform: scale(1.1);
}

.category-card h3 {
  margin: 15px 0 10px;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.category-card p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
  min-height: 40px;
}

.category-count {
  display: inline-block;
  padding: 4px 12px;
  background: #f0f9ff;
  color: #409EFF;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* 商品卡片 */
.products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.product-card {
  border: none;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.product-img-container {
  height: 180px;
  width: 100%;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-img-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-img-text {
  font-size: 48px;
  font-weight: bold;
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.product-info {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-name {
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
  font-weight: 600;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-desc {
  color: #909399;
  font-size: 13px;
  margin-bottom: 15px;
  line-height: 1.5;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-footer {
  margin-bottom: 15px;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.current-price {
  font-size: 20px;
  color: #f56c6c;
  font-weight: bold;
}

.original-price {
  font-size: 14px;
  color: #c0c4cc;
  text-decoration: line-through;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.product-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

/* 促销活动 */
.promotion {
  background: linear-gradient(135deg, #fff5f5 0%, #f0f9ff 100%);
}

.promotions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.promotion-card {
  border: none;
  background: white;
  border-left: 5px solid #f56c6c;
}

.promotion-content {
  padding: 20px;
}

.promotion-badge {
  margin-bottom: 15px;
}

.promotion-content h3 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 18px;
}

.promotion-desc {
  color: #606266;
  margin-bottom: 15px;
  font-size: 14px;
}

.promotion-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
  font-size: 13px;
  margin-bottom: 15px;
}

/* 特色服务 */
.services {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 40px 30px;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.service-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.service-info h4 {
  color: #303133;
  margin-bottom: 5px;
  font-size: 16px;
  font-weight: 600;
}

.service-info p {
  color: #909399;
  font-size: 13px;
}
</style>