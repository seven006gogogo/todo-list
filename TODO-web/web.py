from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 存储任务列表，每个任务是一个字典
tasks = []
task_counter = 1  # 用于生成唯一ID


def reset_task_ids():
    """重置所有任务的ID，使其连续"""
    global task_counter
    for i, task in enumerate(tasks, 1):
        task["id"] = i
    task_counter = len(tasks) + 1 if tasks else 1


@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务"""
    return jsonify({
        "success": True,
        "tasks": tasks,
        "stats": {
            "total": len(tasks),
            "completed": sum(1 for task in tasks if task["completed"]),
            "pending": sum(1 for task in tasks if not task["completed"])
        }
    })


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """添加新任务"""
    data = request.get_json()
    description = data.get('description', '').strip()

    if not description:
        return jsonify({"success": False, "error": "任务描述不能为空"}), 400

    global task_counter
    task = {
        "id": task_counter,
        "description": description,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.append(task)
    task_counter += 1

    return jsonify({
        "success": True,
        "task": task,
        "message": f"✓ 已添加任务: {description}"
    })


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def complete_task(task_id):
    """标记任务为完成状态"""
    for task in tasks:
        if task["id"] == task_id:
            if task["completed"]:
                return jsonify({
                    "success": True,
                    "message": f"任务 {task_id} 已经是完成状态"
                })
            else:
                task["completed"] = True
                return jsonify({
                    "success": True,
                    "task": task,
                    "message": f"✓ 已标记任务 {task_id} 为完成: {task['description']}"
                })

    return jsonify({"success": False, "error": f"找不到ID为 {task_id} 的任务"}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除指定任务"""
    global task_counter
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            description = task["description"]
            tasks.pop(i)
            # 重新编号剩余的任务
            reset_task_ids()
            return jsonify({
                "success": True,
                "message": f"✓ 已删除任务: {description}"
            })

    return jsonify({"success": False, "error": f"找不到ID为 {task_id} 的任务"}), 404


@app.route('/api/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    """切换任务的完成状态"""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            status = "完成" if task["completed"] else "未完成"
            return jsonify({
                "success": True,
                "task": task,
                "message": f"✓ 任务 {task_id} 已标记为{status}"
            })

    return jsonify({"success": False, "error": f"找不到ID为 {task_id} 的任务"}), 404


if __name__ == '__main__':
    # 添加示例任务
    example_tasks = ["学习Python", "写项目文档", "准备会议"]
    for task_desc in example_tasks:
        task = {
            "id": task_counter,
            "description": task_desc,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks.append(task)
        task_counter += 1

    app.run(debug=True, port=5000)