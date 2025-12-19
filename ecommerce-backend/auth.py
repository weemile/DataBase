from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

from database import db
from models import UserLogin, UserRegister, Token

router = APIRouter(prefix="/auth", tags=["认证"])

# JWT配置 - 使用你的.env中的密钥
SECRET_KEY = "your-super-secret-jwt-key-12345-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    user = db.execute_query(
        "SELECT user_id, username, email, phone, user_type FROM [User] WHERE user_id = ?",
        (int(user_id),)
    )
    if not user:
        raise credentials_exception
    
    return user[0]

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """用户登录 - 针对明文密码版本"""
    try:
        print(f"🔐 收到登录请求: 用户名={user_data.username}")
        
        # 1. 查询用户（兼容用户名或邮箱登录）
        user_result = db.execute_query(
            "SELECT user_id, username, password, user_type FROM [User] WHERE username = ? OR email = ?",
            (user_data.username, user_data.username)
        )
        
        if not user_result:
            print(f"❌ 用户不存在: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        user = user_result[0]
        stored_password = user["password"]
        
        print(f"📋 找到用户: ID={user['user_id']}, 用户名={user['username']}")
        print(f"🔑 数据库密码: {stored_password}, 输入密码: {user_data.password}")
        
        # 2. 密码验证（针对明文密码 - 数据库中是admin123这样的明文）
        if user_data.password != stored_password:
            print("❌ 密码不匹配")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        print("✅ 密码验证成功")
        
        # 3. 更新最后登录时间
        db.execute_update(
            "UPDATE [User] SET last_login_time = GETDATE() WHERE user_id = ?",
            (user["user_id"],)
        )
        
        # 4. 创建token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["user_id"])},
            expires_delta=access_token_expires
        )
        
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["user_id"],
            "username": user["username"],
            "user_type": user["user_type"]
        }
        
        print(f"✅ 登录成功，返回token: {access_token[:20]}...")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 登录异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.post("/register")
async def register(user_data: UserRegister):
    """用户注册"""
    try:
        print(f"📝 注册新用户: {user_data.username}")
        
        # 直接使用明文密码，不进行哈希
        plain_password = user_data.password
        
        # 调用存储过程
        result = db.execute_proc("sp_RegisterUser", [
            user_data.username,
            plain_password,  # 传递明文密码
            user_data.phone,
            user_data.email,
            user_data.user_type,
            0  # @new_user_id (output placeholder)
        ])
        
        print(f"🔍 存储过程返回结果: {result}")
        
        # 方法1：检查是否有返回结果
        if result and len(result) > 0:
            new_user = result[0]
            new_user_id = new_user.get('new_user_id')
            print(f"✅ 注册成功，用户ID: {new_user_id}")
            return {
                "code": 200,
                "message": "注册成功",
                "data": {
                    "user_id": new_user_id,
                    "username": user_data.username
                }
            }
        
       
        user_check = db.execute_query(
            "SELECT user_id FROM [User] WHERE username = ?",
            (user_data.username,)
        )
        
        if user_check:
            user_id = user_check[0]['user_id']
            print(f"✅ 用户已创建成功，用户ID: {user_id}")
            return {
                "code": 200,
                "message": "注册成功",
                "data": {
                    "user_id": user_id,
                    "username": user_data.username
                }
            }
        
        # 如果两种方法都失败
        print("❌ 注册失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )
            
    except Exception as e:
        print(f"💥 注册异常: {str(e)}")
        
        # 检查错误类型，返回对应的错误信息
        error_msg = str(e)
        if "已存在" in error_msg or "2627" in error_msg or "2601" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或邮箱已存在"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"注册失败: {error_msg}"
            )


@router.put("/profile")
async def update_profile(
    user_data: dict,  # 需要定义更新模型
    current_user: dict = Depends(get_current_user)
):
    """更新用户信息"""
    try:
        user_id = current_user["user_id"]
        print(f"📝 更新用户信息: ID={user_id}, 数据={user_data}")
        
        # 调用存储过程 sp_UpdateUserInfo
        result = db.execute_proc("sp_UpdateUserInfo", [
            user_id,
            user_data.get("username"),  # 可以为None
            user_data.get("phone"),     # 可以为None
            user_data.get("email")      # 可以为None
        ])
        
        print(f"✅ 用户信息更新成功")
        return {
            "code": 200,
            "message": "用户信息更新成功",
            "data": {
                "user_id": user_id,
                "updated_fields": [k for k, v in user_data.items() if v is not None]
            }
        }
            
    except Exception as e:
        print(f"💥 更新用户信息异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    print(f"👤 获取用户信息: ID={current_user['user_id']}")
    return {
        "code": 200,
        "message": "success",
        "data": current_user
    }

@router.get("/test")
async def test_auth():
    """测试认证模块是否正常工作"""
    return {
        "code": 200,
        "message": "认证模块工作正常",
        "timestamp": datetime.now().isoformat()
    }