import os

# 项目目录
project_dir = "."

# 要创建的文件列表
files = {
    "main.py": """from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import uvicorn

from database import db
from auth import router as auth_router
from users import router as users_router
from products import router as products_router
from cart import router as cart_router
from orders import router as orders_router

# 应用生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("启动电商系统API...")
    yield
    # 关闭时
    db.close()
    print("关闭数据库连接")

# 创建FastAPI应用
app = FastAPI(
    title="电商系统API",
    description="电商系统后端接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api", tags=["认证"])
app.include_router(users_router, prefix="/api", tags=["用户"])
app.include_router(products_router, prefix="/api", tags=["商品"])
app.include_router(cart_router, prefix="/api", tags=["购物车"])
app.include_router(orders_router, prefix="/api", tags=["订单"])

@app.get("/")
async def root():
    return {"message": "电商系统API运行中", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
""",
    
    "database.py": """import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        
    def get_connection(self):
        '''获取数据库连接'''
        if self.conn is None or not self.conn._connected:
            try:
                self.conn = pymssql.connect(
                    server=os.getenv("DB_SERVER", "localhost"),
                    user=os.getenv("DB_USER", "sa"),
                    password=os.getenv("DB_PASSWORD", ""),
                    database=os.getenv("DB_NAME", "ECommerceDB"),
                    charset='UTF-8'
                )
                print("数据库连接成功")
            except Exception as e:
                print(f"数据库连接失败: {e}")
                raise
        return self.conn
    
    def close(self):
        '''关闭数据库连接'''
        if self.conn and self.conn._connected:
            self.conn.close()
            print("数据库连接已关闭")
    
    def execute_proc(self, proc_name, params=None):
        '''执行存储过程'''
        conn = self.get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            if params:
                cursor.callproc(proc_name, params)
            else:
                cursor.callproc(proc_name)
            result = cursor.fetchall() if cursor.description else []
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute_query(self, sql, params=None):
        '''执行查询'''
        conn = self.get_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def execute_update(self, sql, params=None):
        '''执行更新'''
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

# 全局数据库实例
db = Database()
""",
    
    "models.py": """from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    user_type: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    phone: str
    email: str
    user_type: int = 0

class ProductSearch(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    page: int = 1
    page_size: int = 20

class CartItem(BaseModel):
    product_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    address_id: int
    cart_ids: List[int]
    remark: Optional[str] = None
""",
    
    ".env": """DB_SERVER=localhost
DB_NAME=ECommerceDB
DB_USER=sa
DB_PASSWORD=你的密码
SECRET_KEY=your-secret-key-for-jwt
""",
    
    "requirements.txt": """fastapi==0.104.1
uvicorn[standard]==0.24.0
pymssql==2.2.8
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
""",
    
    "test_db.py": """from database import db

try:
    # 测试用户表
    users = db.execute_query("SELECT TOP 3 * FROM [User]")
    print(f"数据库连接成功！找到 {len(users)} 个用户")
    for user in users:
        print(f"  - {user['username']} ({user['email']})")
    
    # 测试商品表
    products = db.execute_query("SELECT TOP 3 * FROM Product")
    print(f"找到 {len(products)} 个商品")
    for product in products:
        print(f"  - {product['product_name']} (¥{product['price']})")
        
except Exception as e:
    print(f"错误: {e}")
finally:
    db.close()
"""
}

# 创建文件
for filename, content in files.items():
    filepath = os.path.join(project_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"创建文件: {filename}")

print("\\n文件创建完成！请修改 .env 文件中的数据库配置。")