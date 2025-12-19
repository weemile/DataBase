<template>
  <div class="products-page">
    <!-- 搜索栏和筛选 -->
    <div class="search-section">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品名称或描述"
          size="large"
          clearable
          @input="handleSearch"
          @clear="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>

      <div class="filters">
        <div class="filter-group">
          <span class="filter-label">分类：</span>
          <el-select
            v-model="selectedCategory"
            placeholder="全部分类"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </div>

        <div class="filter-group">
          <span class="filter-label">价格：</span>
          <el-input-number
            v-model="minPrice"
            placeholder="最低价"
            :min="0"
            :max="99999"
            @change="handleFilterChange"
          />
          <span class="price-separator">-</span>
          <el-input-number
            v-model="maxPrice"
            placeholder="最高价"
            :min="0"
            :max="99999"
            @change="handleFilterChange"
          />
        </div>

        <div class="filter-group">
          <span class="filter-label">排序：</span>
          <el-select v-model="sortBy" @change="handleSortChange">
            <el-option label="默认排序" value="default" />
            <el-option label="价格从低到高" value="price_asc" />
            <el-option label="价格从高到低" value="price_desc" />
            <el-option label="销量优先" value="sales_desc" />
            <el-option label="新品优先" value="newest" />
          </el-select>
        </div>

        <el-button type="info" @click="resetFilters">重置筛选</el-button>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="products-section">
      <div class="products-header">
        <h2 class="section-title">
          {{ selectedCategory ? getCategoryName(selectedCategory) : '全部商品' }}
          <span class="product-count">（共 {{ totalProducts}} 件商品）</span>
        </h2>
        <div class="view-controls">
          <el-button-group>
            <el-button
              :type="viewMode === 'grid' ? 'primary' : 'default'"
              @click="viewMode = 'grid'"
              :icon="Grid"
            />
            <el-button
              :type="viewMode === 'list' ? 'primary' : 'default'"
              @click="viewMode = 'list'"
              :icon="List"
            />
          </el-button-group>
        </div>
      </div>

      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="products-grid">
        <div
          v-for="product in paginatedProducts"
          :key="product.id"
          class="product-card"
          @click="goToProductDetail(product.id)"
        >
          <div class="product-image">
            <img :src="product.image" :alt="product.name" />
            <div v-if="product.promotion" class="promotion-tag">
              {{ product.promotion }}
            </div>
            <div v-if="product.stock <= 0" class="sold-out">已售罄</div>
          </div>
          <div class="product-info">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-desc">{{ product.description }}</p>
            <div class="product-meta">
              <div class="rating">
                <el-rate
                  v-model="product.rating"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}分"
                />
              </div>
              <div class="sales">已售 {{ product.sales }}</div>
            </div>
            <div class="product-footer">
              <div class="price-section">
                <span class="current-price">¥{{ product.price }}</span>
                <span v-if="product.originalPrice" class="original-price">
                  ¥{{ product.originalPrice }}
                </span>
              </div>
              <el-button
                type="primary"
                size="small"
                :icon="ShoppingCart"
                :disabled="product.stock <= 0"
                @click.stop="addToCart(product)"
              >
                {{ product.stock <= 0 ? '缺货' : '加入购物车' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="products-list">
        <div
          v-for="product in paginatedProducts"
          :key="product.id"
          class="product-list-item"
          @click="goToProductDetail(product.id)"
        >
          <div class="list-image">
            <img :src="product.image" :alt="product.name" />
          </div>
          <div class="list-info">
            <h3 class="list-name">{{ product.name }}</h3>
            <p class="list-desc">{{ product.description }}</p>
            <div class="list-meta">
              <el-rate
                v-model="product.rating"
                disabled
                show-score
                text-color="#ff9900"
                score-template="{value}分"
              />
              <span class="list-sales">已售 {{ product.sales }}</span>
              <span class="list-stock">库存 {{ product.stock }} 件</span>
            </div>
          </div>
          <div class="list-actions">
            <div class="list-price">
              <div class="current-price">¥{{ product.price }}</div>
              <div v-if="product.originalPrice" class="original-price">
                ¥{{ product.originalPrice }}
              </div>
            </div>
            <el-button
              type="primary"
              :icon="ShoppingCart"
              :disabled="product.stock <= 0"
              @click.stop="addToCart(product)"
            >
              加入购物车
            </el-button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredProducts"
          :page-sizes="[12, 24, 36, 48]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { ElMessage } from 'element-plus'
import { Search, Grid, List, ShoppingCart } from '@element-plus/icons-vue'
import { searchProducts, getCategories } from '@/api/products'

const router = useRouter()
const cartStore = useCartStore()

// 筛选状态
const searchKeyword = ref('')
const selectedCategory = ref('')
const minPrice = ref('')
const maxPrice = ref('')
const sortBy = ref('default')
const viewMode = ref('grid')

// 分页状态
const currentPage = ref(1)
const pageSize = ref(12)

// 分页数据
const totalProducts = ref(0)  // 后端返回的总商品数
const totalPages = ref(1)     // 总页数

// 分类数据
const categories = ref([
  { id: 1, name: '手机数码' },
  { id: 2, name: '电脑办公' },
  { id: 3, name: '服装服饰' },
  { id: 4, name: '家用电器' },
  { id: 5, name: '美妆个护' },
  { id: 6, name: '食品饮料' },
  { id: 7, name: '运动户外' },
  { id: 8, name: '图书音像' }
])

// 商品数据
const products = ref([])

// 计算属性
// 删除原来的 filteredProducts 计算属性，分页和筛选由后端处理

const paginatedProducts = computed(() => {
  // 直接使用 products.value，因为分页由后端控制
  return products.value
})

// 方法
const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  return category ? category.name : '未知分类'
}

// 获取商品数据
const fetchProducts = async () => {
  try {
    // 构建查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    
    // 添加筛选条件
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (minPrice.value) {
      params.min_price = minPrice.value
    }
    if (maxPrice.value) {
      params.max_price = maxPrice.value
    }
    
    // 排序处理（需要映射前端排序值到后端参数）
    if (sortBy.value !== 'default') {
      // 注意：后端目前只支持按时间排序，这里先保留结构
      // 如果后端支持排序，可以在这里添加：params.sort_by = 'sold' 等
    }
    
    const response = await searchProducts(params)
    if (response.data.code === 200) {
      // 保存总数和总页数
      totalProducts.value = response.data.data.total
      totalPages.value = response.data.data.total_pages
      
      console.log('API返回数据:', response.data.data)
      console.log('总数:', response.data.data.total)
      
      // 转换数据格式
      products.value = response.data.data.items.map(product => ({
        id: product.product_id,
        name: product.product_name,
        description: product.description,
        price: product.price,
        originalPrice: null,
        image: '', // 暂时空着
        category: product.category_id, // 使用真实的后端category_id
        stock: product.stock_quantity,
        sales: product.sold_quantity,
        rating: 4.5,
        promotion: null
      }))
    }
  } catch (error) {
    console.error('获取商品列表失败:', error)
  }
}
// 获取分类数据
const fetchCategories = async () => {
  try {
    const response = await getCategories()
    if (response.data.code === 200) {
      // 处理嵌套分类结构，提取所有子分类
      const allCategories = []
      
      const extractCategories = (category) => {
        // 添加当前分类
        allCategories.push({
          id: category.category_id,
          name: category.category_name
        })
        
        // 递归处理子分类
        if (category.children && category.children.length > 0) {
          category.children.forEach(child => extractCategories(child))
        }
      }
      
      // 遍历所有顶级分类
      response.data.data.forEach(category => extractCategories(category))
      
      categories.value = allCategories
    }
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProducts() // 添加这行
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchProducts() // 添加这行
}

const handleSortChange = () => {
  currentPage.value = 1
  fetchProducts() // 添加这行
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedCategory.value = ''
  minPrice.value = ''
  maxPrice.value = ''
  sortBy.value = 'default'
  currentPage.value = 1
  fetchProducts() // 添加这行
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchProducts() // 添加这行
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchProducts() // 添加这行
}

const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`)
}

const addToCart = (product) => {
  console.log('addToCart called with:', product)
  
  if (!product) {
    console.error('错误: product参数为空')
    ElMessage.error('商品信息无效')
    return
  }
  
  // 确保传递正确的格式
  const cartProduct = {
    product_id: product.id,  // 注意：这里应该是product.id还是product.product_id？
    product_name: product.name,
    price: product.price,
    image_url: product.image || '',
    stock_quantity: product.stock
  }
  
  console.log('转换为cartProduct:', cartProduct)
  
  cartStore.addToCart(cartProduct, 1)
  ElMessage.success(`已添加 ${product.name} 到购物车`)
}

onMounted(() => {
  fetchCategories()
  fetchProducts()
  cartStore.initCart()
})
</script>

<style scoped>
.products-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.search-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.search-bar {
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  color: #606266;
  font-size: 14px;
  white-space: nowrap;
}

.price-separator {
  color: #909399;
  padding: 0 5px;
}

.products-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.products-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.product-count {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
  margin-left: 10px;
}

.view-controls {
  margin-left: auto;
}

/* 网格视图 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.product-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.product-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.promotion-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #f56c6c;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.sold-out {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.rating {
  flex: 1;
}

.sales {
  color: #909399;
  font-size: 12px;
  white-space: nowrap;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-section {
  display: flex;
  flex-direction: column;
}

.current-price {
  font-size: 20px;
  color: #f56c6c;
  font-weight: bold;
}

.original-price {
  font-size: 14px;
  color: #909399;
  text-decoration: line-through;
}

/* 列表视图 */
.products-list {
  margin-bottom: 30px;
}

.product-list-item {
  display: flex;
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: background-color 0.3s;
}

.product-list-item:hover {
  background-color: #f5f7fa;
}

.list-image {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  margin-right: 20px;
}

.list-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.list-info {
  flex: 1;
  min-width: 0;
}

.list-name {
  font-size: 18px;
  color: #303133;
  margin-bottom: 10px;
}

.list-desc {
  color: #606266;
  margin-bottom: 15px;
  line-height: 1.5;
}

.list-meta {
  display: flex;
  align-items: center;
  gap: 20px;
}

.list-sales,
.list-stock {
  color: #909399;
  font-size: 14px;
}

.list-actions {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
}

.list-price {
  text-align: right;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    flex-wrap: wrap;
  }
  
  .product-list-item {
    flex-direction: column;
  }
  
  .list-image {
    width: 100%;
    height: 200px;
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .list-actions {
    width: 100%;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    margin-top: 15px;
  }
}
</style>