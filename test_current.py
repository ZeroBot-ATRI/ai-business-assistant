"""快速测试当前功能"""
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"

print("="*60)
print("Week 1 功能测试")
print("="*60)

# 测试1: 订单查询
print("\n【测试1】订单查询")
print("-"*60)
try:
    response = requests.post(
        f"{API_BASE}/chat",
        params={"user_input": "查询订单12345", "user_id": "test"},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 状态: 成功")
        print(f"✓ AI回复: {data['message'][:150]}...")
        debug = data.get('debug', {})
        print(f"✓ 意图: {debug.get('intent')}")
        print(f"✓ 技能: {debug.get('skill')}")
        print(f"✓ 执行时间: {debug.get('execution_time_ms', 0):.0f}ms")
    else:
        print(f"✗ 失败: HTTP {response.status_code}")
except Exception as e:
    print(f"✗ 错误: {e}")

# 测试2: 库存查询
print("\n【测试2】库存查询（优化后的提示词）")
print("-"*60)
try:
    response = requests.post(
        f"{API_BASE}/chat",
        params={"user_input": "查询产品A的库存", "user_id": "test"},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 状态: 成功")
        print(f"✓ AI回复: {data['message'][:150]}...")
        debug = data.get('debug', {})
        print(f"✓ 意图: {debug.get('intent')}")
        print(f"✓ 技能: {debug.get('skill')}")
    else:
        print(f"✗ 失败: HTTP {response.status_code}")
except Exception as e:
    print(f"✗ 错误: {e}")

# 测试3: 服务状态
print("\n【测试3】服务状态检查")
print("-"*60)
services = [
    ("Mock API", "http://localhost:9000/health"),
    ("后端API", "http://localhost:8000/"),
    ("Streamlit", "http://localhost:8501/"),
]

for name, url in services:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {name}: 运行中")
        else:
            print(f"✗ {name}: HTTP {response.status_code}")
    except:
        print(f"✗ {name}: 无法连接")

print("\n" + "="*60)
print("测试完成！")
print("="*60)
print("\n访问地址：")
print("  - 聊天界面: http://localhost:8501")
print("  - 监控看板: http://localhost:8502")
print("  - API文档: http://localhost:8000/docs")
print("  - Mock API文档: http://localhost:9000/docs")
