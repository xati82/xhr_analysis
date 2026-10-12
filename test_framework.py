#!/usr/bin/env python3
"""
测试脚本：验证 XHR 监听器框架
"""
import sys
import os

# 添加 src 目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(script_dir), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from xhr_analysis.monitor.listener import XHRListener, WeChatStoreXHRListener, BrowserPageManager


def test_framework():
    """测试框架"""
    print("=" * 60)
    print("XHR 监听器框架测试")
    print("=" * 60)
    
    # 测试 1：创建监听器实例
    print("\n[测试 1] 创建监听器实例")
    listener = WeChatStoreXHRListener(output_dir="data")
    print(f"✓ 监听器创建成功")
    print(f"  - 目标 URL: {listener.TARGET_URL}")
    print(f"  - 输出目录：data")
    
    # 测试 2：检查基类方法
    print("\n[测试 2] 检查基类方法")
    methods = ['start', 'stop', 'on_request', 'on_response', 'get_requests', 'save_requests']
    for method in methods:
        assert hasattr(listener, method), f"缺少方法：{method}"
    print(f"✓ 所有必需方法存在")
    
    # 测试 3：检查子类特有属性
    print("\n[测试 3] 检查子类属性")
    assert hasattr(listener, 'TARGET_URL'), "缺少 TARGET_URL 属性"
    assert listener.TARGET_URL == "https://store.weixin.qq.com/shop/kf", "TARGET_URL 不正确"
    print(f"✓ TARGET_URL: {listener.TARGET_URL}")
    
    # 测试 4：检查 BrowserPageManager
    print("\n[测试 4] 检查 BrowserPageManager")
    manager = BrowserPageManager()
    assert hasattr(manager, 'launch'), "BrowserPageManager 缺少 launch 方法"
    assert hasattr(manager, 'navigate'), "BrowserPageManager 缺少 navigate 方法"
    assert hasattr(manager, 'close'), "BrowserPageManager 缺少 close 方法"
    print(f"✓ BrowserPageManager 初始化成功")
    
    # 测试 5：获取请求数量
    print("\n[测试 5] 获取请求数量")
    count = listener.get_request_count()
    assert count == 0, "初始请求数量应该为 0"
    print(f"✓ 初始请求数量：{count}")
    
    print("\n" + "=" * 60)
    print("框架测试通过！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_framework()
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)