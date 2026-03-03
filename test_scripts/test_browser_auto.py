#!/usr/bin/env python3
"""
浏览器自动化测试脚本
使用 Selenium 模拟注册流程

用法：
    python test_scripts/test_browser_auto.py

依赖：
    pip install selenium undetected-chromedriver
"""
import sys
import os
import time
import json

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_browser_launch():
    """测试浏览器启动"""
    print("=" * 60)
    print("测试1: 浏览器启动")
    print("=" * 60)
    
    try:
        from core.browser_manager import BrowserManager
        
        print("创建 BrowserManager...")
        bm = BrowserManager()
        
        print("启动浏览器（无头模式）...")
        driver = bm.launch(headless=True)
        
        print("✅ 浏览器启动成功!")
        print(f"当前页面: {driver.current_url}")
        
        # 测试访问页面
        driver.get("https://www.google.com")
        print(f"页面标题: {driver.title}")
        
        bm.quit()
        print("✅ 浏览器已关闭")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_email_creation():
    """测试邮箱创建"""
    print("\n" + "=" * 60)
    print("测试2: 邮箱创建")
    print("=" * 60)
    
    try:
        from core.email_service import SamfunAsiaEmailService
        
        print("创建 SamfunAsiaEmailService...")
        service = SamfunAsiaEmailService()
        
        print("创建临时邮箱...")
        email, jwt = service.create_email()
        
        print(f"✅ 邮箱创建成功!")
        print(f"📧 邮箱: {email}")
        print(f"🔑 JWT: {jwt[:50]}...")
        
        # 保存到文件
        with open("/tmp/test_email_result.json", "w") as f:
            json.dump({"email": email, "jwt": jwt}, f, indent=2)
        
        print("✅ 结果已保存到 /tmp/test_email_result.json")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verification_link_extraction():
    """测试验证链接提取"""
    print("\n" + "=" * 60)
    print("测试3: 验证链接提取")
    print("=" * 60)
    
    # 模拟邮件内容
    test_raw = """
From: Fireworks AI <support@fireworks.ai>
To: test@samfun.asia
Subject: Welcome to Fireworks

Please verify your email by clicking the link below:
https://app.fireworks.ai/signup/confirm?client_id=abc123&user_name=xyz789&confirmation_code=123456

Thank you!
"""
    
    try:
        import re
        
        pattern = r'https://app\.fireworks\.ai/signup/confirm[^"\s<>]+'
        match = re.search(pattern, test_raw, re.IGNORECASE)
        
        if match:
            link = match.group(0)
            print(f"✅ 链接提取成功!")
            print(f"🔗 链接: {link}")
            return True
        else:
            print("❌ 未找到链接")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_full_flow():
    """测试完整流程（示例）"""
    print("\n" + "=" * 60)
    print("测试4: 完整流程示例")
    print("=" * 60)
    
    flow_steps = [
        "1. 创建临时邮箱",
        "2. 启动浏览器",
        "3. 访问注册页面",
        "4. 填写邮箱",
        "5. 点击 Next",
        "6. 填写密码",
        "7. 提交注册",
        "8. 获取验证链接",
        "9. 访问验证链接",
        "10. 登录账号",
        "11. 完成入门引导",
        "12. 创建 API Key",
    ]
    
    print("完整流程步骤:")
    for step in flow_steps:
        print(f"  {step}")
    
    print("\n⚠️  注意: 完整流程测试需要手动运行 main.py")
    print("  python main.py -n 1")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("浏览器自动化测试脚本")
    print("=" * 60 + "\n")
    
    results = []
    
    # 测试1: 浏览器启动
    results.append(("浏览器启动", test_browser_launch()))
    
    # 测试2: 邮箱创建
    results.append(("邮箱创建", test_email_creation()))
    
    # 测试3: 验证链接提取
    results.append(("验证链接提取", test_verification_link_extraction()))
    
    # 测试4: 完整流程示例
    test_full_flow()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()
