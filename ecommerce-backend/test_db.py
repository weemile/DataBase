from database import db

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
