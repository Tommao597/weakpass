import ipaddress
import logging
import re
from typing import List, Union

HOSTNAME_PATTERN = re.compile(
    r"^(?=.{1,253}$)(localhost|[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*)$"
)

logger = logging.getLogger(__name__)


def _is_hostname(value: str) -> bool:
    return bool(HOSTNAME_PATTERN.match(value))


def parse_targets(target: Union[str, List[str]]) -> List[str]:
    targets: List[str] = []

    if isinstance(target, str):
        lines = target.replace("\r\n", "\n").split("\n")
    elif isinstance(target, list):
        lines = [str(item) for item in target if item is not None]
    else:
        logger.warning("Unsupported target input type: %s", type(target))
        return targets

    for line in lines:
        line = line.strip()
        if not line or line.lower() == "string":
            continue

        try:
            if "/" in line:
                network = ipaddress.ip_network(line, strict=False)
                for ip in network.hosts():
                    ip_str = str(ip)
                    if ip_str not in targets:
                        targets.append(ip_str)
                continue

            if "-" in line:
                start_ip, end_ip = [part.strip() for part in line.split("-", 1)]
                start = int(ipaddress.ip_address(start_ip))
                end = int(ipaddress.ip_address(end_ip))

                if start > end:
                    start, end = end, start

                for ip_int in range(start, end + 1):
                    ip_str = str(ipaddress.ip_address(ip_int))
                    if ip_str not in targets:
                        targets.append(ip_str)
                continue

            try:
                ipaddress.ip_address(line)
                candidate = line
            except ValueError:
                if not _is_hostname(line):
                    raise
                candidate = line

            if candidate not in targets:
                targets.append(candidate)

        except ValueError as exc:
            logger.warning("Skipping invalid target %s: %s", line, exc)
        except Exception as exc:
            logger.warning("Skipping target %s due to unexpected error: %s", line, exc)

    return targets
