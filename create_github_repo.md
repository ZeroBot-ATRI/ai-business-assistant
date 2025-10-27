# 创建 GitHub 仓库指南

## 方法 1：通过 GitHub 网页（推荐）

### 第1步：创建仓库
1. 访问：https://github.com/new
2. 填写信息：
   - **Repository name**: `ai-business-assistant`
   - **Description**: `企业AI业务助手 - 15天快速启动方案，基于Claude API + FastAPI + Streamlit`
   - **Visibility**: Public 或 Private（根据需要选择）
   - **不要勾选任何初始化选项**（README、.gitignore等）
3. 点击 **Create repository**

### 第2步：推送代码
复制仓库URL后，在终端运行：

```bash
# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/ai-business-assistant.git

# 重命名分支为main
git branch -M main

# 推送代码
git push -u origin main
```

## 方法 2：使用 GitHub CLI（需先安装）

### 安装 GitHub CLI

**Windows (使用 winget):**
```bash
winget install --id GitHub.cli
```

**或下载安装包:**
https://cli.github.com/

### 安装后使用

```bash
# 登录 GitHub
gh auth login

# 创建仓库并推送（会自动配置remote）
gh repo create ai-business-assistant --public --source=. --remote=origin --push
```

## 验证推送成功

推送完成后，访问你的仓库页面：
```
https://github.com/YOUR_USERNAME/ai-business-assistant
```

你应该能看到：
- ✅ 所有代码文件
- ✅ README.md 作为首页展示
- ✅ 16个文件，3496行代码

## 后续更新代码

每次修改后：
```bash
git add .
git commit -m "更新说明"
git push
```

## 保护敏感信息

**重要提醒：**
- ✅ `.env` 文件已被 `.gitignore` 忽略（不会上传）
- ✅ 虚拟环境 `venv/` 已被忽略
- ✅ 数据库文件 `*.db` 已被忽略
- ⚠️  请确保 `.env` 中的 `CLAUDE_API_KEY` 不要泄露

## 克隆到其他机器

其他人或其他机器使用：
```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/ai-business-assistant.git
cd ai-business-assistant

# 配置环境
cp .env.example .env
# 编辑 .env 填入 CLAUDE_API_KEY

# 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload  # 终端1
streamlit run ui/app.py        # 终端2
```
