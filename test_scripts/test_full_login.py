#!/usr/bin/env python3
"""
完整测试验证后的登录流程
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

def test_full_login():
    print("=" * 50)
    print("完整验证后登录测试")
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
        
        # 注册流程
        print("\n2. 访问注册页...")
        driver.get("https://app.fireworks.ai/signup")
        time.sleep(3)
        
        print("\n3. 输入邮箱...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        email_input.send_keys(email)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(3)
        
        print("\n4. 输入密码...")
        pwd_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        pwd_input.send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(3)
        
        print("\n5. 等待验证邮件...")
        verification_link = email_result.service_instance.get_verification_link(timeout=60)
        if not verification_link:
            print("   ❌ 未获取验证链接")
            return
        print(f"   验证链接: {verification_link[:50]}...")
        
        print("\n6. 访问验证链接...")
        driver.get(verification_link)
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        driver.save_screenshot("test_full_step6.png")
        
        print("\n7. 点击 Sign In...")
        signin_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign In")]'))
        )
        signin_btn.click()
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        
        print("\n8. 点击 Email Login...")
        email_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Email Login")]'))
        )
        email_login.click()
        time.sleep(5)
        print(f"   URL: {driver.current_url}")
        
        # 如果 URL 包含 /login/email，说明进入了邮箱登录页
        if "/login/email" in driver.current_url:
            print("   ✅ 已进入邮箱登录页")
        driver.save_screenshot("test_full_step8.png")
        
        print("\n9. 填写登录信息...")
        # 查找所有可见的 text 输入框
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        email_input = None
        for inp in inputs:
            if inp.is_displayed():
                email_input = inp
                break
        
        if not email_input:
            print("   ❌ 未找到邮箱输入框")
            # 截图调试
            driver.save_screenshot("test_full_step9_error.png")
            return
        
        email_input.clear()
        email_input.send_keys(email)
        print(f"   ✅ 已输入邮箱: {email}")
        
        pwd_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        pwd_input.clear()
        pwd_input.send_keys(password)
        print("   ✅ 已输入密码")
        
        print("\n10. 点击 Next...")
        next_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
        next_btn.click()
        print("   ✅ 已点击 Next")
        
        print("\n11. 等待跳转...")
        time.sleep(8)
        print(f"   当前 URL: {driver.current_url}")
        driver.save_screenshot("test_full_step11.png")
        
        if "/onboarding" in driver.current_url:
            print("\n✅ 成功进入入门引导页面！")
        elif "/account/home" in driver.current_url:
            print("\n✅ 成功进入主页！")
        else:
            print(f"\n⚠️ 未进入预期页面: {driver.current_url}")
        
        print("\n按 Enter 关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        try:
            driver.save_screenshot("test_full_error.png")
            print("   错误截图已保存: test_full_error.png")
        except:
            pass
        import traceback
        traceback.print_exc()
        
    finally:
        browser.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    test_full_login()
