from enum import Enum
from typing import Dict, List, Optional
from typing import Optional
from pydantic import BaseModel
from pydantic import BaseModel, Field


class SmartDictRequest(BaseModel):
    name: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None


class ProtocolType(str, Enum):
    FTP = "ftp"
    SSH = "ssh"
    TELNET = "telnet"
    SMB = "smb"
    RDP = "rdp"
    MYSQL = "mysql"
    REDIS = "redis"
    HTTP = "http"
    HTTPS = "https"
    TOMCAT = "tomcat"
    WORDPRESS = "wordpress"
    JENKINS = "jenkins"


class DetectConfig(BaseModel):
    targets: List[str]
    ports: Optional[Dict[str, List[int]]] = None
    usernames: List[str]
    protocols: List[ProtocolType]
    thread_count: int = Field(default=10, ge=1, le=1000)
    timeout: int = Field(default=5, ge=1, le=60)
    dict_id: Optional[str] = None


class DetectTask(BaseModel):
    id: str
    config: DetectConfig
    status: str
    progress: float
    result: Optional[Dict] = None
    created_at: str


class PasswordDictRequest(BaseModel):

    name: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None

    use_rule: bool = True
    use_ai: bool = True

    limit: int = 500
