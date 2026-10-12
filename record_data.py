#!/usr/bin/env python3
"""
XHR 数据记录模块
采用混合存储：数据库 + JSON + JSONL
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys

# 添加 src 目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # 作为包的一部分导入时（from xhr_analysis.record_data import XHRRecorder）
    from .config.database_config import XHRDatabaseConfig
except ImportError:
    # 直接运行本脚本时（python record_data.py）
    from config.database_config import XHRDatabaseConfig


class XHRRecorder:
    """XHR 数据记录器（混合存储）"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or XHRDatabaseConfig.DATA_DIR
        self.db_path = XHRDatabaseConfig.DB_FILE
        self.json_path = os.path.join(self.output_dir, "xhr_logs.json")
        self.jsonl_path = os.path.join(self.output_dir, "xhr_timeline.jsonl")
        self._request_index = 0
        self._jsonl_buffer = []
        
        # 初始化数据库
        XHRDatabaseConfig.init_database()
    
    def record_request(self, request_data: Dict[str, Any]) -> int:
        """
        记录 XHR 请求（三格式存储）
        
        Args:
            request_data: 包含 request、response、classification 等信息的字典
            
        Returns:
            request_id: 请求 ID
        """
        request_id = self._request_index
        self._request_index += 1
        
        # 1. 写入数据库
        self._write_to_db(request_data)
        
        # 2. 追加到 JSONL 文件
        self._append_to_jsonl(request_data)
        
        # 3. 更新 JSON 文件
        self._update_json(request_data)
        
        return request_id
    
    def _write_to_db(self, request_data: Dict[str, Any]) -> None:
        """写入数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 构建数据库记录
            record = {
                "timestamp": request_data.get("timestamp", datetime.now().isoformat()),
                "page_name": request_data.get("page_name"),
                "tab_index": request_data.get("tab_index", 0),
                "request_time": request_data.get("request_time"),
                "method": request_data.get("request", {}).get("method"),
                "url": request_data.get("request", {}).get("url"),
                "headers": request_data.get("request", {}).get("headers"),
                "body": request_data.get("request", {}).get("body"),
                "status_code": request_data.get("response", {}).get("status_code"),
                "response_time": request_data.get("response", {}).get("response_time_ms"),
                "response_headers": request_data.get("response", {}).get("headers"),
                "response_body": request_data.get("response", {}).get("body"),
                "request_type": request_data.get("classification", {}).get("type"),
                "api_category": request_data.get("classification", {}).get("category"),
                "api_endpoint": request_data.get("classification", {}).get("endpoint"),
                "notes": request_data.get("notes"),
            }
            
            cursor.execute("""
                INSERT INTO xhr_requests 
                (timestamp, page_name, tab_index, request_time, method, url, headers, body,
                 status_code, response_time, response_headers, response_body,
                 request_type, api_category, api_endpoint, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["timestamp"],
                record["page_name"],
                record["tab_index"],
                record["request_time"],
                record["method"],
                record["url"],
                json.dumps(record["headers"], ensure_ascii=False) if record["headers"] else None,
                json.dumps(record["body"], ensure_ascii=False) if record["body"] else None,
                record["status_code"],
                record["response_time"],
                json.dumps(record["response_headers"], ensure_ascii=False) if record["response_headers"] else None,
                json.dumps(record["response_body"], ensure_ascii=False) if record["response_body"] else None,
                record["request_type"],
                record["api_category"],
                record["api_endpoint"],
                record["notes"]
            ))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ 数据库写入失败：{e}")
        finally:
            conn.close()
    
    def _append_to_jsonl(self, request_data: Dict[str, Any]) -> None:
        """追加到 JSONL 文件"""
        with open(self.jsonl_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(request_data, ensure_ascii=False) + '\n')
    
    def _update_json(self, request_data: Dict[str, Any]) -> None:
        """更新 JSON 文件"""
        if not os.path.exists(self.json_path):
            # 文件不存在，创建新文件
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # 读取现有数据
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 追加新数据
        data.append(request_data)
        
        # 写入回文件
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_request_count(self) -> int:
        """获取请求数量"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return len(json.load(f))
        except:
            return 0
    
    def get_requests_by_type(self, request_type: str) -> List[Dict[str, Any]]:
        """按类型获取请求"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                all_requests = json.load(f)
                return [r for r in all_requests if r.get("classification", {}).get("type") == request_type]
        except:
            return []
    
    def save_jsonl_backup(self, backup_path: str) -> None:
        """保存 JSONL 备份"""
        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """测试记录器"""
    recorder = XHRRecorder()
    
    # 测试数据
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "page_name": "客服主页",
        "tab_index": 0,
        "request_time": datetime.now().timestamp(),
        "request": {
            "method": "POST",
            "url": "https://store.weixin.qq.com/shop/kf/api/test",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data"}
        },
        "response": {
            "status_code": 200,
            "response_time_ms": 100,
            "headers": {"Content-Type": "application/json"},
            "body": {"success": True}
        },
        "classification": {
            "type": "test",
            "category": "test",
            "endpoint": "/api/test"
        },
        "notes": "测试记录"
    }
    
    request_id = recorder.record_request(test_data)
    print(f"✓ 请求记录成功，ID: {request_id}")
    print(f"✓ 数据库文件：{recorder.db_path}")
    print(f"✓ JSON 文件：{recorder.json_path}")
    print(f"✓ JSONL 文件：{recorder.jsonl_path}")
    print(f"✓ 当前请求数量：{recorder.get_request_count()}")
    
    return recorder


if __name__ == "__main__":
    main()