#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Day 2 综合测试
测试所有新增功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app.database import Database
from app.skills import MockSkills, SKILLS
from app.models import ChatResponse, AIDecisionRecord

class TestDay2Features(unittest.TestCase):
    """Day 2 功能测试"""

    def setUp(self):
        """每个测试前的准备"""
        self.db = Database(db_path=":memory:")  # 使用内存数据库测试

    def test_database_init(self):
        """测试数据库初始化"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn("ai_decisions", tables)
        self.assertIn("system_metrics", tables)
        self.assertIn("chat_history", tables)

        conn.close()
        print("✅ 数据库初始化测试通过")

    def test_save_decision(self):
        """测试保存决策记录"""
        decision_id = self.db.save_decision(
            user_input="测试输入",
            intent="测试意图",
            action="test_action",
            result={"status": "success"},
            user_id="test_user",
            success=True,
            execution_time_ms=100.5,
            llm_cost=0.001
        )

        self.assertIsNotNone(decision_id)
        self.assertGreater(decision_id, 0)

        # 验证数据
        recent = self.db.get_recent_decisions(limit=1)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["user_input"], "测试输入")
        self.assertEqual(recent[0]["intent"], "测试意图")

        print("✅ 保存决策记录测试通过")

    def test_mock_skills(self):
        """测试Mock技能"""
        # 测试订单查询
        order = MockSkills.get_order("12345")
        self.assertEqual(order["order_id"], "12345")
        self.assertEqual(order["status"], "已发货")
        print(f"  订单查询: {order}")

        # 测试库存查询
        inventory = MockSkills.query_inventory("A")
        self.assertEqual(inventory["product_id"], "A")
        self.assertEqual(inventory["stock"], 100)
        print(f"  库存查询: {inventory}")

        # 测试邮件发送
        email = MockSkills.send_email("test@example.com", "测试内容")
        self.assertTrue(email["sent"])
        self.assertEqual(email["to"], "test@example.com")
        print(f"  邮件发送: {email}")

        # 测试延迟订单
        delayed_order = MockSkills.get_order("999")
        self.assertEqual(delayed_order["status"], "配送延迟")
        print(f"  延迟订单: {delayed_order}")

        # 测试缺货产品
        out_of_stock = MockSkills.query_inventory("C")
        self.assertEqual(out_of_stock["status"], "缺货")
        print(f"  缺货产品: {out_of_stock}")

        print("✅ Mock技能测试通过")

    def test_skills_registry(self):
        """测试技能注册表"""
        self.assertIn("get_order", SKILLS)
        self.assertIn("query_inventory", SKILLS)
        self.assertIn("send_email", SKILLS)
        self.assertIn("query_logistics", SKILLS)
        self.assertIn("generate_apology", SKILLS)
        self.assertIn("offer_compensation", SKILLS)

        # 测试调用
        result = SKILLS["get_order"]("12345")
        self.assertEqual(result["order_id"], "12345")

        print(f"✅ 技能注册表测试通过（共{len(SKILLS)}个技能）")

    def test_stats(self):
        """测试统计功能"""
        # 添加一些测试数据
        for i in range(5):
            self.db.save_decision(
                user_input=f"测试{i}",
                intent="测试",
                action="test",
                result={"status": "ok"},
                success=True,
                execution_time_ms=100.0,
                llm_cost=0.001
            )

        # 添加一个失败记录
        self.db.save_decision(
            user_input="失败测试",
            intent="测试",
            action="test",
            result={"error": "test"},
            success=False
        )

        stats = self.db.get_today_stats()
        self.assertEqual(stats["today_total"], 6)
        self.assertEqual(stats["today_success"], 5)
        self.assertAlmostEqual(stats["success_rate"], 5/6, places=2)

        print(f"✅ 统计功能测试通过")
        print(f"  今日总数: {stats['today_total']}")
        print(f"  成功数: {stats['today_success']}")
        print(f"  成功率: {stats['success_rate']:.1%}")

    def test_intent_distribution(self):
        """测试意图分布"""
        # 添加不同意图的记录
        intents = ["查询订单", "查询库存", "发送邮件", "查询订单", "查询库存", "查询订单"]
        for intent in intents:
            self.db.save_decision(
                user_input=f"测试{intent}",
                intent=intent,
                action="test",
                result={"status": "ok"}
            )

        dist = self.db.get_intent_distribution(days=7)
        self.assertGreater(len(dist), 0)

        # 验证查询订单是最多的
        top_intent = dist[0]
        self.assertEqual(top_intent["intent"], "查询订单")
        self.assertEqual(top_intent["count"], 3)

        print("✅ 意图分布测试通过")
        for item in dist:
            print(f"  {item['intent']}: {item['count']}次")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Day 2 功能测试")
    print("=" * 60)
    print()

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay2Features)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
