# ⚡ 快速启动指南（3分钟）

## 📋 前置检查

```bash
# 1. 检查Python版本（需要3.10+）
python --version

# 2. 检查是否在项目目录
pwd
# 应该显示: .../files
```

---

## 🚀 三步启动

### Step 1: 配置环境（1分钟）

```bash
# 创建.env文件
cp .env.example .env

# 用文本编辑器打开.env，填入你的Claude API Key
# CLAUDE_API_KEY=sk-ant-xxxxx
```

**获取API Key**: https://console.anthropic.com/settings/keys

### Step 2: 安装依赖（1分钟）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Mac/Linux:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### Step 3: 启动服务（1分钟）

**打开两个终端窗口：**

**终端1 - 后端：**
```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动后端
uvicorn app.main:app --reload
```

看到这个输出就成功了：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**终端2 - 前端：**
```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动前端
streamlit run ui/app.py
```

浏览器会自动打开 http://localhost:8501

---

## ✅ 测试功能

在聊天界面输入以下测试：

1. **测试订单查询**
   ```
   查询订单12345的状态
   ```

2. **测试库存查询**
   ```
   产品A还有多少库存？
   ```

3. **测试智能对话**
   ```
   帮我查一下订单12345，如果延迟了就发邮件给客户道歉
   ```

---

## 🔍 验证系统运行

### 检查后端API
打开浏览器访问: http://localhost:8000
应该看到:
```json
{
  "status": "AI Assistant Running",
  "version": "0.1"
}
```

### 检查数据库
```bash
# 查看数据库是否创建成功
ls database.db

# 查看记录（需要sqlite3）
sqlite3 database.db "SELECT * FROM ai_decisions;"
```

---

## 🐛 遇到问题？

### 问题1: ModuleNotFoundError
**原因**: 虚拟环境未激活或依赖未安装
**解决**:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### 问题2: CLAUDE_API_KEY not found
**原因**: .env文件未配置
**解决**:
```bash
# 检查.env文件是否存在
cat .env

# 确保包含:
# CLAUDE_API_KEY=sk-ant-xxxxx
```

### 问题3: 端口被占用
**原因**: 8000或8501端口已被使用
**解决**:
```bash
# Windows查看端口
netstat -ano | findstr :8000

# 更换端口启动
uvicorn app.main:app --reload --port 8001
streamlit run ui/app.py --server.port 8502
```

### 问题4: Streamlit显示"后端未连接"
**原因**: 后端未启动或端口不对
**解决**:
1. 确认终端1的后端正在运行
2. 访问 http://localhost:8000/ 确认后端正常
3. 刷新Streamlit页面

---

## 📊 功能验证清单

- [ ] 后端API启动成功（http://localhost:8000）
- [ ] 前端UI启动成功（http://localhost:8501）
- [ ] 侧边栏显示"✅ 后端运行正常"
- [ ] 可以发送消息并收到AI回复
- [ ] 点击"查看执行详情"可以看到调试信息
- [ ] database.db文件已创建
- [ ] 快捷测试按钮可以正常使用

---

## 🎉 下一步

Day 1-2已完成！你现在有了：
- ✅ 完整的后端API框架
- ✅ 可用的聊天界面
- ✅ AI意图识别和技能执行
- ✅ 数据库记录功能

**Day 3-5计划**:
1. 对接真实的订单API
2. 对接真实的库存系统
3. 实现真实的邮件发送

**保持动力，继续前进！💪**
