import ipaddress


def parse_targets(target: str):

    targets = []

    # CIDR
    if "/" in target:
        net = ipaddress.ip_network(target, strict=False)
        targets = [str(ip) for ip in net.hosts()]

    # IP范围
    elif "-" in target:

        start, end = target.split("-")

        start_ip = list(map(int, start.split(".")))
        end_ip = list(map(int, end.split(".")))

        for i in range(start_ip[3], end_ip[3] + 1):
            targets.append(
                f"{start_ip[0]}.{start_ip[1]}.{start_ip[2]}.{i}"
            )

    else:
        targets.append(target)

    return targets