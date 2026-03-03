#!/usr/bin/env python3
"""
调试登录流程 - 检查验证后的页面结构
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

def debug_login_flow():
    print("=" * 50)
    print("调试登录流程")
    print("=" * 50)
    
    # 启动浏览器
    print("\n1. 启动浏览器...")
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 访问验证链接（使用之前成功的链接格式）
        print("\n2. 访问验证链接...")
        # 这里使用一个示例链接，实际使用时需要替换为真实的验证链接
        verification_link = "https://app.fireworks.ai/signup/confirm"
        driver.get(verification_link)
        time.sleep(5)
        
        print(f"   当前URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")
        
        # 保存截图
        driver.save_screenshot("debug_verification_page.png")
        print("   截图已保存: debug_verification_page.png")
        
        # 检查页面文本
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        print(f"\n3. 页面主要内容:")
        print("-" * 40)
        # 打印前500字符
        print(page_text[:500])
        print("-" * 40)
        
        # 查找所有按钮
        print("\n4. 查找所有按钮:")
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for i, btn in enumerate(buttons):
            try:
                text = btn.text.strip()
                if text:
                    print(f"   [{i}] '{text}'")
            except:
                pass
        
        # 查找所有链接
        print("\n5. 查找所有链接:")
        links = driver.find_elements(By.TAG_NAME, 'a')
        for i, link in enumerate(links[:10]):  # 只显示前10个
            try:
                text = link.text.strip()
                href = link.get_attribute('href') or ''
                if text:
                    print(f"   [{i}] '{text}' -> {href[:50]}...")
            except:
                pass
        
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
    debug_login_flow()
