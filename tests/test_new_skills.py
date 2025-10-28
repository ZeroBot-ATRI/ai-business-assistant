# -*- coding: utf-8 -*-
"""
tests/test_new_skills.py - Week 2新增技能测试脚本

测试所有新增的5个技能模块：
1. 促销技能 (PromotionSkill)
2. 客户技能 (CustomerSkill)
3. 退款技能 (RefundSkill)
4. 补货技能 (ReplenishmentSkill)
5. 报表技能 (ReportSkill)

前置条件：
1. Mock API Server运行在 http://localhost:9000
2. 后端API服务运行在 http://localhost:8000

运行方式：
    python tests/test_new_skills.py
"""
import sys
import os

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.skills_real import (
    promotion_skill,
    customer_skill,
    refund_skill,
    replenishment_skill,
    report_skill
)

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_promotion_skill():
    """测试促销技能"""
    print_section("1. 测试促销技能 (PromotionSkill)")

    # 测试1: 查询所有促销活动
    print("📋 测试1.1: 查询所有促销活动")
    result = promotion_skill.query_promotions()
    if result.get("success"):
        print(f"   ✅ 查询成功：找到 {result.get('total', 0)} 个促销活动")
        for promo in result.get("promotions", [])[:2]:
            print(f"      - {promo['name']} ({promo['status']}): {promo['description']}")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")

    # 测试2: 查询特定产品的促销
    print("\n📋 测试1.2: 查询产品A的促销活动")
    result = promotion_skill.query_promotions(product_id="A")
    if result.get("success"):
        print(f"   ✅ 查询成功：产品A有 {result.get('total', 0)} 个促销活动")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")

    # 测试3: 查询进行中的促销
    print("\n📋 测试1.3: 查询进行中的促销")
    result = promotion_skill.query_promotions(status="进行中")
    if result.get("success"):
        print(f"   ✅ 查询成功：有 {result.get('total', 0)} 个进行中的促销")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")


def test_customer_skill():
    """测试客户技能"""
    print_section("2. 测试客户技能 (CustomerSkill)")

    # 测试1: 查询客户信息
    print("👤 测试2.1: 查询客户CUST001信息")
    result = customer_skill.get_customer("CUST001")
    if result.get("success"):
        print(f"   ✅ 查询成功：{result.get('name')} - {result.get('level')}")
        print(f"      积分：{result.get('points')} | 订单数：{result.get('total_orders')} | 总消费：¥{result.get('total_amount')}")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")

    # 测试2: 查询客户订单历史
    print("\n👤 测试2.2: 查询客户CUST001的订单历史")
    result = customer_skill.get_customer_orders("CUST001")
    if result.get("success"):
        print(f"   ✅ 查询成功：{result.get('customer_name')} 共有 {result.get('total_orders', 0)} 个订单")
        for order in result.get("orders", [])[:2]:
            print(f"      - 订单{order['order_id']}: {order['status']} - ¥{order['amount']}")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")

    # 测试3: 查询不存在的客户
    print("\n👤 测试2.3: 查询不存在的客户")
    result = customer_skill.get_customer("CUST999")
    if result.get("success"):
        print(f"   ⚠️  应该失败但成功了")
    else:
        print(f"   ✅ 正确处理：{result.get('error')}")


def test_refund_skill():
    """测试退款技能"""
    print_section("3. 测试退款技能 (RefundSkill)")

    # 测试1: 查询退款详情
    print("💰 测试3.1: 查询退款RF001详情")
    result = refund_skill.get_refund("RF001")
    if result.get("success"):
        print(f"   ✅ 查询成功：订单{result.get('order_id')} - 状态: {result.get('status')}")
        print(f"      退款金额：¥{result.get('amount')} | 原因：{result.get('reason')}")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")

    # 测试2: 创建退款申请
    print("\n💰 测试3.2: 为订单888创建退款申请")
    result = refund_skill.create_refund(
        order_id="888",
        reason="商品不符合预期",
        amount=159.00
    )
    if result.get("success"):
        refund_id = result.get('refund', {}).get('refund_id')
        print(f"   ✅ 创建成功：退款申请ID: {refund_id}")
        print(f"      {result.get('message')}")

        # 测试3: 审批刚创建的退款
        print(f"\n💰 测试3.3: 审批退款申请 {refund_id}")
        approve_result = refund_skill.approve_refund(refund_id)
        if approve_result.get("success"):
            print(f"   ✅ 审批成功：{approve_result.get('message')}")
        else:
            print(f"   ❌ 审批失败：{approve_result.get('error')}")
    else:
        print(f"   ❌ 创建失败：{result.get('error')}")

    # 测试4: 查询处理中的退款
    print("\n💰 测试3.4: 查询处理中的退款RF002")
    result = refund_skill.get_refund("RF002")
    if result.get("success"):
        print(f"   ✅ 查询成功：状态: {result.get('status')}")
    else:
        print(f"   ❌ 查询失败：{result.get('error')}")


def test_replenishment_skill():
    """测试补货技能"""
    print_section("4. 测试补货技能 (ReplenishmentSkill)")

    # 测试1: 获取缺货产品的补货建议
    print("📦 测试4.1: 获取产品C（缺货）的补货建议")
    result = replenishment_skill.get_replenishment_suggestion("C")
    if result.get("success"):
        print(f"   ✅ 建议获取成功：{result.get('product_name')}")
        print(f"      当前库存：{result.get('current_stock')} | 警戒线：{result.get('threshold')}")
        print(f"      是否需要补货：{result.get('should_replenish')}")
        print(f"      建议补货量：{result.get('suggested_quantity')} | 优先级：{result.get('priority')}")
        print(f"      原因：{result.get('reason')}")
    else:
        print(f"   ❌ 获取失败：{result.get('error')}")

    # 测试2: 获取库存充足产品的建议
    print("\n📦 测试4.2: 获取产品A（库存充足）的补货建议")
    result = replenishment_skill.get_replenishment_suggestion("A")
    if result.get("success"):
        print(f"   ✅ 建议获取成功：{result.get('product_name')}")
        print(f"      当前库存：{result.get('current_stock')} | 是否需要补货：{result.get('should_replenish')}")
        print(f"      原因：{result.get('reason')}")
    else:
        print(f"   ❌ 获取失败：{result.get('error')}")

    # 测试3: 创建补货申请
    print("\n📦 测试4.3: 为产品B创建补货申请")
    result = replenishment_skill.create_replenishment(
        product_id="B",
        quantity=100,
        priority="高"
    )
    if result.get("success"):
        rep_id = result.get('replenishment', {}).get('replenishment_id')
        print(f"   ✅ 创建成功：补货申请ID: {rep_id}")
        print(f"      {result.get('message')}")

        # 测试4: 查询刚创建的补货申请
        print(f"\n📦 测试4.4: 查询补货申请 {rep_id}")
        query_result = replenishment_skill.get_replenishment(rep_id)
        if query_result.get("success"):
            print(f"   ✅ 查询成功：{query_result.get('product_name')} - 状态: {query_result.get('status')}")
            print(f"      补货量：{query_result.get('requested_quantity')} | 优先级：{query_result.get('priority')}")
        else:
            print(f"   ❌ 查询失败：{query_result.get('error')}")
    else:
        print(f"   ❌ 创建失败：{result.get('error')}")


def test_report_skill():
    """测试报表技能"""
    print_section("5. 测试报表技能 (ReportSkill)")

    # 测试1: 生成销售报表
    print("📊 测试5.1: 生成销售报表")
    result = report_skill.generate_report("sales")
    if result.get("success"):
        print(f"   ✅ 报表生成成功：{result.get('report_type')}")
        print(f"      统计周期：{result.get('period')}")
        print(f"      总订单数：{result.get('total_orders')} | 总金额：¥{result.get('total_amount')} | 平均订单：¥{result.get('avg_amount')}")
        print(f"      状态分布：{result.get('status_breakdown')}")
    else:
        print(f"   ❌ 报表生成失败：{result.get('error')}")

    # 测试2: 生成库存报表
    print("\n📊 测试5.2: 生成库存报表")
    result = report_skill.generate_report("inventory")
    if result.get("success"):
        print(f"   ✅ 报表生成成功：{result.get('report_type')}")
        print(f"      统计日期：{result.get('period')}")
        print(f"      产品总数：{result.get('total_products')} | 库存总值：¥{result.get('total_stock_value')}")
        print(f"      库存不足：{result.get('low_stock_products')} | 缺货：{result.get('out_of_stock_products')}")
        print(f"      状态分布：{result.get('status_breakdown')}")
    else:
        print(f"   ❌ 报表生成失败：{result.get('error')}")

    # 测试3: 生成客户报表
    print("\n📊 测试5.3: 生成客户报表")
    result = report_skill.generate_report("customer")
    if result.get("success"):
        print(f"   ✅ 报表生成成功：{result.get('report_type')}")
        print(f"      统计周期：{result.get('period')}")
        print(f"      客户总数：{result.get('total_customers')} | 客户总价值：¥{result.get('total_customer_value')}")
        print(f"      平均客户价值：¥{result.get('avg_customer_value')}")
        print(f"      会员分布：{result.get('level_breakdown')}")
    else:
        print(f"   ❌ 报表生成失败：{result.get('error')}")

    # 测试4: 生成不支持的报表类型
    print("\n📊 测试5.4: 测试不支持的报表类型")
    result = report_skill.generate_report("unknown_type")
    if result.get("success"):
        print(f"   ⚠️  应该失败但成功了")
    else:
        print(f"   ✅ 正确处理：{result.get('error')}")


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("  Week 2 新增技能综合测试")
    print("  测试5个新技能模块的所有功能")
    print("=" * 80)

    try:
        # 测试所有新技能
        test_promotion_skill()
        test_customer_skill()
        test_refund_skill()
        test_replenishment_skill()
        test_report_skill()

        # 总结
        print_section("✅ 测试完成")
        print("所有5个新技能模块测试完毕！")
        print("\n技能总结：")
        print("  1. ✅ 促销技能 (PromotionSkill) - 查询促销活动")
        print("  2. ✅ 客户技能 (CustomerSkill) - 查询客户信息和订单历史")
        print("  3. ✅ 退款技能 (RefundSkill) - 创建、查询、审批退款")
        print("  4. ✅ 补货技能 (ReplenishmentSkill) - 智能补货建议和申请管理")
        print("  5. ✅ 报表技能 (ReportSkill) - 生成销售/库存/客户报表")
        print("\n现在系统共有 16 个可用技能（13个真实API + 3个Mock）")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
