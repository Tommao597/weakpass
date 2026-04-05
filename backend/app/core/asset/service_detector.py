SERVICE_PORT_MAP = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    80: "http",
    443: "https",
    445: "smb",
    3306: "mysql",
    6379: "redis",
    3389: "rdp",
    8080: "tomcat"
}


def detect_service(port: int):
    """识别单个服务"""
    return SERVICE_PORT_MAP.get(port, "unknown")


def detect_services(open_ports: list):
    """识别多个端口"""

    services = []

    for port in open_ports:

        services.append({
            "port": port,
            "service": detect_service(port)
        })

    return services