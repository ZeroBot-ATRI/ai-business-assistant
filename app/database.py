# app/database.py - 数据库管理
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class Database:
    """数据库管理类"""

    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._connection = None  # 用于内存数据库
        if db_path == ":memory:":
            # 内存数据库需要保持连接
            self._connection = sqlite3.connect(db_path)
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        if self._connection:
            return self._connection
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # AI决策记录表（增强版）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                user_input TEXT NOT NULL,
                intent TEXT,
                action TEXT,
                result TEXT,
                success INTEGER DEFAULT 1,
                execution_time_ms REAL,
                llm_cost REAL,
                timestamp TEXT NOT NULL
            )
        ''')

        # 系统指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

        # 会话历史表（为Day 36-40准备）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

        # 创建索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_decisions_timestamp
            ON ai_decisions(timestamp)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_decisions_user
            ON ai_decisions(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metrics_name
            ON system_metrics(metric_name, timestamp)
        ''')

        conn.commit()
        conn.close()

        # 不使用emoji避免Windows编码问题

    def save_decision(
        self,
        user_input: str,
        intent: str,
        action: str,
        result: Any,
        user_id: str = "default",
        success: bool = True,
        execution_time_ms: Optional[float] = None,
        llm_cost: Optional[float] = None
    ) -> int:
        """保存AI决策记录"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 将result转换为JSON字符串
        result_json = json.dumps(result, ensure_ascii=False)

        cursor.execute('''
            INSERT INTO ai_decisions
            (user_id, user_input, intent, action, result, success, execution_time_ms, llm_cost, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            user_input,
            intent,
            action,
            result_json,
            1 if success else 0,
            execution_time_ms,
            llm_cost,
            datetime.now().isoformat()
        ))

        decision_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return decision_id

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的决策记录"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, user_id, user_input, intent, action, result, success, timestamp
            FROM ai_decisions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "user_id": row[1],
                "user_input": row[2],
                "intent": row[3],
                "action": row[4],
                "result": row[5],
                "success": bool(row[6]),
                "timestamp": row[7]
            })

        return results

    def get_today_stats(self) -> Dict[str, Any]:
        """获取今日统计数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 今日总数
        cursor.execute('''
            SELECT COUNT(*) FROM ai_decisions
            WHERE date(timestamp) = date('now')
        ''')
        today_total = cursor.fetchone()[0]

        # 今日成功数
        cursor.execute('''
            SELECT COUNT(*) FROM ai_decisions
            WHERE date(timestamp) = date('now') AND success = 1
        ''')
        today_success = cursor.fetchone()[0]

        # 总成功率
        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(success) as success_count
            FROM ai_decisions
        ''')
        row = cursor.fetchone()
        total_count = row[0]
        success_count = row[1] or 0
        success_rate = (success_count / total_count) if total_count > 0 else 0

        # 今日平均执行时间
        cursor.execute('''
            SELECT AVG(execution_time_ms)
            FROM ai_decisions
            WHERE date(timestamp) = date('now')
            AND execution_time_ms IS NOT NULL
        ''')
        avg_time = cursor.fetchone()[0] or 0

        # 今日总成本
        cursor.execute('''
            SELECT SUM(llm_cost)
            FROM ai_decisions
            WHERE date(timestamp) = date('now')
            AND llm_cost IS NOT NULL
        ''')
        today_cost = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "today_total": today_total,
            "today_success": today_success,
            "success_rate": success_rate,
            "avg_execution_time_ms": avg_time,
            "today_cost": today_cost
        }

    def get_intent_distribution(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取意图分布"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT intent, COUNT(*) as count
            FROM ai_decisions
            WHERE date(timestamp) >= date('now', ?)
            GROUP BY intent
            ORDER BY count DESC
        ''', (f'-{days} days',))

        rows = cursor.fetchall()
        conn.close()

        return [{"intent": row[0], "count": row[1]} for row in rows]

    def save_metric(self, metric_name: str, metric_value: float):
        """保存系统指标"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO system_metrics (metric_name, metric_value, timestamp)
            VALUES (?, ?, ?)
        ''', (metric_name, metric_value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def cleanup_old_data(self, days: int = 90):
        """清理旧数据（保留最近90天）"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM ai_decisions
            WHERE date(timestamp) < date('now', ?)
        ''', (f'-{days} days',))

        cursor.execute('''
            DELETE FROM system_metrics
            WHERE date(timestamp) < date('now', ?)
        ''', (f'-{days} days',))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted
