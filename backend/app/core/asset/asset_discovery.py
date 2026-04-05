import asyncio

from app.core.asset.ip_parser import parse_targets
from app.core.asset.host_alive import is_host_alive
from app.core.asset.port_scanner import scan_ports
from app.core.asset.service_detector import detect_services
from app.core.fingerprint.fingerprint_engine import detect_fingerprint


async def discover_assets(target):

    ips = parse_targets(target)

    assets = []

    for ip in ips:

        alive = await is_host_alive(ip)

        if not alive:
            continue

        ports = await scan_ports(ip)

        for port in ports:

            service = await detect_services(ip, port)

            fingerprint = await detect_fingerprint(
                ip,
                port,
                service
            )

            assets.append({
                "ip": ip,
                "port": port,
                "service": service,
                "fingerprint": fingerprint
            })

    return assets