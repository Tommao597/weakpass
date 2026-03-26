import asyncio


async def scan_port(host: str, port: int, timeout: int = 2) -> bool:
    """
    扫描单个端口
    """
    try:
        conn = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )

        conn[1].close()
        return True

    except:
        return False


async def scan_ports(host: str, ports: list):
    """
    扫描多个端口
    """
    tasks = []

    for port in ports:
        tasks.append(scan_port(host, port))

    results = await asyncio.gather(*tasks)

    open_ports = []

    for port, result in zip(ports, results):
        if result:
            open_ports.append(port)

    return open_ports