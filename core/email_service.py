"""
邮箱服务模块 - 支持多源自动切换
包含: SamfunAsia, Primary(自定义), Mail.tm(备用)
"""
import random
import string
import time
import json
import re
import urllib3
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入 HTTP 工具
try:
    from utils.http_client import http_get, http_post
except ImportError:
    # 如果直接运行此文件，定义备用导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.http_client import http_get, http_post


class EmailServiceType(Enum):
    """邮箱服务类型"""
    SAMFUN_ASIA = "samfun_asia"      # 源1: SamfunAsia
    PRIMARY = "primary"               # 源2: 主服务 (如 chatgpt.org.uk)
    MAIL_TM = "mail_tm"               # 源3: Mail.tm (备用)


@dataclass
class EmailServiceResult:
    """邮箱服务结果"""
    email: str
    service_type: EmailServiceType
    service_instance: Any
    login_url: str


class SamfunAsiaEmailService:
    """
    SamfunAsia 邮箱服务 (samfun.asia)
    主要邮箱服务，优先使用
    """
    
    API_BASE = "https://cloudflare_temp_email.caiql20022000.workers.dev"
    ADMIN_AUTH = "xiaoyibao@1234"
    
    def __init__(self):
        self.email: Optional[str] = None
        self.jwt: Optional[str] = None
    
    def _generate_username(self) -> str:
        """生成随机用户名"""
        adjectives = ['blue', 'green', 'red', 'happy', 'sunny', 'bright', 'cool', 'swift', 
                      'lucky', 'golden', 'silver', 'quick', 'smart', 'wild']
        nouns = ['wave', 'star', 'moon', 'sun', 'cloud', 'river', 'mountain', 'forest', 
                 'ocean', 'breeze', 'flower', 'tree', 'bird', 'fish']
        return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(100, 999)}"
    
    def create_email(self, max_retries: int = 3) -> Tuple[str, str]:
        """
        创建临时邮箱
        
        Returns:
            tuple: (email, jwt)
        """
        import requests
        
        username = self._generate_username()
        headers = {
            "x-admin-auth": self.ADMIN_AUTH,
            "Content-Type": "application/json"
        }
        body = {
            "enablePrefix": True,
            "name": username,
            "domain": "samfun.asia"
        }
        
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    f"{self.API_BASE}/admin/new_address",
                    headers=headers,
                    json=body,
                    timeout=30,
                    verify=False
                )
                data = resp.json()
                self.email = data.get("address")
                self.jwt = data.get("jwt")
                
                if self.email and self.jwt:
                    return self.email, self.jwt
                    
            except Exception as e:
                print(f"[SamfunAsia] 创建邮箱失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        raise Exception("SamfunAsia 创建邮箱失败")
    
    def get_messages(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        获取邮件列表
        
        Returns:
            list: 邮件列表
        """
        import requests
        
        if not self.jwt:
            raise Exception("JWT 未初始化，请先创建邮箱")
        
        headers = {"Authorization": f"Bearer {self.jwt}"}
        
        try:
            resp = requests.get(
                f"{self.API_BASE}/api/mails?limit={limit}&offset={offset}",
                headers=headers,
                timeout=30,
                verify=False
            )
            data = resp.json()
            # API 返回格式: {"results": [...], "count": N}
            if isinstance(data, dict) and "results" in data:
                return data["results"]
            elif isinstance(data, list):
                return data
            else:
                return []
        except Exception as e:
            print(f"[SamfunAsia] 获取邮件失败: {e}")
            return []
    
    def extract_verification_link(self, raw_content: str) -> Optional[str]:
        """
        从邮件内容中提取 Fireworks 验证链接
        
        Returns:
            str: 验证链接，未找到返回 None
        """
        if not raw_content:
            return None
        
        pattern = r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+'
        match = re.search(pattern, raw_content, re.IGNORECASE)
        
        if match:
            return match.group(0)
        return None
    
    def get_verification_link(self, timeout: int = 60, check_interval: int = 3) -> Optional[str]:
        """
        获取 Fireworks 验证链接
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            str: 验证链接，超时返回 None
        """
        print(f"[SamfunAsia] 开始获取验证链接，超时: {timeout}s...")
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < timeout:
            attempt += 1
            try:
                messages = self.get_messages()
                print(f"[SamfunAsia] 第{attempt}轮检查，找到 {len(messages)} 封邮件")
                
                for msg in messages:
                    raw_content = msg.get("raw", "") if isinstance(msg, dict) else str(msg)
                    
                    if "fireworks" in raw_content.lower():
                        print(f"[SamfunAsia] 找到 Fireworks 邮件")
                        link = self.extract_verification_link(raw_content)
                        if link:
                            print(f"[SamfunAsia] 成功提取链接: {link[:60]}...")
                            return link
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"[SamfunAsia] 获取邮件出错: {e}")
                time.sleep(check_interval)
        
        print(f"[SamfunAsia] 获取验证链接超时")
        return None


class PrimaryEmailService:
    """
    主邮箱服务（如 chatgpt.org.uk 或其他自定义 API）
    
    服务格式要求：
    - 生成邮箱: GET /api/generate-email -> { "data": { "email": "xxx" } }
    - 获取邮件: GET /api/emails?email=xxx -> { "data": { "emails": [...] } }
    
    支持多 Key 自动切换: 默认 Key -> 自定义 Key
    """
    
    # 默认 API Key（内置）
    DEFAULT_API_KEY = "gpt-test"
    
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.custom_api_key = api_key  # 自定义 Key（从 env 读取）
        self.email: Optional[str] = None
        self.current_key: str = ""  # 当前使用的 Key
        
        # 初始化 logger
        try:
            from utils.logger import Logger
            self.logger = Logger()
        except:
            # 如果导入失败，使用简单的打印
            class SimpleLogger:
                def info(self, msg): print(f"[INFO] {msg}")
                def warning(self, msg): print(f"[WARN] {msg}")
                def error(self, msg): print(f"[ERROR] {msg}")
            self.logger = SimpleLogger()
    
    def _get_headers(self, api_key: str) -> Dict[str, str]:
        """获取请求头"""
        headers = {"User-Agent": "Mozilla/5.0"}
        if api_key:
            headers["X-API-Key"] = api_key
        return headers
    
    def create_email(self) -> str:
        """创建临时邮箱（支持多 Key 自动切换）"""
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        # 尝试顺序: 1. 默认 Key -> 2. 自定义 Key
        keys_to_try = []
        
        # 添加默认 Key
        if self.DEFAULT_API_KEY:
            keys_to_try.append(("默认", self.DEFAULT_API_KEY))
        
        # 添加自定义 Key（如果与默认不同）
        if self.custom_api_key and self.custom_api_key != self.DEFAULT_API_KEY:
            keys_to_try.append(("自定义", self.custom_api_key))
        
        last_error = None
        
        for key_name, api_key in keys_to_try:
            try:
                self.logger.info(f"尝试使用 {key_name} Key 创建邮箱...")
                resp = requests.get(
                    f"{self.base_url}/api/generate-email",
                    headers=self._get_headers(api_key),
                    timeout=30,
                    verify=False
                )
                data = resp.json()
                
                if "data" in data and "email" in data["data"]:
                    self.email = data["data"]["email"]
                    self.current_key = api_key
                    self.logger.info(f"✅ 使用 {key_name} Key 创建邮箱成功: {self.email}")
                    return self.email
                else:
                    error_msg = data.get("message", "Unknown error")
                    self.logger.warning(f"{key_name} Key 返回错误: {error_msg}")
                    last_error = Exception(f"{key_name} Key 无效: {error_msg}")
                    
            except Exception as e:
                last_error = e
                self.logger.warning(f"{key_name} Key 请求失败: {e}")
                continue
        
        # 所有 Key 都失败了
        raise last_error or Exception("所有 API Key 均无法创建邮箱")
    
    def get_emails(self) -> List[Dict]:
        """获取邮件列表（使用当前生效的 Key）"""
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        if not self.email:
            return []
        
        try:
            headers = self._get_headers(self.current_key)
            resp = requests.get(
                f"{self.base_url}/api/emails?email={self.email}",
                headers=headers,
                timeout=30,
                verify=False
            )
            data = resp.json()
            return data.get("data", {}).get("emails", [])
        except:
            return []
    
    def get_verification_link(self, timeout: int = 60) -> Optional[str]:
        """获取 Fireworks 验证链接"""
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        start = time.time()
        
        while time.time() - start < timeout:
            emails = self.get_emails()
            
            for email in emails:
                from_addr = email.get("from_address", "").lower()
                if "fireworks" in from_addr:
                    html = email.get("html_content", "")
                    text = email.get("subject", "")
                    content = html + " " + text
                    
                    match = re.search(
                        r'https://app\.fireworks\.ai/signup/confirm[^"\s]+',
                        content
                    )
                    if match:
                        return match.group(0)
            
            time.sleep(2)
        
        return None


class MailTMService:
    """
    mail.tm 临时邮箱服务（备用服务）
    """
    
    BASE_URL = "https://api.mail.tm"
    
    def __init__(self):
        self.token: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.account_id: Optional[str] = None
    
    def get_domain(self) -> str:
        """获取可用域名"""
        body, _ = http_get(f"{self.BASE_URL}/domains")
        if not isinstance(body, str):
            raise Exception("获取 mail.tm 域名失败")
        
        data = json.loads(body)
        if "hydra:member" in data and len(data["hydra:member"]) > 0:
            return data["hydra:member"][0]["domain"]
        raise Exception("mail.tm 没有可用域名")
    
    def create_account(self) -> str:
        """创建临时邮箱账户"""
        domain = self.get_domain()
        
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        self.email = f"{username}@{domain}"
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        payload = json.dumps({"address": self.email, "password": self.password})
        headers = {"Content-Type": "application/json"}
        body, _ = http_post(f"{self.BASE_URL}/accounts", payload, headers)
        
        if not isinstance(body, str):
            raise Exception("创建 mail.tm 账户失败")
        
        data = json.loads(body)
        if "id" in data:
            self.account_id = data["id"]
            return self.email
        elif "detail" in data:
            raise Exception(f"创建 mail.tm 账户失败: {data['detail']}")
        else:
            raise Exception(f"创建 mail.tm 账户失败: {body}")
    
    def get_token(self) -> str:
        """获取访问 token"""
        payload = json.dumps({"address": self.email, "password": self.password})
        headers = {"Content-Type": "application/json"}
        body, _ = http_post(f"{self.BASE_URL}/token", payload, headers)
        
        if not isinstance(body, str):
            raise Exception("获取 mail.tm token 失败")
        
        data = json.loads(body)
        if "token" in data:
            self.token = data["token"]
            return self.token
        raise Exception(f"获取 mail.tm token 失败: {data}")
    
    def get_messages(self, retry: bool = True) -> List[Dict]:
        """获取邮件列表"""
        if not self.token:
            self.get_token()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        body, _ = http_get(f"{self.BASE_URL}/messages", headers)
        
        if not isinstance(body, str) and retry:
            print(f"[MailTM] 获取邮件列表失败，尝试重新获取token...")
            self.token = None
            self.get_token()
            return self.get_messages(retry=False)
        
        if not isinstance(body, str):
            return []
        
        try:
            data = json.loads(body)
            return data.get("hydra:member", [])
        except json.JSONDecodeError:
            return []
    
    def get_message_content(self, message_id: str, retry: bool = True) -> Dict:
        """获取邮件内容"""
        if not self.token:
            self.get_token()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        body, _ = http_get(f"{self.BASE_URL}/messages/{message_id}", headers)
        
        if not isinstance(body, str) and retry:
            print(f"[MailTM] 获取邮件内容失败，尝试重新获取token...")
            self.token = None
            self.get_token()
            return self.get_message_content(message_id, retry=False)
        
        if not isinstance(body, str):
            return {}
        
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    
    def get_verification_link(self, timeout: int = 60, check_interval: int = 3) -> Optional[str]:
        """获取验证链接"""
        print(f"[MailTM] 开始获取验证链接，超时时间: {timeout}s...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages()
            
            for msg in messages:
                msg_id = msg.get("id")
                if not msg_id:
                    continue
                
                content = self.get_message_content(msg_id)
                text_content = content.get("text", "")
                html_content = content.get("html", [])
                
                if isinstance(html_content, list):
                    html_content = " ".join(str(item) for item in html_content)
                
                full_content = f"{text_content} {html_content}"
                
                # 检查是否来自 Fireworks
                from_addr = content.get("from", {}).get("address", "").lower()
                if "fireworks" in from_addr or "fireworks" in full_content.lower():
                    match = re.search(
                        r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+',
                        full_content
                    )
                    if match:
                        return match.group(0)
            
            time.sleep(check_interval)
        
        return None


class EmailServiceManager:
    """
    邮箱服务管理器 - 多源自动切换
    
    优先级:
    1. SamfunAsia (samfun.asia)
    2. Primary (如 chatgpt.org.uk)
    3. Mail.tm (备用)
    """
    
    # 默认 Primary 邮箱服务配置 (chatgpt.org.uk)
    DEFAULT_PRIMARY_URL = "https://mail.chatgpt.org.uk"
    DEFAULT_PRIMARY_KEY = "sk-4rt8HwcA"
    
    def __init__(self):
        # 服务优先级: Primary -> Mail.tm -> SamfunAsia
        self.service_order = [
            EmailServiceType.PRIMARY,       # 第一优先级: Primary (chatgpt.uk)
            EmailServiceType.MAIL_TM,       # 第二优先级: Mail.tm
            EmailServiceType.SAMFUN_ASIA    # 第三优先级: SamfunAsia
        ]
        self.current_service: Optional[EmailServiceType] = None
        self.service_instance: Optional[Any] = None
        self.failed_services: set = set()
        
        # 配置 - 使用默认值 (chatgpt.uk)
        self.primary_url: str = self.DEFAULT_PRIMARY_URL
        self.primary_key: str = self.DEFAULT_PRIMARY_KEY
    
    def set_primary_config(self, url: str, api_key: str = ""):
        """设置主服务配置（覆盖默认值）"""
        if url:
            self.primary_url = url
        if api_key:
            self.primary_key = api_key
    
    def _create_service(self, service_type: EmailServiceType) -> Optional[Any]:
        """创建指定类型的服务实例"""
        if service_type == EmailServiceType.SAMFUN_ASIA:
            return SamfunAsiaEmailService()
        elif service_type == EmailServiceType.PRIMARY:
            if self.primary_url:
                return PrimaryEmailService(self.primary_url, self.primary_key)
            return None
        elif service_type == EmailServiceType.MAIL_TM:
            return MailTMService()
        return None
    
    def create_email(self) -> EmailServiceResult:
        """
        创建临时邮箱（按优先级自动切换）
        
        Returns:
            EmailServiceResult: 邮箱服务结果
            
        Raises:
            Exception: 所有源均不可用
        """
        for service_type in self.service_order:
            if service_type in self.failed_services:
                continue
            
            try:
                service = self._create_service(service_type)
                if not service:
                    continue
                
                if service_type == EmailServiceType.SAMFUN_ASIA:
                    email, jwt = service.create_email()
                    result = EmailServiceResult(
                        email=email,
                        service_type=service_type,
                        service_instance=service,
                        login_url="https://mail.samfun.asia/"
                    )
                    
                elif service_type == EmailServiceType.PRIMARY:
                    email = service.create_email()
                    result = EmailServiceResult(
                        email=email,
                        service_type=service_type,
                        service_instance=service,
                        login_url=f"{self.primary_url}/?email={email}"
                    )
                    
                elif service_type == EmailServiceType.MAIL_TM:
                    email = service.create_account()
                    service.get_token()
                    result = EmailServiceResult(
                        email=email,
                        service_type=service_type,
                        service_instance=service,
                        login_url="https://mail.tm/"
                    )
                else:
                    continue
                
                # 成功
                self.current_service = service_type
                self.service_instance = service
                print(f"[EmailManager] 使用 {service_type.value} 创建邮箱成功: {email}")
                return result
                
            except Exception as e:
                print(f"[EmailManager] {service_type.value} 创建失败: {e}")
                self.failed_services.add(service_type)
                continue
        
        # 所有源都失败
        raise Exception("所有邮箱服务源均不可用")
    
    def get_verification_link(self, timeout: int = 60) -> Optional[str]:
        """
        获取验证链接
        
        如果当前源获取失败，不会自动切换（因为邮箱是在该源创建的）
        """
        if not self.service_instance:
            raise Exception("邮箱服务未初始化")
        
        return self.service_instance.get_verification_link(timeout)
    
    def reset_failed_services(self):
        """重置失败记录（用于下次注册时重新尝试）"""
        self.failed_services.clear()
        print("[EmailManager] 已重置失败服务记录")


# 测试代码
if __name__ == "__main__":
    print("测试邮箱服务模块...")
    
    # 测试 SamfunAsia
    print("\n1. 测试 SamfunAsia...")
    try:
        samfun = SamfunAsiaEmailService()
        email, jwt = samfun.create_email()
        print(f"   创建邮箱成功: {email}")
        print(f"   JWT: {jwt[:30]}...")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试 Mail.tm
    print("\n2. 测试 Mail.tm...")
    try:
        mailtm = MailTMService()
        email = mailtm.create_account()
        print(f"   创建邮箱成功: {email}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n测试完成!")
