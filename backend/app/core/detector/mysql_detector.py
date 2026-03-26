import asyncio
import pymysql
from typing import Tuple

class MySQLAttacker:
    def __init__(self, timeout=5):
        self.timeout = timeout
    
    async def attack(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """MySQL弱口令检测"""
        try:
            conn = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pymysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    connect_timeout=self.timeout
                )
            )
            conn.close()
            return True, "成功"
        except pymysql.Error as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)    