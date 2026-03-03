"""
配置管理模块
"""
import os


class Config:
    """应用配置类"""
    
    # 浏览器配置
    BROWSER_HEADLESS = False
    BROWSER_WINDOW_SIZE = (1920, 1080)
    CHROMEDRIVER_CACHE = ".chromedriver_cache"
    
    # 超时配置
    PAGE_LOAD_TIMEOUT = 60      # 页面加载超时增加到60秒
    IMPLICIT_WAIT = 10
    VERIFY_EMAIL_TIMEOUT = 60
    
    # 重试配置
    MAX_RETRY = 3
    RETRY_DELAY = 2
    
    # 人机模拟延迟
    TYPING_MIN_DELAY = 0.05
    TYPING_MAX_DELAY = 0.15
    CLICK_DELAY = 0.5
    BETWEEN_ACCOUNTS = 30  # 账号间间隔，避免频繁注册
    
    # 输出配置
    OUTPUT_DIR = "output"
    RESULTS_FILE = "fireworks_{date}.txt"
    
    # SamfunAsia 配置
    SAMFUN_ASIA_BASE = "https://cloudflare_temp_email.caiql20022000.workers.dev"
    SAMFUN_ASIA_ADMIN_AUTH = "xiaoyibao@1234"
    
    # Mail.tm 配置
    MAIL_TM_BASE = "https://api.mail.tm"


class URLs:
    """URL 常量"""
    BASE = "https://app.fireworks.ai"
    SIGNUP = f"{BASE}/signup"
    LOGIN = f"{BASE}/login"
    EMAIL_LOGIN = f"{BASE}/login/email"
    API_KEYS = f"{BASE}/settings/users/api-keys"
    ONBOARDING = f"{BASE}/onboarding"
    ACCOUNT_HOME = f"{BASE}/account/home"
