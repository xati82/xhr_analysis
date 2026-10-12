#!/usr/bin/env python3
"""
测试脚本：验证 XHR 监听器功能
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from xhr_analysis.monitor.listener import WeChatStoreXHRListener


def test_listener_creation():
    """测试监听器创建"""
    print("=" * 60)
    print("XHR 监听器功能测试")
    print("=" * 60)
    
    print("\n[测试 1] 创建监听器实例")
    print("  注意：WeChatStoreXHRListener 现在需要传入 QWebEngineView 实例")
    print("  创建 Mock 对象用于测试")
    # 创建 Mock 对象用于测试
    class MockWebView:
        pass
    
    mock_view = MockWebView()
    listener = WeChatStoreXHRListener(mock_view)
    print(f"✓ 监听器创建成功")
    print(f"  - 目标 URL: {listener.TARGET_URL}")
    
    print("\n[测试 2] 检查方法")
    methods = ['start', 'stop', 'get_request_count', 'get_requests', 'log']
    for method in methods:
        assert hasattr(listener, method), f"缺少方法：{method}"
    print(f"✓ 所有必需方法存在")
    
    print("\n[测试 3] 检查请求过滤")
    # 测试忽略模式
    assert listener.is_ignored_request("https://example.com/app.js") == True
    assert listener.is_ignored_request("https://example.com/app.png") == True
    assert listener.is_ignored_request("https://example.com/favicon.ico") == True
    assert listener.is_ignored_request("https://example.com/api/data") == False
    print("✓ 请求过滤逻辑正常")
    
    print("\n[测试 4] 检查日志信号")
    from PyQt6.QtCore import QObject
    assert isinstance(listener, QObject)
    assert listener.log_signal is not None
    print("✓ 日志信号正常")
    
    print("\n" + "=" * 60)
    print("创建测试通过！")
    print("=" * 60)
    
    return True


def main():
    """主函数"""
    try:
        test_listener_creation()
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
