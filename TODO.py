# 命令行TODO列表工具
# 功能：支持添加、列出、标记完成、删除任务和退出

tasks = []  # 存储任务列表，每个任务是一个字典

def show_menu():
    """显示菜单"""
    print("\n=== TODO列表 ===")
    print("命令格式:")
    print("  添加任务: add \"任务描述\"")
    print("  列出任务: list")
    print("  标记完成: complete 任务编号")
    print("  删除任务: delete 任务编号")
    print("  退出程序: quit")
    print("=================\n")

def add_task(description):
    """添加新任务"""
    if not description:
        print("错误: 任务描述不能为空")
        return
    
    task = {
        "id": len(tasks) + 1,  # 任务编号从1开始
        "description": description,
        "completed": False,
        "created_at": "刚刚"  # 简化版，实际可以存储时间戳
    }
    tasks.append(task)
    print(f"✓ 已添加任务: {description} (ID: {task['id']})")

def list_tasks():
    """列出所有任务"""
    if not tasks:
        print("当前没有任务")
        return
    
    print(f"任务列表 (共{len(tasks)}个):")
    print("-" * 40)
    
    for task in tasks:
        status = "✓" if task["completed"] else "□"
        print(f"{task['id']:3d}. [{status}] {task['description']}")
    
    # 显示统计信息
    completed_count = sum(1 for task in tasks if task["completed"])
    pending_count = len(tasks) - completed_count
    print("-" * 40)
    print(f"统计: 完成 {completed_count}个, 待办 {pending_count}个")

def complete_task(task_id):
    """标记任务为完成状态"""
    task = find_task_by_id(task_id)
    if task:
        if task["completed"]:
            print(f"任务 {task_id} 已经是完成状态")
        else:
            task["completed"] = True
            print(f"✓ 已标记任务 {task_id} 为完成: {task['description']}")
    else:
        print(f"错误: 找不到ID为 {task_id} 的任务")

def delete_task(task_id):
    """删除指定任务"""
    task = find_task_by_id(task_id)
    if task:
        description = task["description"]
        tasks.remove(task)
        # 重新编号剩余的任务
        for i, task in enumerate(tasks, 1):
            task["id"] = i
        print(f"✓ 已删除任务: {description}")
    else:
        print(f"错误: 找不到ID为 {task_id} 的任务")

def find_task_by_id(task_id):
    """根据ID查找任务"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

def handle_input(user_input):
    """处理用户输入"""
    parts = user_input.strip().split(" ", 1)
    command = parts[0].lower()
    
    if command == "add":
        if len(parts) < 2:
            print("错误: 请提供任务描述，例如: add \"买牛奶\"")
        else:
            # 移除可能的引号
            description = parts[1].strip('"\'')
            add_task(description)
    
    elif command == "list":
        list_tasks()
    
    elif command == "complete":
        if len(parts) < 2:
            print("错误: 请提供任务编号，例如: complete 1")
        else:
            try:
                task_id = int(parts[1])
                complete_task(task_id)
            except ValueError:
                print("错误: 任务编号必须是数字")
    
    elif command == "delete":
        if len(parts) < 2:
            print("错误: 请提供任务编号，例如: delete 1")
        else:
            try:
                task_id = int(parts[1])
                delete_task(task_id)
            except ValueError:
                print("错误: 任务编号必须是数字")
    
    elif command == "help":
        show_menu()
    
    elif command == "quit":
        print("再见！")
        return False
    
    else:
        print(f"未知命令: {command}")
        print("输入 'help' 查看可用命令")
    
    return True

def main():
    """主函数"""
    print("欢迎使用命令行TODO列表工具!")
    show_menu()
    
    # 添加一些示例任务
    example_tasks = ["学习Python", "写项目文档", "准备会议"]
    for task in example_tasks:
        add_task(task)
    print("已添加示例任务，输入 'list' 查看")
    
    # 主循环
    running = True
    while running:
        try:
            user_input = input("\n请输入命令: ").strip()
            if user_input:
                running = handle_input(user_input)
        except KeyboardInterrupt:
            print("\n\n检测到中断信号，正在退出...")
            break
        except EOFError:
            print("\n\n检测到文件结束，正在退出...")
            break
        except Exception as e:
            print(f"发生错误: {e}")

# 程序入口
if __name__ == "__main__":
    main()