import sqlite3
from contextlib import contextmanager
import os
from pathlib import Path

class Database:
    def __init__(self, db_path="db/weakpass.db"):
        """初始化数据库"""
        # 确保数据库文件夹存在
        db_dir = Path("db")
        if not db_dir.exists():
            db_dir.mkdir()
            print(f"✅ 创建数据库文件夹: {db_dir.absolute()}")
            
        self.db_path = db_path
        self._init_db()
        print(f"✅ 数据库文件位置: {Path(db_path).absolute()}")
    
    def _init_db(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建任务表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                protocol TEXT,
                dict_id INTEGER,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建字典表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                size INTEGER NOT NULL,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                target TEXT NOT NULL,
                port INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                risk_level TEXT DEFAULT 'low',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
            ''')
            
            # 创建报告表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                path TEXT NOT NULL,
                format TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
            ''')
            
            # 创建资产扫描表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                status TEXT NOT NULL,
                total_assets INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建资产表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                target TEXT NOT NULL,
                port INTEGER NOT NULL,
                service TEXT NOT NULL,
                fingerprint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES asset_scans (id)
            )
            ''')
            
            conn.commit()
            print(f"✅ 数据库表结构初始化完成")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        # 设置row_factory为字典工厂，这样返回的就是字典而不是Row对象
        conn.row_factory = self._dict_factory
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()):
        """执行SQL语句"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ 数据库执行错误: {e}")
            return False
    
    def fetch_all(self, query: str, params: tuple = ()):
        """获取所有查询结果"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ 数据库查询错误: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = ()): 
        """获取单个查询结果"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"❌ 数据库查询错误: {e}")
            return None

    def execute_with_return_id(self, query: str, params: tuple = ()): 
        """执行SQL语句并返回最后插入的ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"❌ 数据库执行错误: {e}")
            return None
    
    def _dict_factory(self, cursor, row):
        """将查询结果转换为字典"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


class TaskDAO:
    """任务数据访问对象"""
    
    def __init__(self, db):
        self.db = db
    
    def create_task(self, task_data: dict) -> str:
        """创建新任务"""
        query = """
        INSERT INTO tasks (id, name, target, protocol, dict_id, status, progress)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            task_data.get('id'),
            task_data.get('name', '未命名任务'),
            task_data.get('target', ''),
            task_data.get('protocol', ''),
            task_data.get('dict_id'),
            task_data.get('status', 'pending'),
            task_data.get('progress', 0)
        )
        self.db.execute_with_return_id(query, params)
        return task_data.get('id')
    
    def get_task_by_id(self, task_id: str):
        """根据ID获取任务"""
        query = "SELECT * FROM tasks WHERE id = ?"
        return self.db.fetch_one(query, (task_id,))
    
    def get_all_tasks(self):
        """获取所有任务"""
        query = "SELECT * FROM tasks ORDER BY created_at DESC"
        return self.db.fetch_all(query)
    
    def update_task_status(self, task_id: str, status: str, progress: int = None):
        """更新任务状态"""
        if progress is not None:
            query = "UPDATE tasks SET status = ?, progress = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            params = (status, progress, task_id)
        else:
            query = "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            params = (status, task_id)
        return self.db.execute(query, params)
    
    def delete_task(self, task_id: str):
        """删除任务"""
        query = "DELETE FROM tasks WHERE id = ?"
        return self.db.execute(query, (task_id,))


class ResultDAO:
    """结果数据访问对象"""
    
    def __init__(self, db):
        self.db = db
    
    def save_result(self, task_id: str, result: dict):
        """保存检测结果"""
        query = """
        INSERT INTO results (task_id, target, port, protocol, username, password, success, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            task_id,
            result.get('target', ''),
            result.get('port', 0),
            result.get('protocol', ''),
            result.get('username', ''),
            result.get('password', ''),
            result.get('success', False),
            result.get('risk_level', 'low')
        )
        return self.db.execute_with_return_id(query, params)
    
    def get_results_by_task(self, task_id: str):
        """根据任务ID获取结果"""
        query = "SELECT * FROM results WHERE task_id = ? ORDER BY created_at DESC"
        return self.db.fetch_all(query, (task_id,))
    
    def get_successful_results(self, task_id: str):
        """获取成功的检测结果"""
        query = "SELECT * FROM results WHERE task_id = ? AND success = 1 ORDER BY created_at DESC"
        return self.db.fetch_all(query, (task_id,))
    
    def delete_results_by_task(self, task_id: str):
        """删除指定任务的结果"""
        query = "DELETE FROM results WHERE task_id = ?"
        return self.db.execute(query, (task_id,))


class DictionaryDAO:
    """字典数据访问对象"""
    
    def __init__(self, db):
        self.db = db
    
    def create_dict(self, dict_data: dict):
        """创建字典记录"""
        query = """
        INSERT INTO dictionaries (name, type, size, path)
        VALUES (?, ?, ?, ?)
        """
        params = (
            dict_data.get('name'),
            dict_data.get('type', 'custom'),
            dict_data.get('size', 0),
            dict_data.get('path', '')
        )
        return self.db.execute_with_return_id(query, params)
    
    def get_dict_by_id(self, dict_id: int):
        """根据ID获取字典"""
        query = "SELECT * FROM dictionaries WHERE id = ?"
        return self.db.fetch_one(query, (dict_id,))
    
    def get_all_dicts(self):
        """获取所有字典"""
        query = "SELECT * FROM dictionaries ORDER BY created_at DESC"
        return self.db.fetch_all(query)
    
    def update_dict(self, dict_id: int, dict_data: dict):
        """更新字典信息"""
        query = "UPDATE dictionaries SET name = ?, type = ?, size = ?, path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params = (
            dict_data.get('name'),
            dict_data.get('type'),
            dict_data.get('size'),
            dict_data.get('path'),
            dict_id
        )
        return self.db.execute(query, params)
    
    def delete_dict(self, dict_id: int):
        """删除字典"""
        query = "DELETE FROM dictionaries WHERE id = ?"
        return self.db.execute(query, (dict_id,))


class ReportDAO:
    """报告数据访问对象"""
    
    def __init__(self, db):
        self.db = db
    
    def create_report(self, report_data: dict):
        """创建报告记录"""
        query = """
        INSERT INTO reports (task_id, path, format)
        VALUES (?, ?, ?)
        """
        params = (
            report_data.get('task_id'),
            report_data.get('path', ''),
            report_data.get('format', 'pdf')
        )
        return self.db.execute_with_return_id(query, params)
    
    def get_report_by_id(self, report_id: int):
        """根据ID获取报告"""
        query = "SELECT * FROM reports WHERE id = ?"
        return self.db.fetch_one(query, (report_id,))
    
    def get_reports_by_task(self, task_id: str):
        """根据任务ID获取报告"""
        query = "SELECT * FROM reports WHERE task_id = ? ORDER BY created_at DESC"
        return self.db.fetch_all(query, (task_id,))
    
    def delete_report(self, report_id: int):
        """删除报告"""
        query = "DELETE FROM reports WHERE id = ?"
        return self.db.execute(query, (report_id,))


class AssetDAO:
    """资产数据访问对象"""
    
    def __init__(self, db):
        self.db = db
    
    def create_asset_scan(self, scan_data: dict):
        """创建资产扫描记录"""
        # 首先创建扫描记录
        scan_query = """
        INSERT INTO asset_scans (target, status, total_assets)
        VALUES (?, ?, ?)
        """
        scan_params = (
            scan_data.get('target', ''),
            scan_data.get('status', 'completed'),
            scan_data.get('total_assets', 0)
        )
        scan_id = self.db.execute_with_return_id(scan_query, scan_params)
        
        # 然后为每个资产创建记录
        assets = scan_data.get('assets', [])
        for asset in assets:
            asset_query = """
            INSERT INTO assets (scan_id, target, port, service, fingerprint, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """
            asset_params = (
                scan_id,
                asset.get('target', ''),
                asset.get('port', 0),
                asset.get('service', ''),
                asset.get('fingerprint', '')
            )
            self.db.execute_with_return_id(asset_query, asset_params)
        
        return scan_id
    
    def get_asset_scans(self):
        """获取所有资产扫描记录"""
        query = """
        SELECT s.id, s.target, s.status, s.total_assets, s.created_at as scan_time,
               COUNT(a.id) as asset_count
        FROM asset_scans s
        LEFT JOIN assets a ON s.id = a.scan_id
        GROUP BY s.id, s.target, s.status, s.total_assets, s.created_at
        ORDER BY s.created_at DESC
        """
        return self.db.fetch_all(query)
    
    def get_assets_by_scan(self, scan_id: int):
        """根据扫描ID获取资产"""
        query = "SELECT * FROM assets WHERE scan_id = ? ORDER BY port ASC"
        return self.db.fetch_all(query, (scan_id,))
    
    def get_latest_assets(self, target: str):
        """获取指定目标的最新资产扫描"""
        query = """
        SELECT s.id, s.target, s.status, s.total_assets, s.created_at as scan_time,
               COUNT(a.id) as asset_count
        FROM asset_scans s
        LEFT JOIN assets a ON s.id = a.scan_id
        WHERE s.target = ?
        GROUP BY s.id, s.target, s.status, s.total_assets, s.created_at
        ORDER BY s.created_at DESC
        LIMIT 1
        """
        return self.db.fetch_one(query, (target,))


# 创建全局数据库实例和DAO实例
db = Database("db/weakpass.db")
task_dao = TaskDAO(db)
result_dao = ResultDAO(db)
dict_dao = DictionaryDAO(db)
report_dao = ReportDAO(db)
asset_dao = AssetDAO(db)