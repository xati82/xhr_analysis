#!/usr/bin/env python3
"""
数据库配置模块
配置 SQLite 数据库连接和表结构
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional


class XHRDatabaseConfig:
    """XHR 数据库配置"""
    
    # 数据库文件路径
    DATA_DIR = "data"
    DB_FILE = os.path.join(DATA_DIR, "xhr.db")
    BACKUP_DIR = os.path.join(DATA_DIR, "xhr_backup")
    
    # 表名
    TABLE_REQUESTS = "xhr_requests"
    TABLE_API_INFO = "api_info"
    TABLE_API_STATS = "api_stats"
    
    # 请求类型分类
    REQUEST_TYPES = ["login", "message", "status", "business"]
    
    # 初始化数据库
    @staticmethod
    def init_database():
        """初始化数据库和表结构"""
        os.makedirs(XHRDatabaseConfig.DATA_DIR, exist_ok=True)
        os.makedirs(XHRDatabaseConfig.BACKUP_DIR, exist_ok=True)
        
        conn = sqlite3.connect(XHRDatabaseConfig.DB_FILE)
        cursor = conn.cursor()
        
        # 创建请求记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xhr_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                page_name TEXT,
                tab_index INTEGER,
                request_time REAL,
                
                -- 请求信息
                method TEXT,
                url TEXT NOT NULL,
                headers TEXT,
                body TEXT,
                
                -- 响应信息
                status_code INTEGER,
                response_time REAL,
                response_headers TEXT,
                response_body TEXT,
                
                -- 分类标记
                request_type TEXT,
                api_category TEXT,
                api_endpoint TEXT,
                
                -- 备注
                notes TEXT
            )
        """)
        
        # 创建 API 信息汇总表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT UNIQUE,
                method TEXT,
                category TEXT,
                description TEXT,
                required_fields TEXT,
                optional_fields TEXT,
                example_request TEXT,
                example_response TEXT,
                created_at DATETIME
            )
        """)
        
        # 创建 API 调用统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                method TEXT,
                call_count INTEGER,
                total_time REAL,
                avg_time REAL,
                success_count INTEGER,
                failed_count INTEGER,
                first_seen DATETIME,
                last_seen DATETIME
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✓ 数据库初始化成功：{XHRDatabaseConfig.DB_FILE}")
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        return sqlite3.connect(XHRDatabaseConfig.DB_FILE)


def main():
    """初始化数据库"""
    XHRDatabaseConfig.init_database()
    print("数据库配置完成！")
    print(f"数据库文件：{XHRDatabaseConfig.DB_FILE}")
    print(f"备份目录：{XHRDatabaseConfig.BACKUP_DIR}")
    
    return XHRDatabaseConfig


if __name__ == "__main__":
    main()