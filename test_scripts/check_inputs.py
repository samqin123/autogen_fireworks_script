#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from selenium.webdriver.common.by import By
import time

def check():
    browser = BrowserManager()
    browser.launch(headless=False)
    driver = browser.driver
    
    try:
        driver.get("https://app.fireworks.ai/login/email?redirectURI=%2Fsignin")
        time.sleep(5)
        
        print(f"URL: {driver.current_url}")
        print("\n所有输入框:")
        
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        for i, inp in enumerate(inputs):
            try:
                type_attr = inp.get_attribute('type') or 'none'
                name_attr = inp.get_attribute('name') or ''
                id_attr = inp.get_attribute('id') or ''
                displayed = inp.is_displayed()
                print(f"  [{i}] type={type_attr}, name={name_attr}, id={id_attr}, displayed={displayed}")
            except Exception as e:
                print(f"  [{i}] 错误: {e}")
        
        driver.save_screenshot("check_inputs.png")
        print("\n截图已保存: check_inputs.png")
        
        input("\n按 Enter 关闭...")
        
    finally:
        browser.quit()

if __name__ == "__main__":
    check()
