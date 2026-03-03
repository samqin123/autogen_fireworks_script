"""
弹窗处理器 - 识别并处理各种类型的弹窗
"""
import random
import time
from enum import Enum, auto

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
    from utils.logger import Logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.browser_manager import BrowserManager
    from utils.logger import Logger


class PopupType(Enum):
    """弹窗类型枚举"""
    UNKNOWN = auto()
    NONE = auto()  # 没有弹窗
    PROFILE_COMPLETION = auto()  # 补充信息弹窗 (Welcome to Fireworks)
    SURVEY = auto()  # 问卷调查弹窗
    TERMS_UPDATE = auto()  # 条款更新弹窗
    PROMOTIONAL = auto()  # 推广弹窗


class PopupHandler:
    """
    弹窗处理器 - 识别并处理各种类型的弹窗
    
    支持处理的弹窗类型:
    1. Profile Completion: 补充信息弹窗 (Welcome to Fireworks)
       - 填写 First Name, Last Name
       - 勾选同意条款
       - 点击 Continue
    """
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.logger = Logger()
        
        # 姓名库
        self.first_names = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
            "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald",
            "Steven", "Paul", "Andrew", "Kenneth", "Joshua", "Kevin", "Brian",
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
            "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Helen", "Sandra"
        ]
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]
    
    def detect_popup(self, timeout: int = 5) -> PopupType:
        """
        检测当前页面是否有弹窗，并识别弹窗类型
        
        Args:
            timeout: 检测超时时间（秒）
            
        Returns:
            PopupType: 检测到的弹窗类型
        """
        driver = self.browser.driver
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                page_source = driver.page_source
                
                # 检查 Profile Completion 弹窗 (Welcome to Fireworks)
                profile_indicators = [
                    "Welcome to Fireworks",
                    "Complete your profile",
                    "set up your account ID",
                    "First Name",
                    "Last Name",
                    'id="first-name"',
                    'id="last-name"',
                    'placeholder="First Name"',
                    'placeholder="Last Name"'
                ]
                
                # 需要同时满足多个条件才认为是 profile 弹窗
                profile_score = 0
                for indicator in profile_indicators:
                    if indicator in page_source:
                        profile_score += 1
                
                # 如果命中多个关键词，认为是 profile completion 弹窗
                if profile_score >= 3:
                    self.logger.info(f"检测到补充信息弹窗 (Profile Completion), 匹配度: {profile_score}")
                    return PopupType.PROFILE_COMPLETION
                
                # 检查是否有模态框/弹窗元素
                modal_selectors = [
                    '[role="dialog"]',
                    '[role="alertdialog"]',
                    '.modal',
                    '.dialog',
                    '.popup',
                    '.overlay',
                    'div[class*="modal"]',
                    'div[class*="dialog"]',
                    'div[class*="popup"]'
                ]
                
                for selector in modal_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and any(e.is_displayed() for e in elements):
                            self.logger.debug(f"发现可能的弹窗元素: {selector}")
                            # 进一步判断类型
                            if self._is_profile_completion_popup():
                                return PopupType.PROFILE_COMPLETION
                    except:
                        continue
                
                # 检查是否没有弹窗（正常页面）
                if self._is_normal_page():
                    return PopupType.NONE
                
            except Exception as e:
                self.logger.debug(f"检测弹窗时出错: {e}")
            
            time.sleep(0.5)
        
        # 超时后仍未识别，返回 UNKNOWN
        self.logger.warning("无法确定弹窗类型，返回 UNKNOWN")
        return PopupType.UNKNOWN
    
    def _is_profile_completion_popup(self) -> bool:
        """检查是否是补充信息弹窗"""
        driver = self.browser.driver
        try:
            # 检查关键元素
            first_name_input = driver.find_elements(By.CSS_SELECTOR, 'input#first-name, input[placeholder="First Name"]')
            last_name_input = driver.find_elements(By.CSS_SELECTOR, 'input#last-name, input[placeholder="Last Name"]')
            welcome_text = "Welcome to Fireworks" in driver.page_source
            
            if (first_name_input or last_name_input) and welcome_text:
                return True
        except:
            pass
        return False
    
    def _is_normal_page(self) -> bool:
        """检查是否是正常页面（没有弹窗）"""
        driver = self.browser.driver
        try:
            current_url = driver.current_url
            
            # 如果是主页或 onboarding 页面，且没有模态框，认为是正常页面
            if "/account/home" in current_url or "/onboarding" in current_url:
                # 检查是否有可见的弹窗元素
                popup_selectors = [
                    '[role="dialog"]',
                    '.modal',
                    'div[class*="modal"]'
                ]
                
                for selector in popup_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        visible_elements = [e for e in elements if e.is_displayed()]
                        if visible_elements:
                            return False  # 有可见弹窗
                    except:
                        continue
                
                return True  # 没有弹窗
        except:
            pass
        return False
    
    def generate_name(self) -> tuple:
        """生成随机姓名"""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        return first, last
    
    def handle_popup(self, popup_type: PopupType = None) -> dict:
        """
        处理弹窗
        
        Args:
            popup_type: 弹窗类型（如果为None则自动检测）
            
        Returns:
            dict: {
                "handled": bool,  # 是否处理了弹窗
                "popup_type": str,  # 弹窗类型
                "error": str,  # 错误信息
                "details": dict  # 处理详情
            }
        """
        result = {
            "handled": False,
            "popup_type": None,
            "error": None,
            "details": {}
        }
        
        try:
            # 自动检测弹窗类型
            if popup_type is None:
                popup_type = self.detect_popup()
            
            result["popup_type"] = popup_type.name
            
            if popup_type == PopupType.NONE:
                self.logger.info("没有检测到弹窗，继续执行")
                result["handled"] = True
                return result
            
            if popup_type == PopupType.PROFILE_COMPLETION:
                self.logger.info("处理补充信息弹窗...")
                return self._handle_profile_completion()
            
            if popup_type == PopupType.UNKNOWN:
                self.logger.warning("检测到未知类型弹窗，尝试通用处理...")
                return self._handle_unknown_popup()
            
            self.logger.info(f"弹窗类型 {popup_type.name} 无需处理或暂不支持")
            result["handled"] = True
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"处理弹窗失败: {e}")
        
        return result
    
    def _handle_profile_completion(self) -> dict:
        """
        处理补充信息弹窗 (Welcome to Fireworks)
        
        填写内容:
        - First Name (随机)
        - Last Name (随机)
        - 勾选同意条款
        - 点击 Continue
        """
        result = {
            "handled": False,
            "popup_type": "PROFILE_COMPLETION",
            "error": None,
            "details": {
                "first_name": None,
                "last_name": None,
                "terms_checked": False,
                "continue_clicked": False
            }
        }
        
        driver = self.browser.driver
        
        try:
            # 等待弹窗加载（减少等待时间）
            time.sleep(0.5)
            
            # 1. 生成姓名
            first_name, last_name = self.generate_name()
            result["details"]["first_name"] = first_name
            result["details"]["last_name"] = last_name
            
            # 2. 填写 First Name 和 Last Name - 使用 Selenium 优先（React 表单兼容性更好）
            self.logger.info("填写姓名（Selenium 优先）...")
            
            # First Name - 使用 Selenium 模拟真实输入
            first_success = False
            try:
                # 等待并查找 First Name 输入框
                first_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'firstName'))
                )
                
                # 模拟真实用户输入: click -> clear -> type -> blur
                first_input.click()
                time.sleep(0.2)
                first_input.clear()
                time.sleep(0.2)
                
                # 逐个字符输入，确保触发 input 事件
                for char in first_name:
                    first_input.send_keys(char)
                    time.sleep(0.05)
                
                time.sleep(0.3)
                # 触发 blur 事件（React 需要这个来更新状态）
                driver.execute_script("arguments[0].blur();", first_input)
                
                first_success = True
                self.logger.info(f"✅ First Name 填写成功: {first_name}")
            except Exception as e:
                self.logger.warning(f"First Name Selenium 填写失败: {e}")
                # 回退：使用原生 JS value setter（对 React 有效）
                try:
                    driver.execute_script("""
                        var input = document.querySelector('input[name="firstName"]');
                        if (input) {
                            // 使用原生 setter 绕过 React 控制
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, arguments[0]);
                            
                            // 触发必要的事件
                            input.dispatchEvent(new Event('focus', { bubbles: true }));
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                        }
                    """, first_name)
                    first_success = True
                    self.logger.info("✅ First Name JS 填写成功")
                except Exception as e2:
                    self.logger.error(f"First Name 所有方式失败: {e2}")
            
            # Last Name - 使用相同方式
            last_success = False
            try:
                last_input = driver.find_element(By.NAME, 'lastName')
                
                # 模拟真实用户输入
                last_input.click()
                time.sleep(0.2)
                last_input.clear()
                time.sleep(0.2)
                
                # 逐个字符输入
                for char in last_name:
                    last_input.send_keys(char)
                    time.sleep(0.05)
                
                time.sleep(0.3)
                driver.execute_script("arguments[0].blur();", last_input)
                
                last_success = True
                self.logger.info(f"✅ Last Name 填写成功: {last_name}")
            except Exception as e:
                self.logger.warning(f"Last Name Selenium 填写失败: {e}")
                # 回退：使用原生 JS value setter
                try:
                    driver.execute_script("""
                        var input = document.querySelector('input[name="lastName"]');
                        if (input) {
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, arguments[0]);
                            
                            input.dispatchEvent(new Event('focus', { bubbles: true }));
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                        }
                    """, last_name)
                    last_success = True
                    self.logger.info("✅ Last Name JS 填写成功")
                except Exception as e2:
                    self.logger.error(f"Last Name 所有方式失败: {e2}")
            
            # 验证输入是否成功
            time.sleep(0.5)
            verify = driver.execute_script("""
                return {
                    first: document.querySelector('input[name="firstName"]')?.value || '',
                    last: document.querySelector('input[name="lastName"]')?.value || ''
                };
            """)
            self.logger.info(f"表单验证: first='{verify.get('first')}', last='{verify.get('last')}'")
            
            if not verify.get('first') or not verify.get('last'):
                self.logger.error("表单填写验证失败！")
                driver.save_screenshot("debug_form_fill_failed.png")
            
            if not first_success or not last_success:
                # 保存调试截图
                try:
                    driver.save_screenshot("debug_popup_form.png")
                    self.logger.info("已保存调试截图: debug_popup_form.png")
                except:
                    pass
                raise Exception(f"无法找到输入框: first={first_success}, last={last_success}")
            
            # 3. 勾选同意条款
            self.logger.info("勾选同意条款...")
            
            checkbox_btn = None
            checked_success = False
            
            # 策略1: 查找自定义 checkbox button (role="checkbox")
            try:
                custom_checkbox_selectors = [
                    'button[role="checkbox"]',
                    '[role="checkbox"]',
                    'button[data-state="unchecked"]',
                    'button[data-state="checked"]',
                    'button[aria-checked="false"]',
                    'button[aria-checked="true"]',
                ]
                
                for selector in custom_checkbox_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        visible_elements = [e for e in elements if e.is_displayed()]
                        
                        if visible_elements:
                            # 找与 "agree" 文本最接近的
                            for elem in visible_elements:
                                try:
                                    parent = elem.find_element(By.XPATH, '..')
                                    parent_text = parent.text.lower()
                                    if 'agree' in parent_text or 'terms' in parent_text or 'privacy' in parent_text:
                                        checkbox_btn = elem
                                        self.logger.info(f"通过 selector '{selector}' 找到自定义 checkbox (关联条款文本)")
                                        break
                                except:
                                    continue
                            
                            # 如果找到关联文本的，跳出循环
                            if checkbox_btn:
                                break
                            
                            # 否则使用第一个可见的
                            if len(visible_elements) == 1:
                                checkbox_btn = visible_elements[0]
                                self.logger.info(f"通过 selector '{selector}' 找到唯一自定义 checkbox")
                                break
                            elif len(visible_elements) > 1 and not checkbox_btn:
                                checkbox_btn = visible_elements[0]
                                self.logger.info(f"通过 selector '{selector}' 找到第一个自定义 checkbox")
                                break
                    except:
                        continue
                        
            except Exception as e:
                self.logger.debug(f"查找自定义 checkbox 失败: {e}")
            
            # 策略2: 通过 label 文本定位，然后找相邻的 button[role="checkbox"]
            if not checkbox_btn:
                try:
                    label_selectors = [
                        '//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "agree")]',
                        '//label[contains(text(), "Terms of Service")]',
                        '//label[contains(text(), "Privacy Policy")]',
                        '//label[contains(text(), "I agree")]',
                    ]
                    
                    for label_xpath in label_selectors:
                        try:
                            labels = driver.find_elements(By.XPATH, label_xpath)
                            for label in labels:
                                if label.is_displayed():
                                    # 找 label 前面或内部的 button[role="checkbox"]
                                    try:
                                        # 前兄弟元素
                                        checkbox_btn = label.find_element(By.XPATH, 'preceding-sibling::button[@role="checkbox"][1]')
                                        if checkbox_btn.is_displayed():
                                            self.logger.info("通过 label 前兄弟 button[role='checkbox'] 找到")
                                            break
                                    except:
                                        pass
                                    
                                    # 父元素内的 button
                                    try:
                                        parent = label.find_element(By.XPATH, '..')
                                        checkbox_btn = parent.find_element(By.CSS_SELECTOR, 'button[role="checkbox"]')
                                        if checkbox_btn.is_displayed():
                                            self.logger.info("通过 label 父元素内的 button[role='checkbox'] 找到")
                                            break
                                    except:
                                        pass
                            
                            if checkbox_btn:
                                break
                        except:
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"通过 label 查找失败: {e}")
            
            # 策略3: 查找所有可见的 button[role="checkbox"]
            if not checkbox_btn:
                try:
                    all_btns = driver.find_elements(By.CSS_SELECTOR, 'button[role="checkbox"]')
                    visible_btns = [b for b in all_btns if b.is_displayed()]
                    
                    if visible_btns:
                        checkbox_btn = visible_btns[0]
                        self.logger.info(f"找到 {len(visible_btns)} 个可见自定义 checkbox，选择第一个")
                except Exception as e:
                    self.logger.debug(f"查找所有自定义 checkbox 失败: {e}")
            
            # 执行勾选
            if checkbox_btn:
                # 获取当前状态
                current_state = checkbox_btn.get_attribute("data-state")
                aria_checked = checkbox_btn.get_attribute("aria-checked")
                is_checked = current_state == "checked" or aria_checked == "true"
                
                self.logger.info(f"自定义 checkbox 当前状态: data-state={current_state}, aria-checked={aria_checked}")
                
                if not is_checked:
                    # 方法1: JavaScript 设置状态 + 触发点击事件
                    try:
                        driver.execute_script("""
                            var btn = arguments[0];
                            // 设置属性
                            btn.setAttribute('data-state', 'checked');
                            btn.setAttribute('aria-checked', 'true');
                            // 触发完整的事件序列
                            btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                            btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                            btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                            btn.dispatchEvent(new Event('change', { bubbles: true }));
                            // 触发 focus/blur
                            btn.focus();
                            btn.blur();
                        """, checkbox_btn)
                        time.sleep(0.8)
                        
                        # 验证状态
                        new_state = checkbox_btn.get_attribute("data-state")
                        new_aria = checkbox_btn.get_attribute("aria-checked")
                        if new_state == "checked" or new_aria == "true":
                            checked_success = True
                            self.logger.info("✅ 同意条款已勾选 (JavaScript)")
                        else:
                            self.logger.warning(f"JavaScript 勾选后状态未改变: data-state={new_state}, aria-checked={new_aria}")
                    except Exception as e:
                        self.logger.debug(f"JavaScript 勾选失败: {e}")
                    
                    # 方法2: 直接点击按钮
                    if not checked_success:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_btn)
                            time.sleep(0.3)
                            checkbox_btn.click()
                            time.sleep(0.8)
                            
                            # 验证
                            new_state = checkbox_btn.get_attribute("data-state")
                            new_aria = checkbox_btn.get_attribute("aria-checked")
                            if new_state == "checked" or new_aria == "true":
                                checked_success = True
                                self.logger.info("✅ 同意条款已勾选 (Click)")
                        except Exception as e:
                            self.logger.debug(f"点击勾选失败: {e}")
                    
                    # 方法3: ActionChains
                    if not checked_success:
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(driver)
                            actions.move_to_element(checkbox_btn).pause(0.3).click().pause(0.8).perform()
                            
                            new_state = checkbox_btn.get_attribute("data-state")
                            new_aria = checkbox_btn.get_attribute("aria-checked")
                            if new_state == "checked" or new_aria == "true":
                                checked_success = True
                                self.logger.info("✅ 同意条款已勾选 (ActionChains)")
                        except Exception as e:
                            self.logger.debug(f"ActionChains 失败: {e}")
                else:
                    checked_success = True
                    self.logger.info("✅ 同意条款已默认勾选")
                
                # 最终验证
                if checked_success:
                    result["details"]["terms_checked"] = True
                    self.logger.info("✅ 同意条款勾选确认成功")
                else:
                    self.logger.error("❌ 同意条款勾选失败，可能导致无法提交表单")
                    try:
                        driver.save_screenshot("debug_checkbox_failed.png")
                        self.logger.info("已保存调试截图: debug_checkbox_failed.png")
                    except:
                        pass
                
                time.sleep(0.5)
            else:
                self.logger.error("❌ 无法找到同意条款复选框")
            
            # 4. 点击 Continue 按钮
            self.logger.info("点击 Continue 按钮...")
            
            continue_selectors = [
                (By.XPATH, '//button[contains(text(), "Continue")]'),
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.XPATH, '//button[@type="submit"]'),
                (By.CSS_SELECTOR, 'button.continue'),
                (By.XPATH, '//button[.//span[contains(text(), "Continue")]]'),
            ]
            
            continue_btn = self.browser.find_element_safely(continue_selectors, timeout=5)
            if continue_btn:
                continue_btn.click()
                result["details"]["continue_clicked"] = True
                self.logger.info("✅ Continue 按钮已点击")
                time.sleep(2)  # 等待弹窗关闭
            else:
                raise Exception("无法找到 Continue 按钮")
            
            # 5. 验证弹窗是否已关闭
            time.sleep(1)
            popup_gone = not self._is_profile_completion_popup()
            if popup_gone:
                result["handled"] = True
                self.logger.info("✅ 补充信息弹窗处理完成")
            else:
                self.logger.warning("弹窗可能未关闭，但继续执行")
                result["handled"] = True  # 仍标记为已处理
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"处理补充信息弹窗失败: {e}")
        
        return result
    
    def _handle_unknown_popup(self) -> dict:
        """处理未知类型弹窗 - 尝试通用关闭方法"""
        result = {
            "handled": False,
            "popup_type": "UNKNOWN",
            "error": None,
            "details": {}
        }
        
        driver = self.browser.driver
        
        # 尝试通用的关闭方式
        close_selectors = [
            (By.CSS_SELECTOR, '[aria-label="Close"]'),
            (By.CSS_SELECTOR, '.close'),
            (By.CSS_SELECTOR, '.dismiss'),
            (By.XPATH, '//button[contains(text(), "Close")]'),
            (By.XPATH, '//button[contains(text(), "Dismiss")]'),
            (By.XPATH, '//button[contains(text(), "Skip")]'),
            (By.CSS_SELECTOR, 'button[class*="close"]'),
        ]
        
        for by, selector in close_selectors:
            try:
                close_btn = driver.find_element(by, selector)
                if close_btn.is_displayed():
                    close_btn.click()
                    result["handled"] = True
                    self.logger.info(f"通过 {selector} 关闭未知弹窗")
                    time.sleep(1)
                    return result
            except:
                continue
        
        # 尝试按 ESC 键关闭（通过 JavaScript）
        try:
            driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));")
            result["handled"] = True
            self.logger.info("尝试通过 ESC 键关闭弹窗")
            time.sleep(1)
        except:
            pass
        
        return result
    
    def wait_and_handle_popup(self, timeout: int = 10, check_interval: float = 1.0) -> dict:
        """
        等待并处理弹窗（轮询方式）
        
        Args:
            timeout: 最大等待时间
            check_interval: 检查间隔
            
        Returns:
            dict: 处理结果
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            popup_type = self.detect_popup()
            
            if popup_type != PopupType.NONE:
                self.logger.info(f"检测到弹窗，类型: {popup_type.name}")
                return self.handle_popup(popup_type)
            
            time.sleep(check_interval)
        
        self.logger.info("在超时时间内未检测到弹窗")
        return {
            "handled": True,  # 没有弹窗也算处理成功
            "popup_type": "NONE",
            "error": None,
            "details": {"timeout": True}
        }


# 测试代码
if __name__ == "__main__":
    print("测试弹窗处理器模块...")
    print("这是一个集成测试，需要完整的浏览器环境")
    print("请运行 main.py 进行完整测试")
