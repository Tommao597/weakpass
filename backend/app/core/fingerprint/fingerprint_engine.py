from app.core.fingerprint.banner_detector import get_banner, identify_banner_service
from app.core.fingerprint.http_fingerprint import detect_http_fingerprint


async def detect_fingerprint(ip: str, port: int, service: str):
    """统一指纹识别"""

    # 1 Banner识别
    banner = await get_banner(ip, port)

    banner_service = identify_banner_service(banner)

    if banner_service and banner_service != "unknown":
        return banner_service

    # 2 HTTP识别
    if service in ["http", "https", "tomcat"]:

        url = f"http://{ip}:{port}"

        http_service = await detect_http_fingerprint(url)

        if http_service:
            return http_service

    return service