from fastapi import APIRouter
from app.core.asset.port_scanner import scan_ports
from app.core.asset.service_detector import detect_service
from app.core.fingerprint.fingerprint_engine import detect_fingerprint
from app.core.database import asset_dao  # 导入资产DAO

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
            "target": target,
            "port": port,
            "service": service,
            "fingerprint": fingerprint
        })

    # 3 保存扫描结果到数据库
    scan_data = {
        "target": target,
        "status": "completed",
        "total_assets": len(assets),
        "assets": assets
    }
    
    scan_id = asset_dao.create_asset_scan(scan_data)

    # 4 返回结果
    return {
        "scan_id": scan_id,
        "target": target,
        "count": len(assets),
        "assets": assets
    }


@router.get("/assets/scans")
async def get_asset_scans():
    """
    获取资产扫描历史
    """
    scans = asset_dao.get_asset_scans()
    return {
        "scans": scans
    }


@router.get("/assets/scans/target/{target}")
async def get_assets_by_target(target: str):
    """
    根据目标获取资产扫描历史
    """
    scan = asset_dao.get_latest_assets(target)
    if scan:
        assets = asset_dao.get_assets_by_scan(scan['id'])
        return {
            "scan": scan,
            "assets": assets
        }
    else:
        return {
            "scan": None,
            "assets": []
        }


@router.get("/assets/scans/{scan_id}")
async def get_assets_by_scan(scan_id: int):
    """
    根据扫描ID获取资产详情
    """
    # 首先获取扫描信息
    scan_query = """
    SELECT s.id, s.target, s.status, s.total_assets, s.created_at as scan_time,
           COUNT(a.id) as asset_count
    FROM asset_scans s
    LEFT JOIN assets a ON s.id = a.scan_id
    WHERE s.id = ?
    GROUP BY s.id, s.target, s.status, s.total_assets, s.created_at
    """
    scan = asset_dao.db.fetch_one(scan_query, (scan_id,))
    
    if scan:
        assets = asset_dao.get_assets_by_scan(scan_id)
        return {
            "scan": scan,
            "assets": assets
        }
    else:
        return {
            "scan": None,
            "assets": []
        }