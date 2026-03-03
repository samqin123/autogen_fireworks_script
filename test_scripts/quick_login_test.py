#!/usr/bin/env python3
"""
快速测试登录流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test():
    print("快速测试登录页输入...")
    
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 直接访问登录页
        driver.get("https://app.fireworks.ai/login/email?redirectURI=%2Fsignin")
        time.sleep(3)
        print(f"URL: {driver.current_url}")
        
        # 等待并查找输入框
        print("\n查找输入框...")
        time.sleep(2)
        
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        print(f"找到 {len(inputs)} 个 text 输入框")
        
        email_input = None
        for inp in inputs:
            if inp.is_displayed():
                email_input = inp
                print(f"找到可见的 text 输入框")
                break
        
        if email_input:
            email_input.send_keys("test@example.com")
            print("✅ 已输入邮箱")
            
            pwd = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            pwd.send_keys("Test123!")
            print("✅ 已输入密码")
            
            driver.save_screenshot("quick_test_success.png")
            print("✅ 测试成功！")
        else:
            print("❌ 未找到邮箱输入框")
            driver.save_screenshot("quick_test_failed.png")
        
        input("\n按 Enter 关闭...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        driver.save_screenshot("quick_test_error.png")
    finally:
        browser.quit()

if __name__ == "__main__":
    test()
