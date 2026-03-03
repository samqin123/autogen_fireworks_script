# 邮箱服务开发指南

> 多源临时邮箱服务模块，支持自动故障切换和统一管理

## 📋 目录

- [功能特性](#功能特性)
- [支持的邮箱服务](#支持的邮箱服务)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [添加新的邮箱服务](#添加新的邮箱服务)
- [API 参考](#api-参考)
- [配置说明](#配置说明)

---

## ✨ 功能特性

- **多源支持**: 内置 3 种邮箱服务（Primary、Mail.tm、SamfunAsia）
- **自动切换**: 服务故障时自动切换到备用源
- **统一接口**: 所有服务使用相同的 API 接口
- **智能重试**: 支持多 Key 自动切换（如 Primary 服务）
- **验证链接提取**: 自动从邮件中提取 Fireworks 验证链接

---

## 📮 支持的邮箱服务

| 服务 | 类型 | 优先级 | 特点 |
|------|------|--------|------|
| **Primary** | 自定义 API | 1 | 支持多 Key 自动切换，默认使用 chatgpt.uk |
| **Mail.tm** | 公共 API | 2 | 稳定可靠，自动创建账户 |
| **SamfunAsia** | 私有 API | 3 | 备用服务 |

---

## 🚀 快速开始

### 1. 基础用法

```python
from core.email_service import EmailServiceManager

# 创建管理器（自动使用默认配置）
manager = EmailServiceManager()

# 创建邮箱（按优先级自动选择服务）
result = manager.create_email()

print(f"邮箱: {result.email}")
print(f"服务: {result.service_type.value}")
print(f"登录: {result.login_url}")
```

### 2. 获取验证链接

```python
# 获取 Fireworks 验证链接（自动轮询）
verification_link = manager.get_verification_link(timeout=60)

if verification_link:
    print(f"验证链接: {verification_link}")
```

---

## 💡 使用示例

### 示例 1: 自定义 Primary 服务配置

```python
from core.email_service import EmailServiceManager

manager = EmailServiceManager()

# 覆盖默认配置
manager.set_primary_config(
    url="https://your-email-service.com",
    api_key="your-api-key"
)

# 创建邮箱
result = manager.create_email()
```

### 示例 2: 环境变量配置

创建 `.env` 文件：

```bash
PRIMARY_EMAIL_URL=https://mail.chatgpt.org.uk
PRIMARY_EMAIL_API_KEY=sk-4rt8HwcA
```

代码自动读取：

```python
from dotenv import load_dotenv
import os

load_dotenv()

manager = EmailServiceManager()
# 默认已使用环境变量中的配置
```

### 示例 3: 使用特定服务

```python
from core.email_service import (
    EmailServiceManager,
    SamfunAsiaEmailService,
    MailTMService
)

# 直接使用 SamfunAsia
service = SamfunAsiaEmailService()
email, jwt = service.create_email()

# 直接使用 Mail.tm
service = MailTMService()
email = service.create_account()
```

### 示例 4: 获取邮件内容

```python
# 获取所有邮件
emails = manager.get_emails()

for email in emails:
    print(f"来自: {email.get('from_address')}")
    print(f"主题: {email.get('subject')}")
    print(f"内容: {email.get('html_content', '')[:200]}")
```

---

## 🔧 添加新的邮箱服务

### 步骤 1: 创建服务类

```python
class MyEmailService:
    """自定义邮箱服务"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.email: Optional[str] = None
    
    def create_email(self) -> str:
        """创建邮箱，返回邮箱地址"""
        # 实现创建逻辑
        self.email = "user@example.com"
        return self.email
    
    def get_emails(self) -> List[Dict]:
        """获取邮件列表"""
        # 实现获取逻辑
        return []
    
    def get_verification_link(self, timeout: int = 60) -> Optional[str]:
        """获取验证链接（可选）"""
        # 实现验证链接提取
        return None
```

### 步骤 2: 注册到管理器

```python
# 在 EmailServiceType 枚举中添加新类型
class EmailServiceType(Enum):
    SAMFUN_ASIA = "samfun_asia"
    PRIMARY = "primary"
    MAIL_TM = "mail_tm"
    MY_SERVICE = "my_service"  # 新增

# 在 EmailServiceManager 中添加
class EmailServiceManager:
    def __init__(self):
        self.service_order = [
            EmailServiceType.MY_SERVICE,  # 设置优先级
            EmailServiceType.PRIMARY,
            EmailServiceType.MAIL_TM,
        ]
    
    def _create_service(self, service_type):
        if service_type == EmailServiceType.MY_SERVICE:
            return MyEmailService()
        # ... 其他服务
    
    def create_email(self):
        if service_type == EmailServiceType.MY_SERVICE:
            email = service.create_email()
            return EmailServiceResult(
                email=email,
                service_type=service_type,
                service_instance=service,
                login_url="https://my-service.com"
            )
```

---

## 📚 API 参考

### EmailServiceManager

管理器类，负责多源邮箱服务的统一管理和自动切换。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `service_order` | List[EmailServiceType] | 服务优先级列表 |
| `primary_url` | str | Primary 服务 URL |
| `primary_key` | str | Primary 服务 API Key |

#### 方法

##### `set_primary_config(url: str, api_key: str = "")`

设置 Primary 服务配置（覆盖默认值）。

```python
manager.set_primary_config(
    url="https://mail.chatgpt.org.uk",
    api_key="sk-xxx"
)
```

##### `create_email() -> EmailServiceResult`

创建临时邮箱，按优先级自动选择服务。

**返回**: EmailServiceResult 对象

**异常**: 所有服务都失败时抛出 Exception

```python
result = manager.create_email()
print(result.email)        # 邮箱地址
print(result.service_type) # 使用的服务类型
print(result.login_url)    # 邮箱登录/查看 URL
```

##### `get_verification_link(timeout: int = 60) -> Optional[str]`

获取 Fireworks 验证链接。

**参数**:
- `timeout`: 超时时间（秒），默认 60

**返回**: 验证链接或 None

```python
link = manager.get_verification_link(timeout=120)
```

##### `get_emails() -> List[Dict]`

获取邮件列表。

**返回**: 邮件字典列表

##### `reset_failed_services()`

重置失败服务记录，下次创建时重新尝试所有服务。

```python
# 某次创建失败后，重置状态
manager.reset_failed_services()
```

---

### EmailServiceResult

邮箱服务结果数据类。

| 字段 | 类型 | 说明 |
|------|------|------|
| `email` | str | 邮箱地址 |
| `service_type` | EmailServiceType | 使用的服务类型 |
| `service_instance` | Any | 服务实例（用于后续操作） |
| `login_url` | str | 邮箱登录/查看 URL |

---

### 各服务类 API

#### PrimaryEmailService

```python
service = PrimaryEmailService(
    base_url="https://mail.chatgpt.org.uk",
    api_key="gpt-test"  # 可选，默认使用内置 Key
)

# 创建邮箱（自动尝试多个 Key）
email = service.create_email()

# 获取邮件列表
emails = service.get_emails()

# 获取验证链接
link = service.get_verification_link(timeout=60)
```

#### MailTMService

```python
service = MailTMService()

# 创建账户
email = service.create_account()

# 获取 Token（部分操作需要）
service.get_token()

# 获取邮件列表
messages = service.get_messages()

# 获取邮件内容
content = service.get_message_content(message_id)

# 获取验证链接
link = service.get_verification_link(timeout=60)
```

#### SamfunAsiaEmailService

```python
service = SamfunAsiaEmailService()

# 创建邮箱（返回邮箱和 JWT）
email, jwt = service.create_email()

# 获取邮件列表
emails = service.get_emails()

# 获取验证链接
link = service.get_verification_link(timeout=60)
```

---

## ⚙️ 配置说明

### 配置文件 (.env)

```bash
# Primary 邮箱服务配置（可选，有默认值）
PRIMARY_EMAIL_URL=https://mail.chatgpt.org.uk
PRIMARY_EMAIL_API_KEY=sk-4rt8HwcA

# 其他配置
BROWSER_HEADLESS=true
```

### 默认配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DEFAULT_PRIMARY_URL` | `https://mail.chatgpt.org.uk` | Primary 服务地址 |
| `DEFAULT_PRIMARY_KEY` | `gpt-test` | Primary 默认 API Key |
| `service_order` | `[PRIMARY, MAIL_TM, SAMFUN_ASIA]` | 服务优先级 |

### 修改优先级

```python
manager = EmailServiceManager()

# 自定义优先级
manager.service_order = [
    EmailServiceType.MAIL_TM,       # 优先使用 Mail.tm
    EmailServiceType.PRIMARY,
    EmailServiceType.SAMFUN_ASIA,
]
```

---

## 🔍 故障排查

### 问题 1: 所有服务都失败

```python
# 重置失败记录后重试
manager.reset_failed_services()
result = manager.create_email()
```

### 问题 2: Primary Key 失效

```python
# 使用自定义 Key
manager.set_primary_config(
    api_key="your-new-api-key"
)
```

### 问题 3: 获取验证链接超时

```python
# 增加超时时间
link = manager.get_verification_link(timeout=120)
```

---

## 📄 完整示例代码

```python
#!/usr/bin/env python3
"""
邮箱服务使用示例
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.email_service import EmailServiceManager

def main():
    # 1. 创建管理器
    manager = EmailServiceManager()
    
    # 2. 创建邮箱
    print("创建临时邮箱...")
    result = manager.create_email()
    
    print(f"✅ 邮箱创建成功!")
    print(f"   邮箱: {result.email}")
    print(f"   服务: {result.service_type.value}")
    print(f"   登录: {result.login_url}")
    
    # 3. 获取验证链接
    print("\n等待验证邮件...")
    link = manager.get_verification_link(timeout=60)
    
    if link:
        print(f"✅ 验证链接: {link}")
    else:
        print("❌ 未找到验证链接")

if __name__ == "__main__":
    main()
```

---

## 📝 注意事项

1. **API Key 安全**: 不要将真实的 API Key 提交到代码仓库
2. **超时设置**: 根据网络情况调整超时时间
3. **错误处理**: 建议捕获异常并处理服务切换
4. **日志记录**: 可通过设置 logger 查看详细日志

---

**文档版本**: 1.0.0  
**更新日期**: 2026-03-02
