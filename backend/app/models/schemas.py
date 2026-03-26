from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class SmartDictRequest(BaseModel):

    name: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None

class ProtocolType(str, Enum):
    SSH = "ssh"
    RDP = "rdp"
    MYSQL = "mysql"
    HTTP = "http"
    HTTPS = "https"

class DetectConfig(BaseModel):
    targets: List[str]  # IP或域名列表
    ports: Optional[Dict[str, List[int]]]  # 协议对应的端口
    usernames: List[str]
    protocols: List[ProtocolType]
    thread_count: int = 10
    timeout: int = 5
    dict_id: Optional[str] = None

class DetectTask(BaseModel):
    id: str
    config: DetectConfig
    status: str  # pending, running, completed, failed
    progress: float
    result: Optional[Dict] = None
    created_at: str                     