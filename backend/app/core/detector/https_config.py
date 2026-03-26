import ssl
import certifi
from typing import Optional, Tuple
import aiohttp
import asyncio

class HTTPSConfig:
    """HTTPS配置管理"""
    
    def __init__(self, verify_ssl: bool = False, cert_path: Optional[str] = None,
                 key_path: Optional[str] = None, ca_path: Optional[str] = None):
        """
        初始化HTTPS配置
        
        Args:
            verify_ssl: 是否验证SSL证书
            cert_path: 客户端证书路径
            key_path: 客户端密钥路径
            ca_path: CA证书路径
        """
        self.verify_ssl = verify_ssl
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path or certifi.where()
    
    def create_ssl_context(self) -> ssl.SSLContext:
        """创建SSL上下文"""
        if not self.verify_ssl:
            # 不验证证书（用于测试）
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
        
        # 验证证书
        ssl_context = ssl.create_default_context(cafile=self.ca_path)
        
        if self.cert_path and self.key_path:
            ssl_context.load_cert_chain(self.cert_path, self.key_path)
        
        return ssl_context
    
    def create_connector(self) -> aiohttp.TCPConnector:
        """创建连接器"""
        return aiohttp.TCPConnector(
            ssl=self.create_ssl_context(),
            limit=100,
            ttl_dns_cache=300
        )


class HTTPSInspector:
    """HTTPS证书和配置检查器"""
    
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def inspect_certificate(self, host: str, port: int) -> dict:
        """
        检查HTTPS证书信息
        """
        try:
            reader, writer = await asyncio.open_connection(host, port, ssl=self.ssl_context)
            
            # 获取证书
            ssl_object = writer.get_extra_info('ssl_object')
            cert = ssl_object.getpeercert()
            
            writer.close()
            await writer.wait_closed()
            
            if cert:
                # 提取证书信息
                subject = dict(x[0] for x in cert['subject'])
                issuer = dict(x[0] for x in cert['issuer'])
                
                return {
                    'subject': subject,
                    'issuer': issuer,
                    'version': cert.get('version'),
                    'serialNumber': cert.get('serialNumber'),
                    'notBefore': cert.get('notBefore'),
                    'notAfter': cert.get('notAfter'),
                    'subjectAltName': cert.get('subjectAltName', [])
                }
            else:
                return {'error': '未获取到证书'}
                
        except Exception as e:
            return {'error': str(e)}
    
    async def check_ssl_config(self, host: str, port: int) -> dict:
        """
        检查SSL/TLS配置
        """
        # 支持的协议版本
        protocols = {
            ssl.PROTOCOL_TLS: 'TLS',
            ssl.PROTOCOL_TLSv1: 'TLSv1',
            ssl.PROTOCOL_TLSv1_1: 'TLSv1.1',
            ssl.PROTOCOL_TLSv1_2: 'TLSv1.2',
            ssl.PROTOCOL_TLSv1_3: 'TLSv1.3'
        }
        
        results = {}
        
        for protocol, name in protocols.items():
            try:
                context = ssl.SSLContext(protocol)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port, ssl=context),
                    timeout=5
                )
                writer.close()
                await writer.wait_closed()
                
                results[name] = '支持'
            except Exception:
                results[name] = '不支持'
        
        return results
    
    async def check_cipher_suites(self, host: str, port: int) -> list:
        """
        检查支持的加密套件
        """
        # 常见的不安全加密套件
        weak_ciphers = [
            'RC4',
            'DES',
            '3DES',
            'EXPORT',
            'NULL',
            'ANON',
            'MD5'
        ]
        
        # 这里简化处理，实际应使用openssl或专门的库
        return {
            'weak_ciphers': weak_ciphers,
            'note': '需要更详细的检测工具'
        }