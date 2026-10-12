# XHR/Fetch 监听器正确实现方案

## 项目背景

微信小店客服页面 XHR 拦截与分析任务，需要监听内置 QWebEngineView 页面的所有 HTTP 请求和响应。

## 核心问题

Qt WebEngineView 的 JavaScript 和 Python 之间的通信是难点，需要通过轮询方式获取 JavaScript 中的数据。

## 正确实现方案

### 1. JavaScript Hook 注入（模块级常量）

```python
HOOK_JS = r"""
(function () {
    if (window.__xhrHooked) return;
    window.__xhrHooked = true;
    window.__xhr_queue = window.__xhr_queue || [];
    const MAX_BODY = 20000;

    // Hook XMLHttpRequest.prototype
    const XHR = XMLHttpRequest.prototype;
    const origOpen = XHR.open;
    const origSend = XHR.send;

    XHR.open = function (method, url) {
        this.__method = method;
        this.__url = url;
        return origOpen.apply(this, arguments);
    };

    XHR.send = function (body) {
        const self = this;
        self.addEventListener('loadend', function () {
            try {
                window.__xhr_queue.push({
                    kind: 'xhr',
                    method: self.__method || 'GET',
                    url: self.__url || '',
                    status: self.status,
                    responseBody: (self.responseText || '').slice(0, MAX_BODY),
                    timestamp: Date.now()
                });
            } catch (e) {}
        });
        return origSend.apply(this, arguments);
    };

    // Hook window.fetch
    const origFetch = window.fetch;
    if (origFetch) {
        window.fetch = function (input, init) {
            const url = (typeof input === 'string') ? input : (input && input.url) || '';
            const method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase();
            return origFetch.apply(this, arguments).then(function (resp) {
                try {
                    const clone = resp.clone();
                    clone.text().then(function (txt) {
                        window.__xhr_queue.push({
                            kind: 'fetch',
                            method: method,
                            url: url,
                            status: resp.status,
                            responseBody: (txt || '').slice(0, MAX_BODY),
                            timestamp: Date.now()
                        });
                    }).catch(function () {});
                } catch (e) {}
                return resp;
            });
        };
    }
})();
"""
```

**关键点**：
- 只 hook `prototype` 上的 `open` 和 `send`，不要替换构造函数
- 使用 `window.__xhr_queue` 队列存储请求数据
- 同时监听 XHR 和 Fetch 两种请求方式

### 2. 轮询机制（Qt QTimer）

```python
self._poll_timer = QTimer(self)
self._poll_timer.setInterval(800)  # 每 800ms 轮询一次
self._poll_timer.timeout.connect(self._poll)
```

### 3. 轮询方法

```python
def _poll(self):
    if not self.started or not self.web_view:
        return
    page = self.web_view.page()
    if not page:
        return
    # 从 JS 队列获取数据并清空队列
    js = "JSON.stringify((window.__xhr_queue && window.__xhr_queue.splice(0)) || [])"
    page.runJavaScript(js, self._on_poll_result)

def _on_poll_result(self, result):
    if not result:
        return
    try:
        items = json.loads(result)
    except Exception as e:
        self.log(f"解析 JS 队列失败：{e}", "ERROR")
        return
    for item in items:
        url = item.get("url", "")
        if self.is_ignored_request(url):
            continue
        self.requests.append(item)
        self.log(f"{item.get('method')} {url} -> {item.get('status')}", "REQUEST")
```

**关键点**：
- 使用 `splice(0)` 从队列头部取数据并清空
- 将结果返回给 Python，通过回调函数处理

### 4. 页面加载完成后注入 Hook

```python
def _on_load_finished(self, ok: bool):
    if self.started:
        self._setup_xhr_listener()
```

```python
def _setup_xhr_listener(self):
    if not self.web_view:
        self.log("QWebEngineView 未设置", "ERROR")
        return
    page = self.web_view.page()
    if not page:
        self.log("无法获取页面", "ERROR")
        return
    page.runJavaScript(HOOK_JS)
```

**关键点**：
- 页面加载完成后才注入 Hook，确保页面已准备好
- 使用 `loadFinished` 信号连接

### 5. 启动和停止

```python
def start(self) -> None:
    # 连接页面加载信号
    if not self._web_signals_connected:
        self.web_view.loadFinished.connect(self._on_load_finished)
        self._web_signals_connected = True
    
    # 注入 Hook
    self._setup_xhr_listener()
    
    # 启动轮询定时器
    self._poll_timer.start()
    
    self.started = True

def stop(self) -> None:
    self._poll_timer.stop()
    self.started = False
```

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   Qt WebEngineView                       │
│                   (内置浏览器页面)                         │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │              JavaScript Hook                     │   │
│  │  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │ XMLHttpRequest│ │ window.fetch│               │   │
│  │  │   .open     │  │    .send   │               │   │
│  │  └─────────────┘  └─────────────┘               │   │
│  │                    ↓                             │   │
│  │              window.__xhr_queue                  │   │
│  │         [请求 1, 请求 2, 请求 3, ...]             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
                          ↓ (轮询)
┌─────────────────────────────────────────────────────────┐
│                  Python (监听器)                          │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │              QTimer (800ms)                      │   │
│  │                    ↓                             │   │
│  │              _poll()                            │   │
│  │                    ↓                             │   │
│  │              page.runJavaScript()                │   │
│  │              "JSON.stringify(队列.splice(0))"    │   │
│  │                    ↓                             │   │
│  │              _on_poll_result(result)            │   │
│  │                    ↓                             │   │
│  │              过滤 + 记录 + 日志信号               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 数据格式

### XHR 请求格式
```python
{
    "kind": "xhr",
    "method": "GET",
    "url": "https://example.com/api/data",
    "status": 200,
    "responseBody": "...",  # 最多 20000 字符
    "timestamp": 1234567890
}
```

### Fetch 请求格式
```python
{
    "kind": "fetch",
    "method": "POST",
    "url": "https://example.com/api/data",
    "status": 201,
    "responseBody": "...",
    "timestamp": 1234567890
}
```

## 忽略的请求

```python
ignored_patterns = [
    r'\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot|ico|webp|mp4|webm|mp3|wav|ogg)$',
    r'^https://[^/]+/favicon\.ico$',
    r'^about:',
    r'^data:',
    r'^file:',
]
```

## 注意事项

1. **不要替换 XMLHttpRequest 构造函数**，只 hook prototype 方法
2. **页面加载完成后才注入 Hook**，确保页面环境已准备好
3. **使用 splice(0) 清空队列**，避免内存泄漏
4. **同时监听 XHR 和 Fetch**，覆盖所有 HTTP 请求方式
5. **轮询间隔建议 800ms**，平衡性能和实时性
6. **队列长度限制**，避免内存占用过大

## 主项目复用建议

1. 将此监听器代码封装为独立模块
2. 提供配置选项（轮询间隔、忽略模式等）
3. 提供诊断功能（检查 Hook 状态、队列长度等）
4. 支持多种输出方式（日志、数据库、文件等）
