#!/usr/bin/env python3
"""
诊断脚本 - 测试注册页面交互
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def diagnose():
    print("=" * 50)
    print("注册页面诊断测试")
    print("=" * 50)
    
    # 启动浏览器
    print("\n1. 启动浏览器...")
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        # 访问注册页面
        print("2. 访问注册页面...")
        driver.get("https://app.fireworks.ai/signup")
        time.sleep(3)
        
        # 检查页面标题
        print(f"   页面标题: {driver.title}")
        print(f"   当前URL: {driver.current_url}")
        
        # 查找所有 input 元素
        print("\n3. 查找所有 input 元素...")
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        print(f"   找到 {len(inputs)} 个 input 元素")
        
        for i, inp in enumerate(inputs):
            try:
                attrs = {
                    'type': inp.get_attribute('type') or 'none',
                    'name': inp.get_attribute('name') or '',
                    'id': inp.get_attribute('id') or '',
                    'class': inp.get_attribute('class') or '',
                    'placeholder': inp.get_attribute('placeholder') or '',
                    'displayed': inp.is_displayed(),
                    'enabled': inp.is_enabled(),
                }
                print(f"   [{i}] type={attrs['type']}, id={attrs['id']}, name={attrs['name']}, displayed={attrs['displayed']}, enabled={attrs['enabled']}")
            except Exception as e:
                print(f"   [{i}] 错误: {e}")
        
        # 尝试定位邮箱输入框
        print("\n4. 尝试定位邮箱输入框...")
        
        test_selectors = [
            ('CSS', 'input[type="email"]'),
            ('CSS', 'input[name="email"]'),
            ('CSS', 'input[id*="email"]'),
            ('CSS', 'input[placeholder*="mail"]'),
            ('XPATH', '//label[contains(text(),"Email")]/following-sibling::input'),
            ('XPATH', '//input[@placeholder="Email"]'),
        ]
        
        email_input = None
        for selector_type, selector in test_selectors:
            try:
                by = By.CSS_SELECTOR if selector_type == 'CSS' else By.XPATH
                elem = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                if elem.is_displayed():
                    print(f"   ✓ 找到: {selector_type}='{selector}'")
                    email_input = elem
                    break
            except Exception as e:
                print(f"   ✗ 失败: {selector_type}='{selector}'")
        
        if not email_input:
            print("\n   ⚠️ 无法定位邮箱输入框，尝试 JavaScript 方式...")
            # 尝试通过 label 查找
            labels = driver.find_elements(By.TAG_NAME, 'label')
            for label in labels:
                if 'email' in label.text.lower():
                    print(f"   找到 Email label: {label.text}")
                    # 尝试查找相邻的 input
                    parent = driver.execute_script("return arguments[0].parentElement;", label)
                    if parent:
                        inputs_in_parent = parent.find_elements(By.TAG_NAME, 'input')
                        print(f"   父元素内有 {len(inputs_in_parent)} 个 input")
        
        # 尝试填写测试
        if email_input:
            print("\n5. 测试填写邮箱...")
            test_email = "test@example.com"
            
            # 滚动到视图中
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
            time.sleep(1)
            
            # 点击
            email_input.click()
            time.sleep(0.5)
            
            # 清除并输入
            email_input.clear()
            email_input.send_keys(test_email)
            time.sleep(0.5)
            
            # 验证
            actual = email_input.get_attribute('value')
            if actual == test_email:
                print(f"   ✓ 输入成功: {actual}")
            else:
                print(f"   ✗ 输入失败: 期望 '{test_email}', 实际 '{actual}'")
                
                # 尝试 JavaScript 输入
                print("   尝试 JavaScript 输入...")
                driver.execute_script(f"arguments[0].value = '{test_email}';", email_input)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_input)
                time.sleep(0.5)
                actual = email_input.get_attribute('value')
                print(f"   JavaScript 输入结果: {actual}")
        
        # 查找 Next 按钮
        print("\n6. 查找 Next 按钮...")
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        print(f"   找到 {len(buttons)} 个 button 元素")
        
        for i, btn in enumerate(buttons):
            try:
                text = btn.text or ''
                btn_type = btn.get_attribute('type') or ''
                displayed = btn.is_displayed()
                enabled = btn.is_enabled()
                print(f"   [{i}] text='{text}', type={btn_type}, displayed={displayed}, enabled={enabled}")
            except:
                pass
        
        print("\n诊断完成，按 Enter 关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        browser.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    diagnose()
