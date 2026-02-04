"""
SelfAgent API 使用示例
演示如何使用 Python 调用 SelfAgent 的认证和管理 API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# ==================== 1. 用户认证示例 ====================

def example_register():
    """示例：注册新用户"""
    print("\n=== 1. 用户注册 ===")

    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "testuser@example.com",
        "username": "测试用户",
        "password": "password123"
    })

    if response.status_code == 201:
        data = response.json()
        print(f"✅ 注册成功！")
        print(f"   用户 ID: {data['user']['id']}")
        print(f"   邮箱: {data['user']['email']}")
        print(f"   角色: {data['user']['role']}")
        print(f"   Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ 注册失败: {response.text}")
        return None


def example_login():
    """示例：用户登录"""
    print("\n=== 2. 用户登录 ===")

    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@selfagent.com",  # 使用默认管理员
        "password": "admin123"
    })

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功！")
        print(f"   用户: {data['user']['email']}")
        print(f"   角色: {data['user']['role']}")
        print(f"   Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ 登录失败: {response.text}")
        return None


def example_get_user_info(token):
    """示例：获取当前用户信息"""
    print("\n=== 3. 获取用户信息 ===")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 用户信息获取成功！")
        print(f"   ID: {data['id']}")
        print(f"   邮箱: {data['email']}")
        print(f"   用户名: {data['username']}")
        print(f"   角色: {data['role']}")
        print(f"   额度: {data['quota']['daily_used']}/{data['quota']['daily_quota']}")
        print(f"   剩余: {data['quota']['remaining_quota']}")
    else:
        print(f"❌ 获取失败: {response.text}")


def example_get_quota(token):
    """示例：获取额度信息"""
    print("\n=== 4. 获取额度信息 ===")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/quota", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 额度信息获取成功！")
        print(f"   每日额度: {data['daily_quota']}")
        print(f"   已使用: {data['daily_used']}")
        print(f"   剩余: {data['remaining_quota']}")
        print(f"   无限额度: {data['is_unlimited']}")
    else:
        print(f"❌ 获取失败: {response.text}")


# ==================== 2. 管理员 API 示例 ====================

def example_admin_create_user(admin_token):
    """示例：管理员创建用户"""
    print("\n=== 5. 管理员创建用户 ===")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(
        f"{BASE_URL}/api/admin/users",
        headers=headers,
        json={
            "email": "vip@example.com",
            "username": "VIP 用户",
            "password": "vip123",
            "role": "member",  # 会员角色
            "daily_quota": -1   # 无限额度
        }
    )

    if response.status_code == 201:
        data = response.json()
        print(f"✅ 用户创建成功！")
        print(f"   ID: {data['id']}")
        print(f"   邮箱: {data['email']}")
        print(f"   角色: {data['role']}")
        print(f"   额度: {data['quota']['daily_quota']} (无限)")
    else:
        print(f"❌ 创建失败: {response.text}")


def example_admin_list_users(admin_token):
    """示例：管理员获取用户列表"""
    print("\n=== 6. 管理员获取用户列表 ===")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(
        f"{BASE_URL}/api/admin/users",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 用户列表获取成功！")
        print(f"   总用户数: {data['total']}")
        print(f"   当前页: {data['page']}")
        print(f"   每页数量: {data['page_size']}")
        print(f"   用户:")
        for user in data['users']:
            print(f"      - {user['email']} ({user['role']}) - 额度: {user['quota']['daily_used']}/{user['quota']['daily_quota']}")
    else:
        print(f"❌ 获取失败: {response.text}")


def example_admin_update_quota(admin_token, user_id):
    """示例：管理员更新用户额度"""
    print(f"\n=== 7. 管理员更新用户额度 (ID: {user_id}) ===")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.put(
        f"{BASE_URL}/api/admin/users/{user_id}/quota",
        headers=headers,
        json={"daily_quota": 100}  # 设置为每天 100 次
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 额度更新成功！")
        print(f"   每日额度: {data['daily_quota']}")
        print(f"   已使用: {data['daily_used']}")
        print(f"   剩余: {data['remaining_quota']}")
    else:
        print(f"❌ 更新失败: {response.text}")


# ==================== 3. 聊天 API 示例 ====================

def example_chat(token):
    """示例：发送聊天消息"""
    print("\n=== 8. 发送聊天消息 ===")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/frontend/chat",
        headers=headers,
        json={"text": "你好，我感到有点焦虑"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 消息发送成功！")
        print(f"   回复: {data['response'][:100]}...")
        print(f"   检测情绪: {data.get('emotion_detected')}")
        print(f"   风险等级: {data.get('risk_level')}")
    else:
        print(f"❌ 发送失败: {response.text}")


# ==================== 主函数 ====================

def main():
    """运行所有示例"""
    print("=" * 60)
    print("SelfAgent API 使用示例")
    print("=" * 60)
    print(f"\nAPI 基础 URL: {BASE_URL}")
    print("请确保服务器正在运行")

    # 1. 管理员登录
    admin_token = example_login()

    if not admin_token:
        print("\n❌ 无法获取管理员 Token，请检查服务器是否运行")
        return

    # 2. 获取管理员信息
    example_get_user_info(admin_token)
    example_get_quota(admin_token)

    # 3. 管理员创建用户
    example_admin_create_user(admin_token)

    # 4. 管理员获取用户列表
    example_admin_list_users(admin_token)

    # 5. 注册新用户
    user_token = example_register()

    if user_token:
        # 6. 获取新用户信息
        example_get_user_info(user_token)

        # 7. 发送聊天消息
        example_chat(user_token)

    # 8. 管理员更新用户额度 (需要先知道用户 ID)
    # example_admin_update_quota(admin_token, user_id=2)

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保服务器正在运行:")
        print("   ./start.sh")
        print("   或: uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
