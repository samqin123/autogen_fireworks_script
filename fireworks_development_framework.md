# Fireworks AI 自动注册开发框架文档

> **版本**: v1.0  
> **日期**: 2026-02-28  
> **用途**: 自动化测试技术研究

---

## 1. 项目结构

```
fireworks_auto_register/
├── core/
│   ├── __init__.py
│   ├── browser_manager.py      # 浏览器管理（UCDriver）
│   ├── email_service.py        # 邮箱服务（支持多源）
│   └── config.py               # 配置管理
├── services/
│   ├── __init__.py
│   ├── registration.py         # 注册流程核心
│   ├── verification.py         # 邮箱验证处理
│   ├── onboarding.py           # 入门引导（问卷）
│   └── api_key_manager.py      # API Key 管理
├── utils/
│   ├── __init__.py
│   ├── logger.py               # 日志工具
│   ├── helpers.py              # 通用工具
│   ├── file_handler.py         # 文件处理（增量写入）
│   └── validators.py           # 数据验证
├── tests/
│   └── test_flows.py           # 测试用例
├── main.py                     # 主入口
├── requirements.txt
└── .chromedriver_cache/        # 驱动缓存
```

---

## 2. 核心要素

### 2.1 依赖包

```txt
# requirements.txt
undetected-chromedriver>=3.5.0
selenium>=4.15.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### 2.2 关键配置

```python
# config.py
class Config:
    # 浏览器配置
    BROWSER_HEADLESS = False
    BROWSER_WINDOW_SIZE = (1920, 1080)
    CHROMEDRIVER_CACHE = ".chromedriver_cache"
    
    # 超时配置
    PAGE_LOAD_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    VERIFY_EMAIL_TIMEOUT = 60
    
    # 重试配置
    MAX_RETRY = 3
    RETRY_DELAY = 2
    
    # 人机模拟延迟
    TYPING_MIN_DELAY = 0.05
    TYPING_MAX_DELAY = 0.15
    CLICK_DELAY = 0.5
    BETWEEN_ACCOUNTS = 15
    
    # 输出配置
    OUTPUT_DIR = "output"
    RESULTS_FILE = "fireworks_{date}.txt"
```

### 2.3 页面 URL 常量

```python
# constants.py
class URLs:
    BASE = "https://app.fireworks.ai"
    SIGNUP = f"{BASE}/signup"
    LOGIN = f"{BASE}/login"
    EMAIL_LOGIN = f"{BASE}/login/email"
    API_KEYS = f"{BASE}/settings/users/api-keys"
    ONBOARDING = f"{BASE}/onboarding"
    ACCOUNT_HOME = f"{BASE}/account/home"
```

---

## 3. 示例代码

### 3.1 浏览器管理器

```python
# core/browser_manager.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import os
import subprocess


class BrowserManager:
    """
    浏览器管理器 - 负责浏览器生命周期管理
    
    ChromeDriver 版本: 145 (与 Chrome 145 版本适配)
    驱动路径: ./.chromedriver_cache/chromedriver-145
    """
    
    # ChromeDriver 配置
    CHROMEDRIVER_VERSION = "145"
    CHROMEDRIVER_CACHE_DIR = ".chromedriver_cache"
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.driver = None
        self.crashed_count = 0
        self.driver_path = self._get_chromedriver_path()
    
    def _get_chromedriver_path(self) -> str:
        """
        获取 ChromeDriver 路径
        
        优先级:
        1. 项目缓存目录: ./.chromedriver_cache/chromedriver-145
        2. 用户目录: ~/Downloads/chromedriver-mac-arm64_145/chromedriver
        3. 自动下载 (undetected_chromedriver)
        """
        # 优先级1: 项目缓存目录
        cache_driver = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", "..", 
            self.CHROMEDRIVER_CACHE_DIR,
            f"chromedriver-{self.CHROMEDRIVER_VERSION}"
        )
        if os.path.exists(cache_driver) and os.access(cache_driver, os.X_OK):
            print(f"[BrowserManager] 使用缓存驱动: {cache_driver}")
            return cache_driver
        
        # 优先级2: 用户下载目录
        user_driver = os.path.expanduser(
            f"~/Downloads/chromedriver-mac-arm64_{self.CHROMEDRIVER_VERSION}/chromedriver"
        )
        if os.path.exists(user_driver) and os.access(user_driver, os.X_OK):
            print(f"[BrowserManager] 使用用户目录驱动: {user_driver}")
            return user_driver
        
        print(f"[BrowserManager] 未找到本地驱动，将使用自动下载")
        return None
    
    def _get_chrome_version(self) -> str:
        """获取本地 Chrome 版本号"""
        try:
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            result = subprocess.run(
                [chrome_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 输出格式: "Google Chrome 145.0.7632.75"
                version = result.stdout.strip().split()[-1]
                print(f"[BrowserManager] Chrome 版本: {version}")
                return version
        except Exception as e:
            print(f"[BrowserManager] 无法获取 Chrome 版本: {e}")
        
        return "145.0.0.0"  # 默认版本
    
    def _create_options(self, headless: bool = False) -> uc.ChromeOptions:
        """创建 Chrome 选项"""
        chrome_version = self._get_chrome_version()
        
        options = uc.ChromeOptions()
        
        # 窗口大小
        options.add_argument(
            f"--window-size={self.config.BROWSER_WINDOW_SIZE[0]},"
            f"{self.config.BROWSER_WINDOW_SIZE[1]}"
        )
        
        # 无头模式
        if headless:
            options.add_argument("--headless")
        
        # 基础稳定性配置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                           f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36')
        
        # 性能优化
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--js-flags=--max-old-space-size=512')
        
        # 后台运行优化
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        return options
        
    def launch(self, headless=None):
        """
        启动浏览器
        
        策略:
        1. 优先使用本地缓存的 chromedriver-145
        2. 失败后尝试自动下载匹配版本
        """
        headless = headless if headless is not None else self.config.BROWSER_HEADLESS
        options = self._create_options(headless)
        
        # 确保缓存目录存在
        os.makedirs(self.CHROMEDRIVER_CACHE_DIR, exist_ok=True)
        
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # 尝试使用本地驱动
        if self.driver_path:
            try:
                print(f"[BrowserManager] 尝试使用本地 ChromeDriver...")
                self.driver = uc.Chrome(
                    options=options,
                    use_subprocess=True,
                    driver_executable_path=self.driver_path,
                    browser_executable_path=chrome_path
                )
                self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
                self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
                self.crashed_count = 0
                print(f"[BrowserManager] 浏览器启动成功（本地驱动）")
                return self.driver
            except Exception as e:
                print(f"[BrowserManager] 本地驱动失败: {str(e)[:100]}")
        
        # 尝试自动下载
        try:
            print(f"[BrowserManager] 尝试自动下载 ChromeDriver...")
            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                browser_executable_path=chrome_path
            )
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            self.crashed_count = 0
            print(f"[BrowserManager] 浏览器启动成功（自动下载）")
            return self.driver
        except Exception as e:
            self.crashed_count += 1
            raise BrowserCrashError(f"浏览器启动失败: {e}")
    
    def is_healthy(self) -> bool:
        """检查浏览器健康状态"""
        try:
            self.driver.current_url
            return True
        except WebDriverException:
            return False
    
    def restart(self):
        """重启浏览器"""
        self.quit()
        time.sleep(2)
        return self.launch()
    
    def safe_click(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """安全点击元素"""
        for attempt in range(3):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, selector))
                )
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(0.5)
                element.click()
                return True
            except Exception as e:
                if attempt == 2:
                    # 最后尝试用 JS 点击
                    try:
                        element = self.driver.find_element(by, selector)
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except:
                        raise
                time.sleep(1)
        return False
    
    def human_like_typing(self, element, text: str):
        """模拟人类输入"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(
                self.config.TYPING_MIN_DELAY,
                self.config.TYPING_MAX_DELAY
            ))
    
    def wait_for_text(self, text, timeout=10):
        """等待文本出现"""
        start = time.time()
        while time.time() - start < timeout:
            if text in self.driver.page_source:
                return True
            time.sleep(0.5)
        raise TimeoutException(f"等待文本 '{text}' 超时")
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
```

### 3.2 邮箱服务

#### 3.2.1 HTTP 工具函数

```python
# utils/http_client.py
import urllib.request
import json
from typing import Optional, Tuple, Dict


def http_get(url: str, headers: Optional[Dict[str, str]] = None) -> Tuple[str, Dict]:
    """
    HTTP GET 请求
    
    Args:
        url: 请求URL
        headers: 请求头
        
    Returns:
        tuple: (响应体字符串, 响应头字典)
        失败返回 (-1, {})
    """
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=30) as response:
            resp_text = response.read().decode("utf-8")
            resp_headers = dict(response.getheaders())
            return resp_text, resp_headers
    except Exception as e:
        print(f"[HTTP] GET 请求失败: {url}, 错误: {e}")
        return -1, {}


def http_post(url: str, body: str, headers: Dict[str, str]) -> Tuple[str, Dict]:
    """
    HTTP POST 请求
    
    Args:
        url: 请求URL
        body: 请求体
        headers: 请求头
        
    Returns:
        tuple: (响应体字符串, 响应头字典)
    """
    try:
        data = body.encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_text = resp.read().decode("utf-8")
            resp_headers = dict(resp.headers)
            return resp_text, resp_headers
    except Exception as e:
        print(f"[HTTP] POST 请求失败: {url}, 错误: {e}")
        raise
```

#### 3.2.2 Mail.tm 服务（备用）

```python
# core/email_service.py
import random
import string
import time
import json
import re
from typing import Optional, Dict, List
from utils.http_client import http_get, http_post


class MailTMService:
    """
    mail.tm 临时邮箱服务（备用服务）
    
    提供完整的临时邮箱功能：
    1. 创建账户（随机邮箱生成）
    2. 获取 Token
    3. 获取邮件列表
    4. 获取邮件内容（独立方法）
    5. 提取验证链接
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
        """
        创建临时邮箱账户
        
        Returns:
            str: 生成的邮箱地址
        """
        domain = self.get_domain()
        
        # 生成随机用户名
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        self.email = f"{username}@{domain}"
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # 创建账户
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
        """
        获取访问 token
        
        Returns:
            str: Bearer token
        """
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
        """
        获取邮件列表
        
        Args:
            retry: 失败时是否重试（重新获取token）
            
        Returns:
            list: 邮件列表
        """
        if not self.token:
            self.get_token()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        body, _ = http_get(f"{self.BASE_URL}/messages", headers)
        
        # 如果返回错误且允许重试，尝试重新获取token
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
        """
        获取邮件内容（独立方法）
        
        Args:
            message_id: 邮件ID
            retry: 失败时是否重试
            
        Returns:
            dict: 邮件详情，包含以下字段：
                - id: 邮件ID
                - subject: 主题
                - from: 发件人信息
                - text: 纯文本内容
                - html: HTML内容（可能是字符串或列表）
                - createdAt: 创建时间
        """
        if not self.token:
            self.get_token()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        body, _ = http_get(f"{self.BASE_URL}/messages/{message_id}", headers)
        
        # 如果返回错误且允许重试，尝试重新获取token
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
    
    def extract_verification_link(self, content: str) -> Optional[str]:
        """
        从邮件内容中提取 Fireworks 验证链接
        
        Fireworks 验证链接格式：
        https://app.fireworks.ai/signup/confirm?client_id=xxx&user_name=xxx&confirmation_code=xxx
        
        Args:
            content: 邮件内容（text 或 html）
            
        Returns:
            str: 验证链接，未找到返回 None
        """
        # 匹配 Fireworks 确认链接
        pattern = r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+'
        match = re.search(pattern, content)
        if match:
            return match.group(0)
        return None
    
    def get_verification_link(self, timeout: int = 60, check_interval: int = 3) -> Optional[str]:
        """
        获取验证链接（轮询方式）
        
        流程：
        1. 获取邮件列表
        2. 对每个邮件调用 get_message_content 获取详情
        3. 合并 text 和 html 内容进行搜索
        4. 提取验证链接
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            str: 验证链接，超时返回 None
        """
        print(f"[MailTM] 开始获取验证链接，超时时间: {timeout}s...")
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < timeout:
            attempt += 1
            try:
                messages = self.get_messages()
                print(f"[MailTM] 第{attempt}轮检查，找到 {len(messages)} 封邮件")
                
                for msg in messages:
                    # 获取邮件详情（步骤2：邮件内容收取）
                    content = self.get_message_content(msg["id"])
                    
                    if not content:
                        continue
                    
                    # 合并所有内容进行搜索
                    text_content = content.get("text", "") or ""
                    html_content = content.get("html", "")
                    
                    # html 可能是字符串或列表
                    if isinstance(html_content, list):
                        html_content = " ".join(html_content)
                    elif not isinstance(html_content, str):
                        html_content = ""
                    
                    full_content = text_content + " " + html_content
                    
                    # 检查是否来自 Fireworks
                    from_addr = content.get("from", {}).get("address", "").lower()
                    subject = content.get("subject", "").lower()
                    
                    is_fireworks = (
                        "fireworks" in from_addr or 
                        "fireworks" in subject or
                        "verify" in subject
                    )
                    
                    if is_fireworks:
                        print(f"[MailTM] 找到 Fireworks 验证邮件: {content.get('subject', '')}")
                        
                        # 步骤3：提取关键链接
                        link = self.extract_verification_link(full_content)
                        if link:
                            print(f"[MailTM] 成功提取验证链接: {link[:60]}...")
                            return link
                        else:
                            print(f"[MailTM] 邮件中未找到验证链接，继续搜索...")
                
                # 等待后再次检查
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"[MailTM] 获取邮件出错: {e}")
                time.sleep(check_interval)
        
        print(f"[MailTM] 获取验证链接超时（{timeout}s）")
        return None
```

#### 3.2.3 SamfunAsia 邮箱服务

```python
class SamfunAsiaService:
    """
    SamfunAsia 临时邮箱服务（源1）
    
    API 端点: https://cloudflare_temp_email.caiql20022000.workers.dev
    
    特点:
    - 使用 JWT 认证
    - 需要生成随机名称
    - 邮件内容在 raw 字段中
    """
    
    BASE_URL = "https://cloudflare_temp_email.caiql20022000.workers.dev"
    ADMIN_AUTH = "xiaoyibao@1234"
    
    def __init__(self):
        self.email: Optional[str] = None
        self.jwt: Optional[str] = None
    
    def _generate_random_name(self) -> str:
        """生成随机用户名"""
        import random
        import string
        
        # 可选的形容词和名词组合
        adjectives = ["happy", "lucky", "sunny", "bright", "clever", "swift", "cool", "warm"]
        nouns = ["panda", "tiger", "eagle", "dolphin", "rocket", "star", "moon", "sun"]
        
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        num = random.randint(100, 999)
        
        return f"{adj}{noun}{num}"
    
    def create_account(self) -> str:
        """
        创建临时邮箱账户
        
        API: POST /admin/new_address
        请求体: {"enablePrefix": true, "name": "xxx", "domain": "samfun.asia"}
        响应: {"address": "xxx@samfun.asia", "jwt": "xxx"}
        
        Returns:
            str: 邮箱地址
        """
        import ssl
        import urllib.request
        
        name = self._generate_random_name()
        print(f"[SamfunAsia] 生成随机名称: {name}")
        
        payload = json.dumps({
            "enablePrefix": True,
            "name": name,
            "domain": "samfun.asia"
        })
        
        headers = {
            "x-admin-auth": self.ADMIN_AUTH,
            "Content-Type": "application/json"
        }
        
        # 禁用 SSL 验证（兼容某些环境）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            f"{self.BASE_URL}/admin/new_address",
            data=payload.encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.email = data.get("address", "")
                self.jwt = data.get("jwt", "")
                
                if not self.email or not self.jwt:
                    raise Exception(f"创建邮箱失败，响应: {data}")
                
                print(f"[SamfunAsia] 成功创建邮箱: {self.email}")
                return self.email
        except Exception as e:
            raise Exception(f"SamfunAsia 创建邮箱失败: {e}")
    
    def get_messages(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        获取邮件列表
        
        API: GET /api/mails?limit={limit}&offset={offset}
        请求头: Authorization: Bearer {jwt}
        
        Returns:
            list: 邮件列表，每项包含 raw 字段（原始邮件内容）
        """
        import ssl
        import urllib.request
        
        if not self.jwt:
            raise Exception("JWT 未初始化")
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        headers = {
            "Authorization": f"Bearer {self.jwt}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}/api/mails?limit={limit}&offset={offset}"
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                # 响应可能是列表或包含 results 的字典
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "results" in data:
                    return data["results"]
                elif isinstance(data, dict) and "data" in data:
                    return data["data"]
                else:
                    return []
        except Exception as e:
            print(f"[SamfunAsia] 获取邮件失败: {e}")
            return []
    
    def extract_verification_link(self, raw_content: str) -> Optional[str]:
        """
        从原始邮件内容中提取 Fireworks 验证链接
        
        Args:
            raw_content: 邮件 raw 字段内容
            
        Returns:
            str: 验证链接，未找到返回 None
        """
        if not raw_content:
            return None
        
        # Fireworks 链接格式
        pattern = r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+'
        match = re.search(pattern, raw_content, re.IGNORECASE)
        
        if match:
            return match.group(0)
        return None
    
    def get_verification_link(self, timeout: int = 60, check_interval: int = 3) -> Optional[str]:
        """
        获取 Fireworks 验证链接
        
        流程:
        1. 轮询获取邮件列表
        2. 检查每封邮件的 raw 内容
        3. 从 raw 中提取 Fireworks 验证链接
        
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
                    # 获取原始邮件内容
                    raw_content = msg.get("raw", "") if isinstance(msg, dict) else str(msg)
                    
                    # 检查是否来自 Fireworks
                    is_fireworks = "fireworks" in raw_content.lower()
                    
                    if is_fireworks:
                        print(f"[SamfunAsia] 找到 Fireworks 邮件")
                        
                        # 提取验证链接
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
```

#### 3.2.4 主邮箱服务（可选增强）

```python
class PrimaryEmailService:
    """
    主邮箱服务（如 chatgpt.org.uk 或其他自定义 API）
    
    服务格式要求：
    - 生成邮箱: GET /api/generate-email -> { "data": { "email": "xxx" } }
    - 获取邮件: GET /api/emails?email=xxx -> { "data": { "emails": [...] } }
    """
    
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.email: Optional[str] = None
        self.headers = {"User-Agent": "Mozilla/5.0"}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def create_email(self) -> str:
        """创建临时邮箱"""
        body, _ = http_get(f"{self.base_url}/api/generate-email", self.headers)
        
        if isinstance(body, str):
            data = json.loads(body)
            if "data" in data and "email" in data["data"]:
                self.email = data["data"]["email"]
                return self.email
        
        raise Exception("主邮箱服务创建邮箱失败")
    
    def get_emails(self) -> List[Dict]:
        """获取邮件列表"""
        body, _ = http_get(
            f"{self.base_url}/api/emails?email={self.email}",
            self.headers
        )
        
        if isinstance(body, str):
            data = json.loads(body)
            return data.get("data", {}).get("emails", [])
        return []
    
    def get_verification_link(self, timeout: int = 60) -> Optional[str]:
        """获取 Fireworks 验证链接"""
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
```

#### 3.2.5 邮箱服务管理器（多源自动切换）

```python
from enum import Enum
from dataclasses import dataclass


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


class EmailServiceManager:
    """
    邮箱服务管理器 - 多源自动切换
    
    优先级:
    1. SamfunAsia (samfun.asia)
    2. Primary (如 chatgpt.org.uk)
    3. Mail.tm (备用)
    
    自动切换机制:
    - 每个源注册独立 API
    - 服务失效时自动切换到下一个 standby 源
    - 记录失败次数，避免反复尝试已失效源
    """
    
    def __init__(self):
        self.service_order = [
            EmailServiceType.SAMFUN_ASIA,
            EmailServiceType.PRIMARY,
            EmailServiceType.MAIL_TM
        ]
        self.current_service: Optional[EmailServiceType] = None
        self.service_instance: Optional[Any] = None
        self.failed_services: set = set()  # 记录已失败的服务
        
        # 配置
        self.primary_url: str = ""          # 主服务 URL
        self.primary_key: str = ""          # 主服务 API Key
    
    def set_primary_config(self, url: str, api_key: str = ""):
        """设置主服务配置"""
        self.primary_url = url
        self.primary_key = api_key
    
    def _create_service(self, service_type: EmailServiceType) -> Optional[Any]:
        """
        创建指定类型的服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例，失败返回 None
        """
        try:
            if service_type == EmailServiceType.SAMFUN_ASIA:
                return SamfunAsiaService()
            elif service_type == EmailServiceType.PRIMARY:
                if self.primary_url:
                    return PrimaryEmailService(self.primary_url, self.primary_key)
                return None
            elif service_type == EmailServiceType.MAIL_TM:
                return MailTMService()
            return None
        except Exception as e:
            print(f"[EmailManager] 创建 {service_type.value} 服务失败: {e}")
            return None
    
    def _test_service(self, service_type: EmailServiceType) -> bool:
        """
        测试服务是否可用
        
        Args:
            service_type: 服务类型
            
        Returns:
            bool: 可用返回 True
        """
        if service_type in self.failed_services:
            return False
        
        try:
            if service_type == EmailServiceType.SAMFUN_ASIA:
                service = SamfunAsiaService()
                # 只测试 API 是否可达
                import ssl
                import urllib.request
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(
                    service.BASE_URL,
                    method="HEAD"
                )
                urllib.request.urlopen(req, context=ssl_context, timeout=10)
                return True
                
            elif service_type == EmailServiceType.PRIMARY:
                if not self.primary_url:
                    return False
                body, _ = http_get(
                    f"{self.primary_url}/api/generate-email",
                    {"X-API-Key": self.primary_key, "User-Agent": "Mozilla/5.0"}
                )
                if isinstance(body, str):
                    data = json.loads(body)
                    return "data" in data and "email" in data["data"]
                return False
                
            elif service_type == EmailServiceType.MAIL_TM:
                service = MailTMService()
                service.get_domain()
                return True
                
        except Exception as e:
            print(f"[EmailManager] {service_type.value} 测试失败: {e}")
            self.failed_services.add(service_type)
        
        return False
    
    def create_email(self) -> EmailServiceResult:
        """
        创建临时邮箱（自动选择可用源）
        
        按优先级尝试各个源，直到成功或全部失败
        
        Returns:
            EmailServiceResult: 包含邮箱、服务类型、实例、登录链接
            
        Raises:
            Exception: 所有源都失败时抛出
        """
        for service_type in self.service_order:
            if service_type in self.failed_services:
                print(f"[EmailManager] 跳过已失败的源: {service_type.value}")
                continue
            
            print(f"[EmailManager] 尝试使用 {service_type.value}...")
            
            # 创建服务实例
            service = self._create_service(service_type)
            if not service:
                self.failed_services.add(service_type)
                continue
            
            # 尝试创建邮箱
            try:
                if service_type == EmailServiceType.SAMFUN_ASIA:
                    email = service.create_account()
                    result = EmailServiceResult(
                        email=email,
                        service_type=service_type,
                        service_instance=service,
                        login_url=f"https://mail.samfun.asia/"
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
        
        Args:
            timeout: 超时时间
            
        Returns:
            str: 验证链接，失败返回 None
        """
        if not self.service_instance:
            raise Exception("邮箱服务未初始化")
        
        return self.service_instance.get_verification_link(timeout)
    
    def reset_failed_services(self):
        """重置失败记录（用于下次注册时重新尝试）"""
        self.failed_services.clear()
        print("[EmailManager] 已重置失败服务记录")
```

### 3.3 注册服务

```python
# services/registration.py
import time
import random
from core.browser_manager import BrowserManager
from core.email_service import EmailServiceManager, EmailServiceResult
from utils.file_handler import FileHandler
from utils.logger import Logger


class RegistrationService:
    """
    注册服务 - 处理完整注册流程
    
    支持多源邮箱服务自动切换
    """
    
    def __init__(self, browser_manager: BrowserManager, email_manager: EmailServiceManager):
        self.browser = browser_manager
        self.email_manager = email_manager
        self.logger = Logger()
        self.file_handler = FileHandler()
        self.current_email_result: Optional[EmailServiceResult] = None
    
    def generate_password(self) -> str:
        """生成符合规范的密码"""
        # 至少8字符，包含大小写、数字、特殊字符
        lower = random.choice(string.ascii_lowercase)
        upper = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        special = random.choice("!@#$%^&*")
        
        rest = ''.join(random.choices(
            string.ascii_letters + string.digits + "!@#$%^&*",
            k=12
        ))
        
        password = lower + upper + digit + special + rest
        return ''.join(random.sample(password, len(password)))
    
    def register(self) -> dict:
        """
        执行完整注册流程
        
        邮箱服务自动切换逻辑：
        - 优先使用 SamfunAsia (samfun.asia)
        - 失败后自动切换到 Primary 服务
        - 最后使用 Mail.tm 作为备用
        """
        result = {
            "success": False,
            "email": None,
            "password": None,
            "api_key": None,
            "error": None,
            "service_type": None  # 记录使用的邮箱服务类型
        }
        
        try:
            # 1. 创建临时邮箱（多源自动切换）
            self.logger.info("创建临时邮箱（多源自动切换）...")
            email_result = self.email_manager.create_email()
            self.current_email_result = email_result
            
            email = email_result.email
            result["email"] = email
            result["service_type"] = email_result.service_type.value
            self.logger.info(f"邮箱: {email} (源: {email_result.service_type.value})")
            self.logger.info(f"邮箱登录: {email_result.login_url}")
            
            # 2. 访问注册页面
            driver = self.browser.driver
            driver.get("https://app.fireworks.ai/signup")
            time.sleep(2)
            
            # 3. 输入邮箱
            email_input = driver.find_element(By.CSS_SELECTOR, "#email-display")
            self.browser.human_like_typing(email_input, email)
            time.sleep(0.5)
            
            # 4. 点击 Next
            self.browser.safe_click("button[type='submit']")
            time.sleep(3)
            
            # 5. 输入密码
            password = self.generate_password()
            result["password"] = password
            
            pwd_input = driver.find_element(By.CSS_SELECTOR, "#password")
            self.browser.human_like_typing(pwd_input, password)
            time.sleep(0.5)
            
            confirm_input = driver.find_element(By.CSS_SELECTOR, "#confirm-password")
            self.browser.human_like_typing(confirm_input, password)
            time.sleep(0.5)
            
            # 6. 提交注册
            self.browser.safe_click("button[type='submit']")
            
            # 7. 等待验证邮件提示
            self.browser.wait_for_text("verification email has been sent", timeout=10)
            self.logger.info("等待验证邮件...")
            
            # 8. 获取验证链接（使用创建邮箱时的同一服务）
            verification_link = self.email_manager.get_verification_link(timeout=60)
            if not verification_link:
                raise Exception("获取验证链接失败")
            
            self.logger.info(f"验证链接: {verification_link[:50]}...")
            
            # 9. 访问验证链接
            driver.get(verification_link)
            time.sleep(3)
            
            # 10. 点击 Continue
            self.browser.safe_click("button:has-text('Continue')")
            time.sleep(3)
            
            self.logger.info("注册成功！")
            result["success"] = True
            
            # 保存结果
            self.file_handler.save_account(result)
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"注册失败: {e}")
        finally:
            # 重置邮箱服务失败记录（为下次注册做准备）
            if self.email_manager:
                self.email_manager.reset_failed_services()
        
        return result
```

### 3.4 入门引导服务（问卷）

```python
# services/onboarding.py
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OnboardingService:
    """入门引导服务 - 处理问卷和 $5 奖励领取"""
    
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.logger = Logger()
        
        # 问卷选项
        self.goals_options = [
            "Prototype with open models",
            "Flexible capacity for experimentation",
            "Flexible capacity for production",
            "Faster speeds or lower costs",
            "Fine-tune models for quality",
            "High reliability inference for production",
            "Migrate from closed to open models",
            "Migrate from self-hosting to third-party",
            "Other"
        ]
        
        self.use_cases_options = [
            "Code Assistance",
            "Conversational AI",
            "Agentic AI",
            "Search",
            "Multimedia RAG",
            "Other"
        ]
    
    def generate_name(self) -> tuple:
        """生成随机姓名"""
        first_names = ["John", "Michael", "David", "James", "Robert", 
                       "William", "Mary", "Patricia", "Jennifer", "Linda"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                      "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        return random.choice(first_names), random.choice(last_names)
    
    def complete_onboarding(self) -> dict:
        """
        完成入门引导和问卷
        
        ⚠️ 重要：必须完成问卷才能领取 $5 奖励，不要点击 Skip！
        """
        result = {
            "onboarding_completed": False,
            "credits_claimed": False,
            "error": None
        }
        
        try:
            driver = self.browser.driver
            
            # 1. 等待入门引导页面
            self.browser.wait_for_text("Welcome to Fireworks", timeout=15)
            self.logger.info("进入入门引导页面...")
            
            # 2. 填写姓名
            first_name, last_name = self.generate_name()
            
            first_input = driver.find_element(By.CSS_SELECTOR, 
                'input[placeholder="First Name"]')
            self.browser.human_like_typing(first_input, first_name)
            time.sleep(0.5)
            
            last_input = driver.find_element(By.CSS_SELECTOR,
                'input[placeholder="Last Name"]')
            self.browser.human_like_typing(last_input, last_name)
            time.sleep(0.5)
            
            # 3. 勾选同意条款
            checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
            checkbox.click()
            time.sleep(0.5)
            
            # 4. 点击 Continue
            self.browser.safe_click('button:has-text("Continue")')
            time.sleep(3)
            
            # 5. 等待问卷页面
            self.browser.wait_for_text("Want free $5 credit", timeout=15)
            self.logger.info("进入问卷页面，开始填写...")
            
            # 6. 随机选择目标选项（2-3个）
            selected_goals = random.sample(self.goals_options, random.randint(2, 3))
            for option in selected_goals:
                try:
                    # 通过 XPath 定位选项
                    xpath = f'//label[contains(text(), "{option}")]'
                    element = driver.find_element(By.XPATH, xpath)
                    element.click()
                    self.logger.info(f"选择目标: {option}")
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"选择目标失败 {option}: {e}")
            
            # 7. 随机选择用例选项（1-2个）
            selected_use_cases = random.sample(self.use_cases_options, random.randint(1, 2))
            for option in selected_use_cases:
                try:
                    xpath = f'//label[contains(text(), "{option}")]'
                    element = driver.find_element(By.XPATH, xpath)
                    element.click()
                    self.logger.info(f"选择用例: {option}")
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"选择用例失败 {option}: {e}")
            
            # 8. 提交问卷（领取 $5）
            self.browser.safe_click('button:has-text("Submit to get $5 Credits")')
            self.logger.info("提交问卷，领取 $5 奖励...")
            time.sleep(5)
            
            # 9. 等待跳转到主页
            self.browser.wait_for_text("Fireworks AI Platform", timeout=15)
            
            result["onboarding_completed"] = True
            result["credits_claimed"] = True
            self.logger.info("入门引导完成，$5 奖励已领取！")
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"入门引导失败: {e}")
        
        return result
```

### 3.5 API Key 管理

```python
# services/api_key_manager.py
import time
import uuid
from selenium.webdriver.common.by import By

class APIKeyManager:
    """API Key 管理服务"""
    
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.logger = Logger()
    
    def create_api_key(self, key_name: str = None) -> dict:
        """
        创建 API Key
        
        ⚠️ 重要: API Key 只显示一次，必须立即保存
        """
        result = {
            "success": False,
            "key_name": None,
            "api_key": None,
            "error": None
        }
        
        if not key_name:
            key_name = f"auto-gen-{uuid.uuid4().hex[:8]}"
        result["key_name"] = key_name
        
        try:
            driver = self.browser.driver
            
            # 1. 访问 API Keys 页面
            driver.get("https://app.fireworks.ai/settings/users/api-keys")
            time.sleep(3)
            
            # 2. 点击 Create API Key
            self.browser.safe_click('button:has-text("Create API Key")')
            time.sleep(2)
            
            # 3. 选择 API Key 类型
            self.browser.safe_click('div[role="menuitem"]:has-text("API Key")')
            time.sleep(2)
            
            # 4. 输入 Key 名称
            name_input = driver.find_element(By.CSS_SELECTOR, 
                'input[placeholder*="name" i]')
            self.browser.human_like_typing(name_input, key_name)
            time.sleep(0.5)
            
            # 5. 点击 Generate Key
            self.browser.safe_click('button:has-text("Generate Key")')
            time.sleep(2)
            
            # 6. 捕获 API Key（关键！只显示一次）
            self.browser.wait_for_text("Copy your API Key", timeout=10)
            
            # 从页面提取 API Key
            api_key_element = driver.find_element(By.XPATH,
                '//div[contains(text(), "fw_")]')
            api_key = api_key_element.text.strip()
            
            if not api_key.startswith("fw_"):
                raise ValueError(f"Invalid API Key format: {api_key}")
            
            result["api_key"] = api_key
            self.logger.info(f"API Key 生成成功: {api_key[:10]}...")
            
            # 7. 点击复制
            self.browser.safe_click('button:has-text("Copy to clipboard")')
            time.sleep(1)
            
            # 8. 关闭弹窗
            self.browser.safe_click('button:has-text("Close")')
            
            result["success"] = True
            self.logger.info("API Key 创建完成！")
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"创建 API Key 失败: {e}")
        
        return result
```

### 3.6 文件处理器（增量写入）

```python
# utils/file_handler.py
import os
from datetime import datetime

class FileHandler:
    """文件处理器 - 负责结果文件的增量写入"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名 fireworks_YYYYMMDD.txt
        today = datetime.now().strftime("%Y%m%d")
        self.results_file = os.path.join(output_dir, f"fireworks_{today}.txt")
    
    def save_account(self, data: dict):
        """保存账号信息（增量写入）"""
        # 构建输出内容
        lines = [
            "",
            "  项目         验证结果",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  邮箱         {data.get('email', 'N/A')}",
            f"  密码         {data.get('password', 'N/A')}",
            f"  API Key      {data.get('api_key', 'N/A')}",
            f"  Account ID   {data.get('account_id', 'N/A')}",
            "",
            f"  注册时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        
        content = "\n".join(lines)
        
        # 追加写入文件
        mode = "a" if os.path.exists(self.results_file) else "w"
        with open(self.results_file, mode, encoding="utf-8") as f:
            if mode == "w":
                # 首次写入添加标题
                f.write("Fireworks AI 账号注册结果\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
            f.write(content + "\n")
        
        print(f"[FileHandler] 结果已保存到: {self.results_file}")
```

### 3.7 主入口

```python
# main.py
import argparse
import time
import sys
from core.browser_manager import BrowserManager
from core.email_service import EmailServiceManager
from services.registration import RegistrationService
from services.onboarding import OnboardingService
from services.api_key_manager import APIKeyManager
from utils.logger import Logger

def main():
    parser = argparse.ArgumentParser(description="Fireworks AI 自动注册工具")
    parser.add_argument("-n", "--count", type=int, default=1, help="注册账号数量")
    parser.add_argument("--retry", type=int, default=3, help="失败重试次数")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("--skip-onboarding", action="store_true", help="跳进入门引导")
    parser.add_argument("--skip-apikey", action="store_true", help="跳过 API Key 创建")
    # 可选：配置主邮箱服务
    parser.add_argument("--primary-url", type=str, default="", help="主邮箱服务URL")
    parser.add_argument("--primary-key", type=str, default="", help="主邮箱服务API Key")
    
    args = parser.parse_args()
    
    logger = Logger()
    logger.info(f"开始注册 {args.count} 个账号...")
    logger.info("邮箱服务优先级: SamfunAsia -> Primary -> Mail.tm")
    
    success_count = 0
    fail_count = 0
    
    for i in range(args.count):
        logger.info(f"\n{'='*50}")
        logger.info(f"开始注册第 {i+1}/{args.count} 个账号...")
        logger.info(f"{'='*50}\n")
        
        browser = None
        retry_count = 0
        
        while retry_count < args.retry:
            try:
                # 1. 启动浏览器（使用 ChromeDriver 145）
                browser_mgr = BrowserManager()
                browser = browser_mgr.launch(headless=args.headless)
                
                # 2. 创建邮箱服务管理器（多源自动切换）
                email_manager = EmailServiceManager()
                
                # 配置主服务（如果提供了）
                if args.primary_url:
                    email_manager.set_primary_config(args.primary_url, args.primary_key)
                    logger.info(f"已配置主邮箱服务: {args.primary_url}")
                
                # 3. 注册（内部自动切换邮箱源）
                reg_service = RegistrationService(browser_mgr, email_manager)
                reg_result = reg_service.register()
                
                if not reg_result["success"]:
                    raise Exception(reg_result.get("error", "注册失败"))
                
                # 显示使用的邮箱服务类型
                service_type = reg_result.get("service_type", "unknown")
                logger.info(f"使用邮箱服务: {service_type}")
                
                # 4. 入门引导（问卷）
                if not args.skip_onboarding:
                    onboarding_service = OnboardingService(browser_mgr)
                    onboarding_result = onboarding_service.complete_onboarding()
                    
                    if not onboarding_result["onboarding_completed"]:
                        logger.warning("入门引导未完成，但继续执行...")
                
                # 5. 创建 API Key
                if not args.skip_apikey:
                    api_key_mgr = APIKeyManager(browser_mgr)
                    api_result = api_key_mgr.create_api_key()
                    
                    if api_result["success"]:
                        reg_result["api_key"] = api_result["api_key"]
                        reg_result["account_id"] = "见上文"  # 可从页面获取
                
                # 保存最终结果
                from utils.file_handler import FileHandler
                file_handler = FileHandler()
                file_handler.save_account(reg_result)
                
                success_count += 1
                logger.info(f"✅ 第 {i+1} 个账号注册成功！")
                break  # 成功，跳出重试循环
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ 第 {i+1} 个账号注册失败 (尝试 {retry_count}/{args.retry}): {e}")
                
                if browser:
                    try:
                        browser.quit()
                    except:
                        pass
                
                if retry_count < args.retry:
                    wait_time = retry_count * 2
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    fail_count += 1
        
        # 账号间延时
        if i < args.count - 1:
            logger.info(f"等待 15 秒后继续下一个账号...")
            time.sleep(15)
    
    # 总结
    logger.info(f"\n{'='*50}")
    logger.info("注册完成！")
    logger.info(f"成功: {success_count} 个")
    logger.info(f"失败: {fail_count} 个")
    logger.info(f"{'='*50}")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 4. 测试方案

### 4.1 单元测试

```python
# tests/test_flows.py
import pytest
import time
from core.browser_manager import BrowserManager
from core.email_service import MailTMService

class TestRegistration:
    """注册流程测试"""
    
    def test_password_generation(self):
        """测试密码生成器"""
        from services.registration import RegistrationService
        
        service = RegistrationService(None, None)
        password = service.generate_password()
        
        assert len(password) >= 8
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*" for c in password)
    
    def test_email_service(self):
        """测试邮箱服务"""
        service = MailTMService()
        email = service.create_account()
        
        assert email
        assert "@" in email
        assert service.password
    
    def test_browser_launch(self):
        """测试浏览器启动"""
        browser = BrowserManager()
        driver = browser.launch(headless=True)
        
        assert driver is not None
        driver.get("https://www.google.com")
        assert "google" in driver.current_url
        
        browser.quit()

class TestOnboarding:
    """入门引导测试"""
    
    def test_name_generation(self):
        """测试姓名生成"""
        from services.onboarding import OnboardingService
        
        service = OnboardingService(None)
        first, last = service.generate_name()
        
        assert first
        assert last
        assert first[0].isupper()
        assert last[0].isupper()
    
    def test_questionnaire_options(self):
        """测试问卷选项"""
        from services.onboarding import OnboardingService
        
        service = OnboardingService(None)
        
        # 测试随机选择
        selected = random.sample(service.goals_options, 2)
        assert len(selected) == 2
        assert all(opt in service.goals_options for opt in selected)
```

### 4.2 集成测试

```bash
# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_flows.py::TestRegistration -v
```

---

## 5. Bug 处理参考

### 5.1 已知问题与解决方案

| Bug 描述 | 原因 | 解决方案 | 参考代码 |
|---------|------|---------|---------|
| 浏览器崩溃 | 内存不足/驱动问题 | 健康检查 + 自动重启 | `browser_manager.is_healthy()` |
| 元素定位失败 | 页面加载延迟 | 显式等待 + 多重定位 | `safe_click()` |
| 验证码获取超时 | 邮件延迟 | 轮询 + 重试机制 | `get_verification_link()` |
| API Key 捕获失败 | 弹窗未加载 | 等待文本出现 | `wait_for_text("Copy your API Key")` |
| 问卷提交失败 | 选项未正确勾选 | XPath 定位 + 点击验证 | 见 `onboarding.py` |
| SSL 证书错误 | 证书验证失败 | 忽略证书验证 | `ssl._create_unverified_context()` |
| 密码不符合规范 | 缺少字符类型 | 强制包含各类字符 | `generate_password()` |

### 5.2 调试技巧

```python
# 1. 截图保存
 driver.save_screenshot(f"debug_{int(time.time())}.png")

# 2. 页面源码保存
with open("debug_page.html", "w") as f:
    f.write(driver.page_source)

# 3. 日志级别调整
logger.set_level("DEBUG")

# 4. 慢速模式（便于观察）
TYPING_MIN_DELAY = 0.2
TYPING_MAX_DELAY = 0.5
```

### 5.3 常见异常处理

```python
try:
    # 操作代码
except TimeoutException:
    # 超时处理：截图、记录、重试
    driver.save_screenshot("timeout.png")
    raise
except WebDriverException:
    # 浏览器异常：重启浏览器
    browser.restart()
except Exception as e:
    # 其他异常：记录并抛出
    logger.error(f"未知错误: {e}")
    raise
```

---

## 6. 输出文件格式

### 6.1 文件格式规范

文件名格式：`fireworks_YYYYMMDD.txt`

内容格式：
```
Fireworks AI 账号注册结果
生成时间: 2026-02-28 16:53:00
==================================================

  项目         验证结果
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  邮箱         afeja25e@samfun.asia
  密码         Xiaoyibao@1234
  API Key      fw_834YLMBj5jZYm2Z6E3KWTg
  Account ID   afeja25e-dncn0biea67
  
  注册时间: 2026-02-28 16:53:00
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  项目         验证结果
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  邮箱         xxx@example.com
  密码         Xxxxxx@1234
  API Key      fw_xxxxxxxxx
  Account ID   xxxxxx
  
  注册时间: 2026-02-28 17:00:00
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 增量写入代码

```python
def append_result(self, data: dict):
    """增量写入结果"""
    lines = [
        "",
        "  项目         验证结果",
        "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  邮箱         {data.get('email', 'N/A')}",
        f"  密码         {data.get('password', 'N/A')}",
        f"  API Key      {data.get('api_key', 'N/A')}",
        f"  Account ID   {data.get('account_id', 'N/A')}",
        "",
        f"  注册时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    
    mode = "a" if os.path.exists(self.results_file) else "w"
    with open(self.results_file, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("Fireworks AI 账号注册结果\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
        f.write("\n".join(lines) + "\n")
```

---

## 7. 运行命令

```bash
# 基础使用
python main.py

# 注册 5 个账号
python main.py -n 5

# 注册 3 个，失败重试 5 次
python main.py -n 3 --retry 5

# 无头模式（后台运行）
python main.py -n 10 --headless

# 仅注册，不创建 API Key
python main.py --skip-apikey

# 调试模式（显示浏览器）
python main.py --debug
```

---

**文档版本**: v1.0  
**最后更新**: 2026-02-28  
**作者**: AI Assistant  
**用途**: 技术研究学习
