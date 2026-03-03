"""
入门引导服务模块 - 处理问卷和 $5 奖励领取
"""
import random
import time

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


class OnboardingService:
    """
    入门引导服务 - 处理问卷和 $5 奖励领取
    
    ⚠️ 重要：必须完成问卷才能领取 $5 奖励，不要点击 Skip！
    """
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.logger = Logger()
        
        # 问卷选项 - 问题1：目标
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
        
        # 问卷选项 - 问题2：用例
        self.use_cases_options = [
            "Code Assistance",
            "Conversational AI",
            "Agentic AI",
            "Search",
            "Multimedia RAG",
            "Other"
        ]
        
        # 姓名库
        self.first_names = [
            "John", "Michael", "David", "James", "Robert", "William", "Mary",
            "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
            "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Helen"
        ]
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore"
        ]
    
    def generate_name(self) -> tuple:
        """生成随机姓名"""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        return first, last
    
    def complete_onboarding(self) -> dict:
        """
        完成入门引导和问卷
        
        流程：
        1. 等待入门引导页面
        2. 填写姓名
        3. 勾选同意条款
        4. 点击 Continue
        5. 等待问卷页面
        6. 随机选择问卷选项
        7. 提交获取 $5
        
        Returns:
            dict: {
                "onboarding_completed": bool,
                "credits_claimed": bool,
                "account_id": str,
                "error": str
            }
        """
        result = {
            "onboarding_completed": False,
            "credits_claimed": False,
            "account_id": None,
            "error": None
        }
        
        try:
            driver = self.browser.driver
            
            # 1. 检查入门引导页面 (优化: 直接通过URL判断)
            self.logger.info("步骤1: 检查入门引导页面...")
            
            current_url = driver.current_url
            self.logger.info(f"当前 URL: {current_url}")
            
            # 如果已经在主页，说明 onboarding 已完成
            if "/account/home" in current_url or "/home" in current_url:
                self.logger.info("✅ 已在主页，入门引导已完成")
                result["onboarding_completed"] = True
                return result
            
            # URL 已确认是 onboarding，直接处理 (移除多文本检测循环，节省最多35秒)
            if "/onboarding" in current_url:
                self.logger.info(f"✅ 确认进入入门引导: {current_url}")
            else:
                self.logger.warning(f"⚠️ 非入门引导页面: {current_url}，假设已完成")
                result["onboarding_completed"] = True
                return result
            
            # 获取 Account ID
            try:
                account_id_elem = driver.find_element(By.CSS_SELECTOR, 'input#account-id')
                result["account_id"] = account_id_elem.get_attribute("value")
                self.logger.info(f"Account ID: {result['account_id']}")
            except:
                pass
            
            # 2. 检查是否已经填写过信息（通过弹窗处理）
            # 如果页面上没有 First Name 输入框，说明已通过弹窗填写
            first_name_input_exists = False
            try:
                first_inputs = driver.find_elements(By.CSS_SELECTOR, 'input#first-name, input[placeholder="First Name"]')
                first_name_input_exists = len(first_inputs) > 0 and first_inputs[0].is_displayed()
            except:
                pass
            
            if first_name_input_exists:
                self.logger.info("步骤2: 填写姓名...")
                first_name, last_name = self.generate_name()
                
                try:
                    first_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input#first-name, input[placeholder="First Name"]'))
                    )
                except:
                    first_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="First Name"]')
                
                self.browser.human_like_typing(first_input, first_name)
                time.sleep(0.3)  # 减少等待
                
                try:
                    last_input = driver.find_element(By.CSS_SELECTOR, 'input#last-name, input[placeholder="Last Name"]')
                except:
                    last_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Last Name"]')
                
                self.browser.human_like_typing(last_input, last_name)
                time.sleep(0.3)  # 减少等待
                
                # 3. 勾选同意条款 - 使用与 popup_handler 相同的逻辑
                self.logger.info("步骤3: 勾选同意条款...")
                checkbox = None
                
                # 策略1: 通过 label 文本定位
                try:
                    label = driver.find_element(By.XPATH, 
                        '//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "agree")]')
                    checkbox_id = label.get_attribute("for")
                    if checkbox_id:
                        checkbox = driver.find_element(By.ID, checkbox_id)
                        self.logger.info("通过 label for 属性找到 checkbox")
                except:
                    pass
                
                # 策略2: 查找可见的 checkbox
                if not checkbox:
                    try:
                        checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        visible_cbs = [cb for cb in checkboxes if cb.is_displayed()]
                        if visible_cbs:
                            checkbox = visible_cbs[0]
                            self.logger.info(f"找到 {len(visible_cbs)} 个可见 checkbox")
                    except:
                        pass
                
                if checkbox:
                    if not checkbox.is_selected():
                        # 使用 JavaScript 完整事件触发
                        driver.execute_script("""
                            var checkbox = arguments[0];
                            checkbox.checked = true;
                            checkbox.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                            checkbox.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                            checkbox.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                            checkbox.dispatchEvent(new Event('input', { bubbles: true }));
                            checkbox.focus();
                            checkbox.blur();
                        """, checkbox)
                        time.sleep(0.3)  # 减少等待
                        
                        if checkbox.is_selected():
                            self.logger.info("✅ 同意条款已勾选")
                        else:
                            self.logger.warning("⚠️ 同意条款可能未成功勾选")
                    else:
                        self.logger.info("✅ 同意条款已默认勾选")
                else:
                    self.logger.warning("⚠️ 未找到同意条款复选框")
                
                # 4. 点击 Continue
                self.logger.info("步骤4: 点击 Continue...")
                continue_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Continue")]'))
                )
                continue_btn.click()
                time.sleep(1)  # 减少等待，从3秒改为1秒
            else:
                self.logger.info("步骤2: 姓名信息已通过弹窗填写，跳过表单填写")
            
            # 5. 检查问卷页面 (优化: 直接检测选项存在)
            self.logger.info("步骤5: 检查问卷页面...")
            time.sleep(0.5)  # 短暂等待页面加载
            
            # 直接检测是否有选项存在 (移除多文本检测循环，节省最多35秒)
            try:
                options = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"], input[type="radio"], [role="checkbox"], [role="radio"]')
                visible_options = [o for o in options if o.is_displayed()]
                if visible_options:
                    self.logger.info(f"✅ 检测到 {len(visible_options)} 个选项，进入问卷页面")
                    result["onboarding_completed"] = True
                else:
                    self.logger.warning("⚠️ 未检测到选项，可能已完成问卷")
                    result["onboarding_completed"] = True
                    return result
            except Exception as e:
                self.logger.warning(f"⚠️ 检测问卷页面失败: {e}，继续执行...")
            
            # 6. 选择 Goals - 选择前两个 (根据 form-1.md)
            self.logger.info("步骤6: 选择 Goals (What are your goals for using Fireworks?)...")
            time.sleep(0.5)
            
            try:
                # 查找所有 checkbox/radio 及其关联 label
                goal_checkboxes = driver.find_elements(By.CSS_SELECTOR, 
                    'input[type="checkbox"], input[type="radio"], [role="checkbox"], [role="radio"]')
                visible_goals = [cb for cb in goal_checkboxes if cb.is_displayed()]
                self.logger.info(f"  找到 {len(visible_goals)} 个可见选项")
                
                # 选择前两个（根据 form-1.md: "选择第一项，第二项"）
                selected_goals = []
                for i, checkbox in enumerate(visible_goals[:2]):  # 只选前两个
                    try:
                        # 获取关联的 label 文本
                        checkbox_id = checkbox.get_attribute('id')
                        label_text = ""
                        if checkbox_id:
                            try:
                                label = driver.find_element(By.CSS_SELECTOR, f'label[for="{checkbox_id}"]')
                                label_text = label.text.strip()
                            except:
                                # 尝试从父元素获取文本
                                try:
                                    parent = checkbox.find_element(By.XPATH, '..')
                                    label_text = parent.text.strip()[:50]  # 限制长度
                                except:
                                    pass
                        
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", checkbox)
                        selected_goals.append(label_text or f"Option {i+1}")
                        self.logger.info(f"  ✅ 已选择 Goal {i+1}: {label_text or 'Option '+str(i+1)}")
                        time.sleep(0.2)
                    except Exception as e:
                        self.logger.warning(f"  ⚠️ 选择 Goal {i+1} 失败: {e}")
                
                if not selected_goals:
                    self.logger.warning("⚠️ 未成功选择任何 Goals")
            except Exception as e:
                self.logger.warning(f"⚠️ 选择 Goals 失败: {e}")
            
            # 7. 选择 Use Cases - 选择前两个未选择的 (根据 form-1.md)
            self.logger.info("步骤7: 选择 Use Cases (What are your primary use cases?)...")
            time.sleep(0.3)
            
            try:
                # 重新查找所有选项
                all_checkboxes = driver.find_elements(By.CSS_SELECTOR, 
                    'input[type="checkbox"], input[type="radio"], [role="checkbox"], [role="radio"]')
                visible_options = [cb for cb in all_checkboxes if cb.is_displayed()]
                
                # 找出未被选择的选项
                unchecked = [cb for cb in visible_options 
                           if not cb.is_selected() and cb.get_attribute('aria-checked') != 'true']
                self.logger.info(f"  找到 {len(unchecked)} 个未选择的选项")
                
                # 选择前两个未选择的
                selected_use_cases = []
                for i, checkbox in enumerate(unchecked[:2]):  # 只选前两个
                    try:
                        # 获取关联的 label 文本
                        checkbox_id = checkbox.get_attribute('id')
                        label_text = ""
                        if checkbox_id:
                            try:
                                label = driver.find_element(By.CSS_SELECTOR, f'label[for="{checkbox_id}"]')
                                label_text = label.text.strip()
                            except:
                                try:
                                    parent = checkbox.find_element(By.XPATH, '..')
                                    label_text = parent.text.strip()[:50]
                                except:
                                    pass
                        
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", checkbox)
                        selected_use_cases.append(label_text or f"Option {i+1}")
                        self.logger.info(f"  ✅ 已选择 Use Case {i+1}: {label_text or 'Option '+str(i+1)}")
                        time.sleep(0.2)
                    except Exception as e:
                        self.logger.warning(f"  ⚠️ 选择 Use Case {i+1} 失败: {e}")
                
                if not selected_use_cases:
                    self.logger.warning("⚠️ 未成功选择任何 Use Cases")
            except Exception as e:
                self.logger.warning(f"⚠️ 选择 Use Cases 失败: {e}")
            
            # 8. 提交问卷
            self.logger.info("步骤8: 提交问卷获取 $5...")
            submit_success = False
            
            # 尝试多种方式找到提交按钮（根据 form-1.md）
            submit_selectors = [
                (By.XPATH, '//button[contains(text(), "Submit to get") and contains(text(), "Credits")]'),  # 精确匹配
                (By.XPATH, '//button[contains(text(), "$5 Credits")]'),
                (By.XPATH, '//button[contains(text(), "Submit")]'),
                (By.XPATH, '//button[contains(text(), "$5")]'),
                (By.XPATH, '//button[@name="done"]'),  # 根据 form-1.md 的 name="done"
                (By.XPATH, '//button[@type="button" and contains(text(), "Submit")]'),
                (By.XPATH, '//button[contains(text(), "Continue")]'),
                (By.XPATH, '//button[contains(text(), "Next")]'),
                (By.XPATH, '//button[@type="submit"]'),
                (By.CSS_SELECTOR, 'button[type="submit"]'),
            ]
            
            for by, selector in submit_selectors:
                try:
                    submit_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                    time.sleep(0.2)
                    driver.execute_script("arguments[0].click();", submit_btn)  # JS 点击更快
                    submit_success = True
                    result["credits_claimed"] = True
                    self.logger.info(f"✅ 已通过 '{selector}' 提交问卷")
                    break
                except:
                    continue
            
            if not submit_success:
                self.logger.error("❌ 无法找到提交按钮")
                # 保存调试截图
                try:
                    driver.save_screenshot("debug_submit_failed.png")
                    self.logger.info("已保存调试截图: debug_submit_failed.png")
                except:
                    pass
                return result
            
            self.logger.info("已提交问卷，等待跳转...")
            
            # 优化: 等待跳转到主页，最多等待30秒
            home_reached = False
            max_wait = 30
            wait_interval = 2
            elapsed = 0
            
            while elapsed < max_wait:
                current_url = driver.current_url
                if "/account/home" in current_url or "/home" in current_url:
                    home_reached = True
                    self.logger.info(f"✅ 已跳转到主页: {current_url}")
                    break
                
                # 检查是否还在 onboarding
                if "/onboarding" in current_url:
                    self.logger.info(f"  仍在 onboarding 页面，继续等待... ({elapsed}s)")
                else:
                    self.logger.info(f"  当前 URL: {current_url}，继续等待... ({elapsed}s)")
                
                time.sleep(wait_interval)
                elapsed += wait_interval
            
            if home_reached:
                result["onboarding_completed"] = True
                self.logger.info("✅ 入门引导真正完成！")
            else:
                self.logger.warning("⚠️ 等待超时，未跳转到主页")
                # 检查当前页面状态
                if "/onboarding" in driver.current_url:
                    self.logger.error("❌ 仍在 onboarding 页面，流程未完成")
                    result["onboarding_completed"] = False
                    result["error"] = "Onboarding 未完成，仍在 onboarding 页面"
                else:
                    self.logger.info(f"✅ 当前页面: {driver.current_url}，假设已完成")
                    result["onboarding_completed"] = True
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"入门引导失败: {e}")
        
        return result


# 测试代码
if __name__ == "__main__":
    print("测试入门引导服务模块...")
    print("这是一个集成测试，需要完整的浏览器环境")
    print("请运行 main.py 进行完整测试")
