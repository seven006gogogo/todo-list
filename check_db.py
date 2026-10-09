import sqlite3
import os

# 要检查的两个数据库文件
files_to_check = [
    r'C:\Users\Lenovo\Desktop\todo-list\todo.db.legacy-root',
    r'C:\Users\Lenovo\Desktop\todo-list\TODO-web\todo.db',
]

for path in files_to_check:
    print("=" * 60)
    print(f"检查文件: {path}")
    if not os.path.exists(path):
        print("  ❌ 文件不存在")
        continue

    try:
        conn = sqlite3.connect(path)
        c = conn.cursor()

        # 列出所有表
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]
        print(f"  找到的表: {tables}")

        # 查看用户
        if 'users' in tables:
            c.execute("SELECT id, username FROM users")
            users = c.fetchall()
            print(f"  👤 用户数: {len(users)}")
            for uid, uname in users:
                print(f"     - ID={uid}, 用户名={uname}")
        else:
            print("  ⚠️ 没有 users 表")

        # 查看任务数
        if 'tasks' in tables:
            c.execute("SELECT COUNT(*) FROM tasks")
            count = c.fetchone()[0]
            print(f"  📝 任务数: {count}")

        conn.close()
    except Exception as e:
        print(f"  ❌ 出错: {e}")

print("=" * 60)
print("检查完成")
input("按回车键退出...")