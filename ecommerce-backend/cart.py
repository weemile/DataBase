from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from pydantic import BaseModel
from database import db
from auth import get_current_user

router = APIRouter(prefix="/cart")

class CartItem(BaseModel):
    product_id: int
    quantity: int

@router.get("/")
@router.get("")
async def get_cart(current_user: dict = Depends(get_current_user)):
    """获取购物车列表"""
    try:
        sql = """
            SELECT 
                c.cart_id, 
                c.user_id, 
                c.product_id, 
                c.cart_quantity, 
                c.add_time,
                p.product_name,
                p.price,
                p.image AS image_url,
                p.stock_quantity,
                p.product_status
            FROM Cart c
            INNER JOIN Product p ON c.product_id = p.product_id
            WHERE c.user_id = ?
            AND p.product_status = 1
            ORDER BY c.add_time DESC
        """
        items = db.execute_query(sql, (current_user["user_id"],))
        
        # 计算统计信息
        total_items = len(items)
        cart_total = sum(item["price"] * item["cart_quantity"] for item in items) if items else 0
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": [
                    {
                        **item,
                        "quantity": item["cart_quantity"],
                        "selected": True  # 默认选中
                    }
                    for item in items
                ],
                "summary": {
                    "total_items": total_items,
                    "total_amount": cart_total
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取购物车失败: {str(e)}"
        )

@router.post("/add")
async def add_to_cart(
    item: CartItem,
    current_user: dict = Depends(get_current_user)
):
    # Add debug log to see what's being received
    print(f"Debug: Received add_to_cart request with item: {item}")
    """添加商品到购物车"""
    try:
        # 调用存储过程
        result = db.execute_proc("sp_AddToCart", [
            current_user["user_id"],
            item.product_id,
            item.quantity
        ])
        
        return {
            "code": 200,
            "message": "添加成功",
            "data": result[0] if result else []
        }
        
    except Exception as e:
        error_msg = str(e)
        if "库存不足" in error_msg:
            raise HTTPException(status_code=400, detail="库存不足")
        elif "商品不存在" in error_msg:
            raise HTTPException(status_code=404, detail="商品不存在")
        else:
            raise HTTPException(
                status_code=500,
                detail=f"添加到购物车失败: {error_msg}"
            )

@router.delete("/{product_id}")
async def remove_from_cart(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    """从购物车移除商品"""
    try:
        # 先检查商品是否存在
        cart_item = db.execute_query(
            "SELECT * FROM Cart WHERE user_id = ? AND product_id = ?",
            (current_user["user_id"], product_id)
        )
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="商品不在购物车中")
        
        # 删除
        db.execute_update(
            "DELETE FROM Cart WHERE user_id = ? AND product_id = ?",
            (current_user["user_id"], product_id)
        )
        
        return {
            "code": 200,
            "message": "移除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"移除商品失败: {str(e)}"
        )

@router.put("/{product_id}")
async def update_cart_item(
    product_id: int,
    item: CartItem,
    current_user: dict = Depends(get_current_user)
):
    """更新购物车商品数量"""
    try:
        # 先检查库存
        stock_info = db.execute_query(
            "SELECT stock_quantity FROM Product WHERE product_id = ? AND product_status = 1",
            (product_id,)
        )
        
        if not stock_info:
            raise HTTPException(status_code=404, detail="商品不存在")
        
        if stock_info[0]["stock_quantity"] < item.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        
        # 更新数量
        db.execute_update(
            "UPDATE Cart SET cart_quantity = ? WHERE user_id = ? AND product_id = ?",
            (item.quantity, current_user["user_id"], product_id)
        )
        
        return {
            "code": 200,
            "message": "更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新购物车失败: {str(e)}"
        )

@router.delete("/batch")
async def batch_remove_from_cart(
    product_ids: List[int] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """批量删除购物车商品"""
    try:
        if not product_ids:
            raise HTTPException(status_code=400, detail="请选择要删除的商品")
        
        # 使用参数化查询批量删除
        placeholders = ",".join(["?"] * len(product_ids))
        sql = f"DELETE FROM Cart WHERE user_id = ? AND product_id IN ({placeholders})"
        
        # 执行删除
        db.execute_update(sql, (current_user["user_id"], *product_ids))
        
        return {
            "code": 200,
            "message": "批量删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量删除失败: {str(e)}"
        )

@router.delete("/")
async def clear_cart(current_user: dict = Depends(get_current_user)):
    """清空购物车"""
    try:
        db.execute_proc("sp_ClearCart", [current_user["user_id"]])
        
        return {
            "code": 200,
            "message": "购物车已清空"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"清空购物车失败: {str(e)}"
        )
