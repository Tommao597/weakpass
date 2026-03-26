import asyncio
import aiohttp
from typing import Tuple, Dict, Optional
import base64
from urllib.parse import urljoin, urlparse
import ssl
import certifi

class HTTPAttacker:
    """HTTP/HTTPS弱口令检测器"""
    
    def __init__(self, timeout=5, max_redirects=3):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.auth_types = ['basic', 'digest', 'form', 'ntlm']
        
    async def attack(self, host: str, port: int, username: str, password: str, 
                    protocol: str = 'http', path: str = '/', 
                    auth_type: str = 'basic') -> Tuple[bool, str, Dict]:
        """
        执行HTTP/HTTPS弱口令检测
        
        Args:
            host: 目标主机
            port: 端口
            username: 用户名
            password: 密码
            protocol: http 或 https
            path: 认证路径
            auth_type: 认证类型 (basic, digest, form, ntlm)
        
        Returns:
            (是否成功, 消息, 响应信息)
        """
        url = f"{protocol}://{host}:{port}{path}"
        
        # 创建SSL上下文（忽略证书验证）
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                if auth_type == 'basic':
                    return await self._basic_auth_attack(session, url, username, password)
                elif auth_type == 'digest':
                    return await self._digest_auth_attack(session, url, username, password)
                elif auth_type == 'form':
                    return await self._form_auth_attack(session, url, username, password)
                elif auth_type == 'ntlm':
                    return await self._ntlm_auth_attack(session, url, username, password)
                else:
                    return False, f"不支持的认证类型: {auth_type}", {}
                    
        except asyncio.TimeoutError:
            return False, "连接超时", {}
        except aiohttp.ClientError as e:
            return False, f"客户端错误: {str(e)}", {}
        except Exception as e:
            return False, f"未知错误: {str(e)}", {}
    
    async def _basic_auth_attack(self, session, url: str, username: str, 
                                 password: str) -> Tuple[bool, str, Dict]:
        """Basic认证攻击"""
        auth = aiohttp.BasicAuth(username, password)
        
        try:
            async with session.get(url, auth=auth, timeout=self.timeout,
                                 allow_redirects=True, max_redirects=self.max_redirects) as resp:
                
                # 检查响应状态
                if resp.status == 200:
                    # 进一步验证是否真的是认证成功（有些页面可能返回200但实际是登录页）
                    content = await resp.text()
                    if self._is_login_page(content):
                        return False, "返回登录页，可能未认证成功", self._extract_response_info(resp)
                    return True, f"认证成功 (状态码: {resp.status})", self._extract_response_info(resp)
                elif resp.status == 401:
                    return False, "认证失败", self._extract_response_info(resp)
                elif resp.status == 403:
                    return False, "禁止访问", self._extract_response_info(resp)
                else:
                    return False, f"返回状态码: {resp.status}", self._extract_response_info(resp)
                    
        except aiohttp.ClientResponseError as e:
            return False, f"响应错误: {str(e)}", {}
    
    async def _digest_auth_attack(self, session, url: str, username: str,
                                  password: str) -> Tuple[bool, str, Dict]:
        """Digest认证攻击"""
        # 先获取认证质询
        try:
            async with session.get(url, timeout=self.timeout) as resp:
                if resp.status == 401:
                    auth_header = resp.headers.get('WWW-Authenticate', '')
                    if 'digest' not in auth_header.lower():
                        return False, "不是Digest认证", {}
                    
                    # 这里简化处理，实际需要解析digest参数并生成响应
                    # 可以使用aiohttp的digest认证支持
                    from aiohttp import BasicAuth
                    auth = aiohttp.BasicAuth(username, password)
                    
                    async with session.get(url, auth=auth, timeout=self.timeout) as auth_resp:
                        if auth_resp.status == 200:
                            return True, "Digest认证成功", self._extract_response_info(auth_resp)
                        else:
                            return False, f"Digest认证失败: {auth_resp.status}", {}
                else:
                    return False, f"不需要认证或认证方式不支持: {resp.status}", {}
                    
        except Exception as e:
            return False, f"Digest认证错误: {str(e)}", {}
    
    async def _form_auth_attack(self, session, url: str, username: str,
                                password: str) -> Tuple[bool, str, Dict]:
        """表单认证攻击"""
        # 首先尝试获取登录页面，提取表单信息
        try:
            async with session.get(url, timeout=self.timeout) as resp:
                if resp.status != 200:
                    return False, f"获取登录页失败: {resp.status}", {}
                
                html = await resp.text()
                
                # 提取表单信息
                form_info = self._extract_form_info(html, url)
                if not form_info:
                    return False, "未找到登录表单", {}
                
                # 构建登录数据
                login_data = {}
                for field in form_info['fields']:
                    if field['type'] in ['text', 'email', 'username']:
                        login_data[field['name']] = username
                    elif field['type'] == 'password':
                        login_data[field['name']] = password
                    elif field.get('value'):
                        login_data[field['name']] = field['value']
                
                # 发送登录请求
                login_url = form_info['action'] if form_info['action'] else url
                if not login_url.startswith('http'):
                    login_url = urljoin(url, login_url)
                
                async with session.post(login_url, data=login_data, 
                                       allow_redirects=True,
                                       timeout=self.timeout) as login_resp:
                    
                    # 判断登录成功（通过重定向或特定内容）
                    if login_resp.status in [302, 303, 307]:
                        return True, "登录成功（重定向）", self._extract_response_info(login_resp)
                    
                    content = await login_resp.text()
                    
                    # 检查是否包含登录失败特征
                    if self._is_login_failed(content):
                        return False, "登录失败（检测到失败特征）", self._extract_response_info(login_resp)
                    
                    # 检查是否包含登录成功特征
                    if self._is_login_success(content):
                        return True, "登录成功", self._extract_response_info(login_resp)
                    
                    # 无法确定
                    return False, "无法确定登录状态", self._extract_response_info(login_resp)
                    
        except Exception as e:
            return False, f"表单认证错误: {str(e)}", {}
    
    async def _ntlm_auth_attack(self, session, url: str, username: str,
                                password: str) -> Tuple[bool, str, Dict]:
        """NTLM认证攻击"""
        # 需要使用支持NTLM的库，如requests_ntlm
        # 这里简化处理，使用basic auth作为替代
        return await self._basic_auth_attack(session, url, username, password)
    
    def _is_login_page(self, content: str) -> bool:
        """判断是否为登录页面"""
        login_indicators = [
            '<input type="password"',
            'name="password"',
            'id="password"',
            '登录</button>',
            '登陆</button>',
            'Sign in</button>',
            '请登录',
            'login-form'
        ]
        return any(indicator.lower() in content.lower() for indicator in login_indicators)
    
    def _is_login_failed(self, content: str) -> bool:
        """判断登录失败"""
        failed_indicators = [
            '用户名或密码错误',
            '密码错误',
            '账号不存在',
            '登录失败',
            'invalid username or password',
            'incorrect password',
            'authentication failed',
            'login failed'
        ]
        return any(indicator.lower() in content.lower() for indicator in failed_indicators)
    
    def _is_login_success(self, content: str) -> bool:
        """判断登录成功"""
        success_indicators = [
            '登录成功',
            '欢迎回来',
            '欢迎您',
            'dashboard',
            '控制台',
            '个人中心',
            'logout',
            '退出登录'
        ]
        return any(indicator.lower() in content.lower() for indicator in success_indicators)
    
    def _extract_form_info(self, html: str, base_url: str) -> Optional[Dict]:
        """从HTML中提取表单信息"""
        # 简化实现，实际应使用BeautifulSoup等库
        import re
        
        # 查找form标签
        form_pattern = r'<form.*?action=["\'](.*?)["\'].*?>(.*?)</form>'
        form_match = re.search(form_pattern, html, re.DOTALL | re.IGNORECASE)
        
        if not form_match:
            return None
        
        action = form_match.group(1)
        form_content = form_match.group(2)
        
        # 提取input字段
        fields = []
        input_pattern = r'<input.*?(?:name=["\'](.*?)["\']).*?(?:type=["\'](.*?)["\'])?.*?(?:value=["\'](.*?)["\'])?.*?>'
        
        for match in re.finditer(input_pattern, form_content, re.IGNORECASE):
            name = match.group(1)
            field_type = match.group(2) or 'text'
            value = match.group(3) or ''
            
            if name:  # 只包含有name的字段
                fields.append({
                    'name': name,
                    'type': field_type.lower(),
                    'value': value
                })
        
        return {
            'action': action,
            'method': 'post',  # 简化处理
            'fields': fields
        }
    
    def _extract_response_info(self, response) -> Dict:
        """提取响应信息"""
        return {
            'status': response.status,
            'headers': dict(response.headers),
            'url': str(response.url)
        }


class HTTPBatchAttacker:
    """HTTP批量检测器"""
    
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.attacker = HTTPAttacker()
    
    async def batch_attack(self, targets: list, usernames: list, passwords: list,
                          protocol: str = 'http', port: int = None, path: str = '/',
                          auth_type: str = 'basic') -> list:
        """
        批量执行HTTP检测
        
        Args:
            targets: 目标列表
            usernames: 用户名列表
            passwords: 密码列表
            protocol: http/https
            port: 端口
            path: 路径
            auth_type: 认证类型
        
        Returns:
            检测结果列表
        """
        tasks = []
        results = []
        
        for target in targets:
            for username in usernames:
                for password in passwords:
                    task = self._attack_with_semaphore(
                        target, port, username, password, protocol, path, auth_type
                    )
                    tasks.append(task)
        
        # 并发执行
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                results.append({
                    'success': False,
                    'error': str(result)
                })
            else:
                results.append(result)
        
        return results
    
    async def _attack_with_semaphore(self, host, port, username, password,
                                     protocol, path, auth_type):
        """带信号量的检测"""
        async with self.semaphore:
            success, message, info = await self.attacker.attack(
                host, port, username, password, protocol, path, auth_type
            )
            return {
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'success': success,
                'message': message,
                'info': info
            }


# 特定Web系统的检测器（针对常见CMS）
class WordPressAttacker(HTTPAttacker):
    """WordPress弱口令检测"""
    
    async def attack(self, host: str, port: int, username: str, password: str,
                    protocol: str = 'http', **kwargs) -> Tuple[bool, str, Dict]:
        """WordPress登录检测"""
        # WordPress通常使用wp-login.php进行认证
        wp_paths = ['/wp-login.php', '/wp-admin/', '/wp-admin/admin-ajax.php']
        
        for path in wp_paths:
            url = f"{protocol}://{host}:{port}{path}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    if 'wp-login.php' in path:
                        # 表单登录
                        login_data = {
                            'log': username,
                            'pwd': password,
                            'wp-submit': '登录',
                            'redirect_to': f"{protocol}://{host}:{port}/wp-admin/",
                            'testcookie': '1'
                        }
                        
                        async with session.post(url, data=login_data, 
                                               allow_redirects=False) as resp:
                            if resp.status == 302 and 'wp-admin' in resp.headers.get('Location', ''):
                                return True, f"WordPress登录成功 ({path})", {}
                    else:
                        # Basic auth尝试
                        auth = aiohttp.BasicAuth(username, password)
                        async with session.get(url, auth=auth) as resp:
                            if resp.status == 200:
                                content = await resp.text()
                                if 'wp-admin' in str(resp.url) or 'dashboard' in content.lower():
                                    return True, f"WordPress访问成功 ({path})", {}
            
            except Exception as e:
                continue
        
        return False, "WordPress登录失败", {}


class TomcatAttacker(HTTPAttacker):
    """Tomcat Manager弱口令检测"""
    
    async def attack(self, host: str, port: int, username: str, password: str,
                    protocol: str = 'http', **kwargs) -> Tuple[bool, str, Dict]:
        """Tomcat Manager认证检测"""
        # Tomcat Manager通常使用Basic认证
        manager_paths = ['/manager/html', '/manager/status', '/manager']
        
        for path in manager_paths:
            url = f"{protocol}://{host}:{port}{path}"
            
            auth = aiohttp.BasicAuth(username, password)
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, auth=auth) as resp:
                        if resp.status == 200:
                            content = await resp.text()
                            if 'Tomcat' in content and ('Manager' in content or '管理' in content):
                                return True, f"Tomcat Manager登录成功 ({path})", {}
                        elif resp.status == 403:
                            # 403可能表示认证成功但权限不足
                            return True, f"Tomcat认证成功但权限不足 ({path})", {}
            except Exception:
                continue
        
        return False, "Tomcat登录失败", {}


class JenkinsAttacker(HTTPAttacker):
    """Jenkins弱口令检测"""
    
    async def attack(self, host: str, port: int, username: str, password: str,
                    protocol: str = 'http', **kwargs) -> Tuple[bool, str, Dict]:
        """Jenkins认证检测"""
        # Jenkins可以使用多种认证方式
        url = f"{protocol}://{host}:{port}/login"
        
        # 尝试表单登录
        try:
            async with aiohttp.ClientSession() as session:
                # 先获取crumb
                async with session.get(f"{protocol}://{host}:{port}/crumbIssuer/api/json") as resp:
                    crumb_data = await resp.json() if resp.status == 200 else {}
                
                login_data = {
                    'j_username': username,
                    'j_password': password,
                    'from': '/',
                    'Submit': '登录'
                }
                
                if 'crumb' in crumb_data:
                    login_data['Jenkins-Crumb'] = crumb_data['crumb']
                
                async with session.post(f"{protocol}://{host}:{port}/j_spring_security_check",
                                       data=login_data, allow_redirects=False) as resp:
                    
                    if resp.status == 302:
                        location = resp.headers.get('Location', '')
                        if 'loginError' not in location:
                            return True, "Jenkins登录成功", {}
        
        except Exception:
            pass
        
        return False, "Jenkins登录失败", {}