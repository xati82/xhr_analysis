# XHR 拦截与分析任务

## 📋 任务说明

**目标**：拦截微信小店客服页面的 XHR 请求，记录所有关键 API 接口信息，为后续编写自动回复逻辑做准备。

**目标页面**：`https://store.weixin.qq.com/shop/kf`

**状态**：进行中

---

## 📂 目录结构

```
src/xhr_analysis/
├── README.md                 # 本文件
├── PROGRESS.md               # 进度跟踪
├── monitor/                  # 监听器代码
│   ├── __init__.py
│   └── listener.py           # XHR 监听器框架
├── analysis/                 # 分析结果
├── data/                     # 原始数据
└── scripts/                  # 辅助脚本
```

---

## 🛠️ 框架说明

### 核心类

1. **`XHRListener`** - 基类
   - `start()` - 启动监听
   - `stop()` - 停止监听
   - `on_request()` - 请求回调
   - `on_response()` - 响应回调
   - `get_requests()` - 获取请求列表
   - `save_requests()` - 保存请求到文件

2. **`WeChatStoreXHRListener`** - 微信小店专用监听器
   - 继承自 `XHRListener`
   - 目标 URL：`https://store.weixin.qq.com/shop/kf`
   - 提供输出目录配置

3. **`BrowserPageManager`** - 浏览器页面管理器
   - `launch()` - 启动浏览器
   - `navigate()` - 导航到目标页面
   - `close()` - 关闭浏览器

---

## 📝 使用示例

```python
from xhr_analysis.monitor.listener import WeChatStoreXHRListener, BrowserPageManager

# 创建监听器
listener = WeChatStoreXHRListener(output_dir="data")

# 创建浏览器管理器
manager = BrowserPageManager()

# 启动浏览器并导航
manager.launch()
manager.navigate()

# 开始监听
listener.start()

# ... 等待捕获请求 ...

# 停止监听
listener.stop()

# 保存请求记录
listener.save_requests("xhr_logs.json")
```

---

## 🧪 测试框架

```bash
cd /workspace/开发/wechat-assistant/src/xhr_analysis
python test_framework.py
```

---

## 📞 下一步

1. 实现 `WeChatStoreXHRListener` 的监听功能
2. 集成 Playwright 浏览器
3. 捕获并记录 XHR 请求
4. 分析请求数据

---

## 📞 备注

- 所有操作在 `src/xhr_analysis/` 文件夹内进行
- 删除此文件夹不影响主线程序
- 框架已创建完成，等待实现具体功能