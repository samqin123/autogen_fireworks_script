#!/usr/bin/env python3
"""
调试验证后的登录流程
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

def debug_post_verification():
    print("=" * 50)
    print("调试验证后的登录流程")
    print("=" * 50)
    
    # 启动浏览器
    print("\n1. 启动浏览器...")
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 先创建邮箱并注册（简化版，手动输入验证链接）
        print("\n2. 创建临时邮箱...")
        email_mgr = EmailServiceManager()
        email_result = email_mgr.create_email()
        email = email_result.email
        print(f"   邮箱: {email}")
        
        # 访问注册页面
        print("\n3. 访问注册页面...")
        driver.get("https://app.fireworks.ai/signup")
        time.sleep(3)
        
        # 输入邮箱
        print("\n4. 输入邮箱...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        email_input.send_keys(email)
        
        # 点击 Next
        print("\n5. 点击 Next...")
        next_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
        next_btn.click()
        time.sleep(3)
        
        # 输入密码
        print("\n6. 输入密码...")
        password = "TestPass123!"
        pwd_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        pwd_input.send_keys(password)
        
        # 点击 Create Account
        print("\n7. 点击 Create Account...")
        create_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
        create_btn.click()
        time.sleep(3)
        
        print("\n8. 等待验证邮件...")
        print("   请稍等，正在获取验证链接...")
        verification_link = email_result.service_instance.get_verification_link(timeout=60)
        
        if not verification_link:
            print("   ❌ 未能获取验证链接")
            return
        
        print(f"   验证链接: {verification_link[:60]}...")
        
        # 访问验证链接
        print("\n9. 访问验证链接...")
        driver.get(verification_link)
        time.sleep(5)
        
        # 保存截图
        driver.save_screenshot("debug_step9_verification.png")
        print("   截图已保存: debug_step9_verification.png")
        
        # 检查页面文本
        print("\n10. 检查验证后页面...")
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        print(f"   页面文本前300字: {page_text[:300]}")
        
        # 查找 Sign In 按钮
        print("\n11. 查找 Sign In 按钮...")
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for btn in buttons:
            text = btn.text.strip()
            if text:
                print(f"   - '{text}'")
        
        # 尝试点击 Sign In
        print("\n12. 点击 Sign In...")
        try:
            signin_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign In")]'))
            )
            signin_btn.click()
            print("   ✅ 已点击 Sign In")
        except Exception as e:
            print(f"   ❌ 点击 Sign In 失败: {e}")
        
        time.sleep(5)
        
        # 检查当前页面
        print(f"\n13. 当前 URL: {driver.current_url}")
        driver.save_screenshot("debug_step13_after_signin.png")
        print("   截图已保存: debug_step13_after_signin.png")
        
        # 查找 Email Login 链接
        print("\n14. 查找 Email Login 链接...")
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            text = link.text.strip()
            if text:
                print(f"   - '{text}'")
        
        # 尝试点击 Email Login
        print("\n15. 点击 Email Login...")
        try:
            email_login = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Email Login")]'))
            )
            email_login.click()
            print("   ✅ 已点击 Email Login")
        except Exception as e:
            print(f"   ❌ 点击 Email Login 失败: {e}")
        
        time.sleep(3)
        
        # 检查邮箱登录表单
        print(f"\n16. 当前 URL: {driver.current_url}")
        driver.save_screenshot("debug_step16_email_login.png")
        print("   截图已保存: debug_step16_email_login.png")
        
        # 查找输入框
        print("\n17. 查找输入框...")
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        for inp in inputs:
            input_type = inp.get_attribute('type') or 'text'
            input_name = inp.get_attribute('name') or ''
            placeholder = inp.get_attribute('placeholder') or ''
            if inp.is_displayed():
                print(f"   - type={input_type}, name={input_name}, placeholder={placeholder}")
        
        # 尝试填写邮箱和密码
        print("\n18. 尝试填写邮箱和密码...")
        try:
            email_inp = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
            )
            email_inp.clear()
            email_inp.send_keys(email)
            print(f"   ✅ 已输入邮箱: {email}")
            
            pwd_inp = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            pwd_inp.clear()
            pwd_inp.send_keys(password)
            print("   ✅ 已输入密码")
            
            # 点击登录
            submit_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_btn.click()
            print("   ✅ 已点击提交")
            
            time.sleep(5)
            print(f"\n19. 登录后 URL: {driver.current_url}")
            driver.save_screenshot("debug_step19_after_login.png")
            
        except Exception as e:
            print(f"   ❌ 填写登录信息失败: {e}")
        
        print("\n调试完成，按 Enter 关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        browser.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    debug_post_verification()
