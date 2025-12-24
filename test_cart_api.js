// Node.js test script to verify cart API
const axios = require('axios');

// Authentication credentials (update with actual test account)
const USERNAME = 'alice';
const PASSWORD = 'passw0rd';
let TOKEN = '';

// First, authenticate to get a token
async function login() {
  try {
    const response = await axios.post('http://localhost:8000/api/auth/login', {
      username: USERNAME,
      password: PASSWORD
    });
    
    if (response.data.token) {
      TOKEN = response.data.token;
      console.log('✅ 登录成功，获取到Token');
      return true;
    } else {
      console.error('❌ 登录失败：未返回Token');
      return false;
    }
  } catch (error) {
    console.error('❌ 登录失败：', error.response?.data || error.message);
    return false;
  }
}

async function testAddToCart() {
  console.log('开始测试添加到购物车API...');
  
  const API_URL = 'http://localhost:8000/api/cart/add';
  const testData = {
    product_id: 1,
    quantity: 2
  };
  
  try {
    const response = await axios.post(API_URL, testData, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${TOKEN}`
      }
    });
    
    console.log('✅ API调用成功!');
    console.log('响应状态:', response.status);
    console.log('响应数据:', response.data);
    return true;
  } catch (error) {
    console.error('❌ API调用失败!');
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('状态码:', error.response.status);
      console.error('响应数据:', error.response.data);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('没有收到响应:', error.request);
    } else {
      // 请求配置出错
      console.error('请求错误:', error.message);
    }
    return false;
  }
}

// 运行完整测试
async function runFullTest() {
  console.log('开始完整测试流程...');
  
  // 先登录获取Token
  const loginSuccess = await login();
  
  if (loginSuccess) {
    // 登录成功后测试添加到购物车
    await testAddToCart();
  } else {
    console.error('❌ 测试流程终止：登录失败');
  }
}

// 运行测试
runFullTest();