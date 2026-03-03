#!/usr/bin/env python3
"""
快速测试验证后的登录流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_login_flow():
    """测试验证后的登录流程"""
    print("=" * 50)
    print("测试验证后的登录流程")
    print("=" * 50)
    
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 模拟验证后的流程：直接访问登录页
        print("\n1. 访问登录页...")
        driver.get("https://app.fireworks.ai/login")
        time.sleep(3)
        print(f"   URL: {driver.current_url}")
        
        # 保存截图
        driver.save_screenshot("test_login_step1.png")
        
        # 查找 Email Login 链接
        print("\n2. 查找 Email Login 链接...")
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            text = link.text.strip()
            if 'email' in text.lower() or 'login' in text.lower():
                print(f"   找到链接: '{text}'")
        
        # 点击 Email Login
        print("\n3. 点击 Email Login...")
        try:
            email_login = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Email Login")]'))
            )
            email_login.click()
            print("   ✅ 已点击 Email Login")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
        
        # 等待页面跳转
        print("   等待页面跳转...")
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        driver.save_screenshot("test_login_step3.png")
        
        # 查找输入框
        print("\n4. 查找输入框...")
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        for inp in inputs:
            if inp.is_displayed():
                input_type = inp.get_attribute('type') or 'text'
                print(f"   - type={input_type}")
        
        # 填写测试邮箱和密码
        print("\n5. 填写登录信息...")
        test_email = "test@example.com"
        test_password = "TestPass123!"
        
        try:
            # 登录页的邮箱输入框 type="text" - 查找所有可见的 text 输入框
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
            email_input = None
            for inp in inputs:
                if inp.is_displayed():
                    email_input = inp
                    break
            
            if not email_input:
                raise Exception("无法找到邮箱输入框")
            
            email_input.clear()
            email_input.send_keys(test_email)
            print(f"   ✅ 已输入邮箱: {test_email}")
            
            pwd_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            pwd_input.clear()
            pwd_input.send_keys(test_password)
            print("   ✅ 已输入密码")
            
        except Exception as e:
            print(f"   ❌ 输入失败: {e}")
        
        driver.save_screenshot("test_login_step5.png")
        print("\n测试完成，按 Enter 关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        browser.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    test_login_flow()
