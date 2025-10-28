# app/main.py - 核心API（Day 2增强版）
from fastapi import FastAPI, HTTPException
from anthropic import Anthropic
import os
from datetime import datetime
import json
import time
import logging
from dotenv import load_dotenv

# 导入自定义模块
from app.database import Database
from app.models import ChatRequest, ChatResponse
from app.orchestrator import AIOrchestrator  # Day 6新增

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 检查API密钥
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    logger.error("未找到 CLAUDE_API_KEY 环境变量")
    print("⚠️  错误：未找到 CLAUDE_API_KEY 环境变量")
    print("请确保：")
    print("1. .env 文件存在")
    print("2. .env 文件中包含：CLAUDE_API_KEY=sk-ant-xxxxx")
    raise ValueError("CLAUDE_API_KEY 未配置")

app = FastAPI(
    title="AI Business Assistant",
    description="企业AI业务助手 API",
    version="0.2.0"
)
client = Anthropic(api_key=CLAUDE_API_KEY)

# 初始化数据库
db = Database()
logger.info("数据库初始化完成")

# 选择使用真实技能或Mock技能（Day 4）
USE_REAL_SKILLS = os.getenv("USE_REAL_SKILLS", "true").lower() == "true"

if USE_REAL_SKILLS:
    logger.info("使用真实API技能...")
    from app.skills_real import REAL_SKILLS
    from app.skills import MockSkills  # 保留Mock技能作为后备
    from app.notification_skill import notification_skill  # Day 5新增

    # 组合技能：真实技能优先，其他使用Mock
    SKILLS = {
        "get_order": REAL_SKILLS["get_order"],
        "query_inventory": REAL_SKILLS["query_inventory"],
        "query_logistics": REAL_SKILLS["query_logistics"],
        # Day 5: 真实邮件通知技能
        "send_email": notification_skill.send_email,
        "send_notification": notification_skill.send_notification,
        # 其他技能继续使用Mock（Day 6会逐步替换）
        "update_order_status": MockSkills.update_order_status,
        "generate_apology": MockSkills.generate_apology,
        "offer_compensation": MockSkills.offer_compensation
    }
    logger.info(f"加载了 {len(SKILLS)} 个技能（4个真实API + 3个Mock）")
else:
    logger.info("使用Mock技能...")
    from app.skills import SKILLS as SKILL_REGISTRY
    SKILLS = SKILL_REGISTRY
    logger.info(f"加载了 {len(SKILLS)} 个Mock技能")

# Day 6: 初始化AI编排器
orchestrator = AIOrchestrator(CLAUDE_API_KEY)

# 注册所有技能到编排器
orchestrator.register_skill("get_order", SKILLS["get_order"], "查询订单信息", {"order_id": "订单号"})
orchestrator.register_skill("query_inventory", SKILLS["query_inventory"], "查询库存信息", {"product_id": "产品ID（单个字母或数字）"})
orchestrator.register_skill("query_logistics", SKILLS["query_logistics"], "查询物流信息", {"tracking_number": "物流单号"})
orchestrator.register_skill("send_email", SKILLS["send_email"], "发送邮件", {"to": "收件人", "subject": "主题", "content": "内容"})
orchestrator.register_skill("send_notification", SKILLS["send_notification"], "发送通知邮件（使用模板）", {"to": "收件人", "template": "模板名", "context": "模板数据"})
orchestrator.register_skill("update_order_status", SKILLS["update_order_status"], "更新订单状态", {"order_id": "订单号", "status": "新状态"})
orchestrator.register_skill("generate_apology", SKILLS["generate_apology"], "生成道歉信", {"order_id": "订单号", "reason": "原因"})
orchestrator.register_skill("offer_compensation", SKILLS["offer_compensation"], "提供补偿", {"user_id": "用户ID", "policy": "补偿政策"})

logger.info(f"AI编排器初始化完成，已注册 {len(orchestrator.skills)} 个技能")

@app.post("/chat", response_model=ChatResponse)
async def chat(user_input: str, user_id: str = "default"):
    """核心对话接口（Day 2增强版）"""
    start_time = time.time()
    logger.info(f"收到用户请求: user_id={user_id}, input={user_input}")

    try:
        # Step 1: 用Claude识别意图并生成执行计划
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""你是企业AI助手。分析用户请求并生成执行计划。

用户输入："{user_input}"

可用技能：
- get_order(order_id): 查询订单，参数order_id是订单号字符串
- query_inventory(product_id): 查询库存，参数product_id是产品ID字符串（注意：如果用户说"产品A"，ID应该是"A"，不是"产品A"）
- send_email(to, subject, content): 发送邮件，必须提供3个参数：to邮箱地址，subject邮件主题，content邮件内容
- send_notification(to, template, context): 发送通知邮件（使用预置模板），template可选：order_shipped（发货通知）、order_delay（延迟通知）、out_of_stock（缺货通知）

重要提示：
- 产品ID是单个字母或数字，例如用户说"产品A"或"产品A的库存"时，product_id应该是"A"
- 订单号是完整的数字字符串，例如用户说"订单12345"时，order_id是"12345"
- 发货通知、延迟通知等标准场景使用send_notification，自定义邮件使用send_email

示例：
用户: "查询产品A的库存" → skill: "query_inventory", params: {{"product_id": "A"}}
用户: "订单12345的状态" → skill: "get_order", params: {{"order_id": "12345"}}
用户: "发送发货通知给customer@example.com" → skill: "send_notification", params: {{"to": "customer@example.com", "template": "order_shipped", "context": {{"order_id": "xxx", "tracking": "xxx", "carrier": "xxx", "eta": "xxx"}}}}

请严格按照以下JSON格式返回，不要添加任何其他文字说明：
{{
  "intent": "用户意图的简短描述",
  "skill": "要调用的技能名称",
  "params": {{
    "参数名": "参数值"
  }},
  "response_template": "给用户的回复模板，可以用{{result}}表示结果"
}}

只返回JSON，不要有任何其他内容。"""
            }]
        )

        # Step 2: 解析AI返回的计划
        plan_text = response.content[0].text

        # 提取JSON（更健壮的处理）
        # 移除可能的markdown代码块标记
        plan_text = plan_text.strip()
        if "```json" in plan_text:
            plan_text = plan_text.split("```json")[1].split("```")[0]
        elif "```" in plan_text:
            plan_text = plan_text.split("```")[1].split("```")[0]

        # 尝试找到JSON对象
        plan_text = plan_text.strip()

        # 如果文本中有其他内容，尝试提取{}之间的内容
        if not plan_text.startswith("{"):
            import re
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan_text = json_match.group(0)

        plan = json.loads(plan_text)

        # Step 3: 执行技能
        skill_name = plan["skill"]
        params = plan["params"]

        if skill_name in SKILLS:
            result = SKILLS[skill_name](**params)
        else:
            result = {"error": "技能不存在"}

        # Step 4: 生成用户响应
        final_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""执行结果：{json.dumps(result, ensure_ascii=False)}

使用这个模板回复用户：{plan['response_template']}"""
            }]
        )

        user_message = final_response.content[0].text

        # Step 5: 计算执行时间和成本
        execution_time_ms = (time.time() - start_time) * 1000

        # 估算LLM成本（简化版，实际需要根据token数计算）
        # Claude Sonnet 4: input $3/M tokens, output $15/M tokens
        # 这里用粗略估算
        llm_cost = 0.001  # 假设每次调用约0.001美元

        # Step 6: 记录决策（使用新的Database类）
        db.save_decision(
            user_input=user_input,
            intent=plan["intent"],
            action=skill_name,
            result=result,
            user_id=user_id,
            success=True,
            execution_time_ms=execution_time_ms,
            llm_cost=llm_cost
        )

        logger.info(f"请求处理成功: intent={plan['intent']}, skill={skill_name}, time={execution_time_ms:.0f}ms")

        return ChatResponse(
            success=True,
            message=user_message,
            debug={
                "intent": plan["intent"],
                "skill": skill_name,
                "result": result,
                "execution_time_ms": round(execution_time_ms, 2),
                "llm_cost": llm_cost
            }
        )

    except json.JSONDecodeError as e:
        # JSON解析失败
        logger.error(f"JSON解析失败: {str(e)}")
        execution_time_ms = (time.time() - start_time) * 1000
        db.save_decision(
            user_input=user_input,
            intent="解析失败",
            action="none",
            result={"error": str(e)},
            user_id=user_id,
            success=False,
            execution_time_ms=execution_time_ms
        )
        return ChatResponse(
            success=False,
            error=f"JSON解析失败: {str(e)}",
            message="抱歉，我在理解您的请求时遇到了问题，请重新描述。",
            debug={
                "raw_response": plan_text if 'plan_text' in locals() else "未获取到响应",
                "error_detail": str(e)
            }
        )
    except KeyError as e:
        # 缺少必需的字段
        logger.error(f"AI返回的计划缺少必需字段: {str(e)}")
        execution_time_ms = (time.time() - start_time) * 1000
        db.save_decision(
            user_input=user_input,
            intent="字段缺失",
            action="none",
            result={"error": str(e)},
            user_id=user_id,
            success=False,
            execution_time_ms=execution_time_ms
        )
        return ChatResponse(
            success=False,
            error=f"AI返回的计划缺少必需字段: {str(e)}",
            message="抱歉，处理出现异常，请稍后重试。",
            debug={
                "plan": plan if 'plan' in locals() else "未解析计划"
            }
        )
    except Exception as e:
        # 其他错误
        import traceback
        logger.error(f"未知错误: {str(e)}\n{traceback.format_exc()}")
        execution_time_ms = (time.time() - start_time) * 1000
        db.save_decision(
            user_input=user_input,
            intent="系统错误",
            action="none",
            result={"error": str(e)},
            user_id=user_id,
            success=False,
            execution_time_ms=execution_time_ms
        )
        return ChatResponse(
            success=False,
            error=str(e),
            message="抱歉，系统出现错误，请稍后重试。",
            debug={
                "traceback": traceback.format_exc()
            }
        )

@app.get("/")
def root():
    """健康检查接口"""
    return {
        "status": "AI Assistant Running",
        "version": "0.2.0",
        "api": "FastAPI",
        "llm": "Claude Sonnet 4"
    }

@app.get("/metrics")
def metrics():
    """系统指标接口（Day 2增强版 - 用于监控看板）"""
    try:
        # 使用新的Database类获取统计数据
        stats = db.get_today_stats()
        recent_logs = db.get_recent_decisions(limit=10)
        intent_dist = db.get_intent_distribution(days=7)

        # 生成告警
        alerts = []
        if stats["success_rate"] < 0.9:
            alerts.append({
                "level": "warning",
                "message": f"成功率较低: {stats['success_rate']:.1%}"
            })
        if stats["avg_execution_time_ms"] > 2000:
            alerts.append({
                "level": "warning",
                "message": f"响应时间过慢: {stats['avg_execution_time_ms']:.0f}ms"
            })

        return {
            "today_total": stats["today_total"],
            "today_delta": 0,  # 需要与昨天对比
            "success_rate": stats["success_rate"],
            "success_rate_delta": 0.0,
            "avg_response_ms": stats["avg_execution_time_ms"],
            "response_delta": 0.0,
            "today_cost": stats["today_cost"],
            "cost_delta": 0.0,
            "alerts": alerts,
            "recent_logs": recent_logs,
            "hourly_stats": [],  # 需要额外查询
            "intent_distribution": intent_dist,
            "sop_stats": []  # Day 16-17 实现
        }
    except Exception as e:
        logger.error(f"获取指标失败: {str(e)}")
        return {"error": str(e)}

# 运行：uvicorn app.main:app --reload
