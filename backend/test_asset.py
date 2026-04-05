import asyncio
from app.core.asset.asset_discovery import discover_assets


async def test():

    result = await discover_assets("127.0.0.1")

    print(result)


if __name__ == "__main__":

    asyncio.run(test())