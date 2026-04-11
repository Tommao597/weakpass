#!/usr/bin/env python3
"""
数据库基础框架测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db

def test_database_framework():
    """测试数据库基础框架"""
    print("=== 数据库基础框架测试 ===")
    
    # 测试数据库连接
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('tasks', 'dictionaries', 'results', 'reports')
            """)
            tables = cursor.fetchall()
            
            print(f"✅ 数据库连接成功")
            print(f"✅ 找到 {len(tables)} 个表: {[table['name'] for table in tables]}")
            
            # 测试插入任务数据
            cursor.execute("""
                INSERT INTO tasks (id, name, target, status) 
                VALUES (?, ?, ?, ?)
            """, ("test_task_001", "测试任务", "192.168.1.1", "completed"))
            conn.commit()
            
            # 测试查询任务数据
            cursor.execute("SELECT * FROM tasks WHERE id = ?", ("test_task_001",))
            task = cursor.fetchone()
            
            if task:
                print(f"✅ 数据插入和查询测试成功")
                print(f"   任务ID: {task['id']}")
                print(f"   任务名称: {task['name']}")
                print(f"   任务状态: {task['status']}")
            
            # 测试封装方法
            print("\n=== 测试数据库封装方法 ===")
            
            # 测试execute方法
            success = db.execute(
                "INSERT INTO tasks (id, name, target, status) VALUES (?, ?, ?, ?)",
                ("test_task_002", "方法测试任务", "192.168.1.2", "pending")
            )
            
            if success:
                print("✅ execute方法测试成功")
            else:
                print("❌ execute方法测试失败")
                return False
            
            # 测试fetch_one方法
            task = db.fetch_one("SELECT * FROM tasks WHERE id = ?", ("test_task_002",))
            if task:
                print("✅ fetch_one方法测试成功")
                print(f"   任务名称: {task['name']}")
            else:
                print("❌ fetch_one方法测试失败")
                return False
            
            # 测试fetch_all方法
            tasks = db.fetch_all("SELECT * FROM tasks")
            if tasks:
                print("✅ fetch_all方法测试成功")
                print(f"   总任务数: {len(tasks)}")
            else:
                print("❌ fetch_all方法测试失败")
                return False
            
            # 清理测试数据
            cursor.execute("DELETE FROM tasks WHERE id LIKE 'test_task_%'")
            conn.commit()
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    if test_database_framework():
        print("\n🎉 所有测试通过！数据库基础框架工作正常")
        print("\n📁 数据库文件位置: db/weakpass.db")
        print("📋 下一步: 可以开始为具体功能添加数据库支持了")
    else:
        print("\n💥 测试失败，请检查数据库配置")