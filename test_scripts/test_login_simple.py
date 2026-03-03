#!/usr/bin/env python3
"""
简化测试 - 直接访问邮箱登录页
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_login():
    print("=" * 50)
    print("简化登录测试")
    print("=" * 50)
    
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 直接访问邮箱登录页
        print("\n1. 访问邮箱登录页...")
        driver.get("https://app.fireworks.ai/login/email")
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        
        # 保存截图
        driver.save_screenshot("test_login_simple.png")
        
        # 查找所有可见的输入框
        print("\n2. 查找输入框...")
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        visible_inputs = []
        for i, inp in enumerate(inputs):
            try:
                if inp.is_displayed():
                    input_type = inp.get_attribute('type') or 'text'
                    print(f"   [{i}] type={input_type}")
                    visible_inputs.append(inp)
            except:
                pass
        
        if len(visible_inputs) >= 2:
            print("\n3. 填写登录信息...")
            # 第一个可见的 text 输入框是邮箱
            email_input = visible_inputs[0]
            email_input.clear()
            email_input.send_keys("test@example.com")
            print("   ✅ 已输入邮箱")
            
            # 找到 password 输入框
            pwd_input = None
            for inp in visible_inputs:
                if inp.get_attribute('type') == 'password':
                    pwd_input = inp
                    break
            
            if pwd_input:
                pwd_input.clear()
                pwd_input.send_keys("TestPass123!")
                print("   ✅ 已输入密码")
                
                # 截图
                driver.save_screenshot("test_login_filled.png")
                print("\n✅ 登录信息填写成功！")
            else:
                print("   ❌ 未找到密码输入框")
        else:
            print(f"   ❌ 只找到 {len(visible_inputs)} 个可见输入框")
        
        print("\n按 Enter 关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        browser.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    test_login()
