#!/usr/bin/env python3
"""
弹窗处理器测试脚本
用于验证弹窗检测和处理逻辑
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.popup_handler import PopupHandler, PopupType
from core.browser_manager import BrowserManager
from utils.logger import Logger


def test_popup_detection():
    """测试弹窗检测功能"""
    logger = Logger()
    logger.info("=" * 60)
    logger.info("弹窗处理器测试")
    logger.info("=" * 60)
    
    # 测试 PopupType 枚举
    logger.info("\n1. 测试 PopupType 枚举...")
    for popup_type in PopupType:
        logger.info(f"   - {popup_type.name}")
    
    # 测试导入
    logger.info("\n2. 测试模块导入...")
    logger.info("   ✅ PopupHandler 导入成功")
    logger.info("   ✅ PopupType 导入成功")
    
    # 测试姓名生成
    logger.info("\n3. 测试姓名生成...")
    handler = PopupHandler(None)  # 不需要浏览器实例来测试姓名生成
    for i in range(5):
        first, last = handler.generate_name()
        logger.info(f"   - {first} {last}")
    
    logger.info("\n" + "=" * 60)
    logger.info("基础测试完成！")
    logger.info("=" * 60)
    logger.info("\n要进行完整测试，请运行:")
    logger.info("  python main.py -n 1 --headless")


if __name__ == "__main__":
    test_popup_detection()
