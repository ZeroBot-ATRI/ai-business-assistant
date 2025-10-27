#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试聊天API
确保后端正在运行: uvicorn app.main:app --reload
"""

import sys
import io
import requests
import json

# 设置Windows中文环境下的输出编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_api():
    """测试API"""
    print("🔍 测试聊天API...")
    print("=" * 60)

    # 测试后端是否运行
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            print("✅ 后端运行正常")
            print(f"   版本: {response.json().get('version')}")
        else:
            print("❌ 后端响应异常")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端")
        print("\n请先启动后端服务：")
        print("  uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"❌ 错误: {e}")
        return

    print("\n" + "=" * 60)
    print("📝 测试用例")
    print("=" * 60)

    # 测试用例
    test_cases = [
        "查询订单12345的状态",
        "产品A还有多少库存？",
        "帮我看看订单999的情况"
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{i}. 用户输入: {user_input}")
        print("-" * 60)

        try:
            response = requests.post(
                "http://localhost:8000/chat",
                params={"user_input": user_input},
                timeout=30
            )

            data = response.json()

            if data.get("success"):
                print("✅ 成功")
                print(f"AI回复: {data['message']}")
                print(f"\n调试信息:")
                print(f"  - 意图: {data['debug']['intent']}")
                print(f"  - 技能: {data['debug']['skill']}")
                print(f"  - 结果: {json.dumps(data['debug']['result'], ensure_ascii=False)}")
            else:
                print("❌ 失败")
                print(f"错误: {data.get('error')}")
                if 'debug' in data:
                    print(f"\n调试信息:")
                    for key, value in data['debug'].items():
                        print(f"  {key}: {value}")

        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
