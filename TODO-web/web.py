from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)


def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    # 创建用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # 创建任务表
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 在 Flask app 创建后调用一次
init_db()

@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务（从数据库读取）"""
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    # 先固定 user_id = 1，等登录功能做好后改成从session获取
    user_id = 1
    c.execute(
        "SELECT id, description, completed, created_at FROM tasks WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()

    tasks = []
    completed_count = 0
    for row in rows:
        task = {
            "id": row[0],
            "description": row[1],
            "completed": bool(row[2]),
            "created_at": row[3]
        }
        tasks.append(task)
        if task["completed"]:
            completed_count += 1

    return jsonify({
        "success": True,
        "tasks": tasks,
        "stats": {
            "total": len(tasks),
            "completed": completed_count,
            "pending": len(tasks) - completed_count
        }
    })


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """添加新任务（存入数据库）"""
    data = request.get_json()
    description = data.get('description', '').strip()

    if not description:
        return jsonify({"success": False, "error": "任务描述不能为空"}), 400

    user_id = 1  # 暂时固定，等登录功能做好后改成从session获取

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (user_id, description) VALUES (?, ?)",
        (user_id, description)
    )
    conn.commit()
    task_id = c.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "task": {
            "id": task_id,
            "description": description,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "message": f"✓ 已添加任务: {description}"
    })



@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除指定任务"""
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()

    # 先查询任务是否存在
    c.execute("SELECT description FROM tasks WHERE id = ?", (task_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "error": f"找不到ID为 {task_id} 的任务"}), 404

    description = row[0]
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"✓ 已删除任务: {description}"
    })

@app.route('/api/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    """切换任务的完成状态"""
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()

    # 先查询当前状态
    c.execute("SELECT completed, description FROM tasks WHERE id = ?", (task_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "error": f"找不到ID为 {task_id} 的任务"}), 404

    current_status = row[0]
    description = row[1]
    new_status = not current_status

    # 更新状态
    c.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

    status_text = "完成" if new_status else "未完成"
    return jsonify({
        "success": True,
        "message": f"✓ 任务 {task_id} 已标记为{status_text}"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
        task_counter += 1

    app.run(debug=True, port=5000)
