# 启动指南

## 方法1：简化启动脚本（推荐）

**适用于**：已安装依赖，不想使用虚拟环境

```bash
start_simple.bat
```

这会打开3个窗口：
- 窗口1：后端API（端口8000）
- 窗口2：聊天界面（端口8501）
- 窗口3：监控看板（端口8502）

---

## 方法2：手动启动（最稳定）

### 终端1 - 后端API
```bash
# 激活虚拟环境（如果使用）
venv\Scripts\activate

# 启动后端
python -m uvicorn app.main:app --reload
# 或
uvicorn app.main:app --reload
```

看到这个输出就成功了：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 终端2 - 聊天界面
```bash
# 激活虚拟环境（如果使用）
venv\Scripts\activate

# 启动聊天界面
python -m streamlit run ui\app_enhanced.py
# 或
streamlit run ui\app_enhanced.py
```

浏览器会自动打开 http://localhost:8501

### 终端3 - 监控看板
```bash
# 激活虚拟环境（如果使用）
venv\Scripts\activate

# 启动监控看板
python -m streamlit run ui\dashboard.py --server.port 8502
# 或
streamlit run ui\dashboard.py --server.port 8502
```

浏览器会打开 http://localhost:8502

---

## 方法3：使用虚拟环境启动脚本

如果你使用虚拟环境：

```bash
start_all.bat
```

---

## 访问地址

启动成功后，访问以下地址：

| 服务 | 地址 | 说明 |
|-----|------|------|
| 后端API | http://localhost:8000 | API接口 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| 聊天界面 | http://localhost:8501 | 主要交互界面 |
| 监控看板 | http://localhost:8502 | 数据可视化 |

---

## 常见问题

### Q1: "uvicorn不是内部或外部命令"

**原因**：uvicorn未安装或未在PATH中

**解决方法**：
```bash
# 方法1：使用python -m
python -m uvicorn app.main:app --reload

# 方法2：重新安装
pip install uvicorn

# 方法3：激活虚拟环境
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Q2: "streamlit不是内部或外部命令"

**原因**：streamlit未安装

**解决方法**：
```bash
# 方法1：使用python -m
python -m streamlit run ui\app_enhanced.py

# 方法2：安装streamlit
pip install streamlit

# 方法3：安装所有依赖
pip install -r requirements.txt
```

### Q3: 端口被占用

**错误信息**：`Address already in use`

**解决方法**：

**查看占用端口的进程**：
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# 找到PID后，杀掉进程
taskkill /PID [进程ID] /F
```

**或者使用其他端口**：
```bash
# 后端使用8001
uvicorn app.main:app --port 8001

# 聊天界面使用8503
streamlit run ui\app_enhanced.py --server.port 8503
```

### Q4: 后端启动后立即退出

**可能原因**：
1. 没有 `.env` 文件
2. `CLAUDE_API_KEY` 未配置

**解决方法**：
```bash
# 1. 复制配置文件
copy .env.example .env

# 2. 编辑 .env 文件，填入API密钥
notepad .env

# 3. 确保包含这一行
CLAUDE_API_KEY=sk-ant-xxxxx
```

### Q5: 聊天界面显示"后端未连接"

**解决方法**：
1. 确认后端已启动（终端1）
2. 访问 http://localhost:8000 确认后端正常
3. 检查防火墙设置
4. 刷新聊天界面

### Q6: start_all.bat 无法启动

**解决方法**：使用 `start_simple.bat` 或手动启动

---

## 只启动后端（用于测试）

如果只想测试后端API：

```bash
# 启动后端
uvicorn app.main:app --reload

# 访问API文档
http://localhost:8000/docs

# 测试聊天接口
curl -X POST "http://localhost:8000/chat?user_input=查询订单12345的状态"
```

---

## 只启动聊天界面

如果后端已经在运行，只启动聊天界面：

```bash
streamlit run ui\app_enhanced.py
```

或使用原始版本：
```bash
streamlit run ui\app.py
```

---

## 停止服务

### Windows
- 关闭对应的命令行窗口
- 或在窗口中按 `Ctrl+C`

### 使用任务管理器
1. 打开任务管理器（Ctrl+Shift+Esc）
2. 找到 `python.exe` 或 `uvicorn.exe`
3. 右键 → 结束任务

---

## 推荐启动顺序

1. **先启动后端**（等待5秒）
2. **再启动聊天界面**（等待2秒）
3. **最后启动监控看板**

这样可以确保依赖关系正确。

---

## 开发模式 vs 生产模式

### 开发模式（当前）
```bash
uvicorn app.main:app --reload  # 自动重载
```

### 生产模式（部署时）
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 日志查看

### 后端日志
终端1会显示所有请求日志

### Streamlit日志
终端2和终端3会显示前端日志

---

## 性能优化

如果启动较慢：

1. **使用 `--reload` 仅在开发时**
2. **减少日志输出**
3. **关闭不需要的服务**（如只用聊天界面）

---

## 快速测试

启动成功后：

1. 访问 http://localhost:8501
2. 点击侧边栏"查询正常订单"
3. 查看AI响应
4. 访问 http://localhost:8502 查看监控

---

**选择最适合你的启动方式，开始使用吧！** 🚀
