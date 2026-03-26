import asyncio
from typing import Tuple
from ftplib import FTP


class FTPAttacker:

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    async def attack(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        FTP弱口令检测
        """
        loop = asyncio.get_event_loop()

        try:
            def ftp_login():
                ftp = FTP()
                ftp.connect(host, port, timeout=self.timeout)
                ftp.login(username, password)
                ftp.quit()
                return True

            result = await loop.run_in_executor(None, ftp_login)

            if result:
                return True, f"{username}:{password}"

            return False, ""

        except Exception:
            return False, ""