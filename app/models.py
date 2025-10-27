# app/models.py - 数据模型
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============ API 请求/响应模型 ============

class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_input: str = Field(..., description="用户输入内容", min_length=1)
    user_id: Optional[str] = Field(default="default", description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "查询订单12345的状态",
                "user_id": "user_001",
                "session_id": "session_123"
            }
        }


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="给用户的回复消息")
    debug: Optional[Dict[str, Any]] = Field(default=None, description="调试信息")
    error: Optional[str] = Field(default=None, description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "订单12345已发货，物流单号：SF1234567890",
                "debug": {
                    "intent": "查询订单",
                    "skill": "get_order",
                    "result": {"order_id": "12345", "status": "已发货"}
                }
            }
        }


# ============ AI 计划模型 ============

class AIPlan(BaseModel):
    """AI执行计划"""
    intent: str = Field(..., description="用户意图")
    skill: str = Field(..., description="要调用的技能名称")
    params: Dict[str, Any] = Field(..., description="技能参数")
    response_template: str = Field(..., description="响应模板")


# ============ 技能相关模型 ============

class OrderInfo(BaseModel):
    """订单信息"""
    order_id: str
    status: str
    tracking: Optional[str] = None
    customer_email: Optional[str] = None
    create_time: Optional[str] = None
    amount: Optional[float] = None


class InventoryInfo(BaseModel):
    """库存信息"""
    product_id: str
    product_name: Optional[str] = None
    stock: int
    warehouse: str
    threshold: Optional[int] = 20
    status: Optional[str] = None  # "正常", "库存不足", "缺货"


class EmailInfo(BaseModel):
    """邮件信息"""
    to: str
    subject: Optional[str] = "系统通知"
    content: str
    sent: bool = False
    timestamp: Optional[str] = None


# ============ 数据库记录模型 ============

class AIDecisionRecord(BaseModel):
    """AI决策记录"""
    id: Optional[int] = None
    user_id: str = "default"
    user_input: str
    intent: str
    action: str
    result: str
    success: bool = True
    execution_time_ms: Optional[float] = None
    llm_cost: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class MetricsRecord(BaseModel):
    """系统指标记录"""
    id: Optional[int] = None
    metric_name: str
    metric_value: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============ 监控指标模型 ============

class SystemMetrics(BaseModel):
    """系统运行指标"""
    today_total: int = 0
    today_delta: int = 0
    success_rate: float = 0.0
    success_rate_delta: float = 0.0
    avg_response_ms: float = 0.0
    response_delta: float = 0.0
    today_cost: float = 0.0
    cost_delta: float = 0.0
    alerts: List[Dict[str, str]] = []
    recent_logs: List[Dict[str, Any]] = []
    hourly_stats: List[Dict[str, Any]] = []
    intent_distribution: List[Dict[str, Any]] = []
    sop_stats: List[Dict[str, Any]] = []
