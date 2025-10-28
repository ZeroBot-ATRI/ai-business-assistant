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


@app.get("/")
async def root():
    """API根路径"""
    return {
        "service": "Mock Internal API",
        "version": "1.0.0",
        "endpoints": {
            "orders": "/api/orders/{order_id}",
            "inventory": "/api/inventory/{product_id}",
            "logistics": "/api/logistics/{tracking}",
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


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Mock Internal API Server")
    print("=" * 50)
    print("Starting on http://localhost:9000")
    print("API Docs: http://localhost:9000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=9000)
