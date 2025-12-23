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
-- 第 4 部分：验证查询（只读）
-- =========================================

-- 4.1 某用户购物车明细（Bob）
SELECT * FROM dbo.vw_CartDetails WHERE username = 'bob';

-- 4.2 订单全量信息示例（Alice 已完成订单）
SELECT o.order_id, o.order_status, o.create_time, o.pay_time, o.ship_time, o.total_amount,
       oi.item_id, oi.product_id, oi.order_quantity, oi.unit_price, oi.subtotal,
       p.payment_id, p.payment_method, p.payment_amount, p.payment_status, p.payment_time
FROM dbo.[Order] o
LEFT JOIN dbo.OrderItem oi ON o.order_id = oi.order_id
LEFT JOIN dbo.Payment p    ON o.order_id = p.order_id
WHERE o.order_id = 7001;

-- 4.3 热销商品 / 分类销量示例视图
SELECT TOP 10 * FROM dbo.vw_TopSellingProducts ORDER BY sales_rank;

-- 4.4 用户订单统计
SELECT * FROM dbo.vw_UserOrderStatistics;

-- 4.5 当前有效促销商品
SELECT * FROM dbo.vw_PromotionProducts;

-- 4.6 日销售汇总
SELECT * FROM dbo.vw_DailySales ORDER BY sale_date DESC;

-- 4.7 库存状态
SELECT * FROM dbo.vw_InventoryStatus;

-- =========================================
-- 第 5 部分：收尾（恢复触发器）
-- =========================================
IF EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'trg_PreventAfterHoursChanges')
    ENABLE TRIGGER trg_PreventAfterHoursChanges ON dbo.[User];
GO-- =========================================
-- data.sql 演示数据与查询脚本
-- 依赖已执行的 schema + 触发器 + 视图
-- =========================================

-- =========================================
-- 1. 演示用基础数据补充
-- =========================================

-- 1.1 新增 demo 用户
IF NOT EXISTS (SELECT 1 FROM dbo.[User] WHERE username = 'demo_alice')
BEGIN
    INSERT INTO dbo.[User](username, password, phone, email, register_time, user_type, last_login_time, avatar_url)
    VALUES ('demo_alice', 'demo123', '13800000001', 'demo_alice@example.com', GETDATE(), 0, GETDATE(), NULL);
END
IF NOT EXISTS (SELECT 1 FROM dbo.[User] WHERE username = 'demo_bob')
BEGIN
    INSERT INTO dbo.[User](username, password, phone, email, register_time, user_type, last_login_time, avatar_url)
    VALUES ('demo_bob', 'demo123', '13800000002', 'demo_bob@example.com', GETDATE(), 0, GETDATE(), NULL);
END
IF NOT EXISTS (SELECT 1 FROM dbo.[User] WHERE username = 'demo_charlie')
BEGIN
    INSERT INTO dbo.[User](username, password, phone, email, register_time, user_type, last_login_time, avatar_url)
    VALUES ('demo_charlie', 'demo123', '13800000003', 'demo_charlie@example.com', GETDATE(), 0, GETDATE(), NULL);
END

-- 1.2 为 demo 用户新增地址（各 1 条默认）
DECLARE @uid_alice INT = (SELECT user_id FROM dbo.[User] WHERE username = 'demo_alice');
DECLARE @uid_bob   INT = (SELECT user_id FROM dbo.[User] WHERE username = 'demo_bob');
DECLARE @uid_char  INT = (SELECT user_id FROM dbo.[User] WHERE username = 'demo_charlie');

IF NOT EXISTS (SELECT 1 FROM Address WHERE user_id = @uid_alice AND is_default = 1)
BEGIN
    INSERT INTO Address(user_id, receiver_name, receiver_phone, province, city, district, detail_address, postal_code, is_default, create_time)
    VALUES (@uid_alice, N'爱丽丝', '13800000001', N'北京市', N'北京市', N'朝阳区', N'望京SOHO T1 1001', '100000', 1, GETDATE());
END
IF NOT EXISTS (SELECT 1 FROM Address WHERE user_id = @uid_bob AND is_default = 1)
BEGIN
    INSERT INTO Address(user_id, receiver_name, receiver_phone, province, city, district, detail_address, postal_code, is_default, create_time)
    VALUES (@uid_bob, N'鲍勃', '13800000002', N'上海市', N'上海市', N'浦东新区', N'张江高科 8 号楼', '200000', 1, GETDATE());
END
IF NOT EXISTS (SELECT 1 FROM Address WHERE user_id = @uid_char AND is_default = 1)
BEGIN
    INSERT INTO Address(user_id, receiver_name, receiver_phone, province, city, district, detail_address, postal_code, is_default, create_time)
    VALUES (@uid_char, N'查理', '13800000003', N'广东省', N'深圳市', N'南山区', N'科兴科学园 A3-2101', '518000', 1, GETDATE());
END

-- 1.3 新增 demo 商品（含缺货、低库存、促销商品）
DECLARE @cat_phone INT = (SELECT TOP 1 category_id FROM Category WHERE category_name LIKE N'%手机%' OR category_name LIKE N'%电子%' ORDER BY category_id);
DECLARE @cat_laptop INT = (SELECT TOP 1 category_id FROM Category WHERE category_name LIKE N'%电脑%' OR category_name LIKE N'%电子%' ORDER BY category_id);
DECLARE @cat_audio INT = (SELECT TOP 1 category_id FROM Category WHERE category_name LIKE N'%电子%' ORDER BY category_id);

IF NOT EXISTS (SELECT 1 FROM Product WHERE product_name = 'Demo 手机 A')
BEGIN
    INSERT INTO Product(category_id, product_name, product_code, description, price, cost_price, stock_quantity, sold_quantity, image_url, product_status, create_time, weight, brand, model)
    VALUES (ISNULL(@cat_phone,1), 'Demo 手机 A', 'DEMO-PHONE-A', N'演示用缺货商品', 1999.00, 1200.00, 0, 0, 'demo_phone_a.jpg', 1, GETDATE(), 0.20, 'DemoBrand', 'A1');
END
IF NOT EXISTS (SELECT 1 FROM Product WHERE product_name = 'Demo 笔记本 B')
BEGIN
    INSERT INTO Product(category_id, product_name, product_code, description, price, cost_price, stock_quantity, sold_quantity, image_url, product_status, create_time, weight, brand, model)
    VALUES (ISNULL(@cat_laptop,1), 'Demo 笔记本 B', 'DEMO-LAP-B', N'演示用低库存商品', 5999.00, 4000.00, 2, 0, 'demo_laptop_b.jpg', 1, GETDATE(), 1.20, 'DemoBrand', 'B1');
END
IF NOT EXISTS (SELECT 1 FROM Product WHERE product_name = 'Demo 耳机 C')
BEGIN
    INSERT INTO Product(category_id, product_name, product_code, description, price, cost_price, stock_quantity, sold_quantity, image_url, product_status, create_time, weight, brand, model)
    VALUES (ISNULL(@cat_audio,1), 'Demo 耳机 C', 'DEMO-AUDIO-C', N'演示用常规库存商品', 299.00, 120.00, 20, 0, 'demo_headset_c.jpg', 1, GETDATE(), 0.10, 'DemoBrand', 'C1');
END

DECLARE @pid_phone INT = (SELECT product_id FROM Product WHERE product_name = 'Demo 手机 A');
DECLARE @pid_laptop INT = (SELECT product_id FROM Product WHERE product_name = 'Demo 笔记本 B');
DECLARE @pid_audio INT = (SELECT product_id FROM Product WHERE product_name = 'Demo 耳机 C');

-- 1.4 新增一个当前有效促销，关联低库存商品
IF NOT EXISTS (SELECT 1 FROM Promotion WHERE promotion_name = N'Demo 限时 9 折')
BEGIN
    INSERT INTO Promotion(promotion_name, promotion_type, start_time, end_time, discount_type, discount_value, min_order_amount, max_discount_amount, usage_limit, promotion_status, promotion_description, create_time)
    VALUES (N'Demo 限时 9 折', 2, DATEADD(DAY,-1,GETDATE()), DATEADD(DAY,7,GETDATE()), 1, 10.0, NULL, NULL, NULL, 1, N'演示用 9 折促销', GETDATE());
END
DECLARE @promo_id INT = (SELECT promotion_id FROM Promotion WHERE promotion_name = N'Demo 限时 9 折');

IF NOT EXISTS (SELECT 1 FROM Product_Promotion WHERE product_id = @pid_laptop AND promotion_id = @promo_id)
BEGIN
    INSERT INTO Product_Promotion(product_id, promotion_id, create_time)
    VALUES (@pid_laptop, @promo_id, GETDATE());
END

-- =========================================
-- 2. 演示用“业务场景”数据（A/B/C 三条故事线）
-- =========================================

-- 场景 A：demo_alice 成功下单 -> 支付成功 -> 已完成 + 评价 + 收藏
DECLARE @addr_alice INT = (SELECT TOP 1 address_id FROM Address WHERE user_id = @uid_alice ORDER BY address_id);
IF NOT EXISTS (SELECT 1 FROM [Order] WHERE order_no = 'DEMO-ORDER-001')
BEGIN
    INSERT INTO [Order](order_no, user_id, address_id, total_amount, discount_amount, shipping_fee, final_amount, payment_method, order_status, create_time, pay_time, ship_time, receive_time, remark)
    VALUES ('DEMO-ORDER-001', @uid_alice, @addr_alice, 0, 0, 0, 0, '微信支付', 3,
            DATEADD(DAY,-5,GETDATE()), DATEADD(DAY,-5,GETDATE()), DATEADD(DAY,-4,GETDATE()), DATEADD(DAY,-3,GETDATE()),
            N'demo_alice 已完成订单');
END
DECLARE @oid_a INT = (SELECT order_id FROM [Order] WHERE order_no = 'DEMO-ORDER-001');

-- 订单明细（2 件商品）
IF NOT EXISTS (SELECT 1 FROM OrderItem WHERE order_id = @oid_a AND product_id = @pid_laptop)
BEGIN
    INSERT INTO OrderItem(order_id, product_id, product_name, product_image, unit_price, quantity, subtotal, discount_amount, final_price, create_time)
    VALUES (@oid_a, @pid_laptop, 'Demo 笔记本 B', 'demo_laptop_b.jpg', 5999.00, 1, 5999.00, 0, 5999.00, DATEADD(DAY,-5,GETDATE()));
END
IF NOT EXISTS (SELECT 1 FROM OrderItem WHERE order_id = @oid_a AND product_id = @pid_audio)
BEGIN
    INSERT INTO OrderItem(order_id, product_id, product_name, product_image, unit_price, quantity, subtotal, discount_amount, final_price, create_time)
    VALUES (@oid_a, @pid_audio, 'Demo 耳机 C', 'demo_headset_c.jpg', 299.00, 1, 299.00, 0, 299.00, DATEADD(DAY,-5,GETDATE()));
END

-- 支付成功
IF NOT EXISTS (SELECT 1 FROM Payment WHERE payment_no = 'DEMO-PAY-001')
BEGIN
    INSERT INTO Payment(order_id, payment_no, payment_method, payment_amount, payment_status, payment_time, transaction_id, payer_account, receiver_account)
    VALUES (@oid_a, 'DEMO-PAY-001', '微信支付', 6298.00, 1, DATEADD(DAY,-5,GETDATE()), 'TXN-DEMO-001', 'wx_alice', 'MERCHANT-DEMO');
END

-- 审计日志（手工补一条完成状态）
IF NOT EXISTS (SELECT 1 FROM OrderStatusAudit WHERE order_id = @oid_a AND new_status = 3)
BEGIN
    INSERT INTO OrderStatusAudit(order_id, old_status, new_status, changed_at, changed_by, note)
    VALUES (@oid_a, 2, 3, DATEADD(DAY,-3,GETDATE()), 'system', N'演示：订单完成');
END

-- 评价与收藏
IF NOT EXISTS (SELECT 1 FROM Review WHERE order_item_id IN (SELECT TOP 1 item_id FROM OrderItem WHERE order_id = @oid_a))
BEGIN
    DECLARE @item_audio INT = (SELECT TOP 1 item_id FROM OrderItem WHERE order_id = @oid_a AND product_id = @pid_audio);
    INSERT INTO Review(order_item_id, user_id, product_id, rating, content, is_anonymous, review_status, create_time)
    VALUES (@item_audio, @uid_alice, @pid_audio, 5, N'音质不错，性价比高', 0, 1, GETDATE());
END
IF NOT EXISTS (SELECT 1 FROM Favorite WHERE user_id = @uid_alice AND product_id = @pid_laptop)
BEGIN
    INSERT INTO Favorite(user_id, product_id, create_time) VALUES (@uid_alice, @pid_laptop, GETDATE());
END

-- 场景 B：demo_bob 未支付 / 已取消订单 + 购物车保留
DECLARE @addr_bob INT = (SELECT TOP 1 address_id FROM Address WHERE user_id = @uid_bob ORDER BY address_id);
IF NOT EXISTS (SELECT 1 FROM [Order] WHERE order_no = 'DEMO-ORDER-002')
BEGIN
    INSERT INTO [Order](order_no, user_id, address_id, total_amount, discount_amount, shipping_fee, final_amount, payment_method, order_status, create_time, remark)
    VALUES ('DEMO-ORDER-002', @uid_bob, @addr_bob, 1999.00, 0, 0, 1999.00, NULL, 0, DATEADD(DAY,-2,GETDATE()), N'demo_bob 待支付订单');
END
IF NOT EXISTS (SELECT 1 FROM [Order] WHERE order_no = 'DEMO-ORDER-003')
BEGIN
    INSERT INTO [Order](order_no, user_id, address_id, total_amount, discount_amount, shipping_fee, final_amount, payment_method, order_status, create_time, cancel_time, cancel_reason, remark)
    VALUES ('DEMO-ORDER-003', @uid_bob, @addr_bob, 299.00, 0, 0, 299.00, NULL, 4, DATEADD(DAY,-1,GETDATE()), DATEADD(DAY,-1,GETDATE()), N'用户取消', N'demo_bob 已取消订单');
END
DECLARE @oid_b_pending INT = (SELECT order_id FROM [Order] WHERE order_no = 'DEMO-ORDER-002');
DECLARE @oid_b_cancel  INT = (SELECT order_id FROM [Order] WHERE order_no = 'DEMO-ORDER-003');

-- 订单明细（待支付/已取消）
IF NOT EXISTS (SELECT 1 FROM OrderItem WHERE order_id = @oid_b_pending)
BEGIN
    INSERT INTO OrderItem(order_id, product_id, product_name, product_image, unit_price, quantity, subtotal, discount_amount, final_price, create_time)
    VALUES (@oid_b_pending, @pid_phone, 'Demo 手机 A', 'demo_phone_a.jpg', 1999.00, 1, 1999.00, 0, 1999.00, DATEADD(DAY,-2,GETDATE()));
END
IF NOT EXISTS (SELECT 1 FROM OrderItem WHERE order_id = @oid_b_cancel)
BEGIN
    INSERT INTO OrderItem(order_id, product_id, product_name, product_image, unit_price, quantity, subtotal, discount_amount, final_price, create_time)
    VALUES (@oid_b_cancel, @pid_audio, 'Demo 耳机 C', 'demo_headset_c.jpg', 299.00, 1, 299.00, 0, 299.00, DATEADD(DAY,-1,GETDATE()));
END

-- 支付失败记录
IF NOT EXISTS (SELECT 1 FROM Payment WHERE payment_no = 'DEMO-PAY-FAIL-002')
BEGIN
    INSERT INTO Payment(order_id, payment_no, payment_method, payment_amount, payment_status, payment_time, transaction_id, payer_account, receiver_account)
    VALUES (@oid_b_pending, 'DEMO-PAY-FAIL-002', '银行卡', 1999.00, 2, DATEADD(DAY,-2,GETDATE()), 'TXN-FAIL-002', '6222****0002', 'MERCHANT-DEMO');
END

-- 购物车保留
IF NOT EXISTS (SELECT 1 FROM Cart WHERE user_id = @uid_bob AND product_id = @pid_audio)
BEGIN
    INSERT INTO Cart(user_id, product_id, quantity, selected, create_time) VALUES (@uid_bob, @pid_audio, 2, 1, GETDATE());
END
IF NOT EXISTS (SELECT 1 FROM Cart WHERE user_id = @uid_bob AND product_id = @pid_laptop)
BEGIN
    INSERT INTO Cart(user_id, product_id, quantity, selected, create_time) VALUES (@uid_bob, @pid_laptop, 1, 1, GETDATE());
END

-- 场景 C：demo_charlie 促销 + 日销量 + 库存边界
DECLARE @addr_char INT = (SELECT TOP 1 address_id FROM Address WHERE user_id = @uid_char ORDER BY address_id);
IF NOT EXISTS (SELECT 1 FROM [Order] WHERE order_no = 'DEMO-ORDER-004')
BEGIN
    INSERT INTO [Order](order_no, user_id, address_id, total_amount, discount_amount, shipping_fee, final_amount, payment_method, order_status, create_time, pay_time, ship_time, remark)
    VALUES ('DEMO-ORDER-004', @uid_char, @addr_char, 5999.00, 0, 0, 5999.00, '支付宝', 2,
            DATEADD(DAY,-3,GETDATE()), DATEADD(DAY,-3,GETDATE()), DATEADD(DAY,-2,GETDATE()), N'demo_charlie 发货中');
END
IF NOT EXISTS (SELECT 1 FROM [Order] WHERE order_no = 'DEMO-ORDER-005')
BEGIN
    INSERT INTO [Order](order_no, user_id, address_id, total_amount, discount_amount, shipping_fee, final_amount, payment_method, order_status, create_time, pay_time, receive_time, remark)
    VALUES ('DEMO-ORDER-005', @uid_char, @addr_char, 299.00, 0, 0, 299.00, '微信支付', 3,
            DATEADD(DAY,-2,GETDATE()), DATEADD(DAY,-2,GETDATE()), DATEADD(DAY,-1,GETDATE()), N'demo_charlie 完成订单');
END
DECLARE @oid_c_ship INT = (SELECT order_id FROM [Order] WHERE order_no = 'DEMO-ORDER-004');
DECLARE @oid_c_done INT = (SELECT order_id FROM [Order] WHERE order_no = 'DEMO-ORDER-005');

IF NOT EXISTS (SELECT 1 FROM OrderItem WHERE order_id = @oid_c_ship)
BEGIN
    INSERT INTO OrderItem(order_id, product_id, product_name, product_image, unit_price, quantity, subtotal, discount_amount, final_price, create_time)
    VALUES (@oid_c_ship, @pid_laptop, 'Demo 笔记本 B', 'demo_laptop_b.jpg', 5999.00, 1, 5999.00, 0, 5999.00, DATEADD(DAY,-3,GETDATE()));
END
IF NOT EXISTS (SELECT 1 FROM OrderItem WHERE order_id = @oid_c_done)
BEGIN
    INSERT INTO OrderItem(order_id, product_id, product_name, product_image, unit_price, quantity, subtotal, discount_amount, final_price, create_time)
    VALUES (@oid_c_done, @pid_audio, 'Demo 耳机 C', 'demo_headset_c.jpg', 299.00, 1, 299.00, 0, 299.00, DATEADD(DAY,-2,GETDATE()));
END

-- 支付成功记录（发货中 / 已完成）
IF NOT EXISTS (SELECT 1 FROM Payment WHERE payment_no = 'DEMO-PAY-004')
BEGIN
    INSERT INTO Payment(order_id, payment_no, payment_method, payment_amount, payment_status, payment_time, transaction_id, payer_account, receiver_account)
    VALUES (@oid_c_ship, 'DEMO-PAY-004', '支付宝', 5999.00, 1, DATEADD(DAY,-3,GETDATE()), 'TXN-DEMO-004', 'ali_charlie', 'MERCHANT-DEMO');
END
IF NOT EXISTS (SELECT 1 FROM Payment WHERE payment_no = 'DEMO-PAY-005')
BEGIN
    INSERT INTO Payment(order_id, payment_no, payment_method, payment_amount, payment_status, payment_time, transaction_id, payer_account, receiver_account)
    VALUES (@oid_c_done, 'DEMO-PAY-005', '微信支付', 299.00, 1, DATEADD(DAY,-2,GETDATE()), 'TXN-DEMO-005', 'wx_charlie', 'MERCHANT-DEMO');
END

-- 评价（完成订单）
IF NOT EXISTS (SELECT 1 FROM Review WHERE order_item_id IN (SELECT item_id FROM OrderItem WHERE order_id = @oid_c_done))
BEGIN
    DECLARE @item_c_done INT = (SELECT TOP 1 item_id FROM OrderItem WHERE order_id = @oid_c_done);
    INSERT INTO Review(order_item_id, user_id, product_id, rating, content, is_anonymous, review_status, create_time)
    VALUES (@item_c_done, @uid_char, @pid_audio, 4, N'音质不错，发货快', 1, 1, GETDATE());
END

-- 收藏
IF NOT EXISTS (SELECT 1 FROM Favorite WHERE user_id = @uid_char AND product_id = @pid_laptop)
BEGIN
    INSERT INTO Favorite(user_id, product_id, create_time) VALUES (@uid_char, @pid_laptop, GETDATE());
END

-- 更新库存边界（保持缺货/低库存示例）
UPDATE Product SET stock_quantity = 0  WHERE product_id = @pid_phone;  -- 缺货
UPDATE Product SET stock_quantity = 2  WHERE product_id = @pid_laptop; -- 低库存预警
UPDATE Product SET stock_quantity = 20 WHERE product_id = @pid_audio;  -- 正常库存

-- 重新汇总订单金额（保证演示一致性）
UPDATE o
SET o.total_amount  = s.total_sum,
    o.final_amount  = s.total_sum + o.shipping_fee,
    o.discount_amount = ISNULL(o.discount_amount, 0)
FROM [Order] o
JOIN (SELECT order_id, SUM(final_price) AS total_sum FROM OrderItem GROUP BY order_id) s
  ON o.order_id = s.order_id
WHERE o.order_no LIKE 'DEMO-ORDER-%';

-- =========================================
-- 3. 演示查询脚本（只读）
-- =========================================

-- 基础信息：所有 demo 用户
SELECT * FROM dbo.[User] WHERE username LIKE 'demo_%';

-- demo 用户的地址列表，标记默认地址
SELECT a.*, u.username
FROM Address a
JOIN dbo.[User] u ON a.user_id = u.user_id
WHERE u.username LIKE 'demo_%'
ORDER BY u.username, a.is_default DESC, a.address_id;

-- 业务流程：demo_alice 订单列表（多状态示例）
SELECT o.order_no, o.order_status, o.create_time, o.pay_time, o.ship_time, o.receive_time, o.cancel_time, o.final_amount
FROM [Order] o
JOIN dbo.[User] u ON o.user_id = u.user_id
WHERE u.username = 'demo_alice'
ORDER BY o.create_time DESC;

-- 业务流程：查看某订单的完整明细（以 DEMO-ORDER-001 为例）
SELECT o.order_no, oi.product_name, oi.quantity, oi.unit_price, oi.final_price, o.final_amount
FROM OrderItem oi
JOIN [Order] o ON oi.order_id = o.order_id
WHERE o.order_no = 'DEMO-ORDER-001';

-- 支付记录：demo 用户的支付成功/失败
SELECT u.username, o.order_no, p.payment_no, p.payment_method, p.payment_status, p.payment_amount, p.payment_time
FROM Payment p
JOIN [Order] o ON p.order_id = o.order_id
JOIN dbo.[User] u ON o.user_id = u.user_id
WHERE u.username LIKE 'demo_%'
ORDER BY p.payment_time DESC;

-- 视图演示：订单汇总（demo 用户）
SELECT * FROM vw_OrderSummary WHERE username LIKE 'demo_%';

-- 视图演示：商品库存与预警
SELECT * FROM vw_ProductInventoryStats ORDER BY inventory_alert DESC, product_id;

-- 视图演示：用户概览（demo 用户）
SELECT * FROM vw_UserOverview WHERE username LIKE 'demo_%';

-- 视图演示：当前有效促销商品
SELECT * FROM vw_ActivePromotionProducts;

-- 视图演示：日销量汇总（按日期降序）
SELECT * FROM vw_DailySalesSummary ORDER BY sales_date DESC;

-- 边界查询：缺货商品
SELECT product_id, product_name, stock_quantity FROM Product WHERE stock_quantity = 0;

-- 边界查询：低库存商品（<=5）
SELECT product_id, product_name, stock_quantity FROM Product WHERE stock_quantity BETWEEN 1 AND 5;

-- 边界查询：最近 7 天被取消的 demo 订单
SELECT o.order_no, o.cancel_time, o.cancel_reason
FROM [Order] o
JOIN dbo.[User] u ON o.user_id = u.user_id
WHERE u.username LIKE 'demo_%' AND o.order_status = 4 AND o.cancel_time >= DATEADD(DAY,-7,GETDATE());

-- 评价列表：demo 用户
SELECT u.username, r.rating, r.content, r.create_time, p.product_name
FROM Review r
JOIN dbo.[User] u ON r.user_id = u.user_id
JOIN Product p ON r.product_id = p.product_id
WHERE u.username LIKE 'demo_%'
ORDER BY r.create_time DESC;

-- 收藏列表：demo 用户
SELECT u.username, f.product_id, p.product_name, f.create_time
FROM Favorite f
JOIN dbo.[User] u ON f.user_id = u.user_id
JOIN Product p ON f.product_id = p.product_id
WHERE u.username LIKE 'demo_%'
ORDER BY u.username, f.create_time DESC;
