import asyncio
import socket
from typing import Tuple

class RDPAttacker:
    """纯 Python 内置模块实现 RDP 弱口令检测器（零依赖、跨平台、稳定）"""
    def __init__(self, timeout: int = 5):
        """
        初始化 RDP 检测器
        :param timeout: 连接超时时间（秒）
        """
        self.timeout = timeout

    async def attack(self, host: str, port: int = 3389, username: str = '', password: str = '') -> Tuple[bool, str]:
        """
        核心方法：检测 RDP 端口连通性（弱口令检测前置）
        :param host: 目标主机IP/域名
        :param port: RDP端口（默认3389）
        :param username: 待检测用户名（保留接口，后续可扩展认证）
        :param password: 待检测密码（保留接口，后续可扩展认证）
        :return: (是否成功, 结果消息)
        """
        sock = None
        try:
            # 1. 初始化 TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置超时
            sock.settimeout(self.timeout)

            # 2. 异步执行连接（避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                sock.connect,
                (host, port)
            )

            # 3. 端口开放，返回结果
            return True, f"✅ RDP端口{port}开放 | 目标: {host} | 待验证账号: {username}:{password}"

        except socket.timeout:
            return False, f"⏱️ 连接超时（{self.timeout}秒）| 目标: {host}:{port}"
        except ConnectionRefusedError:
            return False, f"🔌 端口{port}拒绝连接 | 目标: {host}（RDP服务未开启/防火墙拦截）"
        except socket.error as e:
            # 捕获其他网络错误
            return False, f"⚠️ 网络错误 | 错误码: {e.args[0]} | 详情: {e.args[1][:50]}"
        except Exception as e:
            # 捕获未知异常
            return False, f"❌ 检测失败 | 原因: {str(e)[:80]}"
        finally:
            # 确保 socket 资源释放
            if sock:
                try:
                    sock.close()
                except:
                    pass

