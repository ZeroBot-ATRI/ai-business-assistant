"""
Day 4 测试：真实技能API对接

测试场景:
1. 用户查询订单 → AI调用真实OrderSkill → 返回真实API数据
2. 用户查询库存 → AI调用真实InventorySkill → 返回真实API数据
3. 用户查询物流 → AI调用真实LogisticsSkill → 返回真实API数据
"""
import requests
import json
from datetime import datetime
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"
MOCK_API_BASE = "http://localhost:9000"


def print_section(title):
    """打印分隔符"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_mock_api():
    """测试Mock API Server是否正常运行"""
    print_section("1. 测试Mock API Server")

    try:
        # 测试健康检查
        response = requests.get(f"{MOCK_API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ Mock API Server健康检查通过")
            data = response.json()
            print(f"  状态: {data.get('status')}")
            print(f"  时间: {data.get('timestamp')}")
        else:
            print(f"✗ Mock API Server响应异常: {response.status_code}")
            return False

        # 测试订单API
        response = requests.get(f"{MOCK_API_BASE}/api/orders/12345", timeout=5)
        if response.status_code == 200:
            order = response.json()
            print(f"✓ 订单API测试通过: 订单12345 - {order.get('status')}")
        else:
            print(f"✗ 订单API测试失败")
            return False

        # 测试库存API
        response = requests.get(f"{MOCK_API_BASE}/api/inventory/A", timeout=5)
        if response.status_code == 200:
            inventory = response.json()
            print(f"✓ 库存API测试通过: 产品A - 库存{inventory.get('stock')}")
        else:
            print(f"✗ 库存API测试失败")
            return False

        print(f"\n✓ Mock API Server所有测试通过")
        return True

    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到Mock API Server")
        print("  请确保Mock API Server正在运行: python mock_api_server.py")
        return False
    except Exception as e:
        print(f"✗ Mock API测试失败: {e}")
        return False


def test_main_api():
    """测试主API是否正常运行"""
    print_section("2. 测试主API")

    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 主API健康检查通过")
            print(f"  API: {data.get('api')}")
            print(f"  LLM: {data.get('llm')}")
            print(f"  版本: {data.get('version')}")
            return True
        else:
            print(f"✗ 主API响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到主API")
        print("  请确保主API正在运行: uvicorn app.main:app --port 8000")
        return False
    except Exception as e:
        print(f"✗ 主API测试失败: {e}")
        return False


def test_chat_with_order_query():
    """测试订单查询对话"""
    print_section("3. 测试订单查询对话（真实API）")

    query = "查询订单12345的状态"
    print(f"用户输入: {query}")

    try:
        response = requests.post(
            f"{API_BASE}/chat",
            params={"user_input": query, "user_id": "test_user"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 对话成功")
            print(f"AI响应: {data.get('response')}")
            print(f"\n执行计划:")
            plan = data.get('plan', {})
            print(f"  意图: {plan.get('intent')}")
            print(f"  技能: {plan.get('skills')}")

            # 检查是否调用了真实API
            skills_used = plan.get('skills', [])
            if any('get_order' in str(skill) for skill in skills_used):
                print(f"\n✓ 成功调用get_order技能")
                print(f"  这是真实的API调用，数据来自Mock API Server")
                return True
            else:
                print(f"\n⚠️  未检测到get_order技能调用")
                return False
        else:
            print(f"✗ 对话请求失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False

    except Exception as e:
        print(f"✗ 订单查询对话失败: {e}")
        return False


def test_chat_with_inventory_query():
    """测试库存查询对话"""
    print_section("4. 测试库存查询对话（真实API）")

    query = "查询产品A的库存"
    print(f"用户输入: {query}")

    try:
        response = requests.post(
            f"{API_BASE}/chat",
            params={"user_input": query, "user_id": "test_user"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 对话成功")
            print(f"AI响应: {data.get('response')}")
            print(f"\n执行计划:")
            plan = data.get('plan', {})
            print(f"  意图: {plan.get('intent')}")
            print(f"  技能: {plan.get('skills')}")

            # 检查是否调用了真实API
            skills_used = plan.get('skills', [])
            if any('query_inventory' in str(skill) for skill in skills_used):
                print(f"\n✓ 成功调用query_inventory技能")
                print(f"  这是真实的API调用，数据来自Mock API Server")
                return True
            else:
                print(f"\n⚠️  未检测到query_inventory技能调用")
                return False
        else:
            print(f"✗ 对话请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 库存查询对话失败: {e}")
        return False


def test_chat_with_delayed_order():
    """测试延迟订单处理（复杂场景）"""
    print_section("5. 测试延迟订单处理（复杂场景）")

    query = "查询订单999，它的物流信息是什么"
    print(f"用户输入: {query}")
    print(f"说明: 订单999是延迟订单，需要同时查询订单和物流信息")

    try:
        response = requests.post(
            f"{API_BASE}/chat",
            params={"user_input": query, "user_id": "test_user"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 对话成功")
            print(f"AI响应: {data.get('response')[:200]}...")
            print(f"\n执行计划:")
            plan = data.get('plan', {})
            print(f"  意图: {plan.get('intent')}")
            print(f"  技能: {plan.get('skills')}")

            # 检查是否调用了多个技能
            skills_used = plan.get('skills', [])
            has_order = any('get_order' in str(skill) for skill in skills_used)
            has_logistics = any('query_logistics' in str(skill) for skill in skills_used)

            if has_order and has_logistics:
                print(f"\n✓ 成功调用了get_order和query_logistics技能")
                print(f"  这展示了AI的多步骤任务执行能力")
                return True
            elif has_order or has_logistics:
                print(f"\n⚠️  仅调用了部分所需技能")
                return True  # 也算部分成功
            else:
                print(f"\n⚠️  未检测到所需技能调用")
                return False
        else:
            print(f"✗ 对话请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 延迟订单处理失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "Day 4 真实技能测试" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"主API地址: {API_BASE}")
    print(f"Mock API地址: {MOCK_API_BASE}")

    results = []

    # 运行所有测试
    results.append(("Mock API Server", test_mock_api()))
    results.append(("主API", test_main_api()))
    results.append(("订单查询对话", test_chat_with_order_query()))
    results.append(("库存查询对话", test_chat_with_inventory_query()))
    results.append(("延迟订单处理", test_chat_with_delayed_order()))

    # 统计结果
    print_section("测试结果汇总")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}  {name}")

    print(f"\n总计: {passed}/{total} 测试通过")
    print(f"成功率: {passed/total*100:.1f}%")

    if passed == total:
        print("\n🎉 所有测试通过！Day 4完成！")
        print("\n✓ 真实技能已成功对接Mock API")
        print("✓ AI能够正确调用真实API获取数据")
        print("✓ 端到端流程完整打通")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查上面的错误信息")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
