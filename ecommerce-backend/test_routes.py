from main import app

# 打印所有注册的路由
print("所有注册的路由:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"路径: {route.path}, 方法: {[method.upper() for method in route.methods] if hasattr(route, 'methods') else 'N/A'}")
