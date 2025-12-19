from database import db

try:
    # 简单测试 - 查询版本
    result = db.execute_query("SELECT @@VERSION as version")
    print("数据库连接成功！")
    print(f"SQL Server版本: {result[0]['version'][:100]}...")
    
    # 测试用户表
    users = db.execute_query("SELECT TOP 2 user_id, username, email FROM [User]")
    print(f"\\n找到 {len(users)} 个用户:")
    for user in users:
        print(f"  ID:{user['user_id']} 用户名:{user['username']} 邮箱:{user['email']}")
    
    # 测试存储过程（如果有）
    try:
        # 测试一个简单的存储过程
        result = db.execute_query("EXEC sp_help 'User'")
        print("\\n存储过程测试成功")
    except:
        print("\\n存储过程测试跳过")
        
except Exception as e:
    print(f"错误: {e}")
finally:
    db.close()