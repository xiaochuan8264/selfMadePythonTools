# -*- coding: utf-8 -*-
import requests
import json
import hashlib
import time
from datetime import datetime
import os
import csv
import ftrack_api

# ==================== 配置 ====================
# 飞书配置
APP_ID = "cli_a9ee46ebc8b81cee"
APP_SECRET = "BHG0jHUSIRIARIEIvl6UleTOQ1AeJr3u"
APP_TOKEN = "Qq3Ybd9ryaX3KQsvgNWcXXgAnMf"
TABLE_ID = "tblKGDFEjbA0X0Ak"

# 缓存配置
TOKEN_CACHE_FILE = "feishu_token.cache"
DATA_CACHE_FILE = "feishu_data.cache"
POLL_INTERVAL = 60  # 轮询间隔（秒）

# 需要监控的字段（不包括状态字段）
WATCH_FIELDS = [
    "开发名", "资产(描述)", "原画对接", "3D对接", "动画对接", "特效对接",
    "Ftrack标签", "父对象", "Ftrack创建状态",
    "更新&创建记录"
]

FTRACK_SERVER = "https://ftrack.legoutech.cn"
FTRACK_API_USER = "tangyunchuan"
FTRACK_API_KEY = "ZDE2MDkzZTgtM2E3OS00YzQ4LTkxOGQtODA4MGM3ZmU0MDIyOjoyYzM2NDFjMy1lNGE3LTQ5YTItYWE0ZS1kMzUzMGU3Yzk4ZTE"


def create_nested_structure_with_auto_populate_disabled(
        project_name, parent_name, structure_config):
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


# ==================== Token 管理器 ====================
class TokenManager:
    """飞书 Token 管理器"""

    def __init__(self, app_id, app_secret, cache_file):
        self.app_id = app_id
        self.app_secret = app_secret
        self.cache_file = cache_file

    def get_token(self):
        """获取 token（优先从缓存）"""
        cached_token = self._read_cache()
        if cached_token:
            return cached_token
        return self._fetch_new_token()

    def _read_cache(self):
        """读取缓存的 token"""
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)

            if time.time() < (data.get('expire_time', 0) - 300):
                print("[Token] 使用缓存")
                return data.get('token')
            else:
                print("[Token] 缓存已过期")
                return None
        except BaseException:
            return None

    def _fetch_new_token(self):
        """获取新 token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}

        response = requests.post(url, json=payload)
        result = response.json()

        if result.get('code') == 0:
            token = result['tenant_access_token']
            expire_in = result.get('expire', 7200)

            cache_data = {
                'token': token,
                'expire_time': time.time() + expire_in
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)

            print("[Token] 已获取新 token，有效期: {0} 秒".format(expire_in))
            return token
        else:
            raise Exception("获取 token 失败: {0}".format(result))

# ==================== 数据缓存管理器 ====================


class DataCacheManager:
    """本地数据缓存管理器"""

    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()

    def _load_cache(self):
        """加载本地缓存"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("[Cache] 加载本地缓存: {0} 条记录".format(len(data)))
            return data
        except BaseException:
            print("[Cache] 无缓存文件，创建新缓存")
            return {}

    def save_cache(self):
        """保存缓存到本地"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        print("[Cache] 已保存缓存: {0} 条记录".format(len(self.cache_data)))

    def get_record_hash(self, fields):
        """生成记录哈希值（排除状态和日志字段）"""
        exclude_fields = ['Ftrack创建状态', '更新日志']
        watched_data = {k: fields.get(
            k) for k in WATCH_FIELDS if k in fields and k not in exclude_fields}
        json_str = json.dumps(watched_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()

    def add_or_update_cache(self, record_id, fields):
        """添加或更新缓存"""
        self.cache_data[record_id] = {
            'hash': self.get_record_hash(fields),
            'fields': fields
        }
        self.save_cache()

    def get_cached_record(self, record_id):
        """获取缓存的记录"""
        return self.cache_data.get(record_id)

    def is_record_changed(self, record_id, current_fields):
        """判断记录是否有变更"""
        cached = self.get_cached_record(record_id)
        if not cached:
            return True

        current_hash = self.get_record_hash(current_fields)
        return current_hash != cached['hash']

# ==================== 飞书 API 调用 ====================


def get_all_records(token, app_token, table_id):
    """获取多维表格所有记录"""
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{0}/tables/{1}/records/search".format(
        app_token, table_id)

    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-Type': 'application/json'
    }

    all_records = []
    page_token = ""
    has_more = True

    while has_more:
        payload = {
            "field_names": WATCH_FIELDS,
            "page_size": 500,
            "page_token": page_token
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if result.get('code') == 0:
            data = result['data']
            all_records.extend(data['items'])
            has_more = data.get('has_more', False)
            page_token = data.get('page_token', '')
        else:
            print("[API] 获取数据失败: {0}".format(result))
            break

    return all_records


def update_record_fields(token, app_token, table_id, record_id, field_updates):
    """
    更新记录的多个字段[1][2]

    Args:
        token: 访问令牌
        app_token: 多维表格 token
        table_id: 数据表 ID
        record_id: 记录 ID
        field_updates: 要更新的字段字典，例如:
                      {
                          "Ftrack创建状态": "已创建",
                          "更新日志": "2025-01-15 创建成功",
                          "原画状态": "进行中"
                      }
    """
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{0}/tables/{1}/records/{2}".format(
        app_token, table_id, record_id)

    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-Type': 'application/json'
    }

    payload = {
        "fields": field_updates
    }

    try:
        response = requests.put(url, headers=headers, json=payload)
        result = response.json()

        if result.get('code') == 0:
            print(
                "  [飞书更新] 成功更新字段: {0}".format(
                    ', '.join(
                        field_updates.keys())))
            return True
        else:
            print("  [飞书更新] 更新失败: {0}".format(result))
            return False
    except Exception as e:
        print("  [飞书更新] 更新异常: {0}".format(e))
        return False

# ==================== 业务处理函数 ====================


def create_operation(record_data):
    """
    创建操作（占位函数）

    Returns:
        dict: 返回需要更新到飞书的字段
    """
    print("  [CREATE] 记录ID: {0}, 开发名: {1}".format(
        record_data['record_id'],
        record_data['fields'].get('开发名', 'N/A')
    ))

    # 这里添加您的 Ftrack 创建逻辑
    time.sleep(0.5)  # 模拟创建耗时

    # 返回需要更新到飞书的字段
    return {
        "Ftrack创建状态": "已创建",
        "更新日志": "{0} - Ftrack任务创建成功".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "Ftrack链接": "测试链接",
    }


def update_operation(record_data):
    """
    更新操作（占位函数）

    Returns:
        dict: 返回需要更新到飞书的字段
    """
    print("  [UPDATE] 记录ID: {0}, 开发名: {1}".format(
        record_data['record_id'],
        record_data['fields'].get('开发名', 'N/A')
    ))

    # 这里添加您的 Ftrack 更新逻辑

    # 返回需要更新到飞书的字段
    return {
        "更新日志": "{0} - Ftrack任务更新成功".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }

# 读取缓存的CSV文件，来找到Ftrack正确的名字


class ChineseEnglishMapper:
    """中英文名称映射工具"""

    def __init__(self, csv_file='names.csv'):
        self.csv_file = csv_file
        self.name_dict = {}

        if os.path.exists(csv_file):
            self.load()
        else:
            print("警告: CSV 文件不存在: {0}".format(csv_file))

    def load(self):
        """加载 CSV 映射（自动检测编码）"""
        # 定义常见编码列表
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'utf-8-sig']

        for encoding in encodings:
            try:
                with open(self.csv_file, 'r', encoding=encoding) as f:
                    reader = csv.reader(f)
                    next(reader, None)  # 跳过表头

                    for row in reader:
                        if len(row) >= 2:
                            chinese = row[0].strip()
                            english = row[1].strip()
                            self.name_dict[chinese] = english

                print("✓ 已加载 {0} 条记录 (编码: {1})".format(
                    len(self.name_dict), encoding))
                return  # 成功后退出

            except UnicodeDecodeError:
                continue  # 尝试下一个编码
            except Exception as e:
                print("✗ 使用 {0} 编码读取失败: {1}".format(encoding, e))
                continue

        print("✗ 所有编码尝试失败，请检查文件")

    def get(self, chinese_name, default=None):
        """获取英文名"""
        return self.name_dict.get(chinese_name, default)

    def batch_get(self, chinese_names):
        """批量获取英文名"""
        result = {}
        for cn in chinese_names:
            result[cn] = self.get(cn, '未找到')
        return result

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
        parent_name: 父对象（如 'rockturtle_lv1'）
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


def batch_set_tags(project_name, parent_name, task_tag_mapping):
    """
    批量为多个任务设置标签

    Args:
        project_name: 项目名称
        parent_name: 父对象名称
        task_tag_mapping: 任务和标签的映射字典
                         格式: {'任务名': ['标签1', '标签2'], ...}
    """
    parent = session.query(
        f'TypedContext where name is "{parent_name}" '
        f'and project.name is "{project_name}"'
    ).first()

    if not parent:
        raise ValueError(f"未找到父对象: {parent_name}")

    for task_name, tags in task_tag_mapping.items():
        try:
            task = session.query(
                f'Task where name is "{task_name}" '
                f'and parent.id is "{parent["id"]}"'
            ).first()

            if task:
                task['custom_attributes']['BeagleAssetsTags'] = tags
                print(f"✓ {task_name}: {tags}")
            else:
                print(f"✗ 未找到任务: {task_name}")

        except Exception as e:
            print(f"✗ 设置任务 '{task_name}' 标签时出错: {e}")

    session.commit()
    print("\n批量设置完成！")


def set_entity_description(entity, description):
    """
    为实体设置描述

    Args:
        entity: Ftrack 实体对象（对象或任务）
        description: 描述内容
    """
    entity['description'] = description
    session.commit()

    print(f"✓ 已为 '{entity['name']}' 设置描述: {description}")


# 上述单个对象任务描述设置成功


def set_task_descriptions_individually(
        project_name,
        parent_name,
        task_descriptions):
    """
    为不同任务设置不同的描述

    Args:
        project_name: 项目名称
        parent_name: 父对象名称
        task_descriptions: 任务和描述的映射
                          格式: {'任务名': '描述内容', ...}
    """
    parent = session.query(
        f'TypedContext where name is "{parent_name}" '
        f'and project.name is "{project_name}"'
    ).first()

    if not parent:
        raise ValueError(f"未找到父对象: {parent_name}")

    for task_name, description in task_descriptions.items():
        task = session.query(
            f'Task where name is "{task_name}" '
            f'and parent.id is "{parent["id"]}"'
        ).first()

        if task:
            task['description'] = description
            print(f"✓ 任务 '{task_name}' 描述: {description}")
        else:
            print(f"✗ 未找到任务: {task_name}")

    session.commit()
    print("\n✓ 所有任务描述设置完成！")


def get_ftrack_web_url(session, entity):
    """
    获取 Ftrack 实体的正确 Web 访问链接

    Args:
        session: Ftrack session
        entity: Ftrack 实体对象

    Returns:
        str: 可在浏览器中打开的完整 URL
    """
    entity_id = entity['id']
    entity_type = entity.entity_type.lower()

    # 根据实体类型确定 itemId 和 view
    if entity_type == 'project':
        item_id = 'projects'
        view = 'overview'
    elif entity_type == 'task':
        item_id = 'projects'
        view = 'tasks'
    else:
        # TypedContext (Folder/AssetBuild/Shot 等)
        item_id = 'projects'
        view = 'tasks'
        entity_type = 'task'  # 统一使用 task

    # 构建完整 URL
    url = "{0}/#entityId={1}&entityType={2}&itemId={3}&view={4}".format(
        session.server_url,
        entity_id,
        entity_type,
        item_id,
        view)

    return url

# ==================== 主流程 ====================


def process_records(token, cache_manager):
    """处理记录"""
    print("[API] 获取在线数据...")
    online_records = get_all_records(token, APP_TOKEN, TABLE_ID)
    print("[API] 获取到 {0} 条记录".format(len(online_records)))

    stats = {
        '未创建': 0,
        '创建中': 0,
        '已创建': 0,
        '已创建-有更新': 0
    }

    for record in online_records:
        record_id = record['record_id']
        fields = record['fields']
        status = fields.get('Ftrack创建状态')
        dev_name = fields.get('开发名')[0].get('text')
        print(dev_name+status)
        g_description = fields.get('资产(描述)')[0].get('text')
        parent = fields.get('父对象')
        tags = fields.get('Ftrack标签')
        concept_person = [person.get('name') for person in fields.get('原画对接')]
        concept_person = [mapper.get(p) for p in concept_person]

        model_person = [person.get('name') for person in fields.get('3D对接')]
        model_person = [mapper.get(p) for p in model_person]

        ani_person = [person.get('name') for person in fields.get('动画对接')]
        ani_person = [mapper.get(p) for p in ani_person]

        vfx_person = [person.get('name') for person in fields.get('特效对接')]
        vfx_person = [mapper.get(p) for p in vfx_person]

        data_structure = {'name': dev_name,
                          'tasks': ['3DAnimation',
                                    '3DStaticAssets',
                                    '3DVfx',
                                    'Concept'],
                          'children': [{'name': 'inputAnimation',
                                        'tasks': ['inputAnimation']},
                                       {'name': 'inputTexture',
                                        'tasks': ['inputTexture']},
                                       {'name': 'model',
                                        'tasks': ['model']}]}
        task_assignments = {
            '3DAnimation': ani_person,
            '3DStaticAssets': model_person,
            '3DVfx': vfx_person,
            'Concept': concept_person}

        task_tags = {'3DAnimation': tags,
                     '3DStaticAssets': tags,
                     'Concept': tags,
                     '3DVfx': tags}
        task_desc_mapping = {
            '3DAnimation': '动画：{0}'.format(g_description),
            '3DStaticAssets': '3D资产：{0}'.format(g_description),
            '3DVfx': '特效：{0}'.format(g_description),
            'Concept': '原画：{0}'.format(g_description)}

        # 1. 未创建 - 跳过
        if status == '未创建':
            stats['未创建'] += 1
            continue

        # 2. 创建中 - 执行创建
        elif status == '创建中':
            stats['创建中'] += 1
            print("\n[创建中] 开发名: {0}".format(fields.get('开发名', 'N/A')))

            # 执行创建操作
            create_nested_structure_with_auto_populate_disabled(
                project_name='BeagleAssets', parent_name=parent, structure_config=data_structure)
            # 设置执行人
            batch_assign_users(
                project_name='BeagleAssets',
                parent_name=dev_name,
                task_assignments=task_assignments)
            # 设置任务标签
            batch_set_tags(
                project_name='BeagleAssets',
                parent_name=dev_name,
                task_tag_mapping=task_tags)

            # 设置文件夹描述
            dev_parent = session.query(
                'TypedContext where name is "{0}" '
                'and project.name is "BeagleAssets"'.format(dev_name)).first()
            set_entity_description(dev_parent, g_description)
            # 设置任务描述
            set_task_descriptions_individually(
                project_name='BeagleAssets',
                parent_name=dev_name,
                task_descriptions=task_desc_mapping)

            # 获取Ftrack链接
            web_url = get_ftrack_web_url(session, dev_parent)

            field_updates = {"Ftrack创建状态": "已创建", "更新&创建记录": "{0} - Ftrack任务创建成功".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "Ftrack链接": web_url, }

            if field_updates:
                # 添加到缓存
                cache_manager.add_or_update_cache(record_id, fields)

                # 更新飞书多维表格的多个字段[1][2]
                update_record_fields(
                    token, APP_TOKEN, TABLE_ID, record_id, field_updates)

        # 3. 已创建 - 检查是否有更新
        elif status == '已创建':
            if cache_manager.is_record_changed(record_id, fields):
                stats['已创建-有更新'] += 1
                print("\n[已创建-有更新] 开发名: {0}".format(fields.get('开发名', 'N/A')))

                # 执行更新操作

                # 设置执行人
                batch_assign_users(
                    project_name='BeagleAssets',
                    parent_name=dev_name,
                    task_assignments=task_assignments)
                # 设置任务标签
                batch_set_tags(
                    project_name='BeagleAssets',
                    parent_name=dev_name,
                    task_tag_mapping=task_tags)

                # 设置文件夹描述
                dev_parent = session.query(
                    'TypedContext where name is "{0}" '
                    'and project.name is "BeagleAssets"'.format(dev_name)).first()
                set_entity_description(dev_parent, g_description)
                # 设置任务描述
                set_task_descriptions_individually(
                    project_name='BeagleAssets',
                    parent_name=dev_name,
                    task_descriptions=task_desc_mapping)
                    
                web_url = get_ftrack_web_url(session, dev_parent)

                field_updates = {
                    "更新&创建记录": "{0} - Ftrack任务更新成功".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "Ftrack链接": web_url,
                }

                if field_updates:
                    # 更新缓存
                    cache_manager.add_or_update_cache(record_id, fields)

                    # 更新飞书多维表格的字段[1][2]
                    update_record_fields(
                        token, APP_TOKEN, TABLE_ID, record_id, field_updates)
            else:
                stats['已创建'] += 1

    print("\n[统计] 未创建: {0}, 创建中: {1}, 已创建(无更新): {2}, 已创建(有更新): {3}".format(
        stats['未创建'], stats['创建中'], stats['已创建'], stats['已创建-有更新']
    ))


def main_loop():
    """主轮询循环"""
    print("\n{0}".format("=" * 60))
    print("飞书多维表格监控服务启动")
    print("轮询间隔: {0} 秒".format(POLL_INTERVAL))
    print("{0}\n".format("=" * 60))

    token_manager = TokenManager(APP_ID, APP_SECRET, TOKEN_CACHE_FILE)
    cache_manager = DataCacheManager(DATA_CACHE_FILE)

    loop_count = 0

    while True:
        loop_count += 1
        print("\n[{0}] 第 {1} 次轮询".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            loop_count
        ))

        try:
            token = token_manager.get_token()
            process_records(token, cache_manager)

        except Exception as e:
            print("[Error] {0}".format(e))

        print("\n等待 {0} 秒后进行下一次轮询...".format(POLL_INTERVAL))
        time.sleep(POLL_INTERVAL)


# ==================== 启动服务 ====================
if __name__ == '__main__':
    mapper = ChineseEnglishMapper('users_in_ftrack.csv')
    session = ftrack_api.Session(server_url=FTRACK_SERVER,
                                 api_key=FTRACK_API_KEY,
                                 api_user=FTRACK_API_USER)
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\n服务已停止")
