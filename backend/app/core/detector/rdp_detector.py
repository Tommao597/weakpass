import asyncio
import socket
from typing import Tuple


class RDPAttacker:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    async def attack(
        self,
        host: str,
        port: int = 3389,
        username: str = "",
        password: str = "",
    ) -> Tuple[bool, str]:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sock.connect, (host, port))

            return (
                False,
                f"RDP {host}:{port} is reachable, but password authentication is not implemented",
            )

        except socket.timeout:
            return False, f"Connection timed out after {self.timeout}s: {host}:{port}"
        except ConnectionRefusedError:
            return False, f"Connection refused: {host}:{port}"
        except socket.error as exc:
            error_code = exc.args[0] if exc.args else "unknown"
            error_message = exc.args[1] if len(exc.args) > 1 else str(exc)
            return False, f"Network error ({error_code}): {str(error_message)[:80]}"
        except Exception as exc:
            return False, f"Detection failed: {str(exc)[:80]}"
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
