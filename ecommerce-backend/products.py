from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import math

from database import db
from models import ProductSearch

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
        
        # 分页查询
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT 
                p.product_id, p.product_name, p.description, p.price,
                p.stock_quantity, p.image AS image,
                c.category_name, c.category_id
            FROM Product p
            LEFT JOIN Category c ON p.category_id = c.category_id
            WHERE {where_clause}
            ORDER BY p.product_id DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        
        params_with_paging = params + [offset, page_size]
        products = db.execute_query(query_sql, params_with_paging)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": products,
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
                p.product_id, p.category_id, p.product_name, p.description, p.price,
                p.stock_quantity, p.image AS image, p.product_status,
                c.category_name
            FROM Product p
            LEFT JOIN Category c ON p.category_id = c.category_id
            WHERE p.product_id = ? AND p.product_status = 1
        """
        product = db.execute_query(sql, (product_id,))
        
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在或已下架")
        
        # 获取促销信息
                promotion_sql = """
                        SELECT pr.promotion_id, pr.promotion_name, pr.start_time, pr.end_time,
                                     pr.discount_tyoe, pr.discount_value, pr.promotion_status, pr.promotion_description
                        FROM Promotion pr
                        JOIN Product_Promotion pp ON pr.promotion_id = pp.promotion_id
                        WHERE pp.product_id = ? 
                            AND pr.promotion_status = 1
                            AND GETDATE() BETWEEN pr.start_time AND pr.end_time
                """
        promotions = db.execute_query(promotion_sql, (product_id,))
        
        # 计算最优促销和折扣价格
        original_price = product[0]["price"]
        best_promotion = None
        best_discounted_price = original_price
        discount_amount = 0
        
        if promotions:
            for promo in promotions:
                # 计算这个促销的折后价
                if promo["discount_tyoe"] == 1:  # 折扣倍数（按视图逻辑）
                    discounted_price = original_price * promo["discount_value"]
                else:  # 2 减金额
                    discounted_price = original_price - promo["discount_value"]
                
                # 确保折扣价不为负
                discounted_price = max(discounted_price, 0)
                
                # 取最优（最低价）
                if discounted_price < best_discounted_price:
                    best_discounted_price = discounted_price
                    best_promotion = promo
        
        # 如果有最优促销，计算节省金额
        if best_promotion:
            discount_amount = original_price - best_discounted_price
        
        result = product[0]
        result["promotions"] = promotions
        result["best_promotion"] = best_promotion
        result["original_price"] = original_price
        result["discounted_price"] = round(best_discounted_price, 2)
        result["discount_amount"] = round(discount_amount, 2)
        result["has_discount"] = best_promotion is not None
        
        # 如果是折扣率类型，计算折扣百分比
        if best_promotion and best_promotion["discount_tyoe"] == 1:
            result["discount_label"] = f"x{best_promotion['discount_value']}"
        elif best_promotion and best_promotion["discount_tyoe"] == 2:
            result["discount_label"] = f"减¥{best_promotion['discount_value']}"
        
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
            detail=f"获取商品详情失败: {str(e)}"
        )