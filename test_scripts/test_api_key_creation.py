#!/usr/bin/env python3
"""
API Key 创建功能验证测试脚本
用于测试和验证 API Key 创建的成功率

用法:
    python test_scripts/test_api_key_creation.py -e "test@example.com" -p "password"
    python test_scripts/test_api_key_creation.py -f "accounts.json"
    python test_scripts/test_api_key_creation.py -f "accounts.json" --headless
"""
import argparse
import json
import csv
import sys
import os
import time
from datetime import datetime
from typing import List, Dict

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from services.api_key_manager import APIKeyManager
from utils.logger import Logger


class APIKeyTester:
    """API Key 创建测试器"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.logger = Logger()
        self.results = []
        
    def test_single_account(self, email: str, password: str) -> Dict:
        """
        测试单个账号的 API Key 创建
        
        Returns:
            dict: 测试结果
        """
        result = {
            "email": email,
            "password": password,
            "success": False,
            "api_key": None,
            "error": None,
            "duration": 0,
            "timestamp": datetime.now().isoformat(),
            "screenshots": []
        }
        
        browser_mgr = None
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"测试账号: {email}")
            self.logger.info(f"{'='*60}")
            
            # 1. 启动浏览器
            self.logger.info("[1/5] 启动浏览器...")
            browser_mgr = BrowserManager()
            browser = browser_mgr.launch(headless=self.headless)
            self.logger.info("✅ 浏览器启动成功")
            
            # 2. 登录账号
            self.logger.info("[2/5] 登录账号...")
            login_success = self._login(browser_mgr, email, password)
            if not login_success:
                raise Exception("登录失败")
            self.logger.info("✅ 登录成功")
            
            # 3. 创建 API Key
            self.logger.info("[3/5] 创建 API Key...")
            api_key_mgr = APIKeyManager(browser_mgr)
            
            # 最多重试3次
            max_retries = 3
            for attempt in range(max_retries):
                self.logger.info(f"  尝试 {attempt + 1}/{max_retries}...")
                api_result = api_key_mgr.create_api_key()
                
                if api_result["success"]:
                    result["api_key"] = api_result["api_key"]
                    result["success"] = True
                    self.logger.info(f"✅ API Key 创建成功: {api_result['api_key'][:20]}...")
                    break
                else:
                    error_msg = api_result.get("error", "未知错误")
                    self.logger.warning(f"  ❌ 失败: {error_msg}")
                    
                    # 保存调试截图
                    try:
                        screenshot_path = f"debug_apikey_fail_{timestamp}_attempt{attempt+1}.png"
                        browser_mgr.driver.save_screenshot(screenshot_path)
                        result["screenshots"].append(screenshot_path)
                        self.logger.info(f"  📸 已保存截图: {screenshot_path}")
                    except:
                        pass
                    
                    if attempt < max_retries - 1:
                        wait_time = 3
                        self.logger.info(f"  等待 {wait_time}s 后重试...")
                        time.sleep(wait_time)
                    else:
                        result["error"] = error_msg
            
            # 4. 验证 API Key（可选）
            if result["success"] and result["api_key"]:
                self.logger.info("[4/5] 验证 API Key 格式...")
                is_valid = self._validate_api_key(result["api_key"])
                if is_valid:
                    self.logger.info("✅ API Key 格式有效")
                else:
                    self.logger.warning("⚠️ API Key 格式可能有问题")
            
            # 5. 关闭弹窗（如果还有）
            self.logger.info("[5/5] 清理...")
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"❌ 测试失败: {e}")
            
            # 保存错误截图
            try:
                if browser_mgr and browser_mgr.driver:
                    screenshot_path = f"debug_apikey_error_{timestamp}.png"
                    browser_mgr.driver.save_screenshot(screenshot_path)
                    result["screenshots"].append(screenshot_path)
            except:
                pass
                
        finally:
            result["duration"] = round(time.time() - start_time, 2)
            
            # 关闭浏览器
            if browser_mgr:
                try:
                    browser_mgr.quit()
                    self.logger.info("✅ 浏览器已关闭")
                except:
                    pass
        
        self.results.append(result)
        return result
    
    def _login(self, browser_mgr, email: str, password: str) -> bool:
        """
        使用邮箱和密码登录
        
        Args:
            browser_mgr: 浏览器管理器
            email: 邮箱地址
            password: 密码
            
        Returns:
            bool: 是否登录成功
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from utils.config import URLs
            
            driver = browser_mgr.driver
            
            # 访问登录页面
            driver.get(URLs.LOGIN)
            time.sleep(2)
            
            # 点击 Email Login
            email_login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Email")]'))
            )
            email_login_btn.click()
            time.sleep(2)
            
            # 输入邮箱
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.clear()
            email_input.send_keys(email)
            
            # 点击 Next
            next_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
            next_btn.click()
            time.sleep(2)
            
            # 输入密码
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.clear()
            password_input.send_keys(password)
            
            # 点击登录
            login_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_btn.click()
            
            # 等待跳转
            time.sleep(5)
            
            # 检查是否登录成功（URL包含 account 或 onboarding）
            current_url = driver.current_url
            return "account" in current_url or "onboarding" in current_url
            
        except Exception as e:
            self.logger.error(f"登录过程出错: {e}")
            return False
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        验证 API Key 格式
        
        Args:
            api_key: API Key 字符串
            
        Returns:
            bool: 格式是否有效
        """
        if not api_key:
            return False
        
        # Fireworks API Key 格式: fw_ 开头，后跟字母数字
        import re
        pattern = r'^fw_[a-zA-Z0-9]{20,64}$'
        return bool(re.match(pattern, api_key))
    
    def test_from_file(self, filepath: str) -> List[Dict]:
        """
        从文件批量测试账号
        
        Args:
            filepath: 账号文件路径（JSON或CSV格式）
            
        Returns:
            List[Dict]: 所有测试结果
        """
        accounts = self._load_accounts(filepath)
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"批量测试: 共 {len(accounts)} 个账号")
        self.logger.info(f"{'='*60}")
        
        for i, account in enumerate(accounts):
            self.logger.info(f"\n--- 测试第 {i+1}/{len(accounts)} 个账号 ---")
            self.test_single_account(
                account.get("email"),
                account.get("password")
            )
            
            # 账号间延时
            if i < len(accounts) - 1:
                delay = 5
                self.logger.info(f"\n等待 {delay}s 后继续...")
                time.sleep(delay)
        
        return self.results
    
    def _load_accounts(self, filepath: str) -> List[Dict]:
        """从文件加载账号列表"""
        accounts = []
        
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    accounts = data
                else:
                    accounts = [data]
                    
        elif filepath.endswith('.csv'):
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                accounts = list(reader)
        else:
            # 尝试解析文本文件（每行: email,password）
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ',' in line:
                        parts = line.split(',')
                        accounts.append({
                            "email": parts[0],
                            "password": parts[1]
                        })
        
        return accounts
    
    def generate_report(self, output_file: str = None) -> str:
        """
        生成测试报告
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            str: 报告内容
        """
        total = len(self.results)
        success = sum(1 for r in self.results if r["success"])
        failed = total - success
        
        report_lines = [
            "=" * 60,
            "API Key 创建测试报告",
            "=" * 60,
            f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"总计测试: {total} 个账号",
            f"成功: {success} 个 ({success/total*100:.1f}%)",
            f"失败: {failed} 个 ({failed/total*100:.1f}%)",
            "=" * 60,
            "",
            "详细结果:",
            "-" * 60,
        ]
        
        for i, result in enumerate(self.results):
            status = "✅ 成功" if result["success"] else "❌ 失败"
            report_lines.append(f"\n[{i+1}] {status} - {result['email']}")
            report_lines.append(f"    用时: {result['duration']}s")
            if result["success"]:
                report_lines.append(f"    API Key: {result['api_key'][:25]}...")
            else:
                report_lines.append(f"    错误: {result.get('error', '未知')}")
            if result["screenshots"]:
                report_lines.append(f"    截图: {', '.join(result['screenshots'])}")
        
        report = "\n".join(report_lines)
        
        # 输出到控制台
        print("\n" + report)
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            self.logger.info(f"\n📄 报告已保存: {output_file}")
        
        # 保存 JSON 结果
        json_file = output_file.replace('.txt', '.json') if output_file else f"apikey_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.logger.info(f"📄 JSON结果已保存: {json_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="API Key 创建功能验证测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 测试单个账号
  python test_scripts/test_api_key_creation.py -e "test@example.com" -p "password123"
  
  # 从JSON文件批量测试
  python test_scripts/test_api_key_creation.py -f "accounts.json"
  
  # 从CSV文件批量测试（无头模式）
  python test_scripts/test_api_key_creation.py -f "accounts.csv" --headless
  
  # 指定输出报告
  python test_scripts/test_api_key_creation.py -f "accounts.json" -o "test_report.txt"
        """
    )
    
    parser.add_argument("-e", "--email", help="测试单个账号的邮箱")
    parser.add_argument("-p", "--password", help="测试单个账号的密码")
    parser.add_argument("-f", "--file", help="账号列表文件（JSON或CSV格式）")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("-o", "--output", help="输出报告文件路径")
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.file and (not args.email or not args.password):
        parser.error("请提供账号信息: 使用 -e/-p 指定单个账号，或使用 -f 指定账号文件")
    
    # 创建测试器
    tester = APIKeyTester(headless=args.headless)
    
    # 执行测试
    if args.file:
        tester.test_from_file(args.file)
    else:
        tester.test_single_account(args.email, args.password)
    
    # 生成报告
    output_file = args.output or f"apikey_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    tester.generate_report(output_file)
    
    # 返回退出码
    success_count = sum(1 for r in tester.results if r["success"])
    return 0 if success_count == len(tester.results) else 1


if __name__ == "__main__":
    sys.exit(main())
