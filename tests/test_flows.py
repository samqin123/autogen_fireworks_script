"""
测试用例 - 注册流程测试
"""
import pytest
import time
import os
import sys

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPasswordGeneration:
    """密码生成测试"""
    
    def test_password_meets_requirements(self):
        """测试密码生成器符合要求"""
        from services.registration import RegistrationService
        
        service = RegistrationService(None, None)
        password = service.generate_password()
        
        assert len(password) >= 8, "密码长度至少8位"
        assert any(c.islower() for c in password), "密码包含小写字母"
        assert any(c.isupper() for c in password), "密码包含大写字母"
        assert any(c.isdigit() for c in password), "密码包含数字"
        assert any(c in "!@#$%^&*" for c in password), "密码包含特殊字符"
        print(f"生成的密码: {password[:3]}***{password[-3:]}")
    
    def test_password_randomness(self):
        """测试密码随机性"""
        from services.registration import RegistrationService
        
        service = RegistrationService(None, None)
        passwords = [service.generate_password() for _ in range(10)]
        
        # 检查没有重复
        assert len(set(passwords)) == 10, "生成的密码应该各不相同"


class TestEmailService:
    """邮箱服务测试"""
    
    def test_samfunasia_create_email(self):
        """测试 SamfunAsia 创建邮箱"""
        from core.email_service import SamfunAsiaEmailService
        
        service = SamfunAsiaEmailService()
        try:
            email, jwt = service.create_email()
            assert email, "邮箱创建失败"
            assert "@" in email, "邮箱格式不正确"
            assert "samfun.asia" in email, "邮箱域名不正确"
            assert jwt, "JWT 获取失败"
            print(f"创建邮箱成功: {email}")
        except Exception as e:
            pytest.skip(f"SamfunAsia 服务不可用: {e}")
    
    def test_mailtm_create_account(self):
        """测试 Mail.tm 创建账户"""
        from core.email_service import MailTMService
        
        service = MailTMService()
        try:
            email = service.create_account()
            assert email, "邮箱创建失败"
            assert "@" in email, "邮箱格式不正确"
            print(f"创建邮箱成功: {email}")
        except Exception as e:
            pytest.skip(f"Mail.tm 服务不可用: {e}")
    
    def test_email_manager_priority(self):
        """测试邮箱管理器优先级"""
        from core.email_service import EmailServiceManager, EmailServiceType
        
        manager = EmailServiceManager()
        
        # 检查默认优先级 (Primary -> Mail.tm -> SamfunAsia)
        assert manager.service_order[0] == EmailServiceType.PRIMARY
        assert manager.service_order[1] == EmailServiceType.MAIL_TM
        assert manager.service_order[2] == EmailServiceType.SAMFUN_ASIA


class TestOnboarding:
    """入门引导测试"""
    
    def test_name_generation(self):
        """测试姓名生成"""
        from services.onboarding import OnboardingService
        
        service = OnboardingService(None)
        first, last = service.generate_name()
        
        assert first, "名字不能为空"
        assert last, "姓氏不能为空"
        assert first[0].isupper(), "名字首字母大写"
        assert last[0].isupper(), "姓氏首字母大写"
        print(f"生成的姓名: {first} {last}")
    
    def test_questionnaire_options(self):
        """测试问卷选项"""
        from services.onboarding import OnboardingService
        
        service = OnboardingService(None)
        
        # 测试目标选项
        assert len(service.goals_options) >= 5, "目标选项数量不足"
        assert "Prototype with open models" in service.goals_options
        
        # 测试用例选项
        assert len(service.use_cases_options) >= 4, "用例选项数量不足"
        assert "Code Assistance" in service.use_cases_options
        
        # 测试随机选择
        selected = random.sample(service.goals_options, 2)
        assert len(selected) == 2
        assert all(opt in service.goals_options for opt in selected)


class TestFileHandler:
    """文件处理器测试"""
    
    def test_save_account(self, tmp_path):
        """测试保存账号信息"""
        from utils.file_handler import FileHandler
        import datetime
        
        # 使用临时目录
        handler = FileHandler(output_dir=str(tmp_path))
        
        test_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "api_key": "fw_test123456789",
            "account_id": "test-account-123"
        }
        
        handler.save_account(test_data)
        
        # 验证文件存在
        assert os.path.exists(handler.results_file), "结果文件未创建"
        
        # 验证内容
        with open(handler.results_file, 'r') as f:
            content = f.read()
            assert "test@example.com" in content
            assert "fw_test123456789" in content


class TestLogger:
    """日志测试"""
    
    def test_logger_levels(self, capsys):
        """测试日志级别"""
        from utils.logger import Logger
        
        logger = Logger("Test")
        
        logger.info("信息日志")
        logger.warning("警告日志")
        logger.error("错误日志")
        
        captured = capsys.readouterr()
        assert "信息日志" in captured.out or "信息日志" in captured.err
        assert "警告日志" in captured.err
        assert "错误日志" in captured.err


class TestPopupHandler:
    """弹窗处理器测试"""
    
    def test_name_generation(self):
        """测试弹窗处理器姓名生成"""
        from services.popup_handler import PopupHandler
        
        handler = PopupHandler(None)
        first, last = handler.generate_name()
        
        assert first, "名字不能为空"
        assert last, "姓氏不能为空"
        assert first[0].isupper(), "名字首字母大写"
        assert last[0].isupper(), "姓氏首字母大写"
        print(f"生成的姓名: {first} {last}")
    
    def test_popup_type_enum(self):
        """测试弹窗类型枚举"""
        from services.popup_handler import PopupType
        
        # 测试所有枚举值
        assert PopupType.UNKNOWN.name == "UNKNOWN"
        assert PopupType.NONE.name == "NONE"
        assert PopupType.PROFILE_COMPLETION.name == "PROFILE_COMPLETION"
        assert PopupType.SURVEY.name == "SURVEY"
        
        # 测试枚举列表
        types = list(PopupType)
        assert len(types) >= 5, "弹窗类型数量不足"


# 导入 random 用于测试
import random


if __name__ == "__main__":
    print("运行测试...")
    pytest.main([__file__, "-v"])
