from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import db
from auth import get_current_user

router = APIRouter(prefix="/user", tags=["用户管理"])

# ==================== 地址模型定义 ====================

class AddressBase(BaseModel):
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail_address: str
    postal_code: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass

class AddressResponse(AddressBase):
    address_id: int
    user_id: int
    is_default: int  # 返回0/1
    create_time: datetime
    update_time: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== 获取地址列表API ====================

@router.get("/addresses", response_model=dict)
async def get_addresses(current_user: dict = Depends(get_current_user)):
    """获取当前用户的地址列表"""
    try:
        user_id = current_user["user_id"]
        print(f"📋 获取用户地址列表，用户ID: {user_id}")
        
        # 查询地址
        addresses = db.execute_query(
            "SELECT * FROM Address WHERE user_id = ? ORDER BY is_default DESC, create_time DESC",
            (user_id,)
        )
        
        # 转换 is_default: 0/1 → False/True（如果需要）
        # 这里先保持0/1，前端自己处理
        
        return {
            "code": 200,
            "message": "success",
            "data": addresses
        }
        
    except Exception as e:
        print(f"💥 获取地址列表异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取地址失败: {str(e)}"
        )

# ==================== 添加地址API ====================

@router.post("/addresses")
async def create_address(
    address_data: AddressCreate,
    current_user: dict = Depends(get_current_user)
):
    """添加新地址"""
    try:
        user_id = current_user["user_id"]
        print(f"📝 添加地址，用户ID: {user_id}, 数据: {address_data.dict()}")
        
        # 转换 is_default: True/False → 1/0
        is_default_int = 1 if address_data.is_default else 0
        
        # 如果设置为默认地址，需要取消其他地址的默认状态
        if is_default_int == 1:
            db.execute_update(
                "UPDATE Address SET is_default = 0 WHERE user_id = ?",
                (user_id,)
            )
        
        # 插入新地址
        sql = """
        INSERT INTO Address 
        (user_id, receiver_name, receiver_phone, province, city, district, 
         detail_address, postal_code, is_default, create_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        
        params = (
            user_id,
            address_data.receiver_name,
            address_data.receiver_phone,
            address_data.province,
            address_data.city,
            address_data.district,
            address_data.detail_address,
            address_data.postal_code,
            is_default_int
        )
        
        db.execute_update(sql, params)
        
        # 获取新插入的地址ID
        new_address = db.execute_query(
            "SELECT TOP 1 * FROM Address WHERE user_id = ? ORDER BY create_time DESC",
            (user_id,)
        )
        
        if new_address:
            return {
                "code": 200,
                "message": "地址添加成功",
                "data": new_address[0]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="地址添加失败"
            )
            
    except Exception as e:
        print(f"💥 添加地址异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加地址失败: {str(e)}"
        )

# ==================== 修改地址API ====================

@router.put("/addresses/{address_id}")
async def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """修改地址"""
    try:
        user_id = current_user["user_id"]
        print(f"📝 修改地址，地址ID: {address_id}, 用户ID: {user_id}")
        
        # 1. 验证地址是否存在且属于当前用户
        existing_address = db.execute_query(
            "SELECT * FROM Address WHERE address_id = ? AND user_id = ?",
            (address_id, user_id)
        )
        
        if not existing_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地址不存在或无权访问"
            )
        
        # 2. 转换 is_default: True/False → 1/0
        is_default_int = 1 if address_data.is_default else 0
        
        # 3. 如果设置为默认地址，需要取消其他地址的默认状态
        if is_default_int == 1:
            db.execute_update(
                "UPDATE Address SET is_default = 0 WHERE user_id = ? AND address_id != ?",
                (user_id, address_id)
            )
        
        # 4. 更新地址信息
        sql = """
        UPDATE Address SET
            receiver_name = ?,
            receiver_phone = ?,
            province = ?,
            city = ?,
            district = ?,
            detail_address = ?,
            postal_code = ?,
            is_default = ?,
            update_time = GETDATE()
        WHERE address_id = ? AND user_id = ?
        """
        
        params = (
            address_data.receiver_name,
            address_data.receiver_phone,
            address_data.province,
            address_data.city,
            address_data.district,
            address_data.detail_address,
            address_data.postal_code,
            is_default_int,
            address_id,
            user_id
        )
        
        rows_affected = db.execute_update(sql, params)
        
        if rows_affected > 0:
            # 获取更新后的地址
            updated_address = db.execute_query(
                "SELECT * FROM Address WHERE address_id = ?",
                (address_id,)
            )
            
            return {
                "code": 200,
                "message": "地址修改成功",
                "data": updated_address[0] if updated_address else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="地址修改失败"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 修改地址异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改地址失败: {str(e)}"
        )

# ==================== 删除地址API ====================

@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除地址"""
    try:
        user_id = current_user["user_id"]
        print(f"🗑️ 删除地址，地址ID: {address_id}, 用户ID: {user_id}")
        
        # 1. 验证地址是否存在且属于当前用户
        existing_address = db.execute_query(
            "SELECT * FROM Address WHERE address_id = ? AND user_id = ?",
            (address_id, user_id)
        )
        
        if not existing_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地址不存在或无权访问"
            )
        
        # 2. 检查是否为默认地址（可选：不允许删除默认地址）
        if existing_address[0]["is_default"] == 1:
            # 可以选择不允许删除默认地址，或者允许但需要处理
            # 这里我们先允许删除，但给出警告
            print("⚠️ 正在删除默认地址")
        
        # 3. 删除地址
        rows_affected = db.execute_update(
            "DELETE FROM Address WHERE address_id = ? AND user_id = ?",
            (address_id, user_id)
        )
        
        if rows_affected > 0:
            return {
                "code": 200,
                "message": "地址删除成功",
                "data": {
                    "address_id": address_id,
                    "deleted": True
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="地址删除失败"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 删除地址异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除地址失败: {str(e)}"
        )

# ==================== 设置默认地址API ====================

@router.put("/addresses/{address_id}/default")
async def set_default_address(
    address_id: int,
    current_user: dict = Depends(get_current_user)
):
    """设置默认地址"""
    try:
        user_id = current_user["user_id"]
        print(f"⭐ 设置默认地址，地址ID: {address_id}, 用户ID: {user_id}")
        
        # 1. 验证地址是否存在且属于当前用户
        existing_address = db.execute_query(
            "SELECT * FROM Address WHERE address_id = ? AND user_id = ?",
            (address_id, user_id)
        )
        
        if not existing_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地址不存在或无权访问"
            )
        
        # 2. 如果已经是默认地址，直接返回成功
        if existing_address[0]["is_default"] == 1:
            return {
                "code": 200,
                "message": "该地址已经是默认地址",
                "data": existing_address[0]
            }
        
        # 3. 开始事务：先取消所有地址的默认状态，再设置指定地址为默认
        # 注意：这里假设数据库支持事务，SQL Server默认支持
        
        # 取消所有地址的默认状态
        db.execute_update(
            "UPDATE Address SET is_default = 0 WHERE user_id = ?",
            (user_id,)
        )
        
        # 设置指定地址为默认
        rows_affected = db.execute_update(
            "UPDATE Address SET is_default = 1, update_time = GETDATE() WHERE address_id = ? AND user_id = ?",
            (address_id, user_id)
        )
        
        if rows_affected > 0:
            # 获取更新后的地址
            updated_address = db.execute_query(
                "SELECT * FROM Address WHERE address_id = ?",
                (address_id,)
            )
            
            return {
                "code": 200,
                "message": "设置默认地址成功",
                "data": updated_address[0] if updated_address else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="设置默认地址失败"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 设置默认地址异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"设置默认地址失败: {str(e)}"
        )