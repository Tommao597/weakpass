import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from app.core.fingerprint.fingerprint_engine import detect_http_fingerprint
from app.core.detector.ftp_detector import FTPAttacker


from app.core.detector.http_detector import (
    HTTPAttacker,
    JenkinsAttacker,
    TomcatAttacker,
    WordPressAttacker,
)
from app.core.detector.mysql_detector import MySQLAttacker
from app.core.detector.rdp_detector import RDPAttacker
from app.core.detector.redis_detector import RedisAttacker
from app.core.detector.smb_detector import SMBDetector
from app.core.detector.ssh_detector import SSHAttacker
from app.core.detector.telnet_detector import TelnetAttacker
from app.core.dict.dict_manager import DictManager
from app.core.database import task_dao, result_dao  # 导入数据库DAO
from app.models.schemas import DetectConfig
from app.utils.port_scan import scan_ports
from app.utils.ports import DEFAULT_PORTS

logger = logging.getLogger(__name__)


class DetectTaskManager:
    def __init__(self):
        self.tasks = {}
        self.dict_manager = DictManager()
        self.attacker_factories = {
            "ssh": SSHAttacker,
            "mysql": MySQLAttacker,
            "http": HTTPAttacker,
            "https": HTTPAttacker,
            "wordpress": WordPressAttacker,
            "tomcat": TomcatAttacker,
            "jenkins": JenkinsAttacker,
            "rdp": RDPAttacker,
            "ftp": FTPAttacker,
            "smb": SMBDetector,
            "telnet": TelnetAttacker,
            "redis": RedisAttacker,
        }
        
        # 从数据库加载历史任务
        self._load_history_tasks()
    
    def _load_history_tasks(self):
        """从数据库加载历史任务到内存"""
        try:
            db_tasks = task_dao.get_all_tasks()
            for db_task in db_tasks:
                # 只加载非完成状态的任务到内存
                if db_task.get('status') in ['running', 'pending', 'paused']:
                    task_id = db_task['id']
                    self.tasks[task_id] = {
                        "task_id": task_id,
                        "status": db_task['status'],
                        "pause_event": asyncio.Event(),
                        "progress": db_task.get('progress', 0),
                        "total": 0,
                        "percent": db_task.get('progress', 0),
                        "current_target": None,
                        "current_user": None,
                        "current_password": None,
                        "result": [],
                        "statistics": {},
                        "start_time": db_task.get('created_at'),
                        "completed_at": db_task.get('updated_at'),
                        "config": None,  # 无法从数据库恢复配置
                    }
                    # 设置暂停事件状态
                    if db_task['status'] == 'paused':
                        self.tasks[task_id]['pause_event'].clear()
                    else:
                        self.tasks[task_id]['pause_event'].set()
            logger.info(f"从数据库加载了 {len(self.tasks)} 个历史任务")
        except Exception as e:
            logger.error(f"加载历史任务失败: {e}")

    def _format_result(
        self,
        target,
        port,
        protocol,
        username,
        password,
        success,
        message="",
        info=None,
    ):
        return {
            "target": target,
            "port": port,
            "protocol": protocol,
            "username": username,
            "password": password,
            "success": success,
            "status": "weak" if success else "fail",
            "message": message,
            "info": info or {},
        }

    def _protocol_names(self, protocols: Iterable) -> List[str]:
        return [
            protocol.value if hasattr(protocol, "value") else str(protocol)
            for protocol in protocols
        ]

    def _build_attackers(self, timeout: int) -> Dict[str, object]:
        attackers = {}
        for protocol, factory in self.attacker_factories.items():
            attackers[protocol] = factory(timeout=timeout)
        return attackers

    def _build_protocol_ports(self, config: DetectConfig) -> Dict[str, List[int]]:
        protocol_ports: Dict[str, List[int]] = {}
        configured_ports = config.ports or {}

        for protocol_name in self._protocol_names(config.protocols):
            if protocol_name in configured_ports and configured_ports[protocol_name]:
                ports = configured_ports[protocol_name]
            else:
                ports = DEFAULT_PORTS.get(protocol_name, [])

            protocol_ports[protocol_name] = list(
                dict.fromkeys(int(port) for port in ports)
            )

        return protocol_ports

    def _build_port_list(self, protocol_ports: Dict[str, List[int]]) -> List[int]:
        return sorted(
            {
                port
                for ports in protocol_ports.values()
                for port in ports
            }
        )

    def _protocols_for_port(
        self,
        port: int,
        protocol_ports: Dict[str, List[int]],
    ) -> List[str]:
        return [
            protocol
            for protocol, ports in protocol_ports.items()
            if port in ports
        ]

    def _infer_web_transport(self, protocol: str, port: int) -> str:
        if protocol == "https" or port in {443, 8443}:
            return "https"
        return "http"

    def _update_progress(self, task_id: str, increment: int = 1):
        task = self.tasks.get(task_id)
        if not task:
            return

        task["progress"] += increment
        total = task["total"]
        task["percent"] = int((task["progress"] / total) * 100) if total else 0

    def _reduce_total(self, task_id: str, decrement: int):
        task = self.tasks.get(task_id)
        if not task or decrement <= 0:
            return

        task["total"] = max(task["progress"], task["total"] - decrement)
        total = task["total"]
        task["percent"] = int((task["progress"] / total) * 100) if total else 0

    def get(self, task_id: str):
        return self.tasks.get(task_id)

    def serialize_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task["task_id"],
            "status": task["status"],
            "progress": task["progress"],
            "total": task["total"],
            "percent": task["percent"],
            "current_target": task.get("current_target"),
            "current_user": task.get("current_user"),
            "current_password": task.get("current_password"),
            "result": task.get("result", []),
            "statistics": task.get("statistics", {}),
            "start_time": task.get("start_time"),
            "completed_at": task.get("completed_at"),
            "config": task["config"].model_dump(),
        }

    def list_serialized_tasks(self):
        return [self.serialize_task(task_id) for task_id in self.tasks]

    def add(self, task_id: str, config: DetectConfig):
        pause_event = asyncio.Event()
        pause_event.set()

        # 创建数据库任务记录
        task_data = {
            'id': task_id,
            'name': f"检测任务-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'target': ",".join(config.targets),
            'protocol': ",".join([p.value if hasattr(p, 'value') else str(p) for p in config.protocols]),
            'dict_id': config.dict_id,
            'status': 'pending',
            'progress': 0
        }
        task_dao.create_task(task_data)

        # 保留内存缓存用于实时状态更新
        self.tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "pause_event": pause_event,
            "progress": 0,
            "total": 0,
            "percent": 0,
            "current_target": None,
            "current_user": None,
            "current_password": None,
            "result": [],
            "statistics": {},
            "start_time": datetime.now().isoformat(),
            "completed_at": None,
            "config": config,
        }

    async def _detect_once(
        self,
        task_id: str,
        attacker,
        protocol: str,
        target: str,
        port: int,
        username: str,
        password: str,
    ) -> Tuple[Optional[Dict], bool]:
        task = self.tasks.get(task_id)
        if not task or task["status"] == "stopped":
            return None, False

        await task["pause_event"].wait()

        task = self.tasks.get(task_id)
        if not task or task["status"] == "stopped":
            return None, False

        task["current_target"] = target
        task["current_user"] = username
        task["current_password"] = password

        try:
            if protocol in {"http", "https"}:
                for auth_type in ["basic", "form", "digest"]:
                    try:
                        success, message, info = await attacker.attack(
                            host=target,
                            port=port,
                            username=username,
                            password=password,
                            protocol=protocol,
                            auth_type=auth_type,
                        )
                        if success:
                            return (
                                self._format_result(
                                    target,
                                    port,
                                    f"{protocol}({auth_type})",
                                    username,
                                    password,
                                    True,
                                    message,
                                    info,
                                ),
                                True,
                            )
                    except Exception as exc:
                        logger.warning(
                            "HTTP detection error %s:%s via %s: %s",
                            target,
                            port,
                            auth_type,
                            exc,
                        )

                return None, True

            if protocol in {"wordpress", "tomcat", "jenkins"}:
                success, message, info = await attacker.attack(
                    host=target,
                    port=port,
                    username=username,
                    password=password,
                    protocol=self._infer_web_transport(protocol, port),
                )
                if success:
                    return (
                        self._format_result(
                            target,
                            port,
                            protocol,
                            username,
                            password,
                            True,
                            message,
                            info,
                        ),
                        True,
                    )
                return None, True

            success, message = await attacker.attack(
                target,
                port,
                username,
                password,
            )

            if success:
                return (
                    self._format_result(
                        target,
                        port,
                        protocol,
                        username,
                        password,
                        True,
                        message,
                    ),
                    True,
                )

        except Exception as exc:
            logger.warning(
                "Detection error %s:%s %s:%s - %s",
                target,
                port,
                username,
                password,
                exc,
            )

        return None, True

    async def _detect_account(
        self,
        task_id: str,
        attacker,
        protocol: str,
        target: str,
        port: int,
        username: str,
        passwords: Sequence[str],
    ) -> Optional[Dict]:
        for index, password in enumerate(passwords):
            task = self.tasks.get(task_id)
            if not task or task["status"] == "stopped":
                self._reduce_total(task_id, len(passwords) - index)
                return None

            result, attempted = await self._detect_once(
                task_id,
                attacker,
                protocol,
                target,
                port,
                username,
                password,
            )

            if not attempted:
                self._reduce_total(task_id, len(passwords) - index)
                return None

            self._update_progress(task_id)

            if result:
                self._reduce_total(task_id, len(passwords) - index - 1)
                return result

        return None

    def _store_result(
        self,
        result: Optional[Dict],
        results: List[Dict],
        result_set: Set[Tuple[str, int, str, str]],
    ):
        if not result:
            return

        result_key = (
            result["target"],
            result["port"],
            result["username"],
            result["password"],
        )
        if result_key in result_set:
            return

        result_set.add(result_key)
        results.append(result)

    async def run_detection(self, task_id: str, config: DetectConfig):
        if task_id not in self.tasks:
            self.add(task_id, config)

        task = self.tasks[task_id]
        task["status"] = "running"
        task["result"] = []
        task["statistics"] = {}
        task["completed_at"] = None
        task["progress"] = 0
        task["total"] = 0
        task["percent"] = 0

        results: List[Dict] = []
        result_set: Set[Tuple[str, int, str, str]] = set()
        running_tasks: Set[asyncio.Task] = set()
        attackers = self._build_attackers(config.timeout)

        try:
            passwords = await self._get_passwords(config.dict_id)
            if not passwords:
                passwords = ["123456", "admin", "password"]

            protocol_ports = self._build_protocol_ports(config)
            ports = self._build_port_list(protocol_ports)
            if not ports:
                task["status"] = "completed"
                task["percent"] = 100
                task["completed_at"] = datetime.now().isoformat()
                return

            for target in config.targets:
                if task["status"] == "stopped":
                    break

                open_ports = await scan_ports(target, ports, timeout=config.timeout)
                if not open_ports:
                    continue

                for port in open_ports:
                    protocols = self._protocols_for_port(port, protocol_ports)
                    for protocol in protocols:
                        if protocol in ["http", "https"]:
                            fingerprint = await detect_http_fingerprint(
                                target,
                                port,
                                protocol
                            )

                            if fingerprint:
                                protocol = fingerprint
                        attacker = attackers.get(protocol)



                        if not attacker:
                            continue

                        for username in config.usernames:
                            if task["status"] == "stopped":
                                break

                            task["total"] += len(passwords)
                            running_tasks.add(
                                asyncio.create_task(
                                    self._detect_account(
                                        task_id=task_id,
                                        attacker=attacker,
                                        protocol=protocol,
                                        target=target,
                                        port=port,
                                        username=username,
                                        passwords=passwords,
                                    )
                                )
                            )

                            if len(running_tasks) >= config.thread_count:
                                done, pending = await asyncio.wait(
                                    running_tasks,
                                    return_when=asyncio.FIRST_COMPLETED,
                                )
                                running_tasks = set(pending)

                                for future in done:
                                    self._store_result(
                                        future.result(),
                                        results,
                                        result_set,
                                    )

            while running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                running_tasks = set(pending)

                for future in done:
                    self._store_result(
                        future.result(),
                        results,
                        result_set,
                    )

            if task["status"] != "stopped":
                task["status"] = "completed"
                task["percent"] = 100
                # 更新数据库任务状态
                task_dao.update_task_status(task_id, "completed", 100)

            task["result"] = results
            task["statistics"] = self._generate_statistics(results)
            task["completed_at"] = datetime.now().isoformat()
            
            # 保存所有结果到数据库
            for result in results:
                if result.get('success'):
                    # 计算风险等级
                    risk_level = 'low'
                    username = result.get('username', '').lower()
                    password = result.get('password', '')
                    
                    if 'admin' in username or 'root' in username:
                        risk_level = 'high'
                    elif len(password) < 8:
                        risk_level = 'medium'
                    
                    result['risk_level'] = risk_level
                    result_dao.save_result(task_id, result)

        except Exception as exc:
            for future in running_tasks:
                future.cancel()

            task["status"] = "failed"
            task["result"] = [{"error": str(exc)}]
            task["completed_at"] = datetime.now().isoformat()
            # 更新数据库任务状态
            task_dao.update_task_status(task_id, "failed")
            logger.exception("Task %s failed: %s", task_id, exc)

    def _generate_statistics(self, results):
        stats = {
            "total": len(results),
            "by_protocol": {},
            "by_target": {},
            "risk_level": {
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        }

        for result in results:
            if "error" in result:
                continue

            protocol = result["protocol"]
            target = result["target"]

            stats["by_protocol"][protocol] = (
                stats["by_protocol"].get(protocol, 0) + 1
            )
            stats["by_target"][target] = stats["by_target"].get(target, 0) + 1

            username = result["username"].lower()
            if "admin" in username or "root" in username:
                stats["risk_level"]["high"] += 1
            elif len(result["password"]) < 8:
                stats["risk_level"]["medium"] += 1
            else:
                stats["risk_level"]["low"] += 1

        return stats

    async def _get_passwords(self, dict_id: str):
        if dict_id:
            passwords = self.dict_manager.get_passwords(dict_id)
            if passwords:
                return passwords

        return [
            "123456",
            "admin",
            "password",
            "root",
            "12345678",
        ]

    def pause_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["status"] = "paused"
        task["pause_event"].clear()
        return True

    def resume_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["status"] = "running"
        task["pause_event"].set()
        return True

    def stop_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["status"] = "stopped"
        task["pause_event"].set()
        return True


tasks = DetectTaskManager()


async def create_detect_task(config: DetectConfig):
    task_id = str(uuid.uuid4())
    tasks.add(task_id, config)
    return task_id


def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return {"status": "not_found"}

    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "percent": task["percent"],
        "completed_at": task["completed_at"],
    }


async def execute_detection(task_id: str, config: DetectConfig):
    try:
        await tasks.run_detection(task_id, config)
    except Exception as exc:
        if task_id in tasks.tasks:
            tasks.tasks[task_id]["status"] = "failed"
            tasks.tasks[task_id]["completed_at"] = datetime.now().isoformat()
        logger.exception("Task %s failed: %s", task_id, exc)