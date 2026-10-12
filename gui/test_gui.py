#!/usr/bin/env python3
"""
测试 GUI 界面
"""
import sys
import os

# 添加 src 目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from xhr_analysis.gui.browser_viewer import XHRListenerGUI, BrowserPageViewer, XHRLogViewer


def test_gui():
    """测试 GUI"""
    print("=" * 60)
    print("XHR 监听器 GUI 测试")
    print("=" * 60)
    
    # 测试 1：创建 GUI 窗口
    print("\n[测试 1] 创建 GUI 窗口")
    app = QApplication(sys.argv)
    window = XHRListenerGUI()
    print(f"✓ GUI 窗口创建成功")
    print(f"  - 窗口标题：{window.windowTitle()}")
    print(f"  - 窗口大小：{window.size().width()}x{window.size().height()}")
    
    # 测试 2：测试日志输出
    print("\n[测试 2] 测试日志输出")
    window.add_log_entry("测试日志 1", "INFO")
    window.add_log_entry("测试日志 2", "WARN")
    print(f"✓ 日志输出成功")
    
    # 测试 3：测试日志面板切换
    print("\n[测试 3] 测试日志面板切换")
    window._toggle_log_panel()
    print(f"✓ 日志面板切换成功")
    
    # 测试 4：测试页面刷新
    print("\n[测试 4] 测试页面刷新")
    window.refresh_page()
    print(f"✓ 页面刷新成功")
    
    print("\n" + "=" * 60)
    print("GUI 测试完成！")
    print("窗口已打开，请手动测试各项功能")
    print("=" * 60)
    
    return window


if __name__ == "__main__":
    try:
        window = test_gui()
        sys.exit(app.exec())
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)