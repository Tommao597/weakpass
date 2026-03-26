import asyncio
from typing import Tuple
import telnetlib3


class TelnetAttacker:

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    async def attack(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        Telnet弱口令检测
        """
        try:
            reader, writer = await asyncio.wait_for(
                telnetlib3.open_connection(host, port),
                timeout=self.timeout
            )

            # 等待用户名提示
            await asyncio.sleep(1)
            writer.write(username + "\n")

            # 等待密码提示
            await asyncio.sleep(1)
            writer.write(password + "\n")

            await asyncio.sleep(2)

            output = await reader.read(100)

            writer.close()

            # 简单判断是否登录成功
            if "incorrect" not in output.lower() and "failed" not in output.lower():
                return True, f"{username}:{password}"

            return False, ""

        except Exception:
            return False, ""