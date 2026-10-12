# XHR 拦截与分析任务 - 进度跟踪

## 📋 任务概述

**目标**：拦截微信小店客服页面的 XHR 请求，记录所有关键 API 接口信息（URL、方法、参数、响应格式等），为后续编写自动回复逻辑做准备。

**状态**：进行中

**创建时间**：2026-10-10

---

## 📍 任务拆分

### 任务列表

| 序号 | 任务名称 | 状态 | 预估时间 | 实际时间 | 备注 |
|------|----------|------|----------|----------|------|
| 1 | 创建基础 XHR 监听器框架 | ✅ 已完成 | 30min | 30min | 创建 `src/xhr_analysis/monitor/listener.py` |
| 2 | 测试监听功能并捕获初始页面加载的 XHR | 🟡 进行中 | 30min | - | 验证监听器工作正常，捕获初始页面 |
| 3 | 分析登录相关的 XHR 请求 | 🟡 待开始 | 1 小时 | - | 登录流程 API 交互 |
| 4 | 分析消息相关 XHR 请求 | 🟡 待开始 | 1.5 小时 | - | 消息收发核心接口 |
| 5 | 分析客服状态相关 XHR 请求 | 🟡 待开始 | 45min | - | 状态切换 API |
| 6 | 分析其他业务相关 XHR 请求 | 🟡 待开始 | 1 小时 | - | 店铺管理、客户列表等 |
| 7 | 整理完整 API 文档并标注自动回复逻辑 | 🟡 待开始 | 1 小时 | - | 整合所有分析结果 |

---

## 📊 当前进度

### 已完成
- ✅ 创建独立任务文件夹 `src/xhr_analysis/`
- ✅ 创建基础 XHR 监听器框架（`monitor/listener.py`）
- ✅ 创建数据记录模块（`record_data.py`）
- ✅ 创建数据库配置模块（`config/database_config.py`）
- ✅ 创建模块初始化文件（`__init__.py`）
- ✅ 创建框架测试脚本（`test_framework.py`）
- ✅ 创建进度跟踪文档（`PROGRESS.md`）
- ✅ 创建任务说明文档（`README.md`）
- ✅ 创建简单 GUI 界面（`gui/browser_viewer.py`）
- ✅ 创建 GUI 测试脚本（`gui/test_gui.py`）
- ✅ 创建 Windows 运行指南（`WINDOWS_GUIDE.md`）
- ✅ **推送到 GitHub** (main 分支)
- ✅ **修复 GUI 导入错误** (QWebEngineView 需从 QtWebEngineWidgets 导入)

### 进行中
- ⏳ 混合存储方案已规划并实现

### 待开始
- ⏹️ 任务 2-7 待开始

---

## 📝 详细计划

### 阶段一：基础框架搭建（任务 1 ✅）
- ✅ 建立 XHR 监听器基础框架
- ✅ 实现数据库配置
- ✅ 实现混合存储（数据库 + JSON + JSONL）
- ✅ 创建简单 GUI 界面
- ✅ 创建 Windows 运行指南
- ✅ 推送到 GitHub
- ✅ 修复 GUI 导入错误

### 阶段二：核心业务分析（任务 3-5）
- ⏳ 分析登录、消息、状态三大核心功能
- 产出：API 接口文档

### 阶段三：扩展功能分析（任务 6）
- ⏳ 分析其他业务功能
- 产出：业务 API 接口文档

### 阶段四：整合与文档（任务 7）
- ⏳ 整理所有分析结果，标注自动回复逻辑
- 产出：完整的 API 接口文档 + 自动回复逻辑分析

---

## 📂 文件组织

```
src/xhr_analysis/
├── PROGRESS.md              # 进度跟踪
├── README.md                # 任务说明
├── WINDOWS_GUIDE.md         # Windows 运行指南 ⭐
├── __init__.py              # 模块初始化
├── test_framework.py        # 框架测试
├── record_data.py           # 数据记录模块
├── config/
│   └── database_config.py   # 数据库配置
├── gui/
│   ├── __init__.py          # GUI 模块初始化
│   ├── browser_viewer.py    # 浏览器查看器（GUI）
│   └── test_gui.py          # GUI 测试
├── monitor/
│   ├── __init__.py
│   └── listener.py          # XHR 监听器框架
├── analysis/                # 分析结果（待创建）
├── data/                    # 原始数据（待创建）
└── scripts/                 # 辅助脚本（待创建）
```

---

## 🖥️ GUI 界面说明

**功能特性：**
- ✅ 浏览器页面显示（默认加载 `https://store.weixin.qq.com/shop/kf`）
- ✅ 日志输出面板（可折叠，默认 200px 高度）
- ✅ 页面刷新按钮
- ✅ 日志展开/折叠切换
- ✅ 日志清空功能
- ✅ 深色主题界面

**界面布局：**
```
+----------------------+------------------+
| XHR 监听器            | [刷新] [日志]   |
+----------------------+------------------+
| 浏览器页面 (1200px)   | 日志面板 (200px) |
|                      |                  |
+----------------------+------------------+
```

**日志面板控制：**
- 点击"查看日志"按钮可切换显示/隐藏
- 点击"展开"按钮可切换展开/折叠
- 点击"清空"按钮可清空日志内容

---

## 📝 数据存储方案（混合存储）

### 存储位置

```
src/xhr_analysis/
├── data/
│   ├── xhr.db                    # SQLite 数据库（结构化）
│   ├── xhr_logs.json             # JSON 原始记录（备份）
│   └── xhr_timeline.jsonl        # 时间线格式（流式）
├── data/xhr_backup/              # 数据库备份
├── analysis/
│   ├── api_summary.md            # API 汇总文档
│   ├── api_documentation.md      # API 详细文档
│   ├── login_api.md              # 登录 API 文档
│   ├── message_api.md            # 消息 API 文档
│   └── status_api.md             # 状态 API 文档
└── scripts/
    ├── record.py                 # 记录脚本
    ├── analyze.py                # 分析脚本
    └── export.py                 # 导出工具
```

### 存储策略

1. **实时记录** → 数据库（`xhr.db`）
2. **批量导出** → JSON 文件（`xhr_logs.json`）
3. **时间线分析** → JSONL 文件（`xhr_timeline.jsonl`）
4. **人工分析** → Markdown 文档（`analysis/`）

---

## 🎯 关键里程碑

- [x] 任务 1 完成：基础框架搭建完成
- [ ] 任务 2：框架测试通过
- [ ] 任务 3-5：核心业务分析完成
- [ ] 任务 6：扩展功能分析完成
- [ ] 任务 7：完整文档输出

---

## 📅 更新日期

- 2026-10-10: 创建任务文件夹和基础框架
- 2026-10-10: 实现混合存储方案
- 2026-10-10: 创建简单 GUI 界面
- 2026-10-10: **推送到 GitHub**
- 2026-10-10: **修复 GUI 导入错误**

---

## 📞 备注

- 所有操作在 `src/xhr_analysis/` 文件夹内进行
- 删除此文件夹不影响主线程序
- 分析结果将用于后续自动回复逻辑开发
- 混合存储方案：数据库 + JSON + JSONL
- GUI 界面采用 PyQt6，深色主题
- **已推送到 GitHub: https://github.com/xati82/wechat-assistant**
- **Windows 运行指南：WINDOWS_GUIDE.md**

---

## 🚀 提交内容

本次提交包含以下文件：

1. `src/xhr_analysis/PROGRESS.md` - 进度跟踪
2. `src/xhr_analysis/README.md` - 任务说明
3. `src/xhr_analysis/WINDOWS_GUIDE.md` - Windows 运行指南 ⭐
4. `src/xhr_analysis/__init__.py` - 模块初始化
5. `src/xhr_analysis/test_framework.py` - 框架测试
6. `src/xhr_analysis/record_data.py` - 数据记录模块
7. `src/xhr_analysis/config/database_config.py` - 数据库配置
8. `src/xhr_analysis/gui/__init__.py` - GUI 模块初始化
9. `src/xhr_analysis/gui/browser_viewer.py` - 浏览器查看器（GUI）
10. `src/xhr_analysis/gui/test_gui.py` - GUI 测试
11. `src/xhr_analysis/monitor/__init__.py` - 监听器模块初始化
12. `src/xhr_analysis/monitor/listener.py` - XHR 监听器框架

---

**提交成功！可以在 Windows 上预览 GUI 界面了！** 🎉