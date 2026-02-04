#!/usr/bin/env python3
"""
系统测试脚本
测试 PostgreSQL 数据库连接和用户认证功能
"""

import sys
import time

def test_database():
    """测试数据库连接"""
    print("=" * 60)
    print("测试 1: 数据库连接")
    print("=" * 60)

    try:
        from app.core.database import init_db, get_db, create_default_admin
        init_db()
        print("✅ 数据库表创建成功")

        db = next(get_db())
        admin = create_default_admin(db)
        print(f"✅ 默认管理员创建成功: {admin.email}")
        db.close()

        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False


def test_models():
    """测试数据模型"""
    print("\n" + "=" * 60)
    print("测试 2: 数据模型")
    print("=" * 60)

    try:
        from app.models.user_models import User, UserQuota, UserRole
        from app.models.user_schemas import UserCreate, Token
        print("✅ 模型导入成功")

        # 测试枚举
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MEMBER.value == "member"
        assert UserRole.USER.value == "user"
        print("✅ 角色枚举正常")

        return True
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False


def test_auth():
    """测试认证功能"""
    print("\n" + "=" * 60)
    print("测试 3: 认证功能")
    print("=" * 60)

    try:
        from app.core.auth import create_access_token, decode_access_token
        from app.models.user_models import UserRole

        # 测试 token 创建
        token = create_access_token(data={"sub": "1", "role": UserRole.ADMIN})
        print(f"✅ Token 创建成功: {token[:50]}...")

        # 测试 token 解码
        payload = decode_access_token(token)
        assert payload["sub"] == "1"
        assert payload["role"] == UserRole.ADMIN
        print("✅ Token 解码成功")

        return True
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")
        return False


def test_password():
    """测试密码加密"""
    print("\n" + "=" * 60)
    print("测试 4: 密码加密")
    print("=" * 60)

    try:
        from app.models.user_models import get_password_hash, verify_password

        password = "test123"
        hashed = get_password_hash(password)
        print(f"✅ 密码哈希生成成功: {hashed[:50]}...")

        assert verify_password(password, hashed) == True
        print("✅ 密码验证成功")

        assert verify_password("wrong", hashed) == False
        print("✅ 错误密码正确拒绝")

        return True
    except Exception as e:
        print(f"❌ 密码测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n🚀 SelfAgent 系统测试")
    print("请确保 PostgreSQL 正在运行 (docker-compose up -d)")
    print()

    results = []

    # 等待数据库启动
    print("⏳ 等待数据库启动...")
    time.sleep(3)

    # 运行测试
    results.append(test_database())
    results.append(test_models())
    results.append(test_auth())
    results.append(test_password())

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n默认管理员账号：")
        print("  邮箱: admin@selfagent.com")
        print("  密码: admin123")
        print("\n启动服务器：")
        print("  ./start.sh")
        print("  或: uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
