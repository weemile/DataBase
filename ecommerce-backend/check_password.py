# check_passwords.py
from database import db

try:
    # 查询所有用户的密码（查看前几个字符即可）
    users = db.execute_query("SELECT TOP 5 user_id, username, LEFT(password, 20) as password_prefix FROM [User]")
    
    print("用户密码检查结果：")
    print("-" * 50)
    for user in users:
        pw = user["password_prefix"]
        # 判断密码类型
        if pw.startswith("$2b$"):
            pw_type = "BCRYPT哈希"
        elif pw.startswith("$2a$"):
            pw_type = "BCRYPT哈希(旧版)"
        elif len(pw) <= 20 and pw.isprintable():
            pw_type = "很可能为明文"
        else:
            pw_type = "未知格式"
        
        print(f"用户ID: {user['user_id']}")
        print(f"用户名: {user['username']}")
        print(f"密码前缀: {pw}")
        print(f"类型: {pw_type}")
        print("-" * 30)
    
    print("\n✅ 如果显示'很可能为明文'，说明是明文密码")
    print("✅ 如果显示'BCRYPT哈希'，说明是哈希密码")
    
except Exception as e:
    print(f"检查失败: {e}")
finally:
    db.close()