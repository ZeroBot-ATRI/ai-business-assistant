#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证环境配置脚本
运行此脚本检查所有依赖是否正确安装
"""

import sys
import os
import io

# 设置Windows中文环境下的输出编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要Python 3.10+")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n🔍 检查依赖包...")
    required = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "anthropic": "anthropic",
        "sqlalchemy": "sqlalchemy",
        "pydantic": "pydantic",
        "streamlit": "streamlit",
        "pandas": "pandas",
        "plotly": "plotly",
        "requests": "requests",
        "pyyaml": "yaml"  # pyyaml包导入时是yaml
    }

    missing = []
    for package_name, import_name in required.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing.append(package_name)

    return len(missing) == 0

def check_env_file():
    """检查环境变量文件"""
    print("\n🔍 检查环境配置...")
    if os.path.exists(".env"):
        print("✅ .env 文件存在")
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            if "CLAUDE_API_KEY" in content:
                if "sk-ant-" in content:
                    print("✅ CLAUDE_API_KEY 已配置")
                    return True
                else:
                    print("⚠️  CLAUDE_API_KEY 格式可能不正确（应该以sk-ant-开头）")
                    return False
            else:
                print("❌ .env 文件中缺少 CLAUDE_API_KEY")
                return False
    else:
        print("❌ .env 文件不存在")
        print("💡 运行: cp .env.example .env")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n🔍 检查项目结构...")
    required_files = [
        "app/main.py",
        "app/__init__.py",
        "ui/app.py",
        "requirements.txt",
        ".env.example"
    ]

    required_dirs = [
        "app",
        "ui",
        "sops",
        "tests"
    ]

    all_good = True

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件缺失")
            all_good = False

    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"✅ {dir}/")
        else:
            print(f"❌ {dir}/ - 目录缺失")
            all_good = False

    return all_good

def test_imports():
    """测试核心导入"""
    print("\n🔍 测试核心模块导入...")
    try:
        from fastapi import FastAPI
        print("✅ FastAPI 导入成功")
    except Exception as e:
        print(f"❌ FastAPI 导入失败: {e}")
        return False

    try:
        from anthropic import Anthropic
        print("✅ Anthropic 导入成功")
    except Exception as e:
        print(f"❌ Anthropic 导入失败: {e}")
        return False

    try:
        import streamlit
        print("✅ Streamlit 导入成功")
    except Exception as e:
        print(f"❌ Streamlit 导入失败: {e}")
        return False

    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI助手环境验证脚本")
    print("=" * 60)

    results = {
        "Python版本": check_python_version(),
        "依赖包": check_dependencies(),
        "环境配置": check_env_file(),
        "项目结构": check_project_structure(),
        "模块导入": test_imports()
    }

    print("\n" + "=" * 60)
    print("📊 验证结果汇总")
    print("=" * 60)

    for name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查通过！你可以开始了！")
        print("\n下一步:")
        print("1. 终端1: uvicorn app.main:app --reload")
        print("2. 终端2: streamlit run ui/app.py")
    else:
        print("⚠️  部分检查未通过，请根据上述提示修复")
        print("\n常见解决方法:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 配置环境: cp .env.example .env (然后编辑.env)")
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
