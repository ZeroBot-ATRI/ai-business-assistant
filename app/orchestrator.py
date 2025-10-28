"""
app/orchestrator.py - AI编排器（Day 6）

核心职责：
1. 意图识别和技能映射
2. 多步骤任务编排
3. 技能执行和结果聚合
4. 响应生成
"""
from typing import Dict, Any, List, Callable, Optional
from anthropic import Anthropic
import json
import logging
import os
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """AI编排器 - 系统的大脑"""

    def __init__(self, api_key: str):
        """
        初始化编排器

        Args:
            api_key: Claude API密钥
        """
        self.client = Anthropic(api_key=api_key)
        self.skills: Dict[str, Callable] = {}
        self.skill_descriptions: Dict[str, str] = {}
        logger.info("AIOrchestrator initialized")

    def register_skill(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Optional[Dict[str, str]] = None
    ) -> None:
        """
        注册技能

        Args:
            name: 技能名称
            func: 技能函数
            description: 技能描述（供AI理解）
            parameters: 参数说明 {"param_name": "param_description"}
        """
        self.skills[name] = func

        # 构建完整描述
        full_description = f"{name}: {description}"
        if parameters:
            params_str = ", ".join([f"{k}({v})" for k, v in parameters.items()])
            full_description += f" - 参数: {params_str}"

        self.skill_descriptions[name] = full_description
        logger.info(f"Registered skill: {name}")

    def get_skill_list(self) -> str:
        """获取技能列表的文本描述"""
        return "\n".join([f"- {desc}" for desc in self.skill_descriptions.values()])

    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        分析用户意图并生成执行计划

        Args:
            user_input: 用户输入

        Returns:
            执行计划字典
        """
        prompt = f"""你是企业AI助手的编排器。分析用户请求并生成执行计划。

用户输入："{user_input}"

可用技能：
{self.get_skill_list()}

重要提示：
- 产品ID是单个字母或数字，例如用户说"产品A"时，product_id应该是"A"
- 订单号是完整的数字字符串
- 如果任务需要多个步骤，请按顺序列出
- 每个步骤只调用一个技能

请严格按照以下JSON格式返回执行计划：
{{
  "intent": "用户意图的简短描述",
  "steps": [
    {{
      "step": 1,
      "skill": "技能名称",
      "params": {{"参数名": "参数值"}},
      "description": "这一步做什么"
    }}
  ],
  "final_response_template": "给用户的回复模板"
}}

示例：
用户: "查询产品A的库存"
→ {{"intent": "查询库存", "steps": [{{"step": 1, "skill": "query_inventory", "params": {{"product_id": "A"}}, "description": "查询产品A库存"}}]}}

用户: "订单12345延迟了，发个道歉邮件给客户"
→ {{"intent": "处理延迟订单", "steps": [
    {{"step": 1, "skill": "get_order", "params": {{"order_id": "12345"}}, "description": "查询订单信息"}},
    {{"step": 2, "skill": "send_notification", "params": {{"to": "客户邮箱", "template": "order_delay", "context": {{}}}}, "description": "发送道歉邮件"}}
]}}

只返回JSON，不要有任何其他内容。"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            plan_text = response.content[0].text.strip()

            # 提取JSON（处理可能的markdown代码块）
            if not plan_text.startswith("{"):
                json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
                if json_match:
                    plan_text = json_match.group(0)

            plan = json.loads(plan_text)
            logger.info(f"Intent analyzed: {plan.get('intent')}, Steps: {len(plan.get('steps', []))}")
            return plan

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, text: {plan_text[:200]}")
            return {
                "intent": "解析失败",
                "steps": [],
                "error": f"无法解析AI响应: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {
                "intent": "分析失败",
                "steps": [],
                "error": str(e)
            }

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行计划

        Args:
            plan: 执行计划

        Returns:
            执行结果
        """
        if "error" in plan:
            return {
                "success": False,
                "error": plan["error"],
                "results": []
            }

        steps = plan.get("steps", [])
        results = []
        context = {}  # 存储步骤间的上下文数据

        for step_info in steps:
            step_num = step_info.get("step", 0)
            skill_name = step_info.get("skill")
            params = step_info.get("params", {})
            description = step_info.get("description", "")

            logger.info(f"Executing step {step_num}: {skill_name} - {description}")

            # 检查技能是否存在
            if skill_name not in self.skills:
                logger.warning(f"Skill not found: {skill_name}")
                results.append({
                    "step": step_num,
                    "skill": skill_name,
                    "success": False,
                    "error": f"技能不存在: {skill_name}"
                })
                continue

            # 参数替换：从上下文中获取动态值
            resolved_params = self._resolve_params(params, context)

            # 执行技能
            try:
                skill_func = self.skills[skill_name]
                result = skill_func(**resolved_params)

                # 存储结果到上下文
                context[f"step{step_num}_result"] = result
                if isinstance(result, dict):
                    # 常用字段也存入上下文
                    for key in ["order_id", "customer_email", "product_id", "tracking"]:
                        if key in result:
                            context[key] = result[key]

                results.append({
                    "step": step_num,
                    "skill": skill_name,
                    "success": result.get("success", True) if isinstance(result, dict) else True,
                    "result": result,
                    "description": description
                })
                logger.info(f"Step {step_num} completed successfully")

            except Exception as e:
                logger.error(f"Step {step_num} failed: {e}")
                results.append({
                    "step": step_num,
                    "skill": skill_name,
                    "success": False,
                    "error": str(e)
                })

        return {
            "success": all(r.get("success", False) for r in results),
            "results": results,
            "context": context
        }

    def _resolve_params(
        self,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        解析参数，从上下文中获取动态值

        Args:
            params: 原始参数
            context: 上下文数据

        Returns:
            解析后的参数
        """
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # $key 表示从上下文获取
                context_key = value[1:]
                resolved[key] = context.get(context_key, value)
            else:
                resolved[key] = value
        return resolved

    def generate_response(
        self,
        user_input: str,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> str:
        """
        生成用户友好的响应

        Args:
            user_input: 用户输入
            plan: 执行计划
            execution_result: 执行结果

        Returns:
            响应文本
        """
        # 准备结果摘要
        results_summary = []
        for result in execution_result.get("results", []):
            step = result.get("step")
            skill = result.get("skill")
            success = result.get("success")
            data = result.get("result", {})

            summary = f"步骤{step}（{skill}）: "
            if success:
                summary += "成功"
                if isinstance(data, dict):
                    # 提取关键信息
                    if "order_id" in data:
                        summary += f" - 订单{data['order_id']}"
                    if "status" in data:
                        summary += f" - 状态{data['status']}"
            else:
                summary += f"失败 - {result.get('error', '未知错误')}"

            results_summary.append(summary)

        prompt = f"""根据执行结果，生成一个友好的回复给用户。

用户输入："{user_input}"

执行计划：{plan.get('intent')}

执行结果：
{chr(10).join(results_summary)}

详细数据：
{json.dumps(execution_result.get('results', []), ensure_ascii=False, indent=2)}

要求：
1. 用自然语言总结执行结果
2. 重点突出用户关心的信息（订单状态、库存数量等）
3. 如果有错误，友好地告知用户
4. 不要包含技术细节（如step、skill等）
5. 保持简洁，3-5句话

直接返回回复内容，不要有多余的格式。"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            # 降级：返回简单的结果摘要
            if execution_result.get("success"):
                return f"已完成您的请求：{plan.get('intent')}"
            else:
                return f"处理请求时遇到问题：{plan.get('intent')}"

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入的完整流程

        Args:
            user_input: 用户输入

        Returns:
            处理结果
        """
        start_time = datetime.now()

        # 1. 分析意图
        plan = self.analyze_intent(user_input)

        # 2. 执行计划
        execution_result = self.execute_plan(plan)

        # 3. 生成响应
        response = self.generate_response(user_input, plan, execution_result)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000

        return {
            "success": execution_result.get("success", False),
            "response": response,
            "plan": plan,
            "execution_result": execution_result,
            "execution_time_ms": execution_time
        }


if __name__ == "__main__":
    # 测试代码
    from dotenv import load_dotenv
    load_dotenv()

    print("="*60)
    print("测试 AIOrchestrator")
    print("="*60)

    # 创建编排器
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("错误：未设置CLAUDE_API_KEY环境变量")
        exit(1)

    orchestrator = AIOrchestrator(api_key)

    # 注册Mock技能
    def mock_get_order(order_id: str):
        return {"order_id": order_id, "status": "已发货", "customer_email": "test@example.com"}

    def mock_send_email(to: str, subject: str, content: str):
        return {"success": True, "to": to, "subject": subject}

    orchestrator.register_skill(
        "get_order",
        mock_get_order,
        "查询订单信息",
        {"order_id": "订单号"}
    )

    orchestrator.register_skill(
        "send_email",
        mock_send_email,
        "发送邮件",
        {"to": "收件人", "subject": "主题", "content": "内容"}
    )

    # 测试单步骤
    print("\n测试1: 单步骤任务")
    result = orchestrator.process("查询订单12345")
    print(f"响应: {result['response']}")
    print(f"执行时间: {result['execution_time_ms']:.0f}ms")

    print("\n" + "="*60)
    print("测试完成！")
