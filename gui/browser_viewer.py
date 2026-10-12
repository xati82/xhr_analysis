#!/usr/bin/env python3
"""
XHR 监听器 - 简单 GUI 界面
包含浏览器页面和日志输出
"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSplitter, QPushButton, QLabel, QLineEdit,
    QTabWidget, QGroupBox, QScrollArea
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from xhr_analysis.monitor.listener import WeChatStoreXHRListener


class XHRLogViewer(QScrollArea):
    """日志查看器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setMinimumWidth(250)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("日志输出")
        self.label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumHeight(16777215)
        self.text_edit.setMinimumHeight(100)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("清空")
        self.expand_btn = QPushButton("展开")
        self.expand_btn.setCheckable(True)
        self.expand_btn.clicked.connect(self.toggle_expand)
        self.expand_btn.setChecked(True)
        
        self.clear_btn.clicked.connect(self.clear_text)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.expand_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setWidget(widget)
        self.expanded = True
        self.text_edit.setVisible(True)
        self.expand_btn.setChecked(True)
    
    def clear_text(self):
        self.text_edit.clear()
    
    def append_text(self, text: str):
        """追加文本"""
        self.text_edit.append(text)
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )
    
    def toggle_expand(self):
        self.expanded = self.expand_btn.isChecked()
        self.text_edit.setVisible(self.expanded)


class BrowserPageViewer(QWebEngineView):
    """浏览器页面查看器"""
    
    def __init__(self, target_url: str = "https://store.weixin.qq.com/shop/kf"):
        super().__init__()
        self.target_url = target_url
        self.setStyleSheet("""
            QWebEngineView {
                background-color: white;
            }
        """)
    
    def navigate_to(self, url: str):
        """导航到 URL"""
        self.setUrl(QUrl(url))


class XHRListenerGUI(QMainWindow):
    """XHR 监听器 GUI"""
    
    def __init__(self):
        super().__init__()
        self.browser_page = None
        self.log_viewer = None
        self.listener = None
        
        self._setup_ui()
        self.browser_page.urlChanged.connect(self._on_url_changed)
        self._load_browser_page()
    
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("XHR 监听器 - 通用 JSON 接口采集")
        self.resize(1000, 700)  # 调整窗口大小以适应浏览器占满的布局
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        # 顶部标题栏
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("XHR 监听器"))
        title_layout.addStretch()
        
        # 控制按钮
        self.navigate_btn = QPushButton("刷新页面")
        self.navigate_btn.clicked.connect(self.refresh_page)
        title_layout.addWidget(self.navigate_btn)
        
        self.log_btn = QPushButton("查看日志")
        self.log_btn.setCheckable(True)
        self.log_btn.setChecked(False)  # 默认隐藏日志面板
        self.log_btn.clicked.connect(self._toggle_log_panel)
        title_layout.addWidget(self.log_btn)
        
        # 启动/停止按钮
        self.start_btn = QPushButton("启动监听")
        self.start_btn.clicked.connect(self._toggle_monitoring)
        self.start_btn.pressed.connect(self._on_start_pressed)
        self.start_btn.released.connect(self._on_start_released)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:pressed:hover {
                background-color: #3a7f3a;
            }
        """)
        title_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止监听")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.pressed.connect(self._on_stop_pressed)
        self.stop_btn.released.connect(self._on_stop_released)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
            QPushButton:pressed:hover {
                background-color: #b71c1c;
            }
        """)
        title_layout.addWidget(self.stop_btn)
        
        self.diag_btn = QPushButton("诊断")
        self.diag_btn.clicked.connect(self._run_diagnose)
        title_layout.addWidget(self.diag_btn)
        
        self.open_dir_btn = QPushButton("打开日志目录")
        self.open_dir_btn.clicked.connect(self._open_log_dir)
        title_layout.addWidget(self.open_dir_btn)
        
        self.layout.addLayout(title_layout)
        
        # 分割器
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)
        
        # 浏览器页面（左侧）- 使用 QWebEngineView，但我们需要将 Playwright 注入或替换为独立浏览器窗口
        # 目前 GUI 中的 QWebEngineView 和点击 "启动监听" 启动的 Playwright 浏览器是两回事！
        # 点击 "启动监听" 会通过 Playwright 启动一个独立的 Chrome 浏览器，而不是在当前的 QWebEngineView 中显示。
        self.browser_page = BrowserPageViewer("https://store.weixin.qq.com/shop/kf")
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)

        # 地址栏
        addr_layout = QHBoxLayout()
        self.addr_edit = QLineEdit()
        self.addr_edit.setPlaceholderText("输入 URL 后回车，例如 store.weixin.qq.com/shop/kf")
        self.addr_edit.returnPressed.connect(self._navigate_to_input)
        self.addr_edit.setText("https://store.weixin.qq.com/shop/kf")
        addr_layout.addWidget(self.addr_edit)

        self.go_btn = QPushButton("转到")
        self.go_btn.clicked.connect(self._navigate_to_input)
        addr_layout.addWidget(self.go_btn)

        browser_layout.addLayout(addr_layout)
        browser_layout.addWidget(self.browser_page)
        
        # 日志输出（右侧，可折叠）
        self.log_viewer = XHRLogViewer()
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.addWidget(self.log_viewer)
        
        # 设置分割比例 - 浏览器占满，日志面板默认隐藏
        self.splitter.addWidget(browser_widget)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.addWidget(log_widget)
        self.splitter.setSizes([900, 300])  # 浏览器 900px，日志 300px
    
    def _navigate_to_input(self):
        text = self.addr_edit.text().strip()
        if not text:
            return
        if not text.startswith(("http://", "https://", "about:", "file:", "data:")):
            text = "https://" + text
            self.addr_edit.setText(text)
        try:
            self.browser_page.setUrl(QUrl(text))
            self._log(f"导航到：{text}", "INFO")
        except Exception as e:
            self._log(f"导航失败：{e}", "ERROR")
    
    def _on_url_changed(self, url: QUrl):
        try:
            self.addr_edit.setText(url.toString())
        except Exception:
            pass
    
    def _load_browser_page(self):
        try:
            url = self.addr_edit.text().strip() or "https://store.weixin.qq.com/shop/kf"
            self.browser_page.setUrl(QUrl(url))
            self._log(f"加载页面：{url}", "INFO")
        except Exception as e:
            self._log(f"加载页面失败：{e}", "ERROR")
    
    def _toggle_log_panel(self):
        if self.log_btn.isChecked():
            self.splitter.setSizes([800, 300])
        else:
            self.splitter.setSizes([self.splitter.width(), 0])
        self.splitter.update()
    
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = self._get_timestamp()
        self.log_viewer.append_text(f"[{timestamp}] {message}\n")
    
    def _get_timestamp(self):
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def refresh_page(self):
        """刷新页面"""
        try:
            self.browser_page.reload()
            self._log("页面已刷新", "INFO")
        except Exception as e:
            self._log(f"刷新页面失败：{e}", "ERROR")
    
    def _toggle_monitoring(self):
        """切换监听状态"""
        if not self.listener:
            self._log("正在启动监听器...", "INFO")
            try:
                self.listener = WeChatStoreXHRListener(self.browser_page)
                self.listener.log_signal.connect(self._handle_log)
            except Exception as e:
                self._log(f"创建监听器失败：{e}", "ERROR")
                return

        if self.listener.started:
            self._log("监听器已在运行", "INFO")
            return

        try:
            self.listener.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self._log("监听器已启动", "SUCCESS")
        except Exception as e:
            self._log(f"启动监听器失败：{e}", "ERROR")
    
    def stop_monitoring(self):
        """停止监听"""
        if self.listener:
            try:
                self.listener.stop()
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self._log("监听器已停止", "INFO")
            except Exception as e:
                self._log(f"停止监听器失败：{e}", "ERROR")
    
    def _on_start_pressed(self):
        """开始监听按钮按下时的视觉效果"""
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
    
    def _on_start_released(self):
        """开始监听按钮释放时的视觉效果"""
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
    
    def _on_stop_pressed(self):
        """停止监听按钮按下时的视觉效果"""
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: white;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
    
    def _on_stop_released(self):
        """停止监听按钮释放时的视觉效果"""
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
    
    def _handle_log(self, message: str):
        print(f"[GUI-LOG] {message}", flush=True)
        timestamp = self._get_timestamp()
        self.log_viewer.append_text(f"[{timestamp}] {message}\n")
    
    def _open_log_dir(self):
        import subprocess, platform, os
        if not self.listener or not getattr(self.listener, "capture_dir", None):
            self._log("还没有记录目录，请先启动监听", "WARNING")
            return
        path = os.path.abspath(self.listener.capture_dir)
        if not os.path.exists(path):
            self._log(f"目录不存在：{path}", "WARNING")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            self._log(f"打开目录：{path}", "INFO")
        except Exception as e:
            self._log(f"打开目录失败：{e}", "ERROR")
    
    def _run_diagnose(self):
        page = self.browser_page.page()
        if not page:
            self._log("诊断失败：无法获取 page", "ERROR")
            return
        js = """
        JSON.stringify({
            hooked: !!window.__xhrHooked,
            queueLen: (window.__xhr_queue || []).length,
            hasFetch: typeof window.fetch === 'function',
            url: location.href
        })
        """
        page.runJavaScript(js, self._on_diagnose_result)
    
    def _on_diagnose_result(self, result):
        self._log(f"诊断结果：{result}", "INFO")
        print(f"[DIAG] {result}", flush=True)
    
    def clear_log(self):
        """清空日志"""
        self.log_viewer.clear_text()
        self._log("日志已清空", "INFO")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = XHRListenerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
