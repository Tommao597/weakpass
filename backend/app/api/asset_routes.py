from fastapi import APIRouter
from app.core.asset.port_scanner import scan_ports
from app.core.asset.service_detector import detect_service
from app.core.fingerprint.fingerprint_engine import detect_fingerprint

router = APIRouter()


@router.post("/assets/scan")
async def scan_assets(target: str):
    """
    资产扫描接口
    """

    # 常见端口
    ports = [21, 22, 23, 80, 443, 445, 3306, 6379, 3389]

    # 1 端口扫描
    open_ports = await scan_ports(target, ports)

    assets = []

    # 2 服务识别 + 指纹识别
    for port in open_ports:

        # 注意：这里不能使用 await
        service = detect_service(port)

        fingerprint = await detect_fingerprint(
            target,
            port,
            service
        )

        assets.append({
            "port": port,
            "service": service,
            "fingerprint": fingerprint
        })

    # 3 返回结果
    return {
        "target": target,
        "count": len(assets),
        "assets": assets
    }