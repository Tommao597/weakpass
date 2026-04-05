import asyncio


async def scan_port(ip: str, port: int, timeout: int = 1):
    """扫描单个端口"""

    try:

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout
        )

        writer.close()
        await writer.wait_closed()

        return port

    except:
        return None


async def scan_ports(ip: str, ports: list, concurrency: int = 100):
    """扫描多个端口"""

    semaphore = asyncio.Semaphore(concurrency)

    async def worker(port):

        async with semaphore:
            return await scan_port(ip, port)

    tasks = [worker(p) for p in ports]

    results = await asyncio.gather(*tasks)

    open_ports = [p for p in results if p]

    return open_ports