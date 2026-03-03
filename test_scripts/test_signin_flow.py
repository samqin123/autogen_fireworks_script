#!/usr/bin/env python3
"""
测试验证后的 signin 流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from core.email_service import EmailServiceManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_signin_flow():
    print("=" * 50)
    print("测试验证后的 signin 流程")
    print("=" * 50)
    
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 创建邮箱
        print("\n1. 创建邮箱...")
        email_mgr = EmailServiceManager()
        email_result = email_mgr.create_email()
        email = email_result.email
        password = "TestPass123!"
        print(f"   邮箱: {email}")
        
        # 注册
        print("\n2. 注册...")
        driver.get("https://app.fireworks.ai/signup")
        time.sleep(3)
        
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(email)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(3)
        
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(3)
        
        # 获取验证链接
        print("\n3. 获取验证链接...")
        verification_link = email_result.service_instance.get_verification_link(timeout=60)
        print(f"   链接: {verification_link[:60]}...")
        
        # 访问验证链接
        print("\n4. 访问验证链接...")
        driver.get(verification_link)
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        driver.save_screenshot("signin_step4.png")
        
        # 点击 Sign In
        print("\n5. 点击 Sign In...")
        signin_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign In")]'))
        )
        signin_btn.click()
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        
        # 点击 Email Login
        print("\n6. 点击 Email Login...")
        email_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Email Login")]'))
        )
        email_login.click()
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        driver.save_screenshot("signin_step6.png")
        
        # 检查是否在 /login/email 页面
        if "/login/email" not in driver.current_url:
            print(f"   ⚠️ 不在预期的 /login/email 页面")
            # 尝试直接访问
            print("   尝试直接访问 /login/email...")
            driver.get("https://app.fireworks.ai/login/email?redirectURI=%2Fsignin")
            time.sleep(3)
            print(f"   URL: {driver.current_url}")
        
        # 填写登录信息
        print("\n7. 填写登录信息...")
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        email_input = None
        for inp in inputs:
            if inp.is_displayed():
                email_input = inp
                break
        
        if not email_input:
            print("   ❌ 未找到邮箱输入框")
            driver.save_screenshot("signin_step7_error.png")
            return
        
        email_input.clear()
        email_input.send_keys(email)
        print(f"   ✅ 已输入邮箱: {email}")
        
        pwd_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        pwd_input.clear()
        pwd_input.send_keys(password)
        print("   ✅ 已输入密码")
        
        driver.save_screenshot("signin_step7_filled.png")
        
        # 点击登录
        print("\n8. 点击登录...")
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        print("   ✅ 已点击登录按钮")
        
        print("\n9. 等待跳转...")
        time.sleep(8)
        print(f"   当前 URL: {driver.current_url}")
        driver.save_screenshot("signin_step9.png")
        
        if "/onboarding" in driver.current_url:
            print("\n✅ 成功进入入门引导！")
        elif "/account/home" in driver.current_url:
            print("\n✅ 成功进入主页！")
        else:
            print(f"\n⚠️ 未进入预期页面")
        
        print("\n按 Enter 关闭...")
        input()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        try:
            driver.save_screenshot("signin_error.png")
        except:
            pass
        import traceback
        traceback.print_exc()
        
    finally:
        browser.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    test_signin_flow()
