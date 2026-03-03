#!/usr/bin/env python3
"""
Fireworks AI 自动注册工具

用法:
    python main.py -n 1                    # 注册1个账号
    python main.py -n 5 --headless         # 注册5个账号，无头模式
    python main.py -n 1 --skip-onboarding  # 跳过入门引导

作者: AI Assistant
版本: 1.0.0
"""
import argparse
import sys
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.browser_manager import BrowserManager, BrowserCrashError
from core.email_service import EmailServiceManager
from services.registration import RegistrationService
from services.onboarding import OnboardingService
from services.api_key_manager import APIKeyManager
from utils.file_handler import FileHandler
from utils.logger import Logger


def main():
    parser = argparse.ArgumentParser(
        description="Fireworks AI 自动注册工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -n 1                           # 注册1个账号
  %(prog)s -n 5 --headless                # 注册5个账号，无头模式
  %(prog)s -n 1 --skip-onboarding         # 跳过入门引导
  %(prog)s -n 1 --skip-apikey             # 跳过 API Key 创建
  %(prog)s -n 1 --retry 5                 # 失败时重试5次
        """
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="注册账号数量 (默认: 1)"
    )
    parser.add_argument(
        "--retry",
        type=int,
        default=3,
        help="失败重试次数 (默认: 3)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式（不显示浏览器窗口）"
    )
    parser.add_argument(
        "--skip-onboarding",
        action="store_true",
        help="跳过入门引导（不领取$5奖励）"
    )
    parser.add_argument(
        "--skip-apikey",
        action="store_true",
        help="跳过 API Key 创建"
    )
    parser.add_argument(
        "--primary-url",
        type=str,
        default="",
        help="主邮箱服务URL（可选）"
    )
    parser.add_argument(
        "--primary-key",
        type=str,
        default="",
        help="主邮箱服务API Key（可选）"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式（保存详细截图和日志）"
    )
    
    args = parser.parse_args()
    
    # 初始化日志
    logger = Logger()
    logger.info("=" * 60)
    logger.info("Fireworks AI 自动注册工具 v1.0.0")
    logger.info("=" * 60)
    logger.info(f"注册数量: {args.count} 个")
    logger.info(f"重试次数: {args.retry} 次")
    logger.info(f"无头模式: {'是' if args.headless else '否'}")
    logger.info(f"跳过入门引导: {'是' if args.skip_onboarding else '否'}")
    logger.info(f"跳过 API Key: {'是' if args.skip_apikey else '否'}")
    logger.info(f"调试模式: {'是' if args.debug else '否'}")
    logger.info("邮箱服务优先级: Primary -> Mail.tm -> SamfunAsia")
    logger.info("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(args.count):
        logger.info(f"\n{'='*60}")
        logger.info(f"开始注册第 {i+1}/{args.count} 个账号...")
        logger.info(f"{'='*60}\n")
        
        browser_mgr = None
        retry_count = 0
        
        while retry_count < args.retry:
            try:
                # 1. 启动浏览器
                logger.info(f"[尝试 {retry_count+1}/{args.retry}] 启动浏览器...")
                browser_mgr = BrowserManager()
                browser = browser_mgr.launch(headless=args.headless)
                logger.info("浏览器启动成功")
                
                # 2. 创建邮箱服务管理器
                logger.info("初始化邮箱服务...")
                email_manager = EmailServiceManager()
                
                # 配置主服务（命令行参数 > 环境变量）
                primary_url = args.primary_url or os.getenv("PRIMARY_EMAIL_URL", "")
                primary_key = args.primary_key or os.getenv("PRIMARY_EMAIL_API_KEY", "")
                
                if primary_url:
                    email_manager.set_primary_config(primary_url, primary_key)
                    logger.info(f"已配置主邮箱服务: {primary_url}")
                
                # 3. 注册
                logger.info("开始注册流程...")
                reg_service = RegistrationService(browser_mgr, email_manager)
                reg_result = reg_service.register()
                
                if not reg_result["success"]:
                    raise Exception(reg_result.get("error", "注册失败"))
                
                service_type = reg_result.get("service_type", "unknown")
                logger.info(f"注册成功！使用邮箱服务: {service_type}")
                logger.info(f"邮箱: {reg_result['email']}")
                logger.info(f"密码: {reg_result['password'][:3]}***{reg_result['password'][-3:]}")
                
                # 4. 入门引导（问卷）
                if not args.skip_onboarding:
                    logger.info("\n开始入门引导流程...")
                    onboarding_service = OnboardingService(browser_mgr)
                    onboarding_result = onboarding_service.complete_onboarding()
                    
                    if onboarding_result["onboarding_completed"]:
                        logger.info("入门引导完成")
                        if onboarding_result.get("account_id"):
                            reg_result["account_id"] = onboarding_result["account_id"]
                        if onboarding_result["credits_claimed"]:
                            logger.info("$5 奖励已领取")
                    else:
                        logger.warning("入门引导未完成，但继续执行...")
                
                # 5. 创建 API Key（带重试机制）
                if not args.skip_apikey:
                    logger.info("\n开始创建 API Key...")
                    api_key_mgr = APIKeyManager(browser_mgr)
                    
                    # API Key 创建重试配置
                    max_api_retries = 3
                    api_success = False
                    
                    for api_attempt in range(max_api_retries):
                        logger.info(f"[API Key 尝试 {api_attempt+1}/{max_api_retries}]...")
                        api_result = api_key_mgr.create_api_key()
                        
                        if api_result["success"]:
                            reg_result["api_key"] = api_result["api_key"]
                            logger.info(f"API Key 创建成功: {api_result['api_key'][:20]}...")
                            api_success = True
                            break
                        else:
                            error_msg = api_result.get("error", "未知错误")
                            logger.warning(f"API Key 创建失败: {error_msg}")
                            
                            if api_attempt < max_api_retries - 1:
                                wait_time = (api_attempt + 1) * 3  # 递增等待时间
                                logger.info(f"等待 {wait_time}s 后重试...")
                                time.sleep(wait_time)
                    
                    if not api_success:
                        logger.warning("API Key 创建最终失败，继续保存账号信息...")
                
                # 保存最终结果
                logger.info("\n保存结果...")
                file_handler = FileHandler()
                file_handler.save_account(reg_result)
                
                success_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"✅ 第 {i+1} 个账号注册成功！")
                logger.info(f"{'='*60}")
                break  # 成功，跳出重试循环
                
            except BrowserCrashError as e:
                retry_count += 1
                logger.error(f"❌ 浏览器崩溃 (尝试 {retry_count}/{args.retry}): {e}")
                
                if browser_mgr:
                    try:
                        browser_mgr.quit()
                    except:
                        pass
                
                if retry_count < args.retry:
                    wait_time = retry_count * 3
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    fail_count += 1
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ 第 {i+1} 个账号注册失败 (尝试 {retry_count}/{args.retry}): {e}")
                
                if browser_mgr:
                    try:
                        browser_mgr.quit()
                    except:
                        pass
                
                if retry_count < args.retry:
                    wait_time = retry_count * 2
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    fail_count += 1
        
        # 关闭浏览器（优雅退出）
        if browser_mgr:
            try:
                logger.info("关闭浏览器...")
                browser_mgr.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.warning(f"浏览器关闭时出错: {e}")
        
        # 账号间延时（默认30秒，避免频繁注册）
        if i < args.count - 1:
            delay = 30
            logger.info(f"\n等待 {delay} 秒后继续下一个账号...")
            time.sleep(delay)
    
    # 总结
    logger.info(f"\n{'='*60}")
    logger.info("注册完成！")
    logger.info(f"成功: {success_count} 个")
    logger.info(f"失败: {fail_count} 个")
    logger.info(f"总计: {args.count} 个")
    logger.info(f"{'='*60}")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
