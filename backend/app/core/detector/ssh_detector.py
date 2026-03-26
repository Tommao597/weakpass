import asyncio
import asyncssh
from typing import Tuple

class SSHAttacker:
    def __init__(self, timeout=5):
        self.timeout = timeout

    async def attack(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        task_id: str = None,
        tasks: dict = None
    ) -> Tuple[bool, str]:

        """SSH弱口令检测"""

        # 更新当前扫描状态
        if task_id and tasks and task_id in tasks:
            task = tasks[task_id]
            task["current_target"] = host
            task["current_user"] = username
            task["current_password"] = password

        try:
            conn = await asyncio.wait_for(
                asyncssh.connect(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    known_hosts=None
                ),
                timeout=self.timeout
            )

            conn.close()

            # 更新进度
            if task_id and tasks and task_id in tasks:
                tasks[task_id]["progress"] += 1

            return True, "成功"

        except asyncssh.Error as e:

            if task_id and tasks and task_id in tasks:
                tasks[task_id]["progress"] += 1

            return False, str(e)

        except asyncio.TimeoutError:

            if task_id and tasks and task_id in tasks:
                tasks[task_id]["progress"] += 1

            return False, "超时"

        except Exception as e:

            if task_id and tasks and task_id in tasks:
                tasks[task_id]["progress"] += 1

            return False, str(e)