import asyncio
from typing import Tuple
import redis


class RedisAttacker:

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    async def attack(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        Redis弱口令检测
        Redis通常没有username，默认只需要password
        """
        loop = asyncio.get_event_loop()

        try:
            def redis_auth():
                r = redis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    socket_connect_timeout=self.timeout,
                    decode_responses=True
                )

                r.ping()
                return True

            result = await loop.run_in_executor(None, redis_auth)

            if result:
                return True, f":{password}"

            return False, ""

        except Exception:
            return False, ""