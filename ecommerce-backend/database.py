import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        
    def get_connection(self):
        '''获取数据库连接（Windows身份验证）'''
        if self.conn is None:
            try:
                # Windows身份验证的连接字符串
                server = os.getenv("DB_SERVER", ".")
                database = os.getenv("DB_NAME", "权限实验")
                
                # 使用Windows身份验证
                connection_string = f"""
                    DRIVER={{ODBC Driver 17 for SQL Server}};
                    SERVER={server};
                    DATABASE={database};
                    Trusted_Connection=yes;
                """
                
                self.conn = pyodbc.connect(connection_string, autocommit=True)
                print(f"数据库连接成功: {server}/{database}")
            except Exception as e:
                print(f"数据库连接失败: {e}")
                raise
        return self.conn
    
    def close(self):
        '''关闭数据库连接'''
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")
            self.conn = None
    
    def execute_proc(self, proc_name, params=None):
        '''执行存储过程'''
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 构建参数占位符
            if params:
                placeholders = ",".join(["?"] * len(params))
                sql = f"{{CALL {proc_name} ({placeholders})}}"
                cursor.execute(sql, params)
            else:
                sql = f"{{CALL {proc_name}}}"
                cursor.execute(sql)
            
            # 获取结果
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            return []
        except Exception as e:
            print(f"执行存储过程失败: {e}")
            raise e
        finally:
            cursor.close()
    
    def execute_query(self, sql, params=None):
        '''执行查询'''
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            return []
        except Exception as e:
            print(f"查询失败: {e}")
            raise e
        finally:
            cursor.close()
    
    def fetch_one(self, sql, params=None):
        '''执行查询并返回第一条记录'''
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    return dict(zip(columns, row))
            return None
        except Exception as e:
            print(f"查询失败: {e}")
            raise e
        finally:
            cursor.close()
    
    def execute_update(self, sql, params=None):
        '''执行更新'''
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            return cursor.rowcount
        except Exception as e:
            print(f"更新失败: {e}")
            raise e
        finally:
            cursor.close()

# 全局数据库实例
db = Database()