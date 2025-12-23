USE [权限实验];
SET NOCOUNT ON;

-- =========================================
-- 第 0 部分：准备（避免非工作时段触发器阻塞插入）
-- =========================================
IF EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'trg_PreventAfterHoursChanges')
    DISABLE TRIGGER trg_PreventAfterHoursChanges ON dbo.[User];

-- =========================================
-- 第 1 部分：清空表数据（按外键从子到父）
-- =========================================
DELETE FROM dbo.Product_Promotion;
DELETE FROM dbo.Payment;
DELETE FROM dbo.OrderItem;
DELETE FROM dbo.[Order];
DELETE FROM dbo.Cart;
DELETE FROM dbo.Address;
DELETE FROM dbo.Promotion;
DELETE FROM dbo.Product;
DELETE FROM dbo.Category;
DELETE FROM dbo.[User];

-- =========================================
-- 第 2 部分：插入基础数据（用户、分类、商品、促销）
-- =========================================

-- 2.1 用户（满足检查：phone 11 位数字，email 合法，password 长度 >= 6）
INSERT INTO dbo.[User] (user_id, username, password, phone, email, register_time, user_type)
VALUES
    (1, 'alice',   'passw0rd', '13800000001', 'alice@example.com',   GETDATE(), 0),
    (2, 'bob',     'passw0rd', '13800000002', 'bob@example.com',     GETDATE(), 0),
    (3, 'charlie', 'passw0rd', '13800000003', 'charlie@example.com', GETDATE(), 1);

-- 2.2 分类（Cat_category_id/parent_id 指向父级，根类置 NULL）
INSERT INTO dbo.Category (category_id, Cat_category_id, category_name, parent_id, sort_order, status)
VALUES
    (10, NULL, 'Electronics', NULL, 1, 1),
    (11, 10,   'Phones',      10,   2, 1),
    (12, 10,   'Laptops',     10,   3, 1);

-- 2.3 商品（库存充足避免触发库存不足；product_status=1 上架）
INSERT INTO dbo.Product (product_id, category_id, product_name, description, price, stock_quantity, image, product_status)
VALUES
    (100, 11, 'Alpha Phone',    'Flagship phone',       3999.00, 200, 'alpha_phone.jpg',    1),
    (101, 12, 'Bravo Laptop',   'Lightweight laptop',   6999.00, 150, 'bravo_laptop.jpg',   1),
    (102, 11, 'Charlie Earbuds','Wireless earbuds',      599.00, 500, 'charlie_buds.jpg',   1);

-- 2.4 促销与商品关联（discount_tyoe: 1=折扣率，2=减金额）
INSERT INTO dbo.Promotion (promotion_id, promotion_name, start_time, end_time, discount_tyoe, discount_value, promotion_status, promotion_description)
VALUES
    (500, N'Summer Sale 10% Off', DATEADD(DAY,-1,GETDATE()), DATEADD(DAY,14,GETDATE()), 1, 0.90, 1, N'全场九折示例促销');

INSERT INTO dbo.Product_Promotion (product_id, promotion_id)
VALUES (101, 500);

-- 2.5 地址（每用户 1 条默认地址）
INSERT INTO dbo.Address (address_id, user_id, receiver_name, receiver_phone, detail_address, postal_code, is_default)
VALUES
    (1001, 1, 'Alice',   '13800000001', '1st Ave 100',  '100000', 1),
    (1002, 2, 'Bob',     '13800000002', '2nd Blvd 200', '200000', 1),
    (1003, 3, 'Charlie', '13800000003', '3rd Rd 300',   '300000', 1);

-- =========================================
-- 第 3 部分：插入业务数据（购物车、订单、明细、支付）
-- =========================================

-- 3.1 购物车（INSTEAD OF INSERT 需提供 cart_id，且库存充足）
INSERT INTO dbo.Cart (cart_id, product_id, user_id, cart_quantity, add_time)
VALUES
    (9001, 102, 2, 2, DATEADD(MINUTE,-30,GETDATE())),
    (9002, 101, 2, 1, DATEADD(MINUTE,-20,GETDATE()));

-- 3.2 订单（order_status：0 待支付，1 已支付，2 已发货，3 已完成）
INSERT INTO dbo.[Order] (order_id, user_id, address_id, total_amount, create_time, pay_time, ship_time, order_status)
VALUES
    (7001, 1, 1001, 0, DATEADD(DAY,-5,GETDATE()), DATEADD(DAY,-5,GETDATE()), DATEADD(DAY,-4,GETDATE()), 3),
    (7002, 2, 1002, 0, DATEADD(DAY,-2,GETDATE()), DATEADD(DAY,-2,GETDATE()), NULL,                         1),
    (7003, 3, 1003, 0, DATEADD(DAY,-1,GETDATE()), NULL,                      NULL,                         0);

-- 3.3 订单明细（触发器自动维护 subtotal、订单总额、库存扣减）
INSERT INTO dbo.OrderItem (item_id, order_id, product_id, order_quantity, unit_price, subtotal)
VALUES
    (8001, 7001, 101, 1, 6999.00, 6999.00),
    (8002, 7001, 102, 2,  599.00, 1198.00),
    (8003, 7002, 100, 1, 3999.00, 3999.00),
    (8004, 7003, 102, 1,  599.00,  599.00);

-- 3.4 支付记录（payment_status：0 未支付，1 已支付）
INSERT INTO dbo.Payment (payment_id, order_id, payment_method, payment_amount, payment_status, payment_time, transaction_id)
VALUES
    (6001, 7001, 'WeChat Pay', 8197.00, 1, DATEADD(DAY,-5,GETDATE()), 'TXN-7001'),
    (6002, 7002, 'Alipay',     3999.00, 1, DATEADD(DAY,-2,GETDATE()), 'TXN-7002');

-- =========================================
-- 第 5 部分：收尾（恢复触发器）
-- =========================================
IF EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'trg_PreventAfterHoursChanges')
    ENABLE TRIGGER trg_PreventAfterHoursChanges ON dbo.[User];
GO

-- =========================================
-- 第 6 部分：演示查询脚本（只读、与 test.sql 对齐）
-- =========================================

-- 6.1 查询所有用户信息
PRINT '===== 用户列表 =====';
SELECT user_id, username, email, phone, register_time, user_type FROM dbo.[User] ORDER BY user_id;

-- 6.2 查询分类层级结构
PRINT '===== 分类层级 =====';
SELECT * FROM dbo.vw_CategoryHierarchy ORDER BY level, category_id;

-- 6.3 查询所有商品及其分类
PRINT '===== 商品列表 =====';
SELECT * FROM dbo.vw_ProductDetails ORDER BY product_id;

-- 6.4 查询用户购物车详情（Bob的购物车）
PRINT '===== Bob的购物车 =====';
SELECT * FROM dbo.vw_CartDetails WHERE username = 'bob';

-- 6.5 查询订单汇总（所有订单概览）
PRINT '===== 订单汇总 =====';
SELECT * FROM dbo.vw_OrderSummary ORDER BY order_id DESC;

-- 6.6 查询订单明细（Order 7001的完整流程）
PRINT '===== 订单 7001 的完整明细 =====';
SELECT 
    o.order_id, 
    o.order_status, 
    o.create_time, 
    o.pay_time, 
    o.ship_time, 
    o.total_amount,
    oi.item_id, 
    oi.product_id, 
    oi.order_quantity, 
    oi.unit_price, 
    oi.subtotal,
    p.payment_id, 
    p.payment_method, 
    p.payment_amount, 
    p.payment_status, 
    p.payment_time
FROM dbo.[Order] o
LEFT JOIN dbo.OrderItem oi ON o.order_id = oi.order_id
LEFT JOIN dbo.Payment p ON o.order_id = p.order_id
WHERE o.order_id = 7001
ORDER BY oi.item_id;

-- 6.7 查询当前有效的促销商品
PRINT '===== 当前有效促销商品 =====';
SELECT * FROM dbo.vw_PromotionProducts;

-- 6.8 查询用户订单统计
PRINT '===== 用户订单统计 =====';
SELECT * FROM dbo.vw_UserOrderStatistics ORDER BY user_id;

-- 6.9 查询支付记录
PRINT '===== 支付记录 =====';
SELECT * FROM dbo.vw_PaymentRecords ORDER BY payment_id DESC;

-- 6.10 查询热销商品排行
PRINT '===== 热销商品排行 (Top 10) =====';
SELECT TOP 10 * FROM dbo.vw_TopSellingProducts ORDER BY sales_rank;

-- 6.11 查询库存状态
PRINT '===== 库存状态预警 =====';
SELECT * FROM dbo.vw_InventoryStatus ORDER BY stock_level DESC, product_id;

-- 6.12 查询每日销售汇总
PRINT '===== 每日销售汇总 =====';
SELECT * FROM dbo.vw_DailySales ORDER BY sale_date DESC;

-- 6.13 查询用户完整档案（包含默认地址）
PRINT '===== 用户完整档案 =====';
SELECT * FROM dbo.vw_UserFullProfile ORDER BY user_id;

-- 6.14 存储过程演示：查询特定用户的购物车统计
PRINT '===== Alice 的购物车统计 =====';
EXEC dbo.sp_GetCart @user_id = 1;

-- 6.15 存储过程演示：查询特定用户的订单（支持状态过滤）
PRINT '===== Charlie 的所有订单 =====';
EXEC dbo.sp_GetUserOrders @user_id = 3, @status_filter = NULL;

-- 6.16 存储过程演示：库存预警
PRINT '===== 库存预警（所有低库存/缺货商品） =====';
EXEC dbo.sp_InventoryAlert @low_threshold = 10, @zero_stock_only = 0;

-- 6.17 业务演示：订单与支付的对应关系
PRINT '===== 订单与支付对应关系 =====';
SELECT 
    o.order_id,
    o.user_id,
    u.username,
    o.order_status,
    o.total_amount,
    p.payment_id,
    p.payment_method,
    p.payment_status,
    p.payment_amount
FROM dbo.[Order] o
INNER JOIN dbo.[User] u ON o.user_id = u.user_id
LEFT JOIN dbo.Payment p ON o.order_id = p.order_id
ORDER BY o.order_id DESC;

-- 6.18 业务演示：订单明细聚合统计
PRINT '===== 订单明细聚合统计 =====';
SELECT 
    o.order_id,
    u.username,
    COUNT(oi.item_id) AS item_count,
    SUM(oi.order_quantity) AS total_quantity,
    SUM(oi.subtotal) AS total_subtotal,
    o.total_amount
FROM dbo.[Order] o
INNER JOIN dbo.[User] u ON o.user_id = u.user_id
LEFT JOIN dbo.OrderItem oi ON o.order_id = oi.order_id
GROUP BY o.order_id, u.username, o.total_amount
ORDER BY o.order_id DESC;

-- 6.19 业务演示：特定地址的订单历史
PRINT '===== 地址 1001 的订单历史 =====';
SELECT 
    o.order_id,
    u.username,
    a.receiver_name,
    o.create_time,
    o.order_status,
    o.total_amount
FROM dbo.[Order] o
INNER JOIN dbo.[User] u ON o.user_id = u.user_id
INNER JOIN dbo.Address a ON o.address_id = a.address_id
WHERE o.address_id = 1001
ORDER BY o.create_time DESC;

-- 6.20 数据完整性检查：确认所有订单都有明细
PRINT '===== 数据完整性检查：无明细的订单 =====';
SELECT o.order_id, u.username
FROM dbo.[Order] o
INNER JOIN dbo.[User] u ON o.user_id = u.user_id
WHERE NOT EXISTS (SELECT 1 FROM dbo.OrderItem oi WHERE oi.order_id = o.order_id);
GO
