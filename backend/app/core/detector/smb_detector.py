from typing import Tuple
from impacket.smbconnection import SMBConnection


class SMBDetector:

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    async def attack(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        SMB弱口令检测
        """
        try:
            conn = SMBConnection(host, host, sess_port=port, timeout=self.timeout)

            conn.login(username, password)

            conn.logoff()

            return True, f"{username}:{password}"

        except Exception:
            return False, ""