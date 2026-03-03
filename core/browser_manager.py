"""
浏览器管理器 - 负责浏览器生命周期管理
ChromeDriver 版本: 145 (与 Chrome 145 版本适配)
"""
import os
import time
import random
import subprocess
from typing import Optional

# Selenium 导入
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[警告] Selenium/undetected-chromedriver 未安装，浏览器功能不可用")

# 导入配置
try:
    from utils.config import Config
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.config import Config


class BrowserCrashError(Exception):
    """浏览器崩溃错误"""
    pass


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
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium/undetected-chromedriver 未安装")
        
        self.config = config or Config()
        self.driver = None
        self.crashed_count = 0
        self.driver_path = self._get_chromedriver_path()
    
    def _get_chromedriver_path(self) -> Optional[str]:
        """
        获取 ChromeDriver 路径
        
        优先级:
        1. 项目缓存目录: ./.chromedriver_cache/chromedriver-145
        2. 用户目录: ~/Downloads/chromedriver-mac-arm64_145/chromedriver
        3. 自动下载 (undetected_chromedriver)
        """
        # 优先级1: 项目缓存目录
        cache_driver = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
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
                version = result.stdout.strip().split()[-1]
                print(f"[BrowserManager] Chrome 版本: {version}")
                return version
        except Exception as e:
            print(f"[BrowserManager] 无法获取 Chrome 版本: {e}")
        
        return "145.0.0.0"  # 默认版本
    
    def _create_options(self, headless: bool = False) -> 'uc.ChromeOptions':
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
        
        # 禁用代理（解决 Bad Gateway 问题）
        options.add_argument('--no-proxy-server')
        options.add_argument('--proxy-bypass-list=*')
        
        # 解决页面加载超时问题
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--force-device-scale-factor=1')
        options.add_argument('--start-maximized')
        
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
        
        # 页面加载优化 - 使用 eager 策略减少超时
        options.page_load_strategy = 'eager'  # 等待 DOM 加载完成，不等待资源
        
        # 修复 renderer 超时问题
        options.add_argument('--disable-features=NetworkService,NetworkServiceInProcess')
        options.add_argument('--disable-hang-monitor')
        options.add_argument('--ipc-connection-timeout=30')
        
        return options
    
    def launch(self, headless=None):
        """
        启动浏览器
        
        策略:
        1. 优先使用本地缓存的 chromedriver-145
        2. 失败后尝试自动下载匹配版本
        
        注意: 每次尝试都需要创建新的 ChromeOptions，不能重用
        """
        headless = headless if headless is not None else self.config.BROWSER_HEADLESS
        
        # 禁用代理环境变量（避免 Bad Gateway 错误）
        import os
        original_env = {}
        for key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
            if key in os.environ:
                original_env[key] = os.environ.pop(key)
        
        # 确保缓存目录存在
        os.makedirs(self.CHROMEDRIVER_CACHE_DIR, exist_ok=True)
        
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # 尝试使用本地驱动
        if self.driver_path:
            try:
                print(f"[BrowserManager] 尝试使用本地 ChromeDriver...")
                # 每次尝试都需要创建新的 options
                options = self._create_options(headless)
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
            # 每次尝试都需要创建新的 options
            options = self._create_options(headless)
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
        finally:
            # 恢复环境变量
            for key, value in original_env.items():
                os.environ[key] = value
    
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
    
    def safe_click(self, selector, by=None, timeout=10):
        """安全点击元素"""
        if by is None:
            if not SELENIUM_AVAILABLE:
                raise ImportError("Selenium 未安装")
            by = By.CSS_SELECTOR
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
    
    def wait_for_url(self, url_part, timeout=10):
        """等待 URL 包含指定部分"""
        start = time.time()
        while time.time() - start < timeout:
            if url_part in self.driver.current_url:
                return True
            time.sleep(0.5)
        raise TimeoutException(f"等待 URL 包含 '{url_part}' 超时")
    
    def find_element_safely(self, selectors: list, timeout=10):
        """
        安全查找元素，尝试多个选择器
        
        Args:
            selectors: [(by, selector), ...] 列表
            timeout: 每个选择器的超时时间
            
        Returns:
            WebElement 或 None
        """
        for by, selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                return element
            except:
                continue
        return None
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None


# 测试代码
if __name__ == "__main__":
    print("测试浏览器管理模块...")
    
    try:
        browser = BrowserManager()
        driver = browser.launch(headless=True)
        
        # 测试访问页面
        driver.get("https://www.google.com")
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        
        browser.quit()
        print("测试成功!")
    except Exception as e:
        print(f"测试失败: {e}")
