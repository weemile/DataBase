// Test script to verify cart functionality
import { cartApi } from './src/api/cart.js';

async function testAddToCart() {
  console.log('开始测试添加到购物车功能...');
  
  try {
    // 测试直接传递product_id和quantity
    const product_id = 1; // 假设这是一个有效的商品ID
    const quantity = 2;
    
    console.log('测试参数:', {
      product_id,
      quantity
    });
    
    const response = await cartApi.addToCart(product_id, quantity);
    console.log('✅ 测试成功! 响应:', response.data);
    
    return true;
  } catch (error) {
    console.error('❌ 测试失败! 错误:', error);
    return false;
  }
}

// 运行测试
testAddToCart();