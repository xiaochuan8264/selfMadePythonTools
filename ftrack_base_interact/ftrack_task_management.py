pip install ftrack-python-api


import os
import ftrack_api

FTRACK_SERVER= "https://ftrack.legoutech.cn"
FTRACK_API_USER= "tangyunchuan"
FTRACK_API_KEY= "ZDE2MDkzZTgtM2E3OS00YzQ4LTkxOGQtODA4MGM3ZmU0MDIyOjoyYzM2NDFjMy1lNGE3LTQ5YTItYWE0ZS1kMzUzMGU3Yzk4ZTE"

session = ftrack_api.Session(
    server_url=FTRACK_SERVER,
    api_key=FTRACK_API_KEY,
    api_user=FTRACK_API_USER
)

# session = ftrack_api.Session()
project_name = 'BeagleAssets'

project = session.query(
    f'Project where name is "{project_name}"'
).first()

print(f"找到项目: {project['name']}")

object_type = session.query(
    'ObjectType where name is "BeagleTask"'
).first()

# 下面是尝试先查询

# 所有任务查询
tasks = session.query(
    f'Task where project.name is "{project_name}"'
).all()

print(f"项目 '{project_name}' 中共有 {len(tasks)} 个任务")


# 尝试在BeagleAssets下创建任务：角色模板 20260128 以下创建任务代码已成功

def create_nested_structure_with_auto_populate_disabled(project_name, parent_name, structure_config):
    """禁用 auto_populate 来避免双向属性冲突"""
    
    # 禁用 session 的自动填充功能
    session.auto_populate = False
    
    try:
        # 查找父对象
        parent_object = session.query(
            f'TypedContext where name is "{parent_name}" and project.name is "{project_name}"'
        ).first()
        
        if not parent_object:
            raise ValueError(f"未找到父对象: {parent_name}")
        
        # 创建主对象
        main_object = session.create('Folder', {
            'name': structure_config['name'],
            'parent': parent_object
        })
        session.commit()
        print(f"创建主对象: {structure_config['name']}")
        
        # 创建直接任务
        if 'tasks' in structure_config:
            for task_name in structure_config['tasks']:
                session.create('Task', {
                    'name': task_name,
                    'parent': main_object
                })
                session.commit()
                print(f"  创建任务: {task_name}")
        
        # 创建子对象
        if 'children' in structure_config:
            for child_config in structure_config['children']:
                child_object = session.create('Folder', {
                    'name': child_config['name'],
                    'parent': main_object
                })
                session.commit()
                print(f"  创建子对象: {child_config['name']}")
                
                # 创建子对象下的任务
                if 'tasks' in child_config:
                    for task_name in child_config['tasks']:
                        session.create('Task', {
                            'name': task_name,
                            'parent': child_object
                        })
                        session.commit()
                        print(f"    创建任务: {task_name}")
        
        print("结构创建完成！")
        return main_object
        
    finally:
        # 恢复 auto_populate 设置
        session.auto_populate = True

# 执行
character_structure = {
    'name': 'rockturtle_lv1',
    'tasks': [
        '3DAnimation',
        '3DStaticAssets',
        '3DVfx',
        'Concept'
    ],
    'children': [
        {
            'name': 'inputAnimation',
            'tasks': ['inputAnimation']
        },
        {
            'name': 'inputTexture',
            'tasks': ['inputTexture']
        },
        {
            'name': 'model',
            'tasks': ['model']
        }
    ]
}

create_nested_structure_with_auto_populate_disabled(
    project_name='BeagleAssets',
    parent_name='beboo',
    structure_config=character_structure
)


# 以上创建任务代码已成功



# 下面尝试分配任务
# 以下任务分配代码也已经成功了，yes

def assign_users_to_task(task_id, usernames):
    """
    为任务分配一个或多个执行人
    
    Args:
        task_id: 任务ID
        usernames: 用户名列表，例如 ['user1', 'user2'] 或单个用户名 'user1'
    """
    # 如果传入的是单个用户名字符串，转换为列表
    if isinstance(usernames, str):
        usernames = [usernames]
    
    # 查询任务
    task = session.query(f'Task where id is "{task_id}"').first()
    
    if not task:
        raise ValueError(f"未找到任务 ID: {task_id}")
    
    print(f"为任务 '{task['name']}' 分配执行人...")
    
    # 为每个用户创建分配
    for username in usernames:
        # 查询用户
        user = session.query(f'User where username is "{username}"').first()
        
        if not user:
            print(f"  ✗ 用户 '{username}' 不存在，跳过")
            continue
        
        # 检查是否已经分配
        existing_assignment = session.query(
            f'Appointment where context_id is "{task_id}" '
            f'and resource_id is "{user["id"]}"'
        ).first()
        
        if existing_assignment:
            print(f"  - 用户 '{username}' 已被分配，跳过")
            continue
        
        # 创建分配（Appointment）
        session.create('Appointment', {
            'context': task,
            'resource': user,
            'type': 'assignment'  # 分配类型
        })
        
        print(f"  ✓ 成功分配用户: {username}")
    
    session.commit()
    print("所有分配完成！")

# 方法一：通过任务名称和父对象分配
def assign_users_by_task_name(project_name, parent_name, task_name, usernames):
    """
    通过任务名称为任务分配执行人
    
    Args:
        project_name: 项目名称
        parent_name: 父对象名称（如 'rockturtle_lv1'）
        task_name: 任务名称
        usernames: 用户名列表
    """
    # 查询父对象
    parent = session.query(
        f'TypedContext where name is "{parent_name}" '
        f'and project.name is "{project_name}"'
    ).first()
    
    if not parent:
        raise ValueError(f"未找到父对象: {parent_name}")
    
    # 查询任务
    task = session.query(
        f'Task where name is "{task_name}" '
        f'and parent.id is "{parent["id"]}"'
    ).first()
    
    if not task:
        raise ValueError(f"未找到任务: {task_name}")
    
    # 分配用户
    assign_users_to_task(task['id'], usernames)


def batch_assign_users(project_name, parent_name, task_assignments):
    """
    批量为多个任务分配执行人
    
    Args:
        project_name: 项目名称
        parent_name: 父对象名称
        task_assignments: 任务和执行人的映射字典
                         格式: {'任务名': ['用户1', '用户2'], ...}
    """
    for task_name, usernames in task_assignments.items():
        try:
            assign_users_by_task_name(
                project_name=project_name,
                parent_name=parent_name,
                task_name=task_name,
                usernames=usernames
            )
        except Exception as e:
            print(f"分配任务 '{task_name}' 时出错: {e}")
            continue

# 使用示例

# 示例1: 为单个任务分配多个执行人
assign_users_by_task_name(
    project_name='BeagleAssets',
    parent_name='rockturtle_lv1',
    task_name='3DAnimation',
    usernames=['john.doe', 'jane.smith', 'bob.lee']  # 多个执行人
)


# 使用示例：批量分配
task_assignments = {
    '3DAnimation': ['chencheng2', 'zounan', 'caolong', 'wangfeng','gengruiyang'],      # 5个执行人
    '3DStaticAssets': ['qinzhen', 'yixiang'],            # 2个执行人
    '3DVfx': ['he'],                              # 1个执行人
    'Concept': ['zhangjiashuai'],                   # 2个执行人
}

# 使用示例：批量分配
task_assignments = {
    '3DAnimation': ['chencheng2', 'caolong', 'wangfeng','gengruiyang']    # 4个执行人 
}

batch_assign_users(
    project_name='BeagleAssets',
    parent_name='rockturtle_lv1',
    task_assignments=task_assignments
)

# 以上单个资产，批量分配执行人代码成功了




# 下面是尝试读取多维表格了
app_id = "cli_a9ee46ebc8b81cee"
app_secret = "BHG0jHUSIRIARIEIvl6UleTOQ1AeJr3u"

app_token= "Qq3Ybd9ryaX3KQsvgNWcXXgAnMf"
table_id = "tblBA8Xy4jeVBbDU"


import requests
import json

# ========== 第一步：获取 access_token ==========
def get_tenant_access_token(app_id, app_secret):
    """获取应用访问凭证"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    
    payload = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    result = response.json()
    
    if result.get('code') == 0:
        return result['tenant_access_token']
    else:
        raise Exception(f"获取token失败: {result}")

# ========== 第二步：读取多维表格数据 ==========
def get_bitable_records(tenant_access_token, app_token, table_id, page_size=500):
    """查询多维表格记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant_access_token}'
    }
    
    payload = json.dumps({
        "page_size": page_size  # 每页最多500条
    })
    
    response = requests.post(url, headers=headers, data=payload)
    result = response.json()
    
    if result.get('code') == 0:
        return result['data']['items']
    else:
        raise Exception(f"读取数据失败: {result}")

# ========== 使用示例 ==========
if __name__ == '__main__':
    # 配置参数（请替换为实际值）
    APP_ID = 'your_app_id'
    APP_SECRET = 'your_app_secret'
    APP_TOKEN = 'your_app_token'
    TABLE_ID = 'your_table_id'
    
    # 获取token
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    print(f"Token: {token}")
    
    # 读取数据
    records = get_bitable_records(token, APP_TOKEN, TABLE_ID)
    
    # 处理数据
    for record in records:
        print(f"记录ID: {record['record_id']}")
        print(f"字段数据: {record['fields']}")
        print("-" * 50)


 # 以上代码已经可以成功读取多维表格数据（所有token已经配置正确，当前配置的是角色表格）