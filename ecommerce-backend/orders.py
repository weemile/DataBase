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
        orders = db.execute_query('SELECT o.order_id, o.user_id, o.address_id, o.total_amount, o.order_status, o.create_time, o.pay_time, o.ship_time, a.receiver_name, a.receiver_phone, a.detail_address FROM [Order] o LEFT JOIN Address a ON o.address_id = a.address_id WHERE o.user_id = ? ORDER BY o.create_time DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY', (current_user["user_id"], offset, page_size))
        
        # 查询总数
        count_result = db.execute_query('SELECT COUNT(*) AS total_count FROM [Order] o WHERE o.user_id = ?', (current_user["user_id"],))
        
        total_count = count_result[0]["total_count"] if count_result else 0
        
        # 处理每个订单，添加必要的字段
        processed_orders = []
        for order in orders:
            # 获取订单商品
            items_sql = 'SELECT oi.item_id, oi.order_id, oi.product_id, oi.order_quantity AS quantity, oi.unit_price, oi.subtotal, p.image AS product_image, p.product_name FROM OrderItem oi LEFT JOIN Product p ON oi.product_id = p.product_id WHERE oi.order_id = ?'
            items = db.execute_query(items_sql, (order["order_id"],))
            
            # 构建完整的订单数据
            processed_order = {
                **order,
                "order_no": f"ORD{order['order_id']:08d}",  # 添加订单号
                "shipping_fee": 0.0,  # 默认值
                "final_amount": order["total_amount"],  # 默认值
                "items": items,  # 添加商品列表
                "item_count": len(items)  # 添加商品数量
            }
            
            processed_orders.append(processed_order)
        
        print(f"查询到的订单数量: {len(processed_orders)}")
        print(f"总订单数: {total_count}")
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": processed_orders,
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
        print("=== 创建订单调试信息 ===")
        print(f"用户ID: {current_user['user_id']}")
        print(f"地址ID: {order_data.address_id}")
        print(f"购物车ID列表: {order_data.cart_ids}")
        print(f"配送费: {order_data.shipping_fee}")
        print(f"备注: {order_data.remark}")

        # 调用存储过程 sp_CreateOrder，当前存储过程只接受user_id、address_id和order_id输出参数
        result = db.execute_proc("sp_CreateOrder", [
            current_user["user_id"],
            order_data.address_id,
            0  # 输出参数占位
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
    payment_method: str = "Online",  # 默认在线支付
    transaction_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # 验证订单属于当前用户
    order_check = db.execute_query(
        "SELECT order_id, user_id FROM [Order] WHERE order_id = ?",
        (order_id,)
    )
    
    if not order_check:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order_check[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权支付此订单")
    """支付订单"""
    try:
        # 调用存储过程 sp_PayOrder(order_id, payment_method, transaction_id)
        result = db.execute_proc("sp_PayOrder", [
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
            SELECT o.order_id, o.user_id, o.address_id, o.total_amount,
                   o.create_time, o.pay_time, o.ship_time, o.order_status,
                   a.receiver_name, a.receiver_phone, a.detail_address
            FROM [Order] o
            LEFT JOIN Address a ON o.address_id = a.address_id
            WHERE o.order_id = ?
        """
        order_info = db.execute_query(order_sql, (order_id,))
        
        if not order_info:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 获取订单商品
        items_sql = """
            SELECT oi.item_id, oi.order_id, oi.product_id, oi.order_quantity, oi.unit_price, oi.subtotal,
                   p.image AS image, p.product_name
            FROM OrderItem oi
            LEFT JOIN Product p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """
        items = db.execute_query(items_sql, (order_id,))
        
        # 获取支付信息
        payment_sql = """
            SELECT payment_id, order_id, payment_method, payment_amount, payment_status, payment_time, transaction_id
            FROM Payment WHERE order_id = ? ORDER BY payment_time DESC
        """
        payments = db.execute_query(payment_sql, (order_id,))
        
        result = order_info[0]
        # 为缺失字段添加默认值
        result["discount_amount"] = 0.0
        result["shipping_fee"] = 0.0
        result["final_amount"] = result["total_amount"]
        result["order_no"] = f"ORD{result['order_id']:08d}"  # 添加订单号
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