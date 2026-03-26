import asyncio
import uuid
from datetime import datetime

from app.core.detector.http_detector import (
    HTTPAttacker,
    WordPressAttacker,
    TomcatAttacker,
    JenkinsAttacker
)

from app.core.detector.ssh_detector import SSHAttacker
from app.core.detector.mysql_detector import MySQLAttacker
from app.core.detector.rdp_detector import RDPAttacker
from app.core.detector.ftp_detector import FTPAttacker
from app.core.detector.smb_detector import SMBDetector
from app.core.detector.telnet_detector import TelnetAttacker
from app.core.detector.redis_detector import RedisAttacker

from app.utils.port_scan import scan_ports
from app.utils.ports import DEFAULT_PORTS

from app.models.schemas import DetectConfig


class DetectTaskManager:

    def __init__(self):

        self.tasks = {}

        # 并发控制
        self.semaphore = asyncio.Semaphore(200)

        # 成功账号缓存 (host,port,username)
        self.success_accounts = set()
        # 结果去重
        self.result_set = set()

        # 协议攻击器
        self.attackers = {
            "ssh": SSHAttacker(),
            "mysql": MySQLAttacker(),
            "http": HTTPAttacker(),
            "https": HTTPAttacker(),
            "wordpress": WordPressAttacker(),
            "tomcat": TomcatAttacker(),
            "jenkins": JenkinsAttacker(),
            "rdp": RDPAttacker(),
            "ftp": FTPAttacker(),
            "smb": SMBDetector(),
            "telnet": TelnetAttacker(),
            "redis": RedisAttacker()
        }

        # 端口 → 协议映射
        self.port_protocol_map = {
            22: "ssh",
            21: "ftp",
            23: "telnet",
            445: "smb",
            3306: "mysql",
            6379: "redis",
            3389: "rdp",
            80: "http",
            443: "https",
            8080: "tomcat",
            
        }
        def _format_result(
            self,
            target,
            port,
            protocol,
            username,
            password,
            success,
            message="",
            info=None
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
                 "info": info or {}
       }

    def get(self, task_id: str):
        return self.tasks.get(task_id)

    def add(self, task_id: str, config: DetectConfig):

        pause_event = asyncio.Event()
        pause_event.set()  # 默认运行

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

            "config": config
        }

    async def _detect_once(
    self,
    task_id,
    attacker,
    protocol,
    target,
    port,
    username,
    password
):

     async with self.semaphore:
         # ⭐新增：任务状态检查
        task = self.tasks.get(task_id)
        if not task:
            return None

        # 如果任务停止
        if task["status"] == "stopped":
            return None

        # 如果暂停就等待
        await task["pause_event"].wait()

        try:

            # HTTP / HTTPS
            if protocol in ["http", "https"]:

                for auth_type in ["basic", "form", "digest"]:

                    try:

                        success, message, info = await attacker.attack(
                            host=target,
                            port=port,
                            username=username,
                            password=password,
                            protocol=protocol,
                            auth_type=auth_type
                        )

                        if success:
                            return self._format_result(
                                target,
                                port,
                                f"{protocol}({auth_type})",
                                username,
                                password,
                                True,
                                message,
                                info
                            )

                    except Exception as e:
                        print(f"HTTP检测错误 {target}:{port} {e}")

                # HTTP三种认证都失败
                return None

            # 其他协议
            else:

                success, message = await attacker.attack(
                    target,
                    port,
                    username,
                    password
                )

                if success:
                    return self._format_result(
                        target,
                        port,
                        protocol,
                        username,
                        password,
                        True,
                        message
                    )

        except Exception as e:

            print(
                f"检测错误: {target}:{port} "
                f"{username}:{password} - {str(e)}"
            )

        return None

    async def run_detection(self, task_id: str, config: DetectConfig):

        if task_id not in self.tasks:
            self.add(task_id, config)

        self.tasks[task_id]["status"] = "running"

        results = []

        try:

            passwords = await self._get_passwords(config.dict_id)

            if not passwords:
                passwords = ["123456", "admin", "password"]

            tasks_list = []

            for target in config.targets:

                # 1 扫描端口
                ports = list(DEFAULT_PORTS.values())

                open_ports = await scan_ports(target, ports)

                if not open_ports:
                    continue

                # 2 根据端口识别协议
                for port in open_ports:

                    protocol = self.port_protocol_map.get(port)

                    if not protocol:
                        continue

                    if protocol not in config.protocols:
                        continue

                    attacker = self.attackers.get(protocol)

                    if not attacker:
                        continue

                    for username in config.usernames:

                        if self.tasks[task_id]["status"] == "stopped":
                            break

                        key = (target, port, username)

                        # 如果这个账号已经成功就跳过
                        if key in self.success_accounts:
                            continue    

                        for password in passwords:
                            if self.tasks[task_id]["status"] == "stopped":
                                break

                            self.tasks[task_id]["current_target"] = target
                            self.tasks[task_id]["current_user"] = username
                            self.tasks[task_id]["current_password"] = password

                            task = asyncio.create_task(

                                self._detect_once(
                                    task_id,
                                    attacker,
                                    protocol,
                                    target,
                                    port,
                                    username,
                                    password
                                )

                            )

                            tasks_list.append(task)

            total = len(tasks_list)

            self.tasks[task_id]["total"] = total

            completed = 0

            for future in asyncio.as_completed(tasks_list):

                result = await future

                completed += 1

                self.tasks[task_id]["progress"] = completed

                percent = int((completed / total) * 100) if total else 0

                self.tasks[task_id]["percent"] = percent

                if result:

                    key = (
                        result["target"],
                        result["port"],
                        result["username"],
                        result["password"]
                    )

                    # 如果已经存在就跳过
                    if key in self.result_set:
                        continue

                    self.result_set.add(key)

                    results.append(result)

                    # 成功账号记录
                    self.success_accounts.add(
                        (result["target"], result["port"], result["username"])
                    )

            self.tasks[task_id]["status"] = "completed"

            self.tasks[task_id]["result"] = results

            self.tasks[task_id]["statistics"] = self._generate_statistics(results)

            self.tasks[task_id]["completed_at"] = datetime.now().isoformat()

        except Exception as e:

            self.tasks[task_id]["status"] = "failed"

            self.tasks[task_id]["result"] = [{"error": str(e)}]

            print(f"任务 {task_id} 执行失败: {e}")

    def _generate_statistics(self, results):

        stats = {
            "total": len(results),
            "by_protocol": {},
            "by_target": {},
            "risk_level": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }

        for result in results:

            if "error" in result:
                continue

            protocol = result["protocol"]

            stats["by_protocol"][protocol] = (
                stats["by_protocol"].get(protocol, 0) + 1
            )

            target = result["target"]

            stats["by_target"][target] = (
                stats["by_target"].get(target, 0) + 1
            )

            if (
                "admin" in result["username"].lower()
                or "root" in result["username"].lower()
            ):
                stats["risk_level"]["high"] += 1

            elif len(result["password"]) < 8:
                stats["risk_level"]["medium"] += 1

            else:
                stats["risk_level"]["low"] += 1

        return stats

    async def _get_passwords(self, dict_id: str):

        return [
            "123456",
            "admin",
            "password",
            "root",
            "12345678"
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

    asyncio.create_task(tasks.run_detection(task_id, config))

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
        "completed_at": task["completed_at"]
    }


async def execute_detection(task_id: str, config: DetectConfig):

    try:

        await tasks.run_detection(task_id, config)

    except Exception as e:

        tasks.tasks[task_id]["status"] = "failed"

        print(f"任务 {task_id} 执行失败: {e}")