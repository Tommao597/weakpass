import asyncio


async def get_banner(ip: str, port: int, timeout: int = 3):
    """获取服务Banner"""

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout
        )

        data = await asyncio.wait_for(reader.read(1024), timeout)

        writer.close()
        await writer.wait_closed()

        return data.decode(errors="ignore")

    except:
        return None


def identify_banner_service(banner: str):
    """根据Banner识别服务"""

    if not banner:
        return None

    banner = banner.lower()

    if "ssh" in banner:
        return "ssh"

    if "redis" in banner:
        return "redis"

    if "mysql" in banner:
        return "mysql"

    if "ftp" in banner:
        return "ftp"

    return "unknown"