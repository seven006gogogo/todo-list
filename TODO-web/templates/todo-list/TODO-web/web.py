from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'todo.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
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

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
    
    # 密码加密
    hashed_password = generate_password_hash(password)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "注册成功，请登录"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "error": "用户名已存在"}), 400
  

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"success": False, "error": "用户名或密码错误"}), 401
    
    user_id = row[0]
    hashed_password = row[1]
    
    if not check_password_hash(hashed_password, password):
        return jsonify({"success": False, "error": "用户名或密码错误"}), 401
    
    # 生成 JWT token，有效期7天
    token = jwt.encode(
        {"user_id": user_id, "username": username, "exp": datetime.utcnow() + timedelta(days=7)},
        "seven006-secret-key",  # 生产环境请改用环境变量
        algorithm="HS256"
    )
    
    return jsonify({"success": True, "token": token, "username": username, "message": "登录成功"})





@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')

# 辅助函数
def get_user_from_token(request):
    """从请求头中获取token，返回user_id，验证失败返回None"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    # 去掉 'Bearer ' 前缀
    if token.startswith('Bearer '):
        token = token[7:]
    try:
        payload = jwt.decode(token, "seven006-secret-key", algorithms=["HS256"])
        return payload.get('user_id')
    except jwt.InvalidTokenError:
        return None


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取当前用户的所有任务"""
    user_id = get_user_from_token(request)
    if not user_id:
        return jsonify({"success": False, "error": "请先登录"}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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
    """添加新任务"""
    user_id = get_user_from_token(request)
    if not user_id:
        return jsonify({"success": False, "error": "请先登录"}), 401
    
    data = request.get_json()
    description = data.get('description', '').strip()
    
    if not description:
        return jsonify({"success": False, "error": "任务描述不能为空"}), 400
    
    conn = sqlite3.connect(DB_PATH)
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
    user_id = get_user_from_token(request)
    if not user_id:
        return jsonify({"success": False, "error": "请先登录"}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 先查询任务是否存在且属于当前用户
    c.execute("SELECT description FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
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
    user_id = get_user_from_token(request)
    if not user_id:
        return jsonify({"success": False, "error": "请先登录"}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 先查询任务是否存在且属于当前用户
    c.execute("SELECT completed, description FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"success": False, "error": f"找不到ID为 {task_id} 的任务"}), 404
    
    current_status = row[0]
    new_status = not current_status
    
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
