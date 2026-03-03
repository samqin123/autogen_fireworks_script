"""
注册服务模块 - 处理完整注册流程
支持多源邮箱服务自动切换
"""
import time
import random
import string
from typing import Optional

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    By = None
    WebDriverWait = None
    EC = None

try:
    from core.browser_manager import BrowserManager
    from core.email_service import EmailServiceManager, EmailServiceResult
    from services.popup_handler import PopupHandler, PopupType
    from utils.file_handler import FileHandler
    from utils.logger import Logger
    from utils.config import URLs
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.browser_manager import BrowserManager
    from core.email_service import EmailServiceManager, EmailServiceResult
    from services.popup_handler import PopupHandler, PopupType
    from utils.file_handler import FileHandler
    from utils.logger import Logger
    from utils.config import URLs


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
        
        Returns:
            dict: {
                "success": bool,
                "email": str,
                "password": str,
                "api_key": str,
                "error": str,
                "service_type": str
            }
        """
        result = {
            "success": False,
            "email": None,
            "password": None,
            "api_key": None,
            "error": None,
            "service_type": None,
            "account_id": None
        }
        
        try:
            # 1. 创建临时邮箱（多源自动切换）
            self.logger.info("=" * 50)
            self.logger.info("步骤1: 创建临时邮箱（多源自动切换）...")
            email_result = self.email_manager.create_email()
            self.current_email_result = email_result
            
            email = email_result.email
            result["email"] = email
            result["service_type"] = email_result.service_type.value
            self.logger.info(f"邮箱: {email}")
            self.logger.info(f"邮箱服务: {email_result.service_type.value}")
            
            # 2. 访问注册页面
            self.logger.info("步骤2: 访问注册页面...")
            driver = self.browser.driver
            
            # 设置页面加载超时时间较短，超时后停止加载继续执行
            driver.set_page_load_timeout(20)
            
            for page_attempt in range(3):
                try:
                    driver.get(URLs.SIGNUP)
                    self.logger.info("页面加载成功")
                    break
                except Exception as e:
                    error_msg = str(e).lower()
                    if ("timeout" in error_msg or "renderer" in error_msg) and page_attempt < 2:
                        self.logger.warning(f"页面加载超时，停止加载并继续...")
                        # 停止页面加载
                        try:
                            driver.execute_script("window.stop();")
                        except:
                            pass
                        time.sleep(2)
                        # 如果URL已改变，说明页面基本加载完成
                        if "fireworks" in driver.current_url:
                            self.logger.info("页面URL已加载，继续执行")
                            break
                    else:
                        raise
            
            # 恢复默认超时设置
            driver.set_page_load_timeout(self.browser.config.PAGE_LOAD_TIMEOUT)
            time.sleep(2)
            
            # 3. 输入邮箱
            self.logger.info("步骤3: 输入邮箱...")
            
            # 等待页面完全加载 - 减少等待时间
            time.sleep(3)
            
            # 调试：截图查看页面状态
            try:
                driver.save_screenshot("debug_step3_page.png")
                self.logger.info("已保存页面截图: debug_step3_page.png")
            except:
                pass
            
            # 多种方式定位邮箱输入框（根据诊断结果优化）
            email_input = None
            selectors = [
                (By.CSS_SELECTOR, 'input[type="email"]'),      # 最可靠的定位方式
                (By.CSS_SELECTOR, '#email-display'),            # ID 选择器
                (By.CSS_SELECTOR, 'input[name="email"]'),
                (By.XPATH, '//input[@placeholder="Email"]'),
            ]
            
            for by, selector in selectors:
                try:
                    email_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    self.logger.info(f"找到邮箱输入框: {selector}")
                    break
                except Exception as e:
                    self.logger.debug(f"定位失败 {selector}: {e}")
                    continue
            
            if not email_input:
                raise Exception("无法找到邮箱输入框")
            
            # 输入邮箱
            try:
                email_input.clear()
                email_input.send_keys(email)
                time.sleep(0.5)
                
                # 验证输入
                actual_value = email_input.get_attribute('value')
                if actual_value == email:
                    self.logger.info(f"✅ 邮箱输入成功: {email}")
                else:
                    # 使用 JavaScript 直接设置值
                    driver.execute_script(f"arguments[0].value = '{email}';", email_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", email_input)
                    self.logger.info(f"✅ 邮箱输入成功 (JavaScript): {email}")
            except Exception as e:
                self.logger.error(f"邮箱输入失败: {e}")
                raise
            
            # 4. 点击 Next
            self.logger.info("步骤4: 点击 Next...")
            
            # 多种方式定位 Next 按钮
            next_clicked = False
            next_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Next')]"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
                (By.CSS_SELECTOR, "button[class*='submit']"),
            ]
            
            for by, selector in next_selectors:
                try:
                    btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    driver.execute_script("arguments[0].click();", btn)
                    self.logger.info(f"点击按钮: {selector}")
                    next_clicked = True
                    break
                except:
                    continue
            
            if not next_clicked:
                raise Exception("无法找到 Next 按钮")
            
            time.sleep(3)
            
            # 5. 输入密码
            self.logger.info("步骤5: 输入密码...")
            password = self.generate_password()
            result["password"] = password
            self.logger.info(f"生成密码: {password[:3]}***{password[-3:]}")
            
            time.sleep(2)  # 等待密码页面加载
            
            # 定位密码输入框
            pwd_input = None
            pwd_selectors = [
                (By.CSS_SELECTOR, "#password"),
                (By.CSS_SELECTOR, 'input[name="password"]'),
                (By.CSS_SELECTOR, 'input[type="password"]'),
            ]
            
            for by, selector in pwd_selectors:
                try:
                    pwd_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except:
                    continue
            
            if not pwd_input:
                raise Exception("无法找到密码输入框")
            
            pwd_input.clear()
            pwd_input.send_keys(password)
            time.sleep(0.5)
            
            # 6. 确认密码
            self.logger.info("步骤6: 确认密码...")
            
            confirm_input = None
            confirm_selectors = [
                (By.CSS_SELECTOR, "#confirm-password"),
                (By.CSS_SELECTOR, 'input[name="confirmPassword"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="confirm" i]'),
            ]
            
            for by, selector in confirm_selectors:
                try:
                    confirm_input = driver.find_element(by, selector)
                    break
                except:
                    continue
            
            if not confirm_input:
                # 如果只有一个密码框，可能不需要确认
                self.logger.warning("未找到确认密码框，可能页面只需要一个密码框")
            else:
                confirm_input.clear()
                confirm_input.send_keys(password)
                time.sleep(0.5)
            
            # 7. 提交注册
            self.logger.info("步骤7: 提交注册...")
            self.browser.safe_click("button[type='submit']")
            
            # 8. 等待验证邮件提示
            self.logger.info("步骤8: 等待验证邮件提示...")
            self.browser.wait_for_text("verification email has been sent", timeout=15)
            self.logger.info("验证邮件已发送，等待邮件到达...")
            
            # 9. 获取验证链接（使用创建邮箱时的同一服务）
            self.logger.info("步骤9: 获取验证链接...")
            verification_link = self.email_manager.get_verification_link(timeout=60)
            if not verification_link:
                raise Exception("获取验证链接失败")
            
            self.logger.info(f"验证链接: {verification_link[:60]}...")
            
            # 10. 访问验证链接
            self.logger.info("步骤10: 访问验证链接...")
            driver.get(verification_link)
            time.sleep(3)
            
            # 11. 点击 Sign In（验证成功页）
            self.logger.info("步骤11: 点击 Sign In...")
            
            # 检查密码是否已设置
            if not result.get("password"):
                self.logger.error("❌ 密码未设置，无法执行登录")
                raise Exception("密码未设置")
            
            try:
                # 等待验证成功页面
                self.logger.info("等待 'Account Confirmed' 文本...")
                self.browser.wait_for_text("Account Confirmed", timeout=10)
                self.logger.info("✅ 检测到 Account Confirmed 页面")
                
                # 点击 Sign In 按钮
                self.logger.info("查找 Sign In 按钮...")
                signin_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign In")]'))
                )
                signin_btn.click()
                self.logger.info("✅ 已点击 Sign In")
                time.sleep(3)
                
                # 等待跳转到登录页
                self.logger.info("等待跳转到 /login...")
                self.browser.wait_for_url("/login", timeout=10)
                self.logger.info(f"✅ 已进入登录页: {driver.current_url}")
                
                # 12. 点击 Email Login
                self.logger.info("步骤12: 点击 Email Login...")
                email_login_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Email Login")]'))
                )
                email_login_link.click()
                self.logger.info("✅ 已点击 Email Login")
                time.sleep(3)
                
                # 等待邮箱登录表单（URL 格式: /login/email?redirectURI=%2Fsignin）
                self.logger.info("等待跳转到 /login/email...")
                try:
                    WebDriverWait(driver, 10).until(EC.url_contains("/login/email"))
                    self.logger.info(f"✅ 已进入邮箱登录页: {driver.current_url}")
                except:
                    self.logger.warning(f"URL 检测超时，当前: {driver.current_url}")
                    # 如果 URL 已经包含 login，可能已经在登录页了
                    if "/login" not in driver.current_url:
                        raise Exception("未进入登录页")
                
                # 13. 登录账号
                self.logger.info("步骤13: 登录账号...")
                self.logger.info(f"使用邮箱: {email}")
                self.logger.info(f"使用密码: {result.get('password', 'NOT SET')[:3]}***")
                
                # 等待页面加载完成
                self.logger.info("等待登录表单加载...")
                time.sleep(3)
                
                # 填写邮箱 - 使用多种定位方式确保找到
                self.logger.info("查找邮箱输入框...")
                email_input = None
                email_selectors = [
                    (By.CSS_SELECTOR, 'input[type="email"]'),
                    (By.NAME, 'email'),
                    (By.CSS_SELECTOR, 'input[placeholder*="mail" i]'),
                    (By.XPATH, '//input[@type="email"]'),
                ]
                for by, selector in email_selectors:
                    try:
                        email_input = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        self.logger.info(f"✅ 找到邮箱输入框: {selector}")
                        break
                    except:
                        continue
                
                if not email_input:
                    raise Exception("无法找到邮箱输入框")
                
                email_input.clear()
                email_input.send_keys(email)
                time.sleep(0.5)
                self.logger.info(f"✅ 已输入邮箱: {email}")
                
                # 填写密码
                self.logger.info("查找密码输入框...")
                pwd_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]'))
                )
                self.logger.info("✅ 找到密码输入框")
                pwd_input.clear()
                pwd_input.send_keys(result["password"])
                time.sleep(0.5)
                self.logger.info("✅ 已输入密码")
                
                # 点击 Next
                self.logger.info("点击 Next 登录...")
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]'))
                )
                next_btn.click()
                self.logger.info("✅ 已点击登录按钮")
                
                # 等待登录成功（跳转到 onboarding 或 home）
                self.logger.info("等待登录跳转...")
                time.sleep(3)
                
                # 检查当前 URL
                current_url = driver.current_url
                self.logger.info(f"当前 URL: {current_url}")
                
                try:
                    # 等待跳转到 onboarding（更长的超时时间）
                    WebDriverWait(driver, 20).until(
                        EC.url_contains("/onboarding")
                    )
                    self.logger.info("✅ 登录成功，进入入门引导页面")
                except:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.url_contains("/account/home")
                        )
                        self.logger.info("✅ 登录成功，进入主页")
                    except:
                        # 保存截图调试
                        try:
                            driver.save_screenshot("debug_login_failed.png")
                            self.logger.info("已保存调试截图: debug_login_failed.png")
                        except:
                            pass
                        self.logger.warning(f"⚠️ 未检测到预期跳转，当前 URL: {driver.current_url}")
                
                # 14. 处理可能的弹窗（Welcome to Fireworks 补充信息弹窗）
                self.logger.info("步骤14: 检查并处理可能的弹窗...")
                try:
                    popup_handler = PopupHandler(self.browser)
                    popup_result = popup_handler.wait_and_handle_popup(timeout=5)
                    
                    if popup_result["handled"]:
                        if popup_result.get("popup_type") != "NONE":
                            self.logger.info(f"✅ 弹窗已处理: {popup_result['popup_type']}")
                            if popup_result["details"].get("first_name"):
                                self.logger.info(f"   姓名: {popup_result['details']['first_name']} {popup_result['details']['last_name']}")
                        else:
                            self.logger.info("没有检测到弹窗，继续执行")
                    else:
                        self.logger.warning(f"⚠️ 弹窗处理失败: {popup_result.get('error')}")
                        
                except Exception as e:
                    self.logger.warning(f"弹窗处理步骤出现问题: {e}，但继续执行")
                
            except Exception as e:
                self.logger.warning(f"登录步骤出现问题: {e}，但注册已完成")
            
            self.logger.info("注册成功！")
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"注册失败: {e}")
        finally:
            # 重置邮箱服务失败记录（为下次注册做准备）
            if self.email_manager:
                self.email_manager.reset_failed_services()
        
        return result


# 测试代码
if __name__ == "__main__":
    print("测试注册服务模块...")
    print("这是一个集成测试，需要完整的浏览器环境")
    print("请运行 main.py 进行完整测试")
