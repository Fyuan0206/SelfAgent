#!/bin/bash

# SelfAgent 启动脚本
# 用于启动 PostgreSQL 数据库和 FastAPI 服务器

set -e

echo "=================================="
echo "SelfAgent 启动脚本"
echo "=================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 1. 启动 PostgreSQL 数据库
echo "📦 启动 PostgreSQL 数据库..."
docker-compose up -d postgres

echo "⏳ 等待数据库启动..."
sleep 5

# 检查数据库是否就绪
until docker-compose exec -T postgres pg_isready -U selfagent > /dev/null 2>&1; do
    echo "⏳ 等待 PostgreSQL 准备就绪..."
    sleep 2
done

echo "✅ PostgreSQL 数据库已启动"
echo ""

# 2. 安装 Python 依赖
echo "📦 安装 Python 依赖..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python 依赖安装完成"
echo ""

# 3. 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，从 .env.example 复制..."
    cp .env.example .env
    echo "请编辑 .env 文件，设置必要的配置（如 OPENAI_API_KEY）"
    echo ""
fi

# 4. 初始化数据库
echo "🗄️  初始化数据库..."
python app/core/database.py

echo "✅ 数据库初始化完成"
echo ""

# 5. 启动 FastAPI 服务器
echo "🚀 启动 FastAPI 服务器..."
echo ""
echo "=================================="
echo "SelfAgent 服务已启动！"
echo "=================================="
echo ""
echo "📍 API 文档: http://localhost:8000/docs"
echo "📍 健康检查: http://localhost:8000/api/health"
echo "📍 前端页面: http://localhost:8000/"
echo ""
echo "默认管理员账号："
echo "  邮箱: admin@selfagent.com"
echo "  密码: admin123"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
