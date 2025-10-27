# AI业务助手 - 快速启动指南

## 🚀 15分钟快速启动

### 第1步: 安装依赖（5分钟）

```bash
# 1. 确认Python版本
python --version  # 需要 Python 3.10+

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 第2步: 配置API密钥（3分钟）

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件，填入你的Claude API Key
# CLAUDE_API_KEY=sk-ant-xxxxx
```

**获取Claude API Key**: https://console.anthropic.com/

### 第3步: 启动服务（2分钟）

**需要打开两个终端窗口：**

```bash
# 终端1: 启动后端API
uvicorn app.main:app --reload

# 终端2: 启动前端UI
streamlit run ui/app.py
```

### 第4步: 测试（5分钟）

1. 打开浏览器访问: http://localhost:8501
2. 在聊天框输入: "查询订单12345的状态"
3. 查看AI响应

**恭喜！你已经完成了Day 1-2的核心工作！🎉**

---

## 📁 项目结构

```
ai-assistant/
├── app/                    # 后端代码
│   ├── __init__.py
│   └── main.py            # FastAPI主程序
├── ui/                     # 前端代码
│   └── app.py             # Streamlit聊天界面
├── sops/                   # SOP配置文件（待开发）
├── tests/                  # 测试代码（待开发）
├── .env.example           # 环境变量模板
├── .env                   # 实际配置（不提交到Git）
├── .gitignore
├── requirements.txt       # Python依赖
├── database.db           # SQLite数据库（自动创建）
├── CLAUDE.md             # Claude Code 指南
└── README.md             # 项目说明
```

---

## 💡 功能特性

### 当前已实现（Day 1-2）
- ✅ FastAPI后端API
- ✅ Claude AI集成
- ✅ SQLite数据库
- ✅ Streamlit聊天界面
- ✅ 基础技能：订单查询、库存查询、邮件发送（Mock数据）
- ✅ 决策记录功能

### 规划中（Day 3+）
- ⏳ 真实API对接
- ⏳ AI编排器增强
- ⏳ SOP自动化流程
- ⏳ 监控看板
- ⏳ 用户认证系统
- ⏳ 多轮对话支持

---

## 🔧 常用命令

### 启动服务
```bash
# 后端（端口8000）
uvicorn app.main:app --reload

# 前端（端口8501）
streamlit run ui/app.py
```

### 测试API
```bash
# 健康检查
curl http://localhost:8000/

# 查看指标
curl http://localhost:8000/metrics
```

### 数据库
```bash
# 手动初始化数据库
python -c "from app.main import init_db; init_db()"

# 查看数据库内容（需要安装sqlite3）
sqlite3 database.db "SELECT * FROM ai_decisions LIMIT 5;"
```

---

## 🐛 常见问题

### Q1: Claude API调用失败？
**解决方法：**
```python
# 检查API Key是否正确
import os
print(os.getenv("CLAUDE_API_KEY"))  # 应该以 sk-ant- 开头
```

### Q2: Streamlit无法连接后端？
**解决方法：**
```bash
# 确认后端正在运行
curl http://localhost:8000/

# 检查端口占用
# Windows:
netstat -ano | findstr :8000
# Mac/Linux:
lsof -i :8000
```

### Q3: 依赖安装失败？
**解决方法：**
```bash
# 更新pip
pip install --upgrade pip

# 使用国内镜像（如果在中国）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: 数据库无法创建？
**解决方法：**
```python
# 手动创建数据库
python -c "from app.main import init_db; init_db()"
```

---

## 📚 技术栈

| 组件 | 技术 | 版本 |
|-----|------|------|
| 后端框架 | FastAPI | 0.109.0 |
| LLM | Anthropic Claude | API |
| 前端UI | Streamlit | 1.31.0 |
| 数据库 | SQLite | 内置 |
| Python | Python | 3.10+ |

---

## 📖 下一步行动

### 立即行动（今天）
1. [ ] 安装依赖并启动服务
2. [ ] 测试基础对话功能
3. [ ] 申请Claude API密钥（如果还没有）

### Week 1目标
1. [ ] 完成Day 1-7的所有任务
2. [ ] 实现2个真实Skill
3. [ ] 准备演示

### 需要帮助？
- Claude API文档: https://docs.anthropic.com/
- FastAPI文档: https://fastapi.tiangolo.com/
- Streamlit文档: https://docs.streamlit.io/

---

## 📄 许可证

本项目仅供学习和内部使用。

---

**记住: 先跑通，再优化！你能行！💪**
