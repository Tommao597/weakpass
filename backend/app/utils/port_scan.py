import asyncio
from typing import Iterable, List


async def scan_port(host: str, port: int, timeout: int = 2) -> bool:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (
        asyncio.TimeoutError,
        ConnectionRefusedError,
        OSError,
    ):
        return False


async def scan_ports(host: str, ports: Iterable[int], timeout: int = 2) -> List[int]:
    port_list = list(dict.fromkeys(int(port) for port in ports))
    results = await asyncio.gather(
        *(scan_port(host, port, timeout=timeout) for port in port_list),
        return_exceptions=False,
    )
    return [port for port, is_open in zip(port_list, results) if is_open]
