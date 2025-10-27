# app/main.py - 核心API（极简版）
from fastapi import FastAPI, HTTPException
from anthropic import Anthropic
import os
from datetime import datetime
import sqlite3
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查API密钥
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    print("⚠️  错误：未找到 CLAUDE_API_KEY 环境变量")
    print("请确保：")
    print("1. .env 文件存在")
    print("2. .env 文件中包含：CLAUDE_API_KEY=sk-ant-xxxxx")
    raise ValueError("CLAUDE_API_KEY 未配置")

app = FastAPI(title="AI Business Assistant")
client = Anthropic(api_key=CLAUDE_API_KEY)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ai_decisions
                 (id INTEGER PRIMARY KEY,
                  user_input TEXT,
                  intent TEXT,
                  action TEXT,
                  result TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 核心技能库（硬编码开始，够用就行）
SKILLS = {
    "get_order": lambda order_id: {
        "order_id": order_id,
        "status": "已发货",
        "tracking": "SF1234567890",
        "customer_email": "customer@example.com"
    },
    "query_inventory": lambda product_id: {
        "product_id": product_id,
        "stock": 100,
        "warehouse": "深圳仓",
        "threshold": 20
    },
    "send_email": lambda to, content: {
        "sent": True,
        "to": to,
        "timestamp": datetime.now().isoformat()
    }
}

@app.post("/chat")
async def chat(user_input: str):
    """核心对话接口"""
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
- query_inventory(product_id): 查询库存，参数product_id是产品ID字符串
- send_email(to, content): 发送邮件，参数to是邮箱地址，content是邮件内容

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

        # Step 5: 记录决策
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO ai_decisions
                     (user_input, intent, action, result, timestamp)
                     VALUES (?, ?, ?, ?, ?)""",
                  (user_input, plan["intent"], skill_name,
                   json.dumps(result, ensure_ascii=False), datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": user_message,
            "debug": {
                "intent": plan["intent"],
                "skill": skill_name,
                "result": result
            }
        }

    except json.JSONDecodeError as e:
        # JSON解析失败，返回详细错误信息
        return {
            "success": False,
            "error": f"JSON解析失败: {str(e)}",
            "debug": {
                "raw_response": plan_text if 'plan_text' in locals() else "未获取到响应",
                "error_detail": str(e)
            }
        }
    except KeyError as e:
        # 缺少必需的字段
        return {
            "success": False,
            "error": f"AI返回的计划缺少必需字段: {str(e)}",
            "debug": {
                "plan": plan if 'plan' in locals() else "未解析计划"
            }
        }
    except Exception as e:
        # 其他错误
        import traceback
        return {
            "success": False,
            "error": str(e),
            "debug": {
                "traceback": traceback.format_exc()
            }
        }

@app.get("/")
def root():
    return {"status": "AI Assistant Running", "version": "0.1"}

@app.get("/metrics")
def metrics():
    """系统指标接口（用于监控看板）"""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # 今日处理量
        c.execute("""SELECT COUNT(*) FROM ai_decisions
                     WHERE date(timestamp) = date('now')""")
        today_total = c.fetchone()[0]

        # 成功率（简化版）
        c.execute("""SELECT COUNT(*) FROM ai_decisions
                     WHERE result NOT LIKE '%error%'""")
        success_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM ai_decisions")
        total_count = c.fetchone()[0]

        success_rate = success_count / total_count if total_count > 0 else 0

        # 最近日志
        c.execute("""SELECT user_input, intent, action, timestamp
                     FROM ai_decisions
                     ORDER BY timestamp DESC LIMIT 10""")
        recent_logs = [
            {
                "user_input": row[0],
                "intent": row[1],
                "result": row[2],
                "timestamp": row[3]
            }
            for row in c.fetchall()
        ]

        conn.close()

        return {
            "today_total": today_total,
            "success_rate": success_rate,
            "avg_response_ms": 1200,  # Mock数据
            "today_cost": 0.15,  # Mock数据
            "alerts": [],
            "recent_logs": recent_logs
        }
    except Exception as e:
        return {"error": str(e)}

# 运行：uvicorn app.main:app --reload
