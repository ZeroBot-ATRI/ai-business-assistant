# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个企业AI助手快速启动包,使用FastAPI后端和Streamlit前端,集成Claude API构建智能业务助手。项目采用单体应用架构,专注快速实现核心价值。

## 技术栈

- **后端**: FastAPI + SQLite/PostgreSQL
- **前端**: Streamlit (聊天界面和监控看板)
- **LLM**: Anthropic Claude API
- **认证**: JWT
- **数据处理**: pandas, plotly

## 核心架构

### 三层架构
1. **API层** (`app/main.py`): FastAPI接口,处理HTTP请求
2. **编排层** (`app/orchestrator.py`): AI编排器,负责意图识别和多步骤执行计划
3. **技能层** (`app/skills.py`): 具体业务技能函数(订单、库存、通知等)

### 关键组件
- **AIOrchestrator**: 系统核心大脑,负责将用户输入转化为执行计划,调用技能并生成响应
- **SOPEngine** (`app/sop_engine.py`): 执行标准操作流程,支持YAML配置的多步骤自动化
- **SessionManager** (`app/session.py`): 管理多轮对话上下文,维护会话历史
- **技能注册机制**: 通过`register_skill()`动态注册业务技能

## 常用命令

### 环境配置
```bash
# 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env填入CLAUDE_API_KEY
```

### 运行服务
```bash
# 启动后端API (默认端口8000)
uvicorn app.main:app --reload

# 启动前端聊天界面 (默认端口8501)
streamlit run ui/app.py

# 启动监控看板
streamlit run ui/dashboard.py --server.port 8502
```

### 测试
```bash
# 运行端到端测试
pytest tests/test_e2e.py -v

# 测试API健康检查
curl http://localhost:8000/

# 手动初始化数据库
python -c "from app.main import init_db; init_db()"
```

## 开发流程

### 添加新技能
1. 在`app/skills.py`中实现技能类和方法
2. 在`app/main.py`的`orchestrator`中注册技能:
   ```python
   orchestrator.register_skill(
       name="skill_name",
       func=skill_instance.method,
       description="技能描述(供AI理解)"
   )
   ```
3. 技能函数应返回`Dict[str, Any]`,包含执行结果或错误信息

### 添加新SOP
1. 在`sops/`目录创建YAML配置文件
2. 定义触发条件、执行步骤和决策逻辑
3. 支持的步骤类型:
   - `skill_call`: 调用已注册技能
   - `decision`: 条件判断
   - `ai_decision`: AI辅助决策
4. 使用`${variable}`语法引用上下文变量

### AI编排工作流程
1. 用户输入 → API接收
2. AI分析意图 → 生成执行计划(JSON格式)
3. 按计划执行技能 → 收集结果
4. AI生成用户友好响应 → 返回
5. 记录决策到数据库(`ai_decisions`表)

## 数据库结构

### `ai_decisions` 表
存储所有AI决策记录,字段包括:
- `user_input`: 用户输入
- `intent`: 识别的意图
- `skills_used`: 使用的技能(JSON)
- `execution_time_ms`: 执行时长
- `llm_cost`: LLM调用成本
- `success`: 执行成功标志

### `metrics` 表
系统运行指标,用于监控看板

## 配置说明

### 环境变量 (.env)
- `CLAUDE_API_KEY`: 必须,从 https://console.anthropic.com/ 获取
- `DATABASE_URL`: 数据库连接字符串,默认SQLite
- `SECRET_KEY`: JWT签名密钥,生产环境必须修改
- `ORDER_API_BASE`, `INVENTORY_API_BASE`: 内部系统API地址

### Claude模型使用
- 使用`claude-sonnet-4-20250514`模型
- 意图识别和计划生成: max_tokens=2000
- 响应生成: max_tokens=1000

## 认证机制

- 测试账号定义在`app/auth.py`的`TEST_USERS`字典
- 所有`/chat`和SOP接口需要JWT token
- 登录接口: `POST /login`
- Token在请求头: `Authorization: Bearer <token>`

## 监控指标

监控看板展示:
- 核心指标: 今日处理量、成功率、平均响应时间、成本
- 实时告警: 成功率<90%或响应时间>2s时触发
- 趋势图: 24小时处理量、意图分布
- SOP统计: 各SOP执行次数和成功率

## 开发原则

1. **快速迭代**: 先用Mock数据跑通流程,再接真实API
2. **错误处理**: 所有外部API调用必须使用try-except,并返回错误信息而非抛出异常
3. **可观测性**: 关键操作必须记录到数据库或日志
4. **渐进增强**: 基础功能优先,高级特性后续迭代
5. **简单优于复杂**: 单体应用,避免过度设计

## 部署注意事项

- 开发环境使用SQLite,生产环境切换到PostgreSQL
- 确保`.env`不提交到Git(已在`.gitignore`中)
- Railway/Render部署时需要设置环境变量
- 生产环境必须修改`SECRET_KEY`
- 建议启用HTTPS和速率限制
