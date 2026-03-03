#!/usr/bin/env python3
"""
Fireworks AI 注册流程集成测试
基于 Chrome DevTools MCP 的实际测试记录

此脚本记录了完整的注册流程，用于验证和调试 registration.py 的逻辑
"""

import re
import json
import time
import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============= 配置 =============
BASE_URL = "https://cloudflare_temp_email.caiql20022000.workers.dev"
FIREWORKS_SIGNUP_URL = "https://app.fireworks.ai/signup"

# ============= Email Service (SamfunAsia) =============

def create_email():
    """创建临时邮箱"""
    url = f"{BASE_URL}/admin/new_address"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(url, headers=headers, verify=False)
    data = response.json()
    return data["jwt"], data["address"]

def get_verification_link(jwt, timeout=60):
    """获取验证链接"""
    url = f"{BASE_URL}/api/mails"
    headers = {"Authorization": f"Bearer {jwt}"}
    
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()
        
        for msg in data.get("results", []):
            raw = msg.get("raw", "")
            # 提取验证链接
            match = re.search(r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+', raw)
            if match:
                return match.group(0)
        
        time.sleep(3)
    
    return None

# ============= 测试主流程 =============

def test_full_flow():
    """测试完整流程（配合 Chrome DevTools 手动操作）"""
    print("=" * 60)
    print("Fireworks AI 注册流程测试")
    print("=" * 60)
    
    # 1. 创建邮箱
    print("\n1. 创建临时邮箱...")
    jwt, email = create_email()
    print(f"   邮箱: {email}")
    print(f"   JWT: {jwt[:30]}...")
    
    # 2. 打开注册页面（手动操作指引）
    print(f"\n2. 请在浏览器中打开: {FIREWORKS_SIGNUP_URL}")
    print(f"   填写邮箱: {email}")
    print("   填写密码: FireTest@2026")
    print("   点击 'Create Account'")
    
    # 3. 等待并获取验证链接
    print("\n3. 等待验证邮件...")
    link = get_verification_link(jwt, timeout=120)
    if link:
        print(f"   验证链接: {link}")
        print(f"\n4. 请在浏览器中打开验证链接")
        print("   点击 'Sign In' 按钮")
        print("   点击 'Email Login' 链接")
        print(f"   填写邮箱: {email}")
        print("   填写密码: FireTest@2026")
    else:
        print("   未收到验证邮件")

if __name__ == "__main__":
    test_full_flow()
