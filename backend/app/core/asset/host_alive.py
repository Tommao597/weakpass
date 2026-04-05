import asyncio


async def is_host_alive(ip):

    try:

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, 80),
            timeout=1
        )

        writer.close()
        await writer.wait_closed()

        return True

    except:
        return False