from app.core.detector.ssh_detector import SSHAttacker
from app.core.detector.ftp_detector import FTPAttacker
from app.core.detector.mysql_detector import MySQLAttacker
from app.core.detector.redis_detector import RedisAttacker
from app.core.detector.rdp_detector import RDPAttacker
from app.core.detector.smb_detector import SMBDetector
from app.core.detector.telnet_detector import TelnetAttacker
from app.core.detector.http_detector import (
    HTTPAttacker,
    WordPressAttacker,
    TomcatAttacker,
    JenkinsAttacker
)

ATTACKER_MAP = {

    "ssh": SSHAttacker,

    "ftp": FTPAttacker,

    "mysql": MySQLAttacker,

    "redis": RedisAttacker,

    "rdp": RDPAttacker,

    "smb": SMBDetector,

    "telnet": TelnetAttacker,

    "http": HTTPAttacker,

    "wordpress": WordPressAttacker,

    "tomcat": TomcatAttacker,

    "jenkins": JenkinsAttacker
}


def get_attacker(fingerprint: str):

    attacker_class = ATTACKER_MAP.get(fingerprint)

    if attacker_class:
        return attacker_class()

    return None