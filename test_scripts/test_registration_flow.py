#!/usr/bin/env python3
"""
完整注册流程测试脚本
基于 Chrome DevTools MCP 的测试流程

用法：
    python test_scripts/test_registration_flow.py
"""
import json
import time


def simulate_registration():
    """
    模拟完整注册流程（供参考）
    
    实际注册时的页面元素定位：
    """
    flow = """
    ============================================
    Fireworks AI 注册流程 - 元素定位参考
    ============================================
    
    【步骤1】访问注册页面
    URL: https://app.fireworks.ai/signup
    
    【步骤2】填写邮箱
    元素: input[type="email"] 或 #email-display
    操作: fill(email)
    
    【步骤3】点击 Next
    元素: button[type="submit"]
    操作: click()
    
    【步骤4】填写密码
    元素: 
      - Password: input#password
      - Confirm: input#confirm-password
    操作: fill(password)
    
    【步骤5】点击 Create Account
    元素: button[type="submit"]
    操作: click()
    
    【步骤6】等待验证邮件提示
    文本: "verification email has been sent"
    
    【步骤7】从邮箱获取验证链接
    API: GET /api/mails?limit=10&offset=0
    提取: https://app.fireworks.ai/signup/confirm?...
    
    【步骤8】访问验证链接
    URL: {verification_link}
    
    【步骤9】点击 Sign In
    元素: button:has-text("Sign In")
    操作: click()
    
    【步骤10】邮箱登录
    URL: https://app.fireworks.ai/login/email
    元素:
      - Email: input[type="email"]
      - Password: input[type="password"]
      - Next: button[type="submit"]
    
    【步骤11】入门引导
    URL: https://app.fireworks.ai/onboarding
    元素:
      - First Name: input[placeholder="First Name"]
      - Last Name: input[placeholder="Last Name"]
      - Checkbox: input[type="checkbox"]
      - Continue: button:has-text("Continue")
    
    【步骤12】问卷（领取$5）
    元素:
      - 多选框: checkbox
      - Submit: button:has-text("Submit to get $5 Credits")
    
    【步骤13】创建 API Key
    URL: https://app.fireworks.ai/settings/users/api-keys
    元素:
      - Create: button:has-text("Create API Key")
      - Menu: div[role="menuitem"]:has-text("API Key")
      - Name: input[placeholder*="name"]
      - Generate: button:has-text("Generate Key")
    
    ============================================
    """
    print(flow)


def print_element_reference():
    """打印元素定位参考表"""
    reference = {
        "注册页": {
            "邮箱输入": ["#email-display", "input[type='email']"],
            "Next按钮": ["button[type='submit']", "//button[contains(text(),'Next')]"],
        },
        "密码页": {
            "密码": ["#password", "input[name='password']"],
            "确认密码": ["#confirm-password", "input[name='confirmPassword']"],
            "Create按钮": ["button[type='submit']"],
        },
        "验证页": {
            "Continue": ["button:has-text('Continue')"],
            "文本提示": ["verification email has been sent"],
        },
        "登录页": {
            "Email": ["input[type='email']"],
            "Password": ["input[type='password']"],
            "Next": ["button[type='submit']"],
        },
        "引导页": {
            "First Name": ["input[placeholder='First Name']"],
            "Last Name": ["input[placeholder='Last Name']"],
            "Checkbox": ["input[type='checkbox']"],
            "Continue": ["button:has-text('Continue')"],
        },
        "问卷页": {
            "选项": ["//label[contains(text(),'xxx')]/preceding-sibling::input", "input[type='checkbox']"],
            "Submit": ["button:has-text('Submit to get $5 Credits')"],
        },
        "API Keys页": {
            "Create": ["button:has-text('Create API Key')"],
            "Menu": ["div[role='menuitem']:has-text('API Key')"],
            "Name": ["input[placeholder*='name']"],
            "Generate": ["button:has-text('Generate Key')"],
            "Copy": ["button:has-text('Copy to clipboard')"],
        },
    }
    
    print("\n" + "=" * 60)
    print("元素定位参考表")
    print("=" * 60)
    
    for page, elements in reference.items():
        print(f"\n【{page}】")
        for name, selectors in elements.items():
            print(f"  {name}:")
            for sel in selectors:
                print(f"    - {sel}")


def print_api_reference():
    """打印 API 参考"""
    api = """
    ============================================
    SamfunAsia 邮箱 API 参考
    ============================================
    
    【创建邮箱】
    POST /admin/new_address
    Headers:
      x-admin-auth: xiaoyibao@1234
      Content-Type: application/json
    Body:
      {
        "enablePrefix": true,
        "name": "username",
        "domain": "samfun.asia"
      }
    Response:
      {
        "address": "xxx@samfun.asia",
        "jwt": "eyJhbGciOi..."
      }
    
    【获取邮件】
    GET /api/mails?limit=10&offset=0
    Headers:
      Authorization: Bearer {jwt}
    Response:
      {
        "results": [
          {
            "id": 123,
            "message_id": "...",
            "source": "...",
            "address": "xxx@samfun.asia",
            "raw": "邮件原始内容...",
            "created_at": "..."
          }
        ],
        "count": 1
      }
    
    【提取验证链接】
    正则: https://app\\.fireworks\\.ai/signup/confirm[^"\\s<>]+
    
    ============================================
    """
    print(api)


def main():
    """主函数"""
    simulate_registration()
    print_element_reference()
    print_api_reference()
    
    print("\n" + "=" * 60)
    print("测试脚本说明")
    print("=" * 60)
    print("""
1. test_email_service.py - 邮箱服务测试
2. test_registration_flow.py - 注册流程参考（本文件）
3. test_browser_auto.py - 浏览器自动化测试

使用方法：
  # 测试邮箱服务
  python test_scripts/test_email_service.py
  
  # 查看流程参考
  python test_scripts/test_registration_flow.py
""")


if __name__ == "__main__":
    main()
