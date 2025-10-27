# 🚀 AI助手快速启动包

## 这个包包含什么？

1. **项目结构模板** - 开箱即用的文件夹结构
2. **核心代码骨架** - Day 1-2就能跑起来的最小代码
3. **配置文件模板** - 环境变量、依赖清单
4. **快速启动脚本** - 一键运行所有服务

## 快速开始（15分钟内运行）

### Step 1: 环境准备（5分钟）

```bash
# 1. 安装Python 3.10+
python --version  # 确认版本

# 2. 克隆或下载这个启动包
cd ai-assistant-starter

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt
```

### Step 2: 配置API密钥（3分钟）

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件，填入你的Claude API Key
# CLAUDE_API_KEY=sk-ant-xxxxx
```

**获取Claude API Key**: https://console.anthropic.com/

### Step 3: 启动服务（2分钟）

```bash
# 终端1: 启动后端API
uvicorn app.main:app --reload

# 终端2: 启动前端UI
streamlit run ui/app.py
```

### Step 4: 测试（5分钟）

1. 打开浏览器访问: http://localhost:8501
2. 在聊天框输入: "你好，介绍一下你自己"
3. 查看AI响应

**恭喜！你已经完成了Day 1-2的核心工作！🎉**

---

## 文件结构说明

```
ai-assistant/
├── app/                    # 后端代码
│   ├── __init__.py
│   ├── main.py            # FastAPI主程序 [Day 1-2]
│   ├── models.py          # 数据模型 [Day 2]
│   ├── orchestrator.py    # AI编排器 [Day 6]
│   ├── skills.py          # 技能库 [Day 4-5]
│   ├── sop_engine.py      # SOP引擎 [Day 16-17]
│   ├── auth.py            # 认证 [Day 29-31]
│   └── session.py         # 会话管理 [Day 32-35]
│
├── ui/                     # 前端代码
│   ├── app.py             # 聊天界面 [Day 3]
│   └── dashboard.py       # 监控看板 [Day 26-30]
│
├── sops/                   # SOP配置文件
│   ├── order_delay.yaml   # 订单延迟处理 [Day 11-12]
│   ├── inventory_alert.yaml
│   └── smart_refund.yaml
│
├── tests/                  # 测试代码
│   ├── test_api.py
│   └── test_e2e.py
│
├── .env.example           # 环境变量模板
├── .env                   # 实际配置（不提交到Git）
├── .gitignore
├── requirements.txt       # Python依赖
├── database.db           # SQLite数据库（自动创建）
└── README.md             # 项目说明
```

---

## 核心代码说明

### `app/main.py` - 后端API核心

**功能**:
- ✅ 接收用户输入
- ✅ 调用Claude识别意图
- ✅ 执行技能并返回结果
- ✅ 记录所有决策到数据库

**关键接口**:
- `POST /chat` - 对话接口
- `GET /` - 健康检查
- `GET /metrics` - 系统指标（Day 9添加）

### `ui/app.py` - 前端聊天界面

**功能**:
- ✅ 聊天输入框
- ✅ 消息历史展示
- ✅ 系统状态监控
- ✅ 快捷测试按钮

### `app/skills.py` - 技能库

**初始技能**（硬编码Mock）:
- `get_order()` - 订单查询
- `query_inventory()` - 库存查询
- `send_email()` - 邮件发送

**Day 4-5任务**: 替换为真实API调用

---

## 开发流程

### Day 1-2: 基础搭建 ✅
- [x] 项目结构
- [x] FastAPI后端
- [x] Claude API集成
- [x] SQLite数据库

### Day 3: UI开发 ⏳
- [ ] Streamlit聊天界面
- [ ] 基础交互功能

### Day 4-5: 真实Skill ⏳
- [ ] 对接内部订单API
- [ ] 对接库存系统
- [ ] 集成邮件服务

### Day 6-7: Orchestrator ⏳
- [ ] 多步骤编排
- [ ] 意图识别优化

---

## 常见问题

### Q1: Claude API调用失败？
```python
# 检查API Key是否正确
import os
print(os.getenv("CLAUDE_API_KEY"))  # 应该以 sk-ant- 开头

# 测试网络连接
curl https://api.anthropic.com/v1/models

# 如果仍然失败，检查代理设置
```

### Q2: Streamlit无法连接后端？
```bash
# 确认后端正在运行
curl http://localhost:8000/

# 检查端口占用
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

### Q3: 数据库无法创建？
```python
# 手动创建数据库
python -c "from app.main import init_db; init_db()"
```

### Q4: 依赖安装失败？
```bash
# 更新pip
pip install --upgrade pip

# 使用国内镜像（如果在中国）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 下一步行动

### 立即行动（今天）:
1. [ ] 安装依赖并启动服务
2. [ ] 测试基础对话功能
3. [ ] 申请Claude API密钥（如果还没有）

### Week 1目标:
1. [ ] 完成Day 1-7的所有任务
2. [ ] 实现2个真实Skill
3. [ ] 准备周一演示

### 需要帮助？
- 技术问题: 查看 `/docs` 目录的详细文档
- Claude API: https://docs.anthropic.com/
- Streamlit: https://docs.streamlit.io/

---

**记住: 先跑通，再优化！你能行！💪**
