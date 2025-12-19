from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

from database import db
from auth import router as auth_router
from products import router as products_router
from cart import router as cart_router
from orders import router as orders_router
from user import router as user_router  # 🔧 新增：导入 user 路由

# 加载环境变量
load_dotenv()

# 应用生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("🚀 启动电商系统API...")
    print("📊 数据库连接测试...")
    
    try:
        # 测试数据库连接
        result = db.execute_query("SELECT @@VERSION as version")
        print(f"✅ 数据库连接成功: {result[0]['version'][:50]}...")
        
        # 测试表是否存在
        tables = db.execute_query("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND TABLE_CATALOG = 'ECommerceDB'
            ORDER BY TABLE_NAME
        """)
        print(f"📁 数据库中有 {len(tables)} 张表")
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        raise
    
    yield
    
    # 关闭时
    db.close()
    print("👋 关闭数据库连接")

app = FastAPI(
    title="电商系统API",
    description="电商系统后端接口 - Vue.js + FastAPI + SQL Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # 改为离线模式
    swagger_js_url=None,    # 不加载外部JS
    swagger_css_url=None,   # 不加载外部CSS
    # 可以删除或保留swagger_favicon_url这一行
    # swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
)

# 配置CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue开发服务器
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(user_router, prefix="/api")  # 🔧 新增：注册 user 路由

# 根路由
@app.get("/")
async def root():
    return {
        "message": "🏪 电商系统API运行中",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc",
        "endpoints": [
            "/api/auth/* - 用户认证",
            "/api/products/* - 商品管理",
            "/api/cart/* - 购物车",
            "/api/orders/* - 订单管理",
            "/api/user/* - 用户管理"  # 🔧 新增：用户管理端点
        ]
    }

# 健康检查
@app.get("/health")
async def health_check():
    try:
        # 测试数据库
        db.execute_query("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-12-15T10:30:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )

# API信息
@app.get("/api/info")
async def api_info():
    return {
        "project": "电商系统",
        "backend": "FastAPI",
        "frontend": "Vue.js 3 + Element Plus",
        "database": "SQL Server",
        "version": "1.0.0",
        "author": "数据库课设",
        "api_docs": "http://localhost:8000/docs",
        "github_repo": "https://github.com/yourusername/ecommerce-system",
        "modules": [  # 🔧 新增：显示所有模块
            "auth - 用户认证模块",
            "user - 用户管理模块",
            "products - 商品管理模块",
            "cart - 购物车模块",
            "orders - 订单管理模块"
        ]
    }

# 测试数据库连接
@app.get("/api/test-db")
async def test_database():
    """测试数据库连接和基本查询"""
    try:
        # 测试用户表
        users = db.execute_query("SELECT TOP 3 user_id, username, email FROM [User]")
        
        # 测试商品表
        products = db.execute_query("SELECT TOP 3 product_id, product_name, price FROM Product WHERE product_status = 1")
        
        # 测试地址表
        addresses = db.execute_query("SELECT TOP 3 address_id, receiver_name, receiver_phone FROM Address")
        
        # 测试存储过程（如果存在）
        try:
            proc_test = db.execute_query("EXEC sp_help 'User'")
            proc_status = "可用"
        except:
            proc_status = "不可用或出错"
        
        return {
            "code": 200,
            "message": "数据库测试成功",
            "data": {
                "user_count": len(users),
                "users": users,
                "product_count": len(products),
                "products": products,
                "address_count": len(addresses),
                "addresses": addresses,
                "stored_procedures": proc_status,
                "connection": "正常",
                "modules": {
                    "auth": "已加载",
                    "user": "已加载",  # 🔧 新增：显示 user 模块状态
                    "products": "已加载",
                    "cart": "已加载",
                    "orders": "已加载"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据库测试失败: {str(e)}"
        )

# 启动应用（开发模式）
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🛒 电商系统后端服务")
    print("="*50)
    print("📚 API文档: http://localhost:8000/docs")
    print("📘 ReDoc文档: http://localhost:8000/redoc")
    print("🌐 前端地址: http://localhost:5173")
    print("🛠️  测试接口: http://localhost:8000/api/test-db")
    print("🔍 用户管理: http://localhost:8000/api/user/addresses")  # 🔧 新增：用户管理地址
    print("="*50 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 允许所有IP访问
        port=8000,
        reload=True,     # 开发模式，代码更改自动重启
        log_level="info"
    )