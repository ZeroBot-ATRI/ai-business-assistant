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


class PromotionSkill:
    """促销技能 - 真实API对接版本"""

    def __init__(self, api_base: str = ORDER_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"PromotionSkill initialized with API: {self.api_base}")

    def query_promotions(self, product_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        查询促销活动

        Args:
            product_id: 产品ID（可选）
            status: 促销状态（可选）

        Returns:
            促销活动列表
        """
        url = f"{self.api_base}/api/promotions"
        params = {}
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status

        logger.info(f"Fetching promotions from {url} with params: {params}")

        try:
            response = self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Promotions fetched successfully: {data.get('total', 0)} items")
                return {
                    "success": True,
                    **data
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code}"
                }

        except httpx.TimeoutException:
            logger.error("Timeout fetching promotions")
            return {
                "success": False,
                "error": "请求超时"
            }
        except httpx.ConnectError:
            logger.error("Connection error fetching promotions")
            return {
                "success": False,
                "error": "无法连接到促销系统API"
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching promotions: {e}")
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


class CustomerSkill:
    """客户信息技能 - 真实API对接版本"""

    def __init__(self, api_base: str = ORDER_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"CustomerSkill initialized with API: {self.api_base}")

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        查询客户信息

        Args:
            customer_id: 客户ID

        Returns:
            客户详情字典
        """
        url = f"{self.api_base}/api/customers/{customer_id}"
        logger.info(f"Fetching customer: {customer_id} from {url}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Customer {customer_id} fetched successfully")
                return {
                    "success": True,
                    "customer_id": customer_id,
                    **data
                }
            elif response.status_code == 404:
                logger.warning(f"Customer {customer_id} not found")
                return {
                    "success": False,
                    "customer_id": customer_id,
                    "error": "客户不存在"
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "customer_id": customer_id,
                    "error": f"API错误: {response.status_code}"
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching customer {customer_id}")
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "请求超时"
            }
        except httpx.ConnectError:
            logger.error(f"Connection error for customer {customer_id}")
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "无法连接到客户系统API"
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching customer {customer_id}: {e}")
            return {
                "success": False,
                "customer_id": customer_id,
                "error": f"未知错误: {str(e)}"
            }

    def get_customer_orders(self, customer_id: str) -> Dict[str, Any]:
        """
        查询客户订单历史

        Args:
            customer_id: 客户ID

        Returns:
            客户订单列表
        """
        url = f"{self.api_base}/api/customers/{customer_id}/orders"
        logger.info(f"Fetching orders for customer: {customer_id}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Customer {customer_id} orders fetched: {data.get('total_orders', 0)} orders")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "customer_id": customer_id,
                    "error": "客户不存在"
                }
            else:
                return {
                    "success": False,
                    "customer_id": customer_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Error fetching customer orders: {e}")
            return {
                "success": False,
                "customer_id": customer_id,
                "error": str(e)
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


class RefundSkill:
    """退款处理技能 - 真实API对接版本"""

    def __init__(self, api_base: str = ORDER_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"RefundSkill initialized with API: {self.api_base}")

    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        """
        查询退款申请详情

        Args:
            refund_id: 退款ID

        Returns:
            退款详情字典
        """
        url = f"{self.api_base}/api/refunds/{refund_id}"
        logger.info(f"Fetching refund: {refund_id} from {url}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Refund {refund_id} fetched successfully")
                return {
                    "success": True,
                    "refund_id": refund_id,
                    **data
                }
            elif response.status_code == 404:
                logger.warning(f"Refund {refund_id} not found")
                return {
                    "success": False,
                    "refund_id": refund_id,
                    "error": "退款申请不存在"
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "refund_id": refund_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Unexpected error fetching refund {refund_id}: {e}")
            return {
                "success": False,
                "refund_id": refund_id,
                "error": f"未知错误: {str(e)}"
            }

    def create_refund(self, order_id: str, reason: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        创建退款申请

        Args:
            order_id: 订单ID
            reason: 退款原因
            amount: 退款金额（可选）

        Returns:
            创建的退款申请
        """
        url = f"{self.api_base}/api/refunds"
        params = {
            "order_id": order_id,
            "reason": reason
        }
        if amount is not None:
            params["amount"] = amount

        logger.info(f"Creating refund for order {order_id}: {reason}")

        try:
            response = self.client.post(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Refund created successfully: {data.get('refund', {}).get('refund_id')}")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "order_id": order_id,
                    "error": "订单不存在"
                }
            else:
                return {
                    "success": False,
                    "order_id": order_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Error creating refund: {e}")
            return {
                "success": False,
                "order_id": order_id,
                "error": str(e)
            }

    def approve_refund(self, refund_id: str) -> Dict[str, Any]:
        """
        审批退款申请

        Args:
            refund_id: 退款ID

        Returns:
            审批结果
        """
        url = f"{self.api_base}/api/refunds/{refund_id}/approve"
        logger.info(f"Approving refund: {refund_id}")

        try:
            response = self.client.post(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Refund {refund_id} approved successfully")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "refund_id": refund_id,
                    "error": "退款申请不存在"
                }
            elif response.status_code == 400:
                error_data = response.json()
                return {
                    "success": False,
                    "refund_id": refund_id,
                    "error": error_data.get("detail", "无法审批退款")
                }
            else:
                return {
                    "success": False,
                    "refund_id": refund_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Error approving refund: {e}")
            return {
                "success": False,
                "refund_id": refund_id,
                "error": str(e)
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


class ReplenishmentSkill:
    """补货技能 - 真实API对接版本"""

    def __init__(self, api_base: str = INVENTORY_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"ReplenishmentSkill initialized with API: {self.api_base}")

    def get_replenishment_suggestion(self, product_id: str) -> Dict[str, Any]:
        """
        获取智能补货建议

        Args:
            product_id: 产品ID

        Returns:
            补货建议字典
        """
        url = f"{self.api_base}/api/replenishment/suggest/{product_id}"
        logger.info(f"Getting replenishment suggestion for product: {product_id}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Suggestion for {product_id}: {data.get('reason')}")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 404:
                logger.warning(f"Product {product_id} not found")
                return {
                    "success": False,
                    "product_id": product_id,
                    "error": "产品不存在"
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "product_id": product_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Unexpected error getting suggestion: {e}")
            return {
                "success": False,
                "product_id": product_id,
                "error": f"未知错误: {str(e)}"
            }

    def create_replenishment(self, product_id: str, quantity: int, priority: str = "正常") -> Dict[str, Any]:
        """
        创建补货申请

        Args:
            product_id: 产品ID
            quantity: 补货数量
            priority: 优先级（正常/高/紧急）

        Returns:
            创建的补货申请
        """
        url = f"{self.api_base}/api/replenishment"
        params = {
            "product_id": product_id,
            "quantity": quantity,
            "priority": priority
        }

        logger.info(f"Creating replenishment for product {product_id}: {quantity} units, priority: {priority}")

        try:
            response = self.client.post(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Replenishment created: {data.get('replenishment', {}).get('replenishment_id')}")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "product_id": product_id,
                    "error": "产品不存在"
                }
            else:
                return {
                    "success": False,
                    "product_id": product_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Error creating replenishment: {e}")
            return {
                "success": False,
                "product_id": product_id,
                "error": str(e)
            }

    def get_replenishment(self, replenishment_id: str) -> Dict[str, Any]:
        """
        查询补货申请详情

        Args:
            replenishment_id: 补货申请ID

        Returns:
            补货申请详情
        """
        url = f"{self.api_base}/api/replenishment/{replenishment_id}"
        logger.info(f"Fetching replenishment: {replenishment_id}")

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Replenishment {replenishment_id} fetched successfully")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "replenishment_id": replenishment_id,
                    "error": "补货申请不存在"
                }
            else:
                return {
                    "success": False,
                    "replenishment_id": replenishment_id,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Error fetching replenishment: {e}")
            return {
                "success": False,
                "replenishment_id": replenishment_id,
                "error": str(e)
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


class ReportSkill:
    """报表分析技能 - 真实API对接版本"""

    def __init__(self, api_base: str = ORDER_API_BASE, timeout: float = DEFAULT_TIMEOUT):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.info(f"ReportSkill initialized with API: {self.api_base}")

    def generate_report(self, report_type: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        生成业务报表

        Args:
            report_type: 报表类型（sales/inventory/customer）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            报表数据
        """
        url = f"{self.api_base}/api/reports/{report_type}"
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        logger.info(f"Generating report: {report_type}")

        try:
            response = self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Report generated successfully: {report_type}")
                return {
                    "success": True,
                    **data
                }
            elif response.status_code == 400:
                error_data = response.json()
                return {
                    "success": False,
                    "report_type": report_type,
                    "error": error_data.get("detail", "不支持的报表类型")
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "report_type": report_type,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Unexpected error generating report: {e}")
            return {
                "success": False,
                "report_type": report_type,
                "error": f"未知错误: {str(e)}"
            }

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


# 创建全局技能实例
order_skill = OrderSkill()
inventory_skill = InventorySkill()
logistics_skill = LogisticsSkill()
promotion_skill = PromotionSkill()
customer_skill = CustomerSkill()
refund_skill = RefundSkill()
replenishment_skill = ReplenishmentSkill()
report_skill = ReportSkill()

# 创建技能字典供main.py使用（保持与Mock版本相同的接口）
REAL_SKILLS = {
    # 原有技能
    "get_order": order_skill.get_order,
    "query_inventory": inventory_skill.query_inventory,
    "query_logistics": logistics_skill.query_logistics,
    # 新增技能
    "query_promotions": promotion_skill.query_promotions,
    "get_customer": customer_skill.get_customer,
    "get_customer_orders": customer_skill.get_customer_orders,
    "get_refund": refund_skill.get_refund,
    "create_refund": refund_skill.create_refund,
    "approve_refund": refund_skill.approve_refund,
    "get_replenishment_suggestion": replenishment_skill.get_replenishment_suggestion,
    "create_replenishment": replenishment_skill.create_replenishment,
    "get_replenishment": replenishment_skill.get_replenishment,
    "generate_report": report_skill.generate_report,
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
