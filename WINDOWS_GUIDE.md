# XHR 拦截与分析任务 - Windows 运行指南

## 📋 项目信息

- **仓库地址**: https://github.com/xati82/wechat-assistant
- **分支**: main
- **任务**: XHR 拦截与分析

---

## 🖥️ Windows 环境准备

### 1. 安装 Python 3.10+

**要求**: Python 3.10 或更高版本（QWebEngineProfile 需要 Python 3.10+）

**安装方法**:
```powershell
# 从 Python 官网下载 installer
https://www.python.org/downloads/

# 安装时务必勾选 "Add Python to PATH"
```

**验证安装**:
```powershell
python --version
# 应该显示 Python 3.10.x 或更高版本
```

---

### 2. 克隆项目代码

**方法 1：使用 GitHub Desktop**（推荐）

1. 下载 GitHub Desktop
   - https://desktop.githubusercontent.com/
2. 克隆仓库：
   - Repository → Clone Repository
   - 选择 https://github.com/xati82/wechat-assistant.git
   - 选择保存路径（如 D:\projects\wechat-assistant）
   - 点击 Clone

**方法 2：使用 Git Bash / PowerShell**

```powershell
# 在目标目录（如 D:\projects）运行：
git clone https://github.com/xati82/wechat-assistant.git

# 进入项目目录：
cd wechat-assistant
```

---

### 3. 创建虚拟环境

```powershell
# 在项目根目录运行：
python -m venv venv

# 激活虚拟环境：
venv\Scripts\Activate.ps1

# 确认激活：
# 命令行前缀应该显示 (venv)
```

---

### 4. 安装依赖

```powershell
# 在激活的虚拟环境中运行：
pip install -r requirements.txt
```

**依赖说明**:
- PyQt6 + PyQt6-WebEngine - GUI 框架和浏览器控件
- playwright - 浏览器自动化（可选，用于后续功能）
- aiohttp - 异步 HTTP 请求（可选）
- pyinstaller >= 6.8.0 - 打包工具（可选）
- chromadb >= 0.4.24 - 向量数据库（可选）
- faiss-cpu >= 1.8.0 - 向量检索引擎（可选）

---

## 🚀 运行 GUI 界面

### 方法 1：直接运行

```powershell
# 在激活的虚拟环境中运行：
cd src/xhr_analysis
python gui/browser_viewer.py
```

### 方法 2：添加快捷方式

1. 创建批处理文件 `run_gui.bat`：
```batch
@echo off
cd /d %~dp0
call venv\Scripts\Activate.ps1
python gui/browser_viewer.py
```

2. 双击运行 `run_gui.bat`

---

## 📊 查看日志输出

**日志面板功能**:
- 点击"查看日志"按钮可切换显示/隐藏
- 点击"展开"按钮可切换展开/折叠
- 点击"清空"按钮可清空日志内容

**日志位置**:
- 数据库文件：`src/xhr_analysis/data/xhr.db`
- JSON 日志：`src/xhr_analysis/data/xhr_logs.json`
- JSONL 日志：`src/xhr_analysis/data/xhr_timeline.jsonl`

---

## 🔧 常见问题

### 问题 1: PyQt6 安装失败

**错误**: `ModuleNotFoundError: No module named 'PyQt6'`

**解决**:
```powershell
pip install PyQt6 PyQt6-WebEngine
```

### 问题 2: 浏览器白屏

**原因**: Windows GPU 渲染问题

**解决**:
```powershell
# 设置环境变量（在系统属性→高级→环境变量中）：
QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"
```

### 问题 3: 页面无法加载

**原因**: 网络连接或微信小店页面限制

**解决**:
- 检查网络连接
- 尝试刷新页面（点击"刷新页面"按钮）

### 问题 4: Python 版本太低

**错误**: `QWebEngineProfile 需要 Python 3.10+`

**解决**:
- 卸载当前 Python
- 从官网下载 Python 3.10 或更高版本
- 重新安装时勾选 "Add Python to PATH"

---

## 📁 项目结构

```
wechat-assistant/
├── src/
│   └── xhr_analysis/           # XHR 分析任务
│       ├── gui/                # GUI 界面
│       │   ├── browser_viewer.py
│       │   └── test_gui.py
│       ├── monitor/            # 监听器框架
│       ├── config/             # 数据库配置
│       ├── record_data.py      # 数据记录模块
│       ├── PROGRESS.md         # 进度跟踪
│       ├── README.md           # 任务说明
│       └── __init__.py
├── requirements.txt            # Python 依赖
└── README.md
```

---

## 📞 下一步

1. **运行 GUI** - 预览浏览器页面和日志输出
2. **测试功能** - 验证各项功能正常工作
3. **实现监听** - 添加 Playwright 监听功能
4. **分析数据** - 分析捕获的 XHR 请求

---

## 🎯 目标

- ✅ 创建独立任务文件夹
- ✅ 实现混合存储方案
- ✅ 创建简单 GUI 界面
- ⏳ 实现 Playwright 集成
- ⏳ 分析 XHR 请求数据
- ⏳ 生成 API 文档

---

**祝开发顺利！** 🚀
