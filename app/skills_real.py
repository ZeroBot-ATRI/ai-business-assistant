"""
app/skills_real.py - 真实技能库（Day 4）

通过HTTP API对接内部系统
"""
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API配置（从环境变量读取，默认使用Mock API Server）
ORDER_API_BASE = os.getenv("ORDER_API_BASE", "http://localhost:9000")
INVENTORY_API_BASE = os.getenv("INVENTORY_API_BASE", "http://localhost:9000")
LOGISTICS_API_BASE = os.getenv("LOGISTICS_API_BASE", "http://localhost:9000")

# HTTP超时配置
DEFAULT_TIMEOUT = 10.0  # 10秒超时
MAX_RETRIES = 2  # 最多重试2次


class OrderSkill:
    """订单技能 - 真实API对接版本"""

    def __init__(self, api_base: str = ORDER_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"OrderSkill initialized with API: {self.api_base}")

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        查询订单信息

        Args:
            order_id: 订单ID

        Returns:
            订单详情字典，包含订单状态、客户信息、商品等
        """
        url = f"{self.api_base}/api/orders/{order_id}"
        logger.info(f"Fetching order: {order_id} from {url}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Order {order_id} fetched successfully")
                return {
                    "success": True,
                    "order_id": order_id,
                    **data
                }
            elif response.status_code == 404:
                logger.warning(f"Order {order_id} not found")
                return {
                    "success": False,
                    "order_id": order_id,
                    "error": "订单不存在",
                    "status": "未找到"
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "order_id": order_id,
                    "error": f"API错误: {response.status_code}",
                    "status": "查询失败"
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching order {order_id}")
            return {
                "success": False,
                "order_id": order_id,
                "error": "请求超时",
                "status": "超时"
            }
        except httpx.ConnectError:
            logger.error(f"Connection error for order {order_id}")
            return {
                "success": False,
                "order_id": order_id,
                "error": "无法连接到订单系统API",
                "status": "连接失败"
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching order {order_id}: {e}")
            return {
                "success": False,
                "order_id": order_id,
                "error": f"未知错误: {str(e)}",
                "status": "错误"
            }

    def list_orders(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        列出订单（可选按状态筛选）

        Args:
            status: 订单状态（可选）

        Returns:
            订单列表
        """
        url = f"{self.api_base}/api/orders"
        params = {"status": status} if status else {}

        try:
            response = self.client.get(url, params=params)
            if response.status_code == 200:
                return {
                    "success": True,
                    **response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error listing orders: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


class InventorySkill:
    """库存技能 - 真实API对接版本"""

    def __init__(self, api_base: str = INVENTORY_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"InventorySkill initialized with API: {self.api_base}")

    def query_inventory(self, product_id: str) -> Dict[str, Any]:
        """
        查询库存信息

        Args:
            product_id: 产品ID

        Returns:
            库存详情字典，包含库存数量、仓库位置等
        """
        url = f"{self.api_base}/api/inventory/{product_id}"
        logger.info(f"Fetching inventory: {product_id} from {url}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Inventory {product_id} fetched successfully")
                return {
                    "success": True,
                    "product_id": product_id,
                    **data
                }
            elif response.status_code == 404:
                logger.warning(f"Product {product_id} not found")
                return {
                    "success": False,
                    "product_id": product_id,
                    "error": "产品不存在",
                    "stock": 0,
                    "status": "未找到"
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "product_id": product_id,
                    "error": f"API错误: {response.status_code}",
                    "status": "查询失败"
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching inventory {product_id}")
            return {
                "success": False,
                "product_id": product_id,
                "error": "请求超时",
                "status": "超时"
            }
        except httpx.ConnectError:
            logger.error(f"Connection error for inventory {product_id}")
            return {
                "success": False,
                "product_id": product_id,
                "error": "无法连接到库存系统API",
                "status": "连接失败"
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching inventory {product_id}: {e}")
            return {
                "success": False,
                "product_id": product_id,
                "error": f"未知错误: {str(e)}",
                "status": "错误"
            }

    def list_inventory(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        列出库存（可选按状态筛选）

        Args:
            status: 库存状态（可选）

        Returns:
            库存列表
        """
        url = f"{self.api_base}/api/inventory"
        params = {"status": status} if status else {}

        try:
            response = self.client.get(url, params=params)
            if response.status_code == 200:
                return {
                    "success": True,
                    **response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error listing inventory: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


class LogisticsSkill:
    """物流技能 - 真实API对接版本"""

    def __init__(self, api_base: str = LOGISTICS_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"LogisticsSkill initialized with API: {self.api_base}")

    def query_logistics(self, tracking_number: str) -> Dict[str, Any]:
        """
        查询物流信息

        Args:
            tracking_number: 物流单号

        Returns:
            物流详情字典
        """
        url = f"{self.api_base}/api/logistics/{tracking_number}"
        logger.info(f"Fetching logistics: {tracking_number} from {url}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Logistics {tracking_number} fetched successfully")
                return {
                    "success": True,
                    "tracking": tracking_number,
                    **data
                }
            elif response.status_code == 404:
                logger.warning(f"Tracking {tracking_number} not found")
                return {
                    "success": False,
                    "tracking": tracking_number,
                    "error": "物流信息未找到",
                    "status": "未找到"
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "tracking": tracking_number,
                    "error": f"API错误: {response.status_code}",
                    "status": "查询失败"
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching logistics {tracking_number}")
            return {
                "success": False,
                "tracking": tracking_number,
                "error": "请求超时",
                "status": "超时"
            }
        except httpx.ConnectError:
            logger.error(f"Connection error for logistics {tracking_number}")
            return {
                "success": False,
                "tracking": tracking_number,
                "error": "无法连接到物流系统API",
                "status": "连接失败"
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching logistics {tracking_number}: {e}")
            return {
                "success": False,
                "tracking": tracking_number,
                "error": f"未知错误: {str(e)}",
                "status": "错误"
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


# 创建全局技能实例
order_skill = OrderSkill()
inventory_skill = InventorySkill()
logistics_skill = LogisticsSkill()

# 创建技能字典供main.py使用（保持与Mock版本相同的接口）
REAL_SKILLS = {
    "get_order": order_skill.get_order,
    "query_inventory": inventory_skill.query_inventory,
    "query_logistics": logistics_skill.query_logistics,
}


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("测试真实技能API对接")
    print("=" * 60)
    print(f"订单API: {ORDER_API_BASE}")
    print(f"库存API: {INVENTORY_API_BASE}")
    print(f"物流API: {LOGISTICS_API_BASE}")
    print("=" * 60)

    # 测试订单查询
    print("\n1. 测试订单查询:")
    result = order_skill.get_order("12345")
    print(f"   订单12345: {result.get('status', 'Error')}")

    # 测试库存查询
    print("\n2. 测试库存查询:")
    result = inventory_skill.query_inventory("A")
    print(f"   产品A: 库存 {result.get('stock', 'Error')} - {result.get('status', 'Error')}")

    # 测试物流查询
    print("\n3. 测试物流查询:")
    result = logistics_skill.query_logistics("SF1234567890")
    print(f"   快递SF1234567890: {result.get('status', 'Error')}")

    # 测试不存在的订单
    print("\n4. 测试不存在的订单:")
    result = order_skill.get_order("99999")
    print(f"   订单99999: {result.get('error', 'Error')}")

    print("\n" + "=" * 60)
    print("测试完成！")
