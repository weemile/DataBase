from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import math

from database import db
from models import ProductSearch, APIResponse

router = APIRouter(prefix="/products", tags=["商品"])

@router.get("/")
async def get_products(
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取商品列表"""
    try:
        # 构建查询条件
        conditions = ["p.product_status = 1"]  # 只查询上架商品
        params = []
        
        if keyword:
            conditions.append("(p.product_name LIKE ? OR p.description LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        
        if min_price is not None:
            conditions.append("p.price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("p.price <= ?")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions)
        
        # 计算总数
        count_sql = f"""
            SELECT COUNT(*) as total 
            FROM Product p
            LEFT JOIN Category c ON p.category_id = c.category_id
            WHERE {where_clause}
        """
        total_result = db.execute_query(count_sql, params)
        total = total_result[0]["total"] if total_result else 0
        
        # 分页查询 - 添加了促销信息的连接查询
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT 
                p.product_id AS id, p.product_name AS name, p.description, p.price,
                p.stock_quantity AS stock, p.image,
                c.category_name, c.category_id, 0 AS sold_quantity
            FROM Product p
            LEFT JOIN Category c ON p.category_id = c.category_id
            WHERE {where_clause}
            ORDER BY p.product_id DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        
        params_with_paging = params + [offset, page_size]
        products = db.execute_query(query_sql, params_with_paging)
        
        # 转换商品数据格式，确保与前端期望一致
        formatted_products = []
        for product in products:
            original_price = float(product["price"])
            discounted_price = original_price
            has_discount = False
            promotion = None
            
            # 获取该商品的促销信息
            promotion_query = """
                SELECT 
                    pr.promotion_id, pr.discount_tyoe AS discount_type,
                    pr.discount_value, pr.start_time, pr.end_time, pr.promotion_status
                FROM Promotion pr
                JOIN Product_Promotion pp ON pr.promotion_id = pp.promotion_id
                WHERE pp.product_id = ? AND pr.promotion_status = 1 AND GETDATE() BETWEEN pr.start_time AND pr.end_time
            """
            promotion_result = db.execute_query(promotion_query, (product["id"],))
            
            if promotion_result:
                # 计算最优促销
                best_promotion = None
                best_discounted_price = original_price
                
                for promo in promotion_result:
                    if promo["discount_type"] == 1:  # 百分比折扣
                        discount_percentage = float(promo["discount_value"])
                        current_discounted = max(0.01, round(original_price * (discount_percentage / 100), 2))
                    elif promo["discount_type"] == 2:  # 固定金额折扣
                        discount_amount = float(promo["discount_value"])
                        current_discounted = max(0.01, round(original_price - discount_amount, 2))
                    else:
                        current_discounted = original_price
                    
                    if current_discounted < best_discounted_price:
                        best_discounted_price = current_discounted
                        best_promotion = promo
                
                if best_promotion:
                    has_discount = True
                    discounted_price = best_discounted_price
                    
                    # 格式化促销信息
                    if best_promotion["discount_type"] == 1:
                        promotion_tag = f"{int(best_promotion['discount_value'])}折"
                    else:
                        promotion_tag = f"立减¥{best_promotion['discount_value']}"
                    
                    promotion = {
                        "id": best_promotion["promotion_id"],
                        "type": best_promotion["discount_type"],
                        "value": best_promotion["discount_value"],
                        "tag": promotion_tag,
                        "start_time": best_promotion["start_time"],
                        "end_time": best_promotion["end_time"]
                    }
            
            formatted_product = {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": discounted_price,  # 返回折后价
                "original_price": original_price,  # 返回原价
                "has_discount": has_discount,
                "stock": product["stock"],
                "sold_quantity": product["sold_quantity"],
                "image": product["image"],
                "category": {
                    "id": product["category_id"],
                    "name": product["category_name"]
                },
                "promotion": promotion_tag if promotion else None
            }
            formatted_products.append(formatted_product)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": formatted_products,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil(total / page_size) if page_size > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询商品失败: {str(e)}"
        )

@router.get("/categories")
async def get_categories():
    """获取商品分类"""
    try:
        sql = """
            SELECT category_id, category_name, parent_id
            FROM Category
            WHERE status = 1
            ORDER BY sort_order, category_id
        """
        categories = db.execute_query(sql)
        
        # 构建树形结构
        category_map = {}
        root_categories = []
        
        for cat in categories:
            cat["children"] = []
            category_map[cat["category_id"]] = cat
        
        for cat in categories:
            parent_id = cat["parent_id"]
            if parent_id and parent_id in category_map:
                category_map[parent_id]["children"].append(cat)
            else:
                root_categories.append(cat)
        
        return {
            "code": 200,
            "message": "success",
            "data": root_categories
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取分类失败: {str(e)}"
        )

@router.get("/{product_id}")
async def get_product_detail(product_id: int):
    """获取商品详情"""
    try:
        sql = """
            SELECT 
                p.product_id AS id, p.category_id, p.product_name AS name, p.description, p.price,
                p.stock_quantity AS stock, p.image AS image, p.product_status,
                c.category_name, c.category_id, 0 AS sold_quantity
            FROM Product p
            LEFT JOIN Category c ON p.category_id = c.category_id
            WHERE p.product_id = ? AND p.product_status = 1
        """
        product = db.execute_query(sql, (product_id,))
        
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在或已下架")
        
        # 获取该商品的促销信息
        promotion_query = """
            SELECT 
                pr.promotion_id, pr.discount_tyoe AS discount_type,
                pr.discount_value, pr.start_time, pr.end_time, pr.promotion_status
            FROM Promotion pr
            JOIN Product_Promotion pp ON pr.promotion_id = pp.promotion_id
            WHERE pp.product_id = ? AND pr.promotion_status = 1 AND GETDATE() BETWEEN pr.start_time AND pr.end_time
        """
        promotion_result = db.execute_query(promotion_query, (product_id,))
        
        # 处理促销价格逻辑
        original_price = float(product[0]["price"])
        discounted_price = original_price
        has_discount = False
        promotion_info = None
        
        if promotion_result:
            # 计算最优促销
            best_promotion = None
            best_discounted_price = original_price
            
            for promotion in promotion_result:
                # 计算这个促销的折后价
                # 注意：discount_type在数据库中是smallint类型
                # 假设1=percentage（百分比折扣），2=fixed（固定金额折扣）
                if promotion["discount_type"] == 1:  # 百分比折扣
                    discount_percentage = float(promotion["discount_value"]) / 100
                    current_discounted = max(0.01, round(original_price * (1 - discount_percentage), 2))
                elif promotion["discount_type"] == 2:  # 固定金额折扣
                    discount_amount = float(promotion["discount_value"])
                    current_discounted = max(0.01, round(original_price - discount_amount, 2))
                else:
                    current_discounted = original_price
                
                # 取最优（最低价）
                if current_discounted < best_discounted_price:
                    best_discounted_price = current_discounted
                    best_promotion = promotion
            
            if best_promotion:
                has_discount = True
                discounted_price = best_discounted_price
                
                # 格式化促销信息
                promotion_info = {
                    "id": best_promotion["promotion_id"],
                    "type": best_promotion["discount_type"],
                    "value": best_promotion["discount_value"],
                    "start_time": best_promotion["start_time"],
                    "end_time": best_promotion["end_time"]
                }
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "id": product[0]["id"],
                "name": product[0]["name"],
                "description": product[0]["description"],
                "price": original_price,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "has_discount": has_discount,
                "stock": product[0]["stock"],
                "sold_quantity": product[0]["sold_quantity"],
                "image": product[0]["image"],
                "category": {
                    "id": product[0]["category_id"],
                    "name": product[0]["category_name"]
                },
                "promotion": promotion_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取商品详情失败: {str(e)}"
        )