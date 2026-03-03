"""
API Key 管理服务模块
根据 element.md 中的准确元素信息实现
"""
import time
import uuid
import re

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
    from utils.config import URLs
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.browser_manager import BrowserManager
    from utils.logger import Logger
    from utils.config import URLs


class APIKeyManager:
    """
    API Key 管理服务
    
    流程：
    1. 访问 API Keys 页面
    2. 点击 "Create API Key" 按钮（下拉菜单）
    3. 选择 "API Key" 选项
    4. 输入 API Key Name（id="name"）
    5. 点击 "Generate Key" 按钮（type="submit"）
    6. 从 <code> 标签提取 API Key（fw_ 开头）
    7. 点击复制按钮
    8. 关闭弹窗
    """
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.logger = Logger()
    
    def create_api_key(self, key_name: str = None) -> dict:
        """
        创建 API Key
        
        Returns:
            dict: {
                "success": bool,
                "key_name": str,
                "api_key": str,
                "error": str
            }
        """
        result = {
            "success": False,
            "key_name": None,
            "api_key": None,
            "error": None
        }
        
        if not key_name:
            key_name = f"auto-{uuid.uuid4().hex[:8]}"
        result["key_name"] = key_name
        
        try:
            driver = self.browser.driver
            
            # Step 1: 访问 API Keys 页面
            self.logger.info("步骤1: 访问 API Keys 页面...")
            driver.get(URLs.API_KEYS)
            time.sleep(2)
            
            # Step 2: 点击 "Create API Key" 按钮（触发下拉菜单）
            self.logger.info("步骤2: 点击 Create API Key 按钮...")
            
            # 尝试多种方式定位按钮（优化: 增加更多选择器）
            create_btn = None
            used_selector = None
            create_selectors = [
                # 方式1: 精确文本匹配（最可靠）
                (By.XPATH, '//button[contains(text(), "Create API Key")]'),
                # 方式2: 通过 aria-haspopup="menu" 找下拉按钮
                (By.CSS_SELECTOR, 'button[aria-haspopup="menu"]'),
                # 方式3: 找包含加号/创建图标的按钮
                (By.XPATH, '//button[.//*[contains(local-name(), "svg")]][contains(., "Create") or contains(., "+")]'),
                # 方式4: 页面右上角区域的下拉按钮
                (By.XPATH, '(//button[@aria-haspopup="menu"])[last()]'),
                # 方式5: 文本匹配（宽松）
                (By.XPATH, '//*[contains(text(), "Create API") or contains(text(), "Create key")]'),
                # 方式6: 通过 data-sentry-source-file 属性
                (By.CSS_SELECTOR, 'button[data-sentry-source-file="AddNewKeyModal.tsx"]'),
                # 方式7: 找包含加号图标的按钮
                (By.XPATH, '//button[.//svg[contains(@class, "plus") or contains(@class, "Plus")]]'),
            ]
            
            for by, selector in create_selectors:
                try:
                    create_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    used_selector = selector
                    self.logger.info(f"✅ 找到 Create API Key 按钮: {selector}")
                    break
                except:
                    continue
            
            # 如果还找不到，使用 JS 查询作为最后手段
            if not create_btn:
                self.logger.warning("所有选择器失败，尝试 JS 查询...")
                try:
                    js_result = driver.execute_script("""
                        // 找包含 "Create" 和 "API" 文本的按钮
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].innerText || buttons[i].textContent;
                            if (text && text.includes('Create') && (text.includes('API') || text.includes('Key'))) {
                                return buttons[i];
                            }
                        }
                        // 找有 aria-haspopup 的按钮
                        var menuBtn = document.querySelector('button[aria-haspopup="menu"]');
                        if (menuBtn) return menuBtn;
                        return null;
                    """)
                    if js_result:
                        create_btn = js_result
                        used_selector = "JS_QUERY"
                        self.logger.info("✅ 通过 JS 找到 Create API Key 按钮")
                except Exception as e:
                    self.logger.error(f"JS 查询也失败: {e}")
            
            if not create_btn:
                # 保存调试截图（带时间戳避免覆盖）
                try:
                    timestamp = int(time.time())
                    screenshot_path = f"debug_api_key_button_{timestamp}.png"
                    driver.save_screenshot(screenshot_path)
                    self.logger.info(f"已保存调试截图: {screenshot_path}")
                except:
                    pass
                raise Exception("无法找到 Create API Key 按钮")
            
            # 尝试点击
            try:
                create_btn.click()
                self.logger.info("✅ 已点击 Create API Key 按钮")
            except Exception as e:
                self.logger.warning(f"正常点击失败，使用 JS 点击: {e}")
                driver.execute_script("arguments[0].click();", create_btn)
                self.logger.info("✅ 已用 JS 点击 Create API Key 按钮")
            
            # 等待下拉菜单展开（优化: 动态等待替代固定sleep）
            time.sleep(1.0)
            
            # Step 3: 从下拉菜单选择 "API Key"（带钥匙图标）
            self.logger.info("步骤3: 选择 API Key 类型...")
            menu_clicked = False
            
            try:
                # 等待菜单元素出现
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[role="menu"], [class*="menu"], [class*="dropdown"]'))
                )
                
                # 方法1: 找包含 "API Key" 文本的菜单项
                api_key_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        '//*[@role="menuitem"]//*[contains(text(), "API Key")] | '
                        '//*[contains(@class, "menuitem")]//*[contains(text(), "API Key")]'
                    ))
                )
                api_key_option.click()
                menu_clicked = True
                self.logger.info("✅ 已选择 API Key 类型 (文本匹配)")
            except Exception as e1:
                # 方法2: JS 查找并点击
                try:
                    clicked = driver.execute_script("""
                        // 找包含 "API Key" 的元素
                        var elements = document.querySelectorAll('[role="menuitem"], [class*="menu-item"]');
                        for (var i = 0; i < elements.length; i++) {
                            var text = elements[i].innerText || elements[i].textContent;
                            if (text && text.includes('API Key')) {
                                elements[i].click();
                                return true;
                            }
                        }
                        // 如果没找到 API Key，点击第一个菜单项（通常是默认）
                        var firstMenu = document.querySelector('[role="menuitem"]');
                        if (firstMenu) {
                            firstMenu.click();
                            return 'FIRST_ITEM';
                        }
                        return false;
                    """)
                    if clicked:
                        if clicked == 'FIRST_ITEM':
                            self.logger.info("✅ 已点击第一个菜单项（可能已是 API Key）")
                        else:
                            self.logger.info("✅ 已选择 API Key 类型 (JS)")
                        menu_clicked = True
                    else:
                        self.logger.warning("⚠️ JS 选择 API Key 也失败")
                except Exception as e2:
                    self.logger.warning(f"选择 API Key 类型失败: {e1}, {e2}")
            
            # 等待弹窗出现
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'name'))
                )
                self.logger.info("✅ API Key 弹窗已出现")
            except:
                self.logger.warning("⚠️ 等待弹窗超时，继续执行...")
            
            # Step 4: 输入 API Key Name（id="name"）
            self.logger.info("步骤4: 输入 Key 名称...")
            try:
                # 根据 element.md，input 的 id="name"，name="name"
                name_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'name'))
                )
                
                # 确保输入框可见并可交互
                if not name_input.is_displayed():
                    raise Exception("输入框不可见")
                
                name_input.clear()
                name_input.send_keys(key_name)
                self.logger.info(f"✅ 已输入 Key 名称: {key_name}")
            except Exception as e:
                self.logger.error(f"输入 Key 名称失败: {e}")
                # 保存调试截图
                try:
                    driver.save_screenshot("debug_api_key_input.png")
                    self.logger.info("已保存调试截图: debug_api_key_input.png")
                except:
                    pass
                raise Exception("无法找到或操作 API Key 名称输入框")
            
            time.sleep(0.5)
            
            # Step 5: 点击 "Generate Key" 按钮（type="submit"）
            self.logger.info("步骤5: 点击 Generate Key...")
            try:
                generate_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(text(), "Generate")]'))
                )
                generate_btn.click()
                self.logger.info("✅ 已点击 Generate Key")
            except Exception as e:
                self.logger.warning(f"正常点击失败，尝试 JS 点击: {e}")
                # 使用 JavaScript 点击
                driver.execute_script('document.querySelector("button[type=\'submit\']").click();')
                self.logger.info("✅ 已用 JavaScript 点击 Generate Key")
            
            # Step 6: 等待 API Key 显示并提取（优化: 添加轮询机制）
            self.logger.info("步骤6: 捕获 API Key...")
            
            api_key = None
            max_retries = 10  # 增加重试次数
            retry_delay = 1.5  # 增加等待时间
            
            for attempt in range(max_retries):
                self.logger.info(f"  尝试提取 API Key ({attempt + 1}/{max_retries})...")
                
                # 方式1: 从 <code> 标签提取（最可靠）
                if not api_key:
                    try:
                        code_elems = driver.find_elements(By.XPATH, '//code[contains(text(), "fw_")]')
                        for elem in code_elems:
                            text = elem.text.strip()
                            if text and text.startswith("fw_") and len(text) > 30:
                                api_key = text
                                self.logger.info(f"✅ 从 <code> 标签获取: {api_key[:25]}...")
                                break
                    except Exception as e:
                        self.logger.debug(f"方式1失败: {e}")
                
                # 方式2: 从 input 元素提取
                if not api_key:
                    try:
                        input_elems = driver.find_elements(By.XPATH, '//input[contains(@value, "fw_")]')
                        for elem in input_elems:
                            value = elem.get_attribute("value")
                            if value and value.startswith("fw_") and len(value) > 30:
                                api_key = value
                                self.logger.info(f"✅ 从 input 获取: {api_key[:25]}...")
                                break
                    except Exception as e:
                        self.logger.debug(f"方式2失败: {e}")
                
                # 方式3: 从页面源码正则提取
                if not api_key:
                    try:
                        page_source = driver.page_source
                        # 更精确的正则：fw_ 后跟 32-64 个字母数字
                        matches = re.findall(r'fw_[a-zA-Z0-9]{32,64}', page_source)
                        if matches:
                            api_key = matches[0]
                            self.logger.info(f"✅ 从源码获取: {api_key[:25]}...")
                            break
                    except Exception as e:
                        self.logger.debug(f"方式3失败: {e}")
                
                if api_key:
                    break
                    
                # 等待后重试
                if attempt < max_retries - 1:
                    self.logger.info(f"  未找到 API Key，等待 {retry_delay}s 后重试...")
                    time.sleep(retry_delay)
            
            if not api_key:
                # 保存调试截图（带时间戳避免覆盖）
                try:
                    timestamp = int(time.time())
                    screenshot_path = f"debug_api_key_result_{timestamp}.png"
                    driver.save_screenshot(screenshot_path)
                    self.logger.info(f"已保存调试截图: {screenshot_path}")
                except:
                    pass
                raise Exception("无法获取 API Key")
            
            result["api_key"] = api_key
            
            # Step 7: 点击复制按钮（aria-label="Copy to clipboard"）
            self.logger.info("步骤7: 点击复制按钮...")
            try:
                copy_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Copy to clipboard"]'))
                )
                copy_btn.click()
                self.logger.info("✅ 已点击复制")
                time.sleep(0.5)
            except:
                self.logger.warning("⚠️ 点击复制按钮失败，但 API Key 已获取")
            
            # Step 8: 关闭弹窗
            self.logger.info("步骤8: 关闭弹窗...")
            try:
                # 找关闭按钮（可能是 X 图标或 Close 按钮）
                close_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        '//button[contains(text(), "Close")] | '
                        '//button[contains(@aria-label, "Close")] | '
                        '//div[@role="dialog"]//button[last()]'
                    ))
                )
                close_btn.click()
                self.logger.info("✅ 已关闭弹窗")
            except:
                pass  # 可能已经自动关闭
            
            result["success"] = True
            self.logger.info("✅ API Key 创建完成！")
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"创建 API Key 失败: {e}")
        
        return result


if __name__ == "__main__":
    print("测试 API Key 管理服务模块...")
