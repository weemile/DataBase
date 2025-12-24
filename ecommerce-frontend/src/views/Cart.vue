<template>
  <div class="cart-page">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>购物车</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 购物车内容 -->
    <div class="cart-container" v-if="cartStore.cartItems.length > 0">
      <!-- 购物车头部 -->
      <div class="cart-header">
        <div class="header-left">
          <el-checkbox
            v-model="isAllSelected"
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
          >
            全选
          </el-checkbox>
          <span class="header-title">商品信息</span>
        </div>
        <div class="header-right">
          <div class="header-column">单价</div>
          <div class="header-column">数量</div>
          <div class="header-column">小计</div>
          <div class="header-column">操作</div>
        </div>
      </div>

      <!-- 购物车商品列表 -->
      <div class="cart-items">
        <div
          v-for="item in cartStore.cartItems"
          :key="item.product_id"
          class="cart-item"
          :class="{ 'item-disabled': item.stock_quantity <= 0 }"
        >
          <div class="item-left">
            <el-checkbox
              v-model="item.selected"
              :disabled="item.stock_quantity <= 0"
              @change="handleItemSelect(item)"
            />
            <div class="item-image" @click="goToProductDetail(item.product_id)">
              <img :src="item.image_url || defaultImage" :alt="item.product_name" />
              <div v-if="item.stock_quantity <= 0" class="sold-out-badge">已售罄</div>
            </div>
            <div class="item-info">
              <h3 class="item-name" @click="goToProductDetail(item.product_id)">
                {{ item.product_name }}
              </h3>
              <div class="item-spec" v-if="item.spec">规格：{{ item.spec }}</div>
              <div class="item-stock">
                库存：
                <span :class="{ 'low-stock': item.stock_quantity <= 10 }">
                  {{ item.stock_quantity > 0 ? `${item.stock_quantity} 件` : '缺货' }}
                </span>
              </div>
            </div>
          </div>

          <div class="item-right">
            <div class="item-column price-column">
              <div class="current-price">¥{{ item.price.toFixed(2) }}</div>
              <div v-if="item.original_price" class="original-price">
                ¥{{ item.original_price.toFixed(2) }}
              </div>
            </div>

            <div class="item-column quantity-column">
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="Math.min(item.stock_quantity, 99)"
                :disabled="item.stock_quantity <= 0"
                controls-position="right"
                @change="updateQuantity(item)"
              />
            </div>

            <div class="item-column subtotal-column">
              <div class="subtotal">¥{{ (item.price * item.quantity).toFixed(2) }}</div>
              <div v-if="item.discount" class="discount">
                已省 ¥{{ item.discount.toFixed(2) }}
              </div>
            </div>

            <div class="item-column action-column">
              <el-button
                type="danger"
                link
                :icon="Delete"
                @click="removeItem(item.product_id)"
              >
                删除
              </el-button>
              <el-button
                type="info"
                link
                :icon="Star"
                @click="addToFavorites(item)"
              >
                收藏
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 购物车底部 -->
      <div class="cart-footer">
        <div class="footer-left">
          <el-checkbox
            v-model="isAllSelected"
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
          >
            全选
          </el-checkbox>
          <el-button type="danger" link @click="clearSelectedItems">
            删除选中
          </el-button>
          <el-button type="info" link @click="clearCart">
            清空购物车
          </el-button>
          <div class="selected-count">
            已选 {{ selectedItems.length }} 件商品
          </div>
        </div>

        <div class="footer-right">
          <div class="total-info">
            <div class="total-amount">
              合计：
              <span class="total-price">¥{{ selectedTotalAmount }}</span>
            </div>
            <div class="total-discount" v-if="selectedTotalDiscount > 0">
              已节省：¥{{ selectedTotalDiscount.toFixed(2) }}
            </div>
          </div>

          <el-button
            type="danger"
            size="large"
            :disabled="selectedItems.length === 0 || hasOutOfStock"
            @click="goToCheckout"
            class="checkout-btn"
          >
            去结算 ({{ selectedItems.length }})
          </el-button>
        </div>
      </div>

      <!-- 你可能还喜欢 -->
      <div class="recommendations">
        <h2 class="section-title">你可能还喜欢</h2>
        <div class="recommend-list">
          <div
            v-for="product in recommendedProducts"
            :key="product.id"
            class="recommend-item"
            @click="goToProductDetail(product.id)"
          >
            <img :src="product.image" :alt="product.name" />
            <div class="recommend-info">
              <h3>{{ product.name }}</h3>
              <div class="recommend-price">¥{{ product.price }}</div>
              <el-button
                type="primary"
                size="small"
                :icon="ShoppingCart"
                @click.stop="addRecommendedToCart(product)"
              >
                加入购物车
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空购物车 -->
    <div v-else class="empty-cart">
      <div class="empty-content">
        <el-icon :size="100" color="#c0c4cc">
          <ShoppingCart />
        </el-icon>
        <h2>购物车空空如也</h2>
        <p>快去挑选心仪的商品吧</p>
        <el-button type="primary" size="large" @click="goToProducts">
          去逛逛
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Star, ShoppingCart } from '@element-plus/icons-vue'

const router = useRouter()
const cartStore = useCartStore()

const defaultImage = 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=300&h=300&fit=crop'

// 推荐商品
const recommendedProducts = [
  {
    id: 101,
    name: '无线蓝牙耳机',
    price: 299,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=200&h=200&fit=crop'
  },
  {
    id: 102,
    name: '机械键盘',
    price: 499,
    image: 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=200&h=200&fit=crop'
  },
  {
    id: 103,
    name: '智能手表',
    price: 1299,
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=200&h=200&fit=crop'
  },
  {
    id: 104,
    name: '移动电源',
    price: 199,
    image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&h=200&fit=crop'
  }
]

// 计算属性
const selectedItems = computed(() => cartStore.selectedItems)
const isAllSelected = computed({
  get: () => {
    if (cartStore.cartItems.length === 0) return false
    return cartStore.cartItems.every(item => item.selected || item.stock_quantity <= 0)
  },
  set: (value) => cartStore.toggleSelectAll(value)
})

const isIndeterminate = computed(() => {
  const hasSelected = cartStore.cartItems.some(item => item.selected)
  const hasUnselected = cartStore.cartItems.some(item => !item.selected && item.stock_quantity > 0)
  return hasSelected && hasUnselected
})

const selectedTotalAmount = computed(() => cartStore.selectedAmount)
const selectedTotalDiscount = computed(() => {
  return selectedItems.value.reduce((total, item) => {
    if (item.original_price) {
      return total + (item.original_price - item.price) * item.quantity
    }
    return total
  }, 0)
})

const hasOutOfStock = computed(() => {
  return selectedItems.value.some(item => item.stock_quantity <= 0)
})

// 方法
const handleSelectAll = (selected) => {
  cartStore.toggleSelectAll(selected)
}

const handleItemSelect = (item) => {
  // 触发重新计算
  cartStore.cartItems = [...cartStore.cartItems]
}

const updateQuantity = (item) => {
  if (item.quantity > item.stock_quantity) {
    ElMessage.warning('库存不足')
    item.quantity = item.stock_quantity
    return
  }
  cartStore.updateQuantity(item.product_id, item.quantity)
}

const removeItem = (productId) => {
  ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    cartStore.removeFromCart(productId)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const clearSelectedItems = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要删除的商品')
    return
  }
  
  ElMessageBox.confirm('确定要删除选中的商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    cartStore.removeSelectedItems()
  }).catch(() => {})
}

const clearCart = () => {
  if (cartStore.cartItems.length === 0) return
  
  ElMessageBox.confirm('确定要清空购物车吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    cartStore.clearCart()
    ElMessage.success('购物车已清空')
  }).catch(() => {})
}

const addToFavorites = (item) => {
  ElMessage.success(`已收藏商品：${item.product_name}`)
}

const addRecommendedToCart = (product) => {
  cartStore.addToCart({
    product_id: product.id,
    product_name: product.name,
    price: product.price,
    image_url: product.image,
    stock_quantity: 100
  })
  ElMessage.success(`已添加 ${product.name} 到购物车`)
}

const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`)
}

const goToProducts = () => {
  router.push('/products')
}

const goToCheckout = () => {
  if (hasOutOfStock.value) {
    ElMessage.error('选中的商品中有缺货商品，请重新选择')
    return
  }
  router.push('/checkout')
}

// 初始化
onMounted(() => {
  cartStore.initCart()
})
</script>

<style scoped>
.cart-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.cart-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.cart-header {
  display: grid;
  grid-template-columns: 2fr 3fr;
  background: #f5f7fa;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-title {
  color: #606266;
  font-weight: 500;
}

.header-right {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 20px;
  text-align: center;
}

.header-column {
  color: #606266;
  font-weight: 500;
}

.cart-items {
  padding: 20px;
}

.cart-item {
  display: grid;
  grid-template-columns: 2fr 3fr;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  transition: background-color 0.3s;
}

.cart-item:hover {
  background-color: #fafafa;
}

.item-disabled {
  opacity: 0.6;
  background-color: #f5f7fa;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.item-image {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  cursor: pointer;
  border-radius: 6px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sold-out-badge {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-name:hover {
  color: #409EFF;
}

.item-spec {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.item-stock {
  color: #606266;
  font-size: 14px;
}

.low-stock {
  color: #f56c6c;
  font-weight: 500;
}

.item-right {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 20px;
  align-items: center;
}

.item-column {
  text-align: center;
}

.price-column {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.current-price {
  font-size: 18px;
  color: #f56c6c;
  font-weight: bold;
}

.original-price {
  font-size: 14px;
  color: #909399;
  text-decoration: line-through;
}

.quantity-column {
  display: flex;
  justify-content: center;
}

.subtotal-column {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.subtotal {
  font-size: 18px;
  color: #303133;
  font-weight: 500;
}

.discount {
  font-size: 12px;
  color: #67c23a;
}

.action-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.selected-count {
  color: #606266;
  font-size: 14px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 40px;
}

.total-info {
  text-align: right;
}

.total-amount {
  font-size: 18px;
  color: #303133;
  margin-bottom: 5px;
}

.total-price {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}

.total-discount {
  color: #67c23a;
  font-size: 14px;
}

.checkout-btn {
  width: 200px;
  height: 48px;
  font-size: 16px;
}

.recommendations {
  padding: 40px 20px;
  border-top: 1px solid #e4e7ed;
}

.section-title {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
  text-align: center;
}

.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.recommend-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
  cursor: pointer;
}

.recommend-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.recommend-item img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.recommend-info {
  padding: 15px;
  text-align: center;
}

.recommend-info h3 {
  font-size: 14px;
  color: #303133;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-price {
  font-size: 18px;
  color: #f56c6c;
  font-weight: bold;
  margin-bottom: 10px;
}

.empty-cart {
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.empty-content {
  text-align: center;
}

.empty-content h2 {
  font-size: 24px;
  color: #303133;
  margin: 20px 0 10px;
}

.empty-content p {
  color: #909399;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .cart-header,
  .cart-item {
    grid-template-columns: 1fr;
  }
  
  .header-right {
    display: none;
  }
  
  .item-right {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px dashed #e4e7ed;
  }
  
  .cart-footer {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
  }
  
  .checkout-btn {
    width: 100%;
  }
}
</style>