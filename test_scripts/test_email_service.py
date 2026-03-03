#!/usr/bin/env python3
"""
邮箱服务测试脚本
功能：
1. 创建临时邮箱（SamfunAsia）
2. 保存邮箱信息到文件
3. 轮询获取验证邮件
4. 提取 Fireworks 验证链接

用法：
    python test_scripts/test_email_service.py
"""
import requests
import json
import re
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置
API_BASE = "https://cloudflare_temp_email.caiql20022000.workers.dev"
ADMIN_AUTH = "xiaoyibao@1234"
DOMAIN = "samfun.asia"


def generate_username():
    """生成随机用户名"""
    import random
    import string
    adjectives = ['blue', 'green', 'red', 'happy', 'sunny', 'bright', 'cool', 'swift', 
                  'lucky', 'golden', 'silver', 'quick', 'smart', 'wild']
    nouns = ['wave', 'star', 'moon', 'sun', 'cloud', 'river', 'mountain', 'forest', 
             'ocean', 'breeze', 'flower', 'tree', 'bird', 'fish']
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(100, 999)}"


def create_email():
    """
    创建临时邮箱
    
    Returns:
        dict: {"email": str, "jwt": str}
    """
    print("=" * 50)
    print("步骤1: 创建临时邮箱")
    print("=" * 50)
    
    username = generate_username()
    headers = {
        "x-admin-auth": ADMIN_AUTH,
        "Content-Type": "application/json"
    }
    body = {
        "enablePrefix": True,
        "name": username,
        "domain": DOMAIN
    }
    
    try:
        resp = requests.post(
            f"{API_BASE}/admin/new_address",
            headers=headers,
            json=body,
            timeout=30,
            verify=False
        )
        data = resp.json()
        email = data.get("address")
        jwt = data.get("jwt")
        
        # 保存到文件
        email_data = {
            "email": email,
            "jwt": jwt,
            "created_at": datetime.now().isoformat()
        }
        with open("/tmp/test_email.json", "w") as f:
            json.dump(email_data, f, indent=2)
        
        print(f"✅ 邮箱创建成功: {email}")
        print(f"✅ JWT 已保存到 /tmp/test_email.json")
        return email_data
        
    except Exception as e:
        print(f"❌ 创建邮箱失败: {e}")
        raise


def get_messages(jwt):
    """
    获取邮件列表
    
    Args:
        jwt: 邮箱 JWT token
        
    Returns:
        list: 邮件列表
    """
    headers = {"Authorization": f"Bearer {jwt}"}
    
    try:
        resp = requests.get(
            f"{API_BASE}/api/mails?limit=10&offset=0",
            headers=headers,
            timeout=30,
            verify=False
        )
        data = resp.json()
        # API 返回格式: {"results": [...], "count": N}
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return []
    except Exception as e:
        print(f"❌ 获取邮件失败: {e}")
        return []


def extract_verification_link(raw_content):
    """
    从邮件内容中提取 Fireworks 验证链接
    
    Args:
        raw_content: 邮件 raw 字段内容
        
    Returns:
        str: 验证链接，未找到返回 None
    """
    if not raw_content:
        return None
    
    pattern = r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+'
    match = re.search(pattern, raw_content, re.IGNORECASE)
    
    if match:
        return match.group(0)
    return None


def get_verification_link(jwt, timeout=120, check_interval=3):
    """
    获取 Fireworks 验证链接（轮询方式）
    
    Args:
        jwt: 邮箱 JWT token
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
        
    Returns:
        str: 验证链接，超时返回 None
    """
    print("\n" + "=" * 50)
    print("步骤2: 获取验证链接")
    print("=" * 50)
    print(f"⏱️  轮询获取邮件，超时: {timeout}s...")
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            messages = get_messages(jwt)
            print(f"[尝试 {attempt}] 找到 {len(messages)} 封邮件")
            
            for msg in messages:
                raw_content = msg.get("raw", "") if isinstance(msg, dict) else str(msg)
                
                # 检查是否是 Fireworks 邮件
                if "fireworks" in raw_content.lower():
                    print(f"🔥 找到 Fireworks 邮件!")
                    
                    link = extract_verification_link(raw_content)
                    if link:
                        print(f"✅ 验证链接: {link}")
                        # 保存到文件
                        with open("/tmp/verify_link.txt", "w") as f:
                            f.write(link)
                        print(f"✅ 链接已保存到 /tmp/verify_link.txt")
                        return link
            
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"⚠️  获取邮件出错: {e}")
            time.sleep(check_interval)
    
    print("❌ 获取验证链接超时")
    return None


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("邮箱服务测试脚本")
    print("=" * 60 + "\n")
    
    # 1. 创建邮箱
    email_data = create_email()
    email = email_data["email"]
    jwt = email_data["jwt"]
    
    print(f"\n📧 邮箱: {email}")
    print(f"🔑 JWT: {jwt[:50]}...")
    
    # 2. 等待并获取验证链接
    print("\n⚠️  请完成注册流程，等待验证邮件...")
    link = get_verification_link(jwt)
    
    if link:
        print("\n" + "=" * 60)
        print("✅ 成功获取验证链接!")
        print("=" * 60)
        print(f"链接: {link}")
    else:
        print("\n❌ 未获取到验证链接")
    
    # 3. 显示保存的文件
    print("\n" + "=" * 60)
    print("文件保存位置:")
    print("=" * 60)
    print("📄 /tmp/test_email.json  - 邮箱信息")
    print("📄 /tmp/verify_link.txt   - 验证链接")


if __name__ == "__main__":
    main()
