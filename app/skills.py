# app/skills.py - 技能库（Day 2 Mock版本）
from datetime import datetime
from typing import Dict, Any
import random

class MockSkills:
    """Mock技能类 - Day 4-5会替换为真实API"""

    # 模拟订单数据库
    MOCK_ORDERS = {
        "12345": {
            "order_id": "12345",
            "status": "已发货",
            "tracking": "SF1234567890",
            "customer_email": "customer@example.com",
            "create_time": "2025-01-20 10:30:00",
            "amount": 299.00,
            "products": ["产品A x 2", "产品B x 1"]
        },
        "999": {
            "order_id": "999",
            "status": "配送延迟",
            "tracking": "YT9876543210",
            "customer_email": "delayed@example.com",
            "create_time": "2025-01-15 14:20:00",
            "amount": 599.00,
            "delay_reason": "天气原因",
            "products": ["产品C x 1"]
        },
        "888": {
            "order_id": "888",
            "status": "待发货",
            "tracking": None,
            "customer_email": "pending@example.com",
            "create_time": "2025-01-26 16:45:00",
            "amount": 159.00,
            "products": ["产品D x 3"]
        }
    }

    # 模拟库存数据库
    MOCK_INVENTORY = {
        "A": {
            "product_id": "A",
            "product_name": "产品A",
            "stock": 100,
            "warehouse": "深圳仓",
            "threshold": 20,
            "status": "正常"
        },
        "B": {
            "product_id": "B",
            "product_name": "产品B",
            "stock": 15,
            "warehouse": "上海仓",
            "threshold": 20,
            "status": "库存不足"
        },
        "C": {
            "product_id": "C",
            "product_name": "产品C",
            "stock": 0,
            "warehouse": "北京仓",
            "threshold": 10,
            "status": "缺货"
        },
        "D": {
            "product_id": "D",
            "product_name": "产品D",
            "stock": 500,
            "warehouse": "广州仓",
            "threshold": 50,
            "status": "正常"
        }
    }

    @staticmethod
    def get_order(order_id: str) -> Dict[str, Any]:
        """查询订单（Mock）"""
        order = MockSkills.MOCK_ORDERS.get(order_id)
        if order:
            return order.copy()
        else:
            return {
                "order_id": order_id,
                "error": "订单不存在",
                "status": "未找到"
            }

    @staticmethod
    def query_inventory(product_id: str) -> Dict[str, Any]:
        """查询库存（Mock）"""
        inventory = MockSkills.MOCK_INVENTORY.get(product_id)
        if inventory:
            return inventory.copy()
        else:
            return {
                "product_id": product_id,
                "error": "产品不存在",
                "stock": 0,
                "status": "未找到"
            }

    @staticmethod
    def send_email(to: str, content: str, subject: str = "系统通知") -> Dict[str, Any]:
        """发送邮件（Mock）"""
        # 模拟邮件发送
        return {
            "sent": True,
            "to": to,
            "subject": subject,
            "content": content[:100] + "..." if len(content) > 100 else content,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"mock-{random.randint(1000, 9999)}"
        }

    @staticmethod
    def update_order_status(order_id: str, status: str) -> Dict[str, Any]:
        """更新订单状态（Mock - 为后续扩展准备）"""
        if order_id in MockSkills.MOCK_ORDERS:
            return {
                "success": True,
                "order_id": order_id,
                "old_status": MockSkills.MOCK_ORDERS[order_id]["status"],
                "new_status": status,
                "updated_at": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "订单不存在"
            }

    @staticmethod
    def query_logistics(tracking_number: str) -> Dict[str, Any]:
        """查询物流（Mock - 为Day 18-22 SOP准备）"""
        # 模拟物流查询
        mock_logistics = {
            "SF1234567890": {
                "tracking": "SF1234567890",
                "carrier": "顺丰速运",
                "status": "运输中",
                "location": "深圳分拨中心",
                "estimated_delivery": "2025-01-28"
            },
            "YT9876543210": {
                "tracking": "YT9876543210",
                "carrier": "圆通速递",
                "status": "delayed",
                "location": "北京转运中心",
                "delay_reason": "天气原因",
                "estimated_delivery": "2025-01-30"
            }
        }
        return mock_logistics.get(tracking_number, {
            "tracking": tracking_number,
            "error": "物流信息未找到"
        })

    @staticmethod
    def generate_apology(order_id: str, reason: str) -> Dict[str, Any]:
        """生成道歉信（Mock - 为Day 18-22 SOP准备）"""
        templates = {
            "天气原因": f"尊敬的客户，您的订单{order_id}因天气原因配送延迟，我们深表歉意。我们会尽快为您配送。",
            "库存不足": f"尊敬的客户，您的订单{order_id}因库存不足暂时无法发货，我们正在加急补货，预计3日内发货。",
            "default": f"尊敬的客户，您的订单{order_id}处理出现延迟，我们深表歉意，正在加急处理中。"
        }
        content = templates.get(reason, templates["default"])
        return {
            "order_id": order_id,
            "reason": reason,
            "content": content,
            "generated_at": datetime.now().isoformat()
        }

    @staticmethod
    def offer_compensation(user_id: str, policy: str = "standard_delay") -> Dict[str, Any]:
        """提供补偿（Mock - 为Day 18-22 SOP准备）"""
        compensation_policies = {
            "standard_delay": {
                "type": "优惠券",
                "value": 20,
                "description": "20元无门槛优惠券"
            },
            "severe_delay": {
                "type": "优惠券",
                "value": 50,
                "description": "50元无门槛优惠券"
            },
            "out_of_stock": {
                "type": "积分",
                "value": 200,
                "description": "200积分补偿"
            }
        }
        comp = compensation_policies.get(policy, compensation_policies["standard_delay"])
        return {
            "user_id": user_id,
            "policy": policy,
            "compensation": comp,
            "issued_at": datetime.now().isoformat()
        }


# 创建技能字典供main.py使用
SKILLS = {
    "get_order": MockSkills.get_order,
    "query_inventory": MockSkills.query_inventory,
    "send_email": MockSkills.send_email,
    "update_order_status": MockSkills.update_order_status,
    "query_logistics": MockSkills.query_logistics,
    "generate_apology": MockSkills.generate_apology,
    "offer_compensation": MockSkills.offer_compensation
}
