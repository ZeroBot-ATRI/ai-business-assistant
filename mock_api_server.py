"""
Mock API Server - 模拟内部订单和库存系统API
用于Day 4演示真实的API对接

运行方式:
    uvicorn mock_api_server:app --port 9000
"""
from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI(title="Mock Internal API", version="1.0.0")

# 模拟订单数据库
ORDERS_DB = {
    "12345": {
        "order_id": "12345",
        "status": "已发货",
        "tracking": "SF1234567890",
        "customer_name": "张三",
        "customer_email": "customer@example.com",
        "customer_phone": "13800138000",
        "create_time": "2025-01-20 10:30:00",
        "ship_time": "2025-01-21 15:20:00",
        "amount": 299.00,
        "products": [
            {"name": "产品A", "quantity": 2, "price": 99.50},
            {"name": "产品B", "quantity": 1, "price": 100.00}
        ],
        "address": "广东省深圳市南山区科技园"
    },
    "999": {
        "order_id": "999",
        "status": "配送延迟",
        "tracking": "YT9876543210",
        "customer_name": "李四",
        "customer_email": "delayed@example.com",
        "customer_phone": "13900139000",
        "create_time": "2025-01-15 14:20:00",
        "ship_time": "2025-01-16 09:00:00",
        "amount": 599.00,
        "delay_reason": "天气原因",
        "products": [
            {"name": "产品C", "quantity": 1, "price": 599.00}
        ],
        "address": "北京市朝阳区望京街道"
    },
    "888": {
        "order_id": "888",
        "status": "待发货",
        "tracking": None,
        "customer_name": "王五",
        "customer_email": "pending@example.com",
        "customer_phone": "13700137000",
        "create_time": "2025-01-26 16:45:00",
        "ship_time": None,
        "amount": 159.00,
        "products": [
            {"name": "产品D", "quantity": 3, "price": 53.00}
        ],
        "address": "上海市浦东新区张江高科"
    },
    "777": {
        "order_id": "777",
        "status": "已完成",
        "tracking": "JD8888999900",
        "customer_name": "赵六",
        "customer_email": "completed@example.com",
        "customer_phone": "13600136000",
        "create_time": "2025-01-10 11:00:00",
        "ship_time": "2025-01-11 10:00:00",
        "delivery_time": "2025-01-13 14:30:00",
        "amount": 899.00,
        "products": [
            {"name": "产品E", "quantity": 1, "price": 899.00}
        ],
        "address": "广州市天河区珠江新城"
    }
}

# 模拟库存数据库
INVENTORY_DB = {
    "A": {
        "product_id": "A",
        "product_name": "产品A",
        "sku": "SKU-A-001",
        "stock": 100,
        "warehouse": "深圳仓",
        "warehouse_address": "深圳市宝安区物流园",
        "threshold": 20,
        "status": "正常",
        "price": 99.50,
        "reserved": 10,  # 已预留库存
        "available": 90   # 可用库存
    },
    "B": {
        "product_id": "B",
        "product_name": "产品B",
        "sku": "SKU-B-002",
        "stock": 15,
        "warehouse": "上海仓",
        "warehouse_address": "上海市嘉定区仓储中心",
        "threshold": 20,
        "status": "库存不足",
        "price": 100.00,
        "reserved": 5,
        "available": 10
    },
    "C": {
        "product_id": "C",
        "product_name": "产品C",
        "sku": "SKU-C-003",
        "stock": 0,
        "warehouse": "北京仓",
        "warehouse_address": "北京市大兴区物流基地",
        "threshold": 10,
        "status": "缺货",
        "price": 599.00,
        "reserved": 0,
        "available": 0
    },
    "D": {
        "product_id": "D",
        "product_name": "产品D",
        "sku": "SKU-D-004",
        "stock": 500,
        "warehouse": "广州仓",
        "warehouse_address": "广州市白云区物流中心",
        "threshold": 50,
        "status": "正常",
        "price": 53.00,
        "reserved": 50,
        "available": 450
    },
    "E": {
        "product_id": "E",
        "product_name": "产品E",
        "sku": "SKU-E-005",
        "stock": 200,
        "warehouse": "杭州仓",
        "warehouse_address": "杭州市余杭区仓储园",
        "threshold": 30,
        "status": "正常",
        "price": 899.00,
        "reserved": 20,
        "available": 180
    }
}

# 模拟物流信息数据库
LOGISTICS_DB = {
    "SF1234567890": {
        "tracking": "SF1234567890",
        "carrier": "顺丰速运",
        "carrier_phone": "95338",
        "status": "运输中",
        "current_location": "深圳分拨中心",
        "estimated_delivery": "2025-01-28",
        "history": [
            {"time": "2025-01-21 15:30", "location": "深圳市南山区", "status": "已揽收"},
            {"time": "2025-01-21 18:00", "location": "深圳分拨中心", "status": "分拣中"},
            {"time": "2025-01-22 08:00", "location": "深圳分拨中心", "status": "已发出"}
        ]
    },
    "YT9876543210": {
        "tracking": "YT9876543210",
        "carrier": "圆通速递",
        "carrier_phone": "95554",
        "status": "延迟",
        "current_location": "北京转运中心",
        "delay_reason": "天气原因",
        "estimated_delivery": "2025-01-30",
        "history": [
            {"time": "2025-01-16 09:30", "location": "北京市朝阳区", "status": "已揽收"},
            {"time": "2025-01-16 14:00", "location": "北京转运中心", "status": "到达"},
            {"time": "2025-01-17 10:00", "location": "北京转运中心", "status": "因天气原因延迟"}
        ]
    },
    "JD8888999900": {
        "tracking": "JD8888999900",
        "carrier": "京东物流",
        "carrier_phone": "950616",
        "status": "已签收",
        "current_location": "广州市天河区",
        "delivery_time": "2025-01-13 14:30:00",
        "receiver": "赵六",
        "estimated_delivery": "2025-01-13",
        "history": [
            {"time": "2025-01-11 10:30", "location": "广州市番禺区", "status": "已揽收"},
            {"time": "2025-01-11 15:00", "location": "广州分拨中心", "status": "分拣完成"},
            {"time": "2025-01-12 09:00", "location": "天河区配送站", "status": "派送中"},
            {"time": "2025-01-13 14:30", "location": "天河区珠江新城", "status": "已签收"}
        ]
    }
}

# 模拟促销活动数据库
PROMOTIONS_DB = {
    "PROMO001": {
        "promo_id": "PROMO001",
        "name": "新春特惠",
        "type": "折扣",
        "discount": 0.8,  # 8折
        "start_date": "2025-01-20",
        "end_date": "2025-02-10",
        "status": "进行中",
        "products": ["A", "B", "E"],
        "min_amount": 200.00,
        "description": "全场8折，满200元可用"
    },
    "PROMO002": {
        "promo_id": "PROMO002",
        "name": "满减优惠",
        "type": "满减",
        "discount_amount": 50.00,
        "start_date": "2025-01-25",
        "end_date": "2025-02-05",
        "status": "进行中",
        "products": ["C", "D"],
        "min_amount": 300.00,
        "description": "满300减50"
    },
    "PROMO003": {
        "promo_id": "PROMO003",
        "name": "限时秒杀",
        "type": "特价",
        "special_price": 399.00,
        "start_date": "2025-01-28",
        "end_date": "2025-01-28",
        "status": "即将开始",
        "products": ["C"],
        "description": "产品C限时秒杀价399元"
    }
}

# 模拟客户信息数据库
CUSTOMERS_DB = {
    "CUST001": {
        "customer_id": "CUST001",
        "name": "张三",
        "email": "customer@example.com",
        "phone": "13800138000",
        "level": "金牌会员",
        "points": 1500,
        "total_orders": 12,
        "total_amount": 5680.00,
        "register_date": "2024-06-15",
        "last_order_date": "2025-01-20",
        "address": [
            {"id": 1, "address": "广东省深圳市南山区科技园", "is_default": True},
            {"id": 2, "address": "广东省广州市天河区珠江新城", "is_default": False}
        ]
    },
    "CUST002": {
        "customer_id": "CUST002",
        "name": "李四",
        "email": "delayed@example.com",
        "phone": "13900139000",
        "level": "银牌会员",
        "points": 800,
        "total_orders": 6,
        "total_amount": 2340.00,
        "register_date": "2024-09-20",
        "last_order_date": "2025-01-15",
        "address": [
            {"id": 1, "address": "北京市朝阳区望京街道", "is_default": True}
        ]
    },
    "CUST003": {
        "customer_id": "CUST003",
        "name": "王五",
        "email": "pending@example.com",
        "phone": "13700137000",
        "level": "普通会员",
        "points": 200,
        "total_orders": 2,
        "total_amount": 458.00,
        "register_date": "2025-01-10",
        "last_order_date": "2025-01-26",
        "address": [
            {"id": 1, "address": "上海市浦东新区张江高科", "is_default": True}
        ]
    }
}

# 模拟退款申请数据库
REFUNDS_DB = {
    "RF001": {
        "refund_id": "RF001",
        "order_id": "777",
        "customer_id": "CUST006",
        "amount": 899.00,
        "reason": "不想要了",
        "status": "已退款",
        "create_time": "2025-01-14 10:00:00",
        "approve_time": "2025-01-14 11:30:00",
        "refund_time": "2025-01-14 15:00:00",
        "approve_by": "system",
        "notes": "7天无理由退货"
    },
    "RF002": {
        "refund_id": "RF002",
        "order_id": "999",
        "customer_id": "CUST002",
        "amount": 599.00,
        "reason": "配送延迟",
        "status": "处理中",
        "create_time": "2025-01-25 14:20:00",
        "approve_time": None,
        "refund_time": None,
        "approve_by": None,
        "notes": "因物流延迟申请退款"
    }
}

# 模拟补货申请数据库
REPLENISHMENT_DB = {
    "REP001": {
        "replenishment_id": "REP001",
        "product_id": "B",
        "product_name": "产品B",
        "current_stock": 15,
        "requested_quantity": 100,
        "warehouse": "上海仓",
        "status": "已批准",
        "priority": "高",
        "create_time": "2025-01-25 09:00:00",
        "approve_time": "2025-01-25 10:30:00",
        "expected_arrival": "2025-01-30"
    },
    "REP002": {
        "replenishment_id": "REP002",
        "product_id": "C",
        "product_name": "产品C",
        "current_stock": 0,
        "requested_quantity": 50,
        "warehouse": "北京仓",
        "status": "待审批",
        "priority": "紧急",
        "create_time": "2025-01-26 14:00:00",
        "approve_time": None,
        "expected_arrival": "2025-02-01"
    }
}


@app.get("/")
async def root():
    """API根路径"""
    return {
        "service": "Mock Internal API",
        "version": "2.0.0",
        "endpoints": {
            "orders": "/api/orders/{order_id}",
            "inventory": "/api/inventory/{product_id}",
            "logistics": "/api/logistics/{tracking}",
            "promotions": "/api/promotions",
            "customers": "/api/customers/{customer_id}",
            "refunds": "/api/refunds/{refund_id}",
            "replenishment": "/api/replenishment/{replenishment_id}",
            "reports": "/api/reports/{report_type}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str) -> Dict[str, Any]:
    """
    获取订单信息

    Args:
        order_id: 订单ID

    Returns:
        订单详情

    Raises:
        HTTPException: 订单不存在时返回404
    """
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"订单 {order_id} 不存在")

    # 添加查询时间戳
    result = order.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


@app.get("/api/inventory/{product_id}")
async def get_inventory(product_id: str) -> Dict[str, Any]:
    """
    获取库存信息

    Args:
        product_id: 产品ID

    Returns:
        库存详情

    Raises:
        HTTPException: 产品不存在时返回404
    """
    inventory = INVENTORY_DB.get(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail=f"产品 {product_id} 不存在")

    # 添加查询时间戳
    result = inventory.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


@app.get("/api/logistics/{tracking}")
async def get_logistics(tracking: str) -> Dict[str, Any]:
    """
    获取物流信息

    Args:
        tracking: 物流单号

    Returns:
        物流详情

    Raises:
        HTTPException: 物流信息不存在时返回404
    """
    logistics = LOGISTICS_DB.get(tracking)
    if not logistics:
        raise HTTPException(status_code=404, detail=f"物流单号 {tracking} 不存在")

    # 添加查询时间戳
    result = logistics.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


@app.get("/api/orders")
async def list_orders(status: str = None) -> Dict[str, Any]:
    """
    列出订单（可选按状态筛选）

    Args:
        status: 订单状态（可选）

    Returns:
        订单列表
    """
    orders = list(ORDERS_DB.values())
    if status:
        orders = [o for o in orders if o["status"] == status]

    return {
        "total": len(orders),
        "orders": orders,
        "query_time": datetime.now().isoformat()
    }


@app.get("/api/inventory")
async def list_inventory(status: str = None) -> Dict[str, Any]:
    """
    列出库存（可选按状态筛选）

    Args:
        status: 库存状态（可选）

    Returns:
        库存列表
    """
    inventory = list(INVENTORY_DB.values())
    if status:
        inventory = [i for i in inventory if i["status"] == status]

    return {
        "total": len(inventory),
        "inventory": inventory,
        "query_time": datetime.now().isoformat()
    }


# ==================== 促销相关API ====================

@app.get("/api/promotions")
async def list_promotions(status: str = None, product_id: str = None) -> Dict[str, Any]:
    """
    列出促销活动

    Args:
        status: 促销状态（可选）
        product_id: 产品ID（可选，查询该产品相关的促销）

    Returns:
        促销活动列表
    """
    promotions = list(PROMOTIONS_DB.values())

    if status:
        promotions = [p for p in promotions if p["status"] == status]

    if product_id:
        promotions = [p for p in promotions if product_id in p.get("products", [])]

    return {
        "total": len(promotions),
        "promotions": promotions,
        "query_time": datetime.now().isoformat()
    }


@app.get("/api/promotions/{promo_id}")
async def get_promotion(promo_id: str) -> Dict[str, Any]:
    """
    获取促销活动详情

    Args:
        promo_id: 促销活动ID

    Returns:
        促销活动详情
    """
    promotion = PROMOTIONS_DB.get(promo_id)
    if not promotion:
        raise HTTPException(status_code=404, detail=f"促销活动 {promo_id} 不存在")

    result = promotion.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


# ==================== 客户相关API ====================

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str) -> Dict[str, Any]:
    """
    获取客户信息

    Args:
        customer_id: 客户ID

    Returns:
        客户详情
    """
    customer = CUSTOMERS_DB.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"客户 {customer_id} 不存在")

    result = customer.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


@app.get("/api/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: str) -> Dict[str, Any]:
    """
    获取客户订单历史

    Args:
        customer_id: 客户ID

    Returns:
        客户订单列表
    """
    customer = CUSTOMERS_DB.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"客户 {customer_id} 不存在")

    # 根据客户邮箱查找订单
    customer_orders = [o for o in ORDERS_DB.values() if o.get("customer_email") == customer["email"]]

    return {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "total_orders": len(customer_orders),
        "orders": customer_orders,
        "query_time": datetime.now().isoformat()
    }


# ==================== 退款相关API ====================

@app.get("/api/refunds/{refund_id}")
async def get_refund(refund_id: str) -> Dict[str, Any]:
    """
    获取退款申请详情

    Args:
        refund_id: 退款ID

    Returns:
        退款详情
    """
    refund = REFUNDS_DB.get(refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail=f"退款申请 {refund_id} 不存在")

    result = refund.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


@app.post("/api/refunds")
async def create_refund(order_id: str, reason: str, amount: float = None) -> Dict[str, Any]:
    """
    创建退款申请

    Args:
        order_id: 订单ID
        reason: 退款原因
        amount: 退款金额（可选，默认为订单金额）

    Returns:
        创建的退款申请
    """
    # 检查订单是否存在
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"订单 {order_id} 不存在")

    # 生成退款ID
    refund_id = f"RF{len(REFUNDS_DB) + 1:03d}"

    # 创建退款申请
    refund = {
        "refund_id": refund_id,
        "order_id": order_id,
        "customer_id": "CUST_AUTO",
        "amount": amount or order["amount"],
        "reason": reason,
        "status": "待审批",
        "create_time": datetime.now().isoformat(),
        "approve_time": None,
        "refund_time": None,
        "approve_by": None,
        "notes": f"系统自动创建退款申请，原因：{reason}"
    }

    REFUNDS_DB[refund_id] = refund

    return {
        "success": True,
        "refund": refund,
        "message": f"退款申请 {refund_id} 已创建，等待审批"
    }


@app.post("/api/refunds/{refund_id}/approve")
async def approve_refund(refund_id: str) -> Dict[str, Any]:
    """
    审批退款申请

    Args:
        refund_id: 退款ID

    Returns:
        审批结果
    """
    refund = REFUNDS_DB.get(refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail=f"退款申请 {refund_id} 不存在")

    if refund["status"] != "待审批" and refund["status"] != "处理中":
        raise HTTPException(status_code=400, detail=f"退款申请状态为 {refund['status']}，无法审批")

    # 更新退款状态
    refund["status"] = "已批准"
    refund["approve_time"] = datetime.now().isoformat()
    refund["approve_by"] = "system_auto"

    return {
        "success": True,
        "refund_id": refund_id,
        "message": "退款申请已批准"
    }


# ==================== 补货相关API ====================

@app.get("/api/replenishment/{replenishment_id}")
async def get_replenishment(replenishment_id: str) -> Dict[str, Any]:
    """
    获取补货申请详情

    Args:
        replenishment_id: 补货申请ID

    Returns:
        补货申请详情
    """
    replenishment = REPLENISHMENT_DB.get(replenishment_id)
    if not replenishment:
        raise HTTPException(status_code=404, detail=f"补货申请 {replenishment_id} 不存在")

    result = replenishment.copy()
    result["query_time"] = datetime.now().isoformat()
    return result


@app.post("/api/replenishment")
async def create_replenishment(product_id: str, quantity: int, priority: str = "正常") -> Dict[str, Any]:
    """
    创建补货申请

    Args:
        product_id: 产品ID
        quantity: 补货数量
        priority: 优先级（正常/高/紧急）

    Returns:
        创建的补货申请
    """
    # 检查产品是否存在
    inventory = INVENTORY_DB.get(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail=f"产品 {product_id} 不存在")

    # 生成补货申请ID
    rep_id = f"REP{len(REPLENISHMENT_DB) + 1:03d}"

    # 创建补货申请
    replenishment = {
        "replenishment_id": rep_id,
        "product_id": product_id,
        "product_name": inventory["product_name"],
        "current_stock": inventory["stock"],
        "requested_quantity": quantity,
        "warehouse": inventory["warehouse"],
        "status": "待审批",
        "priority": priority,
        "create_time": datetime.now().isoformat(),
        "approve_time": None,
        "expected_arrival": None
    }

    REPLENISHMENT_DB[rep_id] = replenishment

    return {
        "success": True,
        "replenishment": replenishment,
        "message": f"补货申请 {rep_id} 已创建"
    }


@app.get("/api/replenishment/suggest/{product_id}")
async def get_replenishment_suggestion(product_id: str) -> Dict[str, Any]:
    """
    获取智能补货建议

    Args:
        product_id: 产品ID

    Returns:
        补货建议
    """
    inventory = INVENTORY_DB.get(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail=f"产品 {product_id} 不存在")

    current_stock = inventory["stock"]
    threshold = inventory["threshold"]

    # 简单的补货逻辑
    if current_stock == 0:
        suggestion = {
            "should_replenish": True,
            "priority": "紧急",
            "suggested_quantity": threshold * 3,
            "reason": "库存为0，建议紧急补货"
        }
    elif current_stock < threshold:
        suggestion = {
            "should_replenish": True,
            "priority": "高",
            "suggested_quantity": threshold * 2 - current_stock,
            "reason": f"库存低于警戒线（{threshold}），建议尽快补货"
        }
    else:
        suggestion = {
            "should_replenish": False,
            "priority": "正常",
            "suggested_quantity": 0,
            "reason": "库存充足，暂不需要补货"
        }

    return {
        "product_id": product_id,
        "product_name": inventory["product_name"],
        "current_stock": current_stock,
        "threshold": threshold,
        "warehouse": inventory["warehouse"],
        **suggestion,
        "query_time": datetime.now().isoformat()
    }


# ==================== 报表相关API ====================

@app.get("/api/reports/{report_type}")
async def get_report(report_type: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """
    生成业务报表

    Args:
        report_type: 报表类型（sales/inventory/customer）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）

    Returns:
        报表数据
    """
    if report_type == "sales":
        # 销售报表
        total_orders = len(ORDERS_DB)
        total_amount = sum(o["amount"] for o in ORDERS_DB.values())
        avg_amount = total_amount / total_orders if total_orders > 0 else 0

        return {
            "report_type": "销售报表",
            "period": f"{start_date or '2025-01-01'} 至 {end_date or datetime.now().date().isoformat()}",
            "total_orders": total_orders,
            "total_amount": round(total_amount, 2),
            "avg_amount": round(avg_amount, 2),
            "status_breakdown": {
                "已完成": len([o for o in ORDERS_DB.values() if o["status"] == "已完成"]),
                "已发货": len([o for o in ORDERS_DB.values() if o["status"] == "已发货"]),
                "待发货": len([o for o in ORDERS_DB.values() if o["status"] == "待发货"]),
                "配送延迟": len([o for o in ORDERS_DB.values() if o["status"] == "配送延迟"])
            },
            "query_time": datetime.now().isoformat()
        }

    elif report_type == "inventory":
        # 库存报表
        total_products = len(INVENTORY_DB)
        total_value = sum(i["stock"] * i["price"] for i in INVENTORY_DB.values())
        low_stock_count = len([i for i in INVENTORY_DB.values() if i["stock"] < i["threshold"]])
        out_of_stock_count = len([i for i in INVENTORY_DB.values() if i["stock"] == 0])

        return {
            "report_type": "库存报表",
            "period": datetime.now().date().isoformat(),
            "total_products": total_products,
            "total_stock_value": round(total_value, 2),
            "low_stock_products": low_stock_count,
            "out_of_stock_products": out_of_stock_count,
            "status_breakdown": {
                "正常": len([i for i in INVENTORY_DB.values() if i["status"] == "正常"]),
                "库存不足": len([i for i in INVENTORY_DB.values() if i["status"] == "库存不足"]),
                "缺货": len([i for i in INVENTORY_DB.values() if i["status"] == "缺货"])
            },
            "query_time": datetime.now().isoformat()
        }

    elif report_type == "customer":
        # 客户报表
        total_customers = len(CUSTOMERS_DB)
        total_customer_value = sum(c["total_amount"] for c in CUSTOMERS_DB.values())
        avg_customer_value = total_customer_value / total_customers if total_customers > 0 else 0

        return {
            "report_type": "客户报表",
            "period": f"{start_date or '2024-01-01'} 至 {end_date or datetime.now().date().isoformat()}",
            "total_customers": total_customers,
            "total_customer_value": round(total_customer_value, 2),
            "avg_customer_value": round(avg_customer_value, 2),
            "level_breakdown": {
                "金牌会员": len([c for c in CUSTOMERS_DB.values() if c["level"] == "金牌会员"]),
                "银牌会员": len([c for c in CUSTOMERS_DB.values() if c["level"] == "银牌会员"]),
                "普通会员": len([c for c in CUSTOMERS_DB.values() if c["level"] == "普通会员"])
            },
            "query_time": datetime.now().isoformat()
        }

    else:
        raise HTTPException(status_code=400, detail=f"不支持的报表类型: {report_type}，支持的类型: sales, inventory, customer")


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Mock Internal API Server v2.0")
    print("=" * 50)
    print("Starting on http://localhost:9000")
    print("API Docs: http://localhost:9000/docs")
    print("=" * 50)
    print("\n新增功能:")
    print("  - 促销管理 (/api/promotions)")
    print("  - 客户管理 (/api/customers)")
    print("  - 退款处理 (/api/refunds)")
    print("  - 智能补货 (/api/replenishment)")
    print("  - 业务报表 (/api/reports)")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=9000)
