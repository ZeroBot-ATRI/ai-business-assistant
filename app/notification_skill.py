"""
app/notification_skill.py - 邮件通知技能（Day 5）

支持多种邮件后端：
1. Mock模式 - 用于开发测试
2. SMTP模式 - 标准邮件服务器
3. SendGrid模式 - 第三方邮件服务（可选）
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificationSkill:
    """邮件通知技能"""

    def __init__(
        self,
        mode: str = "mock",  # mock, smtp, sendgrid
        smtp_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化邮件通知技能

        Args:
            mode: 邮件发送模式 (mock/smtp/sendgrid)
            smtp_config: SMTP配置（mode=smtp时需要）
                {
                    "host": "smtp.gmail.com",
                    "port": 587,
                    "username": "your@gmail.com",
                    "password": "your_password",
                    "from_email": "your@gmail.com",
                    "from_name": "AI助手"
                }
        """
        self.mode = mode.lower()
        self.smtp_config = smtp_config or {}
        logger.info(f"NotificationSkill initialized with mode: {self.mode}")

        # 从环境变量读取配置（如果没有传入）
        if not self.smtp_config and self.mode == "smtp":
            self.smtp_config = {
                "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
                "port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("SMTP_USERNAME", ""),
                "password": os.getenv("SMTP_PASSWORD", ""),
                "from_email": os.getenv("FROM_EMAIL", "noreply@example.com"),
                "from_name": os.getenv("FROM_NAME", "AI助手")
            }

    def send_email(
        self,
        to: str,
        subject: str,
        content: str,
        content_type: str = "plain"  # plain or html
    ) -> Dict[str, Any]:
        """
        发送邮件

        Args:
            to: 收件人邮箱地址
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 (plain/html)

        Returns:
            发送结果字典
        """
        logger.info(f"Sending email to {to} with subject: {subject}")

        if self.mode == "mock":
            return self._send_mock_email(to, subject, content)
        elif self.mode == "smtp":
            return self._send_smtp_email(to, subject, content, content_type)
        elif self.mode == "sendgrid":
            return self._send_sendgrid_email(to, subject, content, content_type)
        else:
            return {
                "success": False,
                "error": f"不支持的邮件模式: {self.mode}"
            }

    def _send_mock_email(
        self,
        to: str,
        subject: str,
        content: str
    ) -> Dict[str, Any]:
        """Mock邮件发送（用于测试）"""
        logger.info(f"[MOCK] Email sent to {to}")
        logger.info(f"[MOCK] Subject: {subject}")
        logger.info(f"[MOCK] Content: {content[:100]}...")

        return {
            "success": True,
            "mode": "mock",
            "to": to,
            "subject": subject,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "message_id": f"mock-{datetime.now().timestamp()}",
            "sent_at": datetime.now().isoformat(),
            "note": "这是Mock邮件，未实际发送"
        }

    def _send_smtp_email(
        self,
        to: str,
        subject: str,
        content: str,
        content_type: str
    ) -> Dict[str, Any]:
        """通过SMTP发送真实邮件"""
        try:
            # 验证配置
            if not self.smtp_config.get("username") or not self.smtp_config.get("password"):
                logger.warning("SMTP配置不完整，切换到Mock模式")
                return self._send_mock_email(to, subject, content)

            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = f"{self.smtp_config.get('from_name', 'AI助手')} <{self.smtp_config['from_email']}>"
            msg['To'] = to
            msg['Subject'] = subject

            # 添加邮件内容
            if content_type == "html":
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # 连接SMTP服务器并发送
            server = smtplib.SMTP(
                self.smtp_config['host'],
                self.smtp_config['port']
            )
            server.starttls()
            server.login(
                self.smtp_config['username'],
                self.smtp_config['password']
            )
            server.send_message(msg)
            server.quit()

            logger.info(f"[SMTP] Email sent successfully to {to}")
            return {
                "success": True,
                "mode": "smtp",
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "smtp_host": self.smtp_config['host']
            }

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP认证失败")
            return {
                "success": False,
                "error": "SMTP认证失败，请检查用户名和密码"
            }
        except smtplib.SMTPException as e:
            logger.error(f"SMTP错误: {e}")
            return {
                "success": False,
                "error": f"SMTP发送失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"邮件发送异常: {e}")
            return {
                "success": False,
                "error": f"邮件发送异常: {str(e)}"
            }

    def _send_sendgrid_email(
        self,
        to: str,
        subject: str,
        content: str,
        content_type: str
    ) -> Dict[str, Any]:
        """通过SendGrid发送邮件（需要安装sendgrid库）"""
        try:
            # 尝试导入SendGrid
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            api_key = os.getenv("SENDGRID_API_KEY")
            if not api_key:
                logger.warning("未配置SendGrid API Key，切换到Mock模式")
                return self._send_mock_email(to, subject, content)

            message = Mail(
                from_email=self.smtp_config.get('from_email', 'noreply@example.com'),
                to_emails=to,
                subject=subject,
                plain_text_content=content if content_type == "plain" else None,
                html_content=content if content_type == "html" else None
            )

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)

            logger.info(f"[SendGrid] Email sent successfully to {to}")
            return {
                "success": True,
                "mode": "sendgrid",
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "status_code": response.status_code
            }

        except ImportError:
            logger.warning("未安装sendgrid库，切换到Mock模式")
            return self._send_mock_email(to, subject, content)
        except Exception as e:
            logger.error(f"SendGrid发送失败: {e}")
            return {
                "success": False,
                "error": f"SendGrid发送失败: {str(e)}"
            }

    def send_notification(
        self,
        to: str,
        template: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用模板发送通知邮件

        Args:
            to: 收件人
            template: 模板名称 (order_delay, out_of_stock, etc.)
            context: 模板上下文数据

        Returns:
            发送结果
        """
        templates = {
            "order_delay": {
                "subject": "订单配送延迟通知",
                "content": """尊敬的客户：

您好！您的订单 {order_id} 因{reason}出现配送延迟。

订单详情：
- 订单号：{order_id}
- 下单时间：{create_time}
- 原预计送达：{original_eta}
- 新预计送达：{new_eta}

我们深表歉意，并已为您准备了{compensation}作为补偿。

如有任何疑问，请随时联系我们。

祝好！
客服团队"""
            },
            "out_of_stock": {
                "subject": "商品缺货通知",
                "content": """尊敬的客户：

您好！您订购的商品 {product_name} 目前库存不足。

订单详情：
- 订单号：{order_id}
- 商品：{product_name}
- 数量：{quantity}

我们正在加急补货，预计{restock_date}到货。
届时将优先为您发货。

感谢您的理解与支持！

祝好！
客服团队"""
            },
            "order_shipped": {
                "subject": "订单已发货",
                "content": """尊敬的客户：

您好！您的订单 {order_id} 已发货。

物流信息：
- 物流公司：{carrier}
- 物流单号：{tracking}
- 预计送达：{eta}

您可以通过物流单号查询配送进度。

祝好！
客服团队"""
            }
        }

        template_data = templates.get(template)
        if not template_data:
            return {
                "success": False,
                "error": f"未知的模板: {template}"
            }

        # 渲染模板
        subject = template_data["subject"]
        content = template_data["content"].format(**context)

        # 发送邮件
        return self.send_email(to, subject, content)


# 创建全局实例
notification_skill = NotificationSkill(mode=os.getenv("EMAIL_MODE", "mock"))


if __name__ == "__main__":
    # 测试代码
    print("="*60)
    print("测试邮件通知技能")
    print("="*60)

    # 测试1: Mock邮件
    print("\n1. 测试Mock邮件:")
    skill = NotificationSkill(mode="mock")
    result = skill.send_email(
        to="customer@example.com",
        subject="测试邮件",
        content="这是一封测试邮件"
    )
    print(f"结果: {result}")

    # 测试2: 模板邮件
    print("\n2. 测试模板邮件:")
    result = skill.send_notification(
        to="customer@example.com",
        template="order_delay",
        context={
            "order_id": "12345",
            "reason": "天气原因",
            "create_time": "2025-01-20 10:30:00",
            "original_eta": "2025-01-25",
            "new_eta": "2025-01-28",
            "compensation": "20元优惠券"
        }
    )
    print(f"结果: {result}")

    print("\n" + "="*60)
    print("测试完成！")
