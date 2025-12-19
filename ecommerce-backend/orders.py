from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List

from database import db
from models import OrderCreate
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["订单"])

@router.get("/")
async def get_orders(
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """获取用户订单列表"""
    try:
        print(f"=== 调试订单列表 ===")
        
        # 使用直接SQL查询，避免存储过程格式问题
        offset = (page - 1) * page_size
        
        # 查询订单列表
        orders = db.execute_query("""
            SELECT   
                o.order_id, o.order_no, o.user_id, o.address_id,  
                o.total_amount, o.discount_amount, o.shipping_fee, o.final_amount,  
                o.payment_method, o.order_status, o.create_time, o.pay_time,  
                o.ship_time, o.receive_time, o.cancel_time, o.cancel_reason, o.remark,  
                a.receiver_name, a.receiver_phone, a.province, a.city, a.district, a.detail_address,  
                (SELECT COUNT(*) FROM OrderItem WHERE order_id = o.order_id) AS item_count  
            FROM [Order] o  
            LEFT JOIN Address a ON o.address_id = a.address_id  
            WHERE o.user_id = ?
            ORDER BY o.create_time DESC
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """, (current_user["user_id"], offset, page_size))
        
        # 查询总数
        count_result = db.execute_query("""
            SELECT COUNT(*) AS total_count
            FROM [Order] o  
            WHERE o.user_id = ?
        """, (current_user["user_id"],))
        
        total_count = count_result[0]["total_count"] if count_result else 0
        
        print(f"查询到的订单数量: {len(orders)}")
        print(f"总订单数: {total_count}")
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": orders,
                "total": total_count,
                "page": page,
                "page_size": page_size
            }
        }
        
    except Exception as e:
        print(f"获取订单列表异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取订单列表失败: {str(e)}"
        )
@router.post("/")
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建订单"""
    try:
        # 将cart_ids列表转换为JSON字符串
        import json
        cart_ids_json = json.dumps(order_data.cart_ids)
        
        print("=== 创建订单调试信息 ===")
        print(f"用户ID: {current_user['user_id']}")
        print(f"地址ID: {order_data.address_id}")
        print(f"购物车IDs: {order_data.cart_ids}")
        print(f"购物车JSON: {cart_ids_json}")
        print(f"运费: {order_data.shipping_fee}")
        print(f"备注: {order_data.remark}")
        
        # 调用存储过程
        result = db.execute_proc("USP_CreateOrder", [
            current_user["user_id"],
            order_data.address_id,
            cart_ids_json,
            order_data.shipping_fee,
            order_data.remark or "",
            "",  # @order_no (output placeholder)
            0    # @order_id (output placeholder)
        ])
        
        print(f"存储过程返回: {result}")
        
        if result and len(result) > 0:
            order_info = result[0]
            print(f"订单创建成功: {order_info}")
            return {
                "code": 200,
                "message": "订单创建成功",
                "data": order_info
            }
        else:
            print("存储过程返回空结果")
            raise HTTPException(status_code=400, detail="订单创建失败")
        
    except Exception as e:
        error_msg = str(e)
        print(f"创建订单异常: {error_msg}")
        if "购物车为空" in error_msg:
            raise HTTPException(status_code=400, detail="购物车为空")
        elif "地址不存在" in error_msg:
            raise HTTPException(status_code=400, detail="地址不存在")
        else:
            raise HTTPException(
                status_code=500,
                detail=f"创建订单失败: {error_msg}"
            )

@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    payment_method: str,
    transaction_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """支付订单"""
    try:
        # 调用存储过程
        result = db.execute_proc("USP_PayOrder", [
            order_id,
            payment_method,
            transaction_id or ""
        ])
        
        if result and len(result) > 0:
            return {
                "code": 200,
                "message": "支付成功",
                "data": result[0]
            }
        else:
            raise HTTPException(status_code=400, detail="支付失败")
        
    except Exception as e:
        error_msg = str(e)
        if "订单状态不正确" in error_msg:
            raise HTTPException(status_code=400, detail="订单状态不正确，无法支付")
        elif "订单不存在" in error_msg:
            raise HTTPException(status_code=404, detail="订单不存在")
        else:
            raise HTTPException(
                status_code=500,
                detail=f"支付失败: {error_msg}"
            )

@router.get("/{order_id}")
async def get_order_detail(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    try:
        # 验证订单属于当前用户
        order_check = db.execute_query(
            "SELECT order_id, user_id FROM [Order] WHERE order_id = ?",
            (order_id,)
        )
        
        if not order_check:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        if order_check[0]["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权查看此订单")
        
        # 获取订单基本信息
        order_sql = """
            SELECT o.*, 
                   a.receiver_name, a.receiver_phone,
                   a.province, a.city, a.district, a.detail_address
            FROM [Order] o
            LEFT JOIN Address a ON o.address_id = a.address_id
            WHERE o.order_id = ?
        """
        order_info = db.execute_query(order_sql, (order_id,))
        
        if not order_info:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 获取订单商品
        items_sql = """
            SELECT oi.*, p.image_url
            FROM OrderItem oi
            LEFT JOIN Product p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """
        items = db.execute_query(items_sql, (order_id,))
        
        # 获取支付信息
        payment_sql = """
            SELECT * FROM Payment WHERE order_id = ? ORDER BY create_time DESC
        """
        payments = db.execute_query(payment_sql, (order_id,))
        
        result = order_info[0]
        result["items"] = items
        result["payments"] = payments
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取订单详情失败: {str(e)}"
        )