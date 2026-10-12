#!/usr/bin/env python3
"""
XHR 监听器框架 - 监听 QWebEngineView 页面的 XHR 请求
用于拦截和记录微信小店客服页面的 XHR 请求
"""
import json
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView


def _looks_like_json(text: str) -> bool:
    if not text:
        return False
    s = text.strip()
    for prefix in (")]}'", "while(1);", "for(;;);"):
        if s.startswith(prefix):
            s = s[len(prefix):].lstrip()
            break
    if not (s.startswith("{") or s.startswith("[")):
        return False
    try:
        json.loads(s)
        return True
    except Exception:
        return False


def _pretty_json(text: str) -> str:
    s = (text or "").strip()
    for prefix in (")]}'", "while(1);", "for(;;);"):
        if s.startswith(prefix):
            s = s[len(prefix):].lstrip()
            break
    try:
        obj = json.loads(s)
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return s if s else "(空)"


# 可选：URL 关键词过滤（默认关闭，主过滤靠 JSON 检测）
FILTER_ENABLED = False

FILTER_KEYWORDS = [
    "cgi-bin",
    "login",
    "scan",
    "qrcode",
    "auth",
    "token",
    "session",
    "msg",
    "message",
    "sync",
    "push",
    "notify",
    "poll",
    "kf",
    "customer",
    "conversation",
    "shop",
    "store",
]


LOGS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")


def _make_run_dir():
    from datetime import datetime
    name = "capture_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = os.path.join(LOGS_ROOT, name)
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, "responses"), exist_ok=True)
    return path


# 模块级常量：XHR Hook JavaScript 代码
HOOK_JS = r"""
(function () {
    if (window.__xhrHooked) return;
    window.__xhrHooked = true;
    window.__xhr_queue = window.__xhr_queue || [];
    const MAX_BODY = 500000;

    const XHR = XMLHttpRequest.prototype;
    const origOpen = XHR.open;
    const origSend = XHR.send;

    XHR.open = function (method, url) {
        this.__method = method;
        this.__url = url;
        return origOpen.apply(this, arguments);
    };

    const origSetHeader = XHR.setRequestHeader;
    XHR.setRequestHeader = function (name, value) {
        if (!this.__reqHeaders) this.__reqHeaders = {};
        this.__reqHeaders[name] = value;
        return origSetHeader.apply(this, arguments);
    };

    XHR.send = function (body) {
        const self = this;
        self.__reqBody = body;
        self.addEventListener('loadend', function () {
            try {
                window.__xhr_queue.push({
                    kind: 'xhr',
                    method: self.__method || 'GET',
                    url: self.__url || '',
                    status: self.status,
                    requestHeaders: self.__reqHeaders || {},
                    requestBody: self.__reqBody == null ? '' : String(self.__reqBody).slice(0, MAX_BODY),
                    responseBody: (self.responseText || '').slice(0, MAX_BODY),
                    timestamp: Date.now()
                });
            } catch (e) {}
        });
        return origSend.apply(this, arguments);
    };

    const origFetch = window.fetch;
    if (origFetch) {
        window.fetch = function (input, init) {
            const url = (typeof input === 'string') ? input : (input && input.url) || '';
            const method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase();
            const reqBody = init && init.body ? String(init.body).slice(0, MAX_BODY) : '';
            return origFetch.apply(this, arguments).then(function (resp) {
                try {
                    const clone = resp.clone();
                    clone.text().then(function (txt) {
                        window.__xhr_queue.push({
                            kind: 'fetch',
                            method: method,
                            url: url,
                            status: resp.status,
                            requestHeaders: (init && init.headers) || {},
                            requestBody: reqBody,
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


class XHRListener(QObject):
    """XHR 监听器基类 - 监听 QWebEngineView 页面"""
    
    # 信号：用于向 GUI 发送日志
    log_signal = pyqtSignal(str)
    
    def __init__(self, web_view: QWebEngineView):
        super().__init__()
        self.web_view = web_view
        self.requests: List[Dict[str, Any]] = []
        self.started = False
        self._page = None
        self._web_signals_connected = False
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(800)
        self._poll_timer.timeout.connect(self._poll)
        
        self.capture_dir = None
        self.capture_file = None
        self.responses_dir = None
        self._request_index = 0
    
    def is_ignored_request(self, url: str) -> bool:
        """判断请求是否应该被忽略"""
        ignored_patterns = [
            r'\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot|ico|webp|mp4|webm|mp3|wav|ogg)$',
            r'^https://[^/]+/favicon\.ico$',
            r'^about:',
            r'^data:',
            r'^file:',
        ]
        for pattern in ignored_patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def should_record(self, url: str) -> bool:
        if not FILTER_ENABLED:
            return True
        if not url:
            return False
        lower = url.lower()
        for kw in FILTER_KEYWORDS:
            if kw.lower() in lower:
                return True
        return False
    
    def should_log_request(self, request: Any) -> bool:
        """判断请求是否应该记录"""
        url = request.url
        return not self.is_ignored_request(url) and self.should_record(url)
    
    def get_request_info(self, request: Any, response: Any = None) -> Dict[str, Any]:
        """提取请求信息"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": request.url,
            "request_headers": dict(request.headers),
        }
        
        if response:
            info["status"] = response.status
            info["response_headers"] = dict(response.headers)
            try:
                if response.content_length and response.content_length < 10000:
                    info["response_body"] = response.text
                elif response.content_length and response.content_length > 0:
                    info["response_body"] = f"[响应内容长度：{response.content_length}]"
                else:
                    info["response_body"] = "[响应内容未知]"
            except Exception:
                info["response_body"] = "[无法获取响应内容]"
        
        return info
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[LISTENER] [{level}] {message}", flush=True)
        self.log_signal.emit(f"[{level}] {message}")
    
    def _setup_xhr_listener(self):
        """设置 XHR 监听器 - 使用 JavaScript 注入方式"""
        if not self.web_view:
            self.log("QWebEngineView 未设置", "ERROR")
            return
        page = self.web_view.page()
        if not page:
            self.log("无法获取页面", "ERROR")
            return
        page.runJavaScript(HOOK_JS)
    
    def _poll(self):
        if not self.started or not self.web_view:
            return
        page = self.web_view.page()
        if not page:
            return
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
            if not self.should_record(url):
                continue

            body = item.get("responseBody", "") or ""
            if not _looks_like_json(body):
                print(f"[FILTER-SKIP] {url} 长度={len(body)} 头部={body[:80]!r}", flush=True)
                continue

            self.requests.append(item)
            self._save_json_record(item)
            self.log(
                f"{item.get('method')} {url} -> {item.get('status')} [JSON {len(body)}B]",
                "REQUEST",
            )
    
    def _on_load_finished(self, ok: bool):
        if self.started:
            self._setup_xhr_listener()
    
    def _save_json_record(self, item: Dict[str, Any]):
        if not self.capture_dir or not self.responses_dir or not self.capture_file:
            return
        try:
            os.makedirs(self.capture_dir, exist_ok=True)
            os.makedirs(self.responses_dir, exist_ok=True)
            self._request_index += 1
            idx = self._request_index

            method = item.get("method", "GET")
            url = item.get("url", "")
            status = item.get("status", "")
            req_headers = item.get("requestHeaders") or {}
            req_body = item.get("requestBody") or ""
            resp_body = item.get("responseBody") or ""

            short = re.sub(r'[^a-zA-Z0-9_\-]+', '_', url.split('?')[0])
            short = short.strip('_')[-40:] or "resp"
            fname = f"{idx:03d}_{short}.json"
            fpath = os.path.join(self.responses_dir, fname)

            with open(fpath, "w", encoding="utf-8") as f:
                f.write(_pretty_json(resp_body))

            lines = []
            lines.append(f"## [{idx}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {method} {url}")
            lines.append("")
            lines.append(f"**Status**: {status}")
            lines.append(f"**Response**: responses/{fname}")
            lines.append("")
            lines.append("### Request Headers")
            if req_headers:
                for k, v in req_headers.items():
                    lines.append(f"- {k}: {v}")
            else:
                lines.append("(无)")
            lines.append("")
            lines.append("### Request Body")
            lines.append("```")
            lines.append(str(req_body) if req_body else "(空)")
            lines.append("```")
            lines.append("")
            lines.append("---")
            lines.append("")

            with open(self.capture_file, "a", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            self.log(f"保存记录失败：{e}", "ERROR")
        except Exception as e:
            self.log(f"保存记录失败：{e}", "ERROR")
    
    def start(self) -> None:
        """启动监听器"""
        if self.started:
            return
        
        try:
            self.log("启动监听器...", "INFO")
            
            # 连接页面加载信号
            if not self._web_signals_connected:
                self.web_view.loadFinished.connect(self._on_load_finished)
                self._web_signals_connected = True
            
            # 注入 JavaScript 监听代码
            self._setup_xhr_listener()
            
            # 启动轮询定时器
            # 每次启动新建一个独立目录
            try:
                self.capture_dir = _make_run_dir()
                self.capture_file = os.path.join(self.capture_dir, "index.md")
                self.responses_dir = os.path.join(self.capture_dir, "responses")
                self._request_index = 0

                with open(self.capture_file, "w", encoding="utf-8") as f:
                    f.write("# XHR 抓取索引\n\n")
                    f.write(f"抓取开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("每个请求的 Response 单独存放在 responses/ 目录下。\n\n")
                    f.write("---\n\n")

                self.log(f"本次记录目录：{self.capture_dir}", "INFO")
            except Exception as e:
                self.log(f"初始化日志目录失败：{e}", "ERROR")
                raise

            self._poll_timer.start()
            
            self.started = True
            self.log("监听已启动，监听 QWebEngineView 页面", "SUCCESS")
            
        except Exception as e:
            self.log(f"启动失败：{e}", "ERROR")
            raise
    
    def stop(self) -> None:
        """停止监听器"""
        if not self.started:
            return
        
        self._poll_timer.stop()
        self.started = False
        self.log("监听已停止", "INFO")
    
    def get_request_count(self) -> int:
        """获取请求数量"""
        return len(self.requests)
    
    def get_requests(self) -> List[Dict[str, Any]]:
        """获取所有请求记录"""
        return self.requests.copy()
    
    def clear_requests(self):
        """清空请求记录"""
        self.requests.clear()
        self.log("请求记录已清空", "INFO")


class WeChatStoreXHRListener(XHRListener):
    """微信小店客服页面 XHR 监听器"""
    
    TARGET_URL = "https://store.weixin.qq.com/shop/kf"
    
    def __init__(self, web_view: QWebEngineView):
        super().__init__(web_view)


class BrowserPageManager:
    """浏览器页面管理器"""
    
    def __init__(self, target_url: str = WeChatStoreXHRListener.TARGET_URL):
        self.target_url = target_url
