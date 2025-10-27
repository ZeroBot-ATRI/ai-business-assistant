#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端API是否能正常启动
"""

import sys
import io

# 设置Windows中文环境下的输出编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("🔍 测试后端API配置...")

try:
    from dotenv import load_dotenv
    import os

    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ 未找到 CLAUDE_API_KEY")
        sys.exit(1)

    if not api_key.startswith("sk-ant-"):
        print("❌ CLAUDE_API_KEY 格式不正确（应该以 sk-ant- 开头）")
        sys.exit(1)

    print(f"✅ CLAUDE_API_KEY 已配置（{api_key[:15]}...）")

    # 测试导入主模块
    print("\n🔍 测试导入 app.main...")
    from app.main import app, client
    print("✅ app.main 导入成功")

    # 测试数据库
    print("\n🔍 测试数据库...")
    import os.path
    if os.path.exists("database.db"):
        print("✅ database.db 已创建")
    else:
        print("⚠️  database.db 尚未创建（首次运行时会自动创建）")

    print("\n" + "=" * 60)
    print("🎉 后端API配置正确！")
    print("\n可以启动后端了：")
    print("  uvicorn app.main:app --reload")
    print("=" * 60)

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保已安装所有依赖：")
    print("  pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
