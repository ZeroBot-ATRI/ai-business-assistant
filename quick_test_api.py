# -*- coding: utf-8 -*-
"""快速测试Mock API Server的新端点"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

API_BASE = "http://localhost:9000"

print("\n测试Mock API Server v2.0新端点...")
print("=" * 60)

# 测试促销端点
print("\n1. 测试促销端点 /api/promotions")
try:
    response = requests.get(f"{API_BASE}/api/promotions", timeout=5)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 成功！找到 {data.get('total', 0)} 个促销活动")
    else:
        print(f"   ❌ 失败: 端点不存在或返回错误")
except Exception as e:
    print(f"   ❌ 连接失败: {e}")

# 测试客户端点
print("\n2. 测试客户端点 /api/customers/CUST001")
try:
    response = requests.get(f"{API_BASE}/api/customers/CUST001", timeout=5)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 成功！客户: {data.get('name')}")
    else:
        print(f"   ❌ 失败: 端点不存在或返回错误")
except Exception as e:
    print(f"   ❌ 连接失败: {e}")

# 测试报表端点
print("\n3. 测试报表端点 /api/reports/sales")
try:
    response = requests.get(f"{API_BASE}/api/reports/sales", timeout=5)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 成功！报表类型: {data.get('report_type')}")
    else:
        print(f"   ❌ 失败: 端点不存在或返回错误")
except Exception as e:
    print(f"   ❌ 连接失败: {e}")

# 测试根路径查看版本
print("\n4. 测试根路径 / 查看API版本")
try:
    response = requests.get(f"{API_BASE}/", timeout=5)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        version = data.get('version', 'unknown')
        print(f"   API版本: {version}")
        if version == "2.0.0":
            print(f"   ✅ 运行的是 v2.0！")
        else:
            print(f"   ⚠️  运行的是旧版本 {version}")
except Exception as e:
    print(f"   ❌ 连接失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
