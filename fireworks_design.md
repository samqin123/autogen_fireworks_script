# Fireworks AI 自动注册技术研究设计文档

> **用途声明**：本文档仅用于自动化测试技术的学习与研究，所有操作需严格遵守相关法律法规和服务条款。

---

## 1. 法律合规声明

### 1.1 使用限制
- **仅供学习研究**：本文档及相应代码仅用于自动化测试技术的学习与研究目的
- **遵守 ToS**：使用本技术必须遵守 Fireworks AI 的服务条款 (Terms of Service)
- **合规测试**：仅用于合法的安全测试和自动化流程研究
- **数据保护**：妥善处理所有生成的测试数据，不得用于非法用途

### 1.2 技术伦理
- 不得用于批量注册恶意账号
- 不得用于绕过平台安全机制
- 不得用于数据爬取或资源滥用
- 测试结果仅用于技术改进和漏洞报告

---

## 2. 项目概述

### 2.1 目标
构建一个完整的 Fireworks AI 账号自动化注册流程，涵盖：
- 邮箱验证自动化
- 账号注册流程
- API Key 申请与获取

### 2.2 技术栈
| 组件 | 技术 | 用途 |
|------|------|------|
| 浏览器自动化 | Selenium / undetected-chromedriver | 模拟用户操作 |
| 邮箱服务 | mail.tm / 自建邮箱 | 接收验证邮件 |
| 编程语言 | Python 3.12+ | 核心逻辑 |
| 数据存储 | JSON / SQLite | 账号信息持久化 |

---

## 3. 系统架构

### 3.1 整体流程图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   开始注册      │────▶│   获取临时邮箱   │────▶│   访问注册页面   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
┌─────────────────┐     ┌─────────────────┐              ▼
│   完成注册      │◀────│   邮箱验证      │◀────┌─────────────────┐
│   保存信息      │     │   点击链接      │     │   填写注册信息   │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   入门引导      │────▶│   完成问卷      │────▶│   领取 $5       │
│  (Onboarding)   │     │  (随机勾选)     │     │   奖励          │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  申请 API Key   │────▶│  捕获 API Key   │────▶│   登录账号      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 3.2 模块划分

```
fireworks_auto_register/
├── core/
│   ├── __init__.py
│   ├── browser_manager.py      # 浏览器管理（启动、健康监控）
│   ├── email_service.py        # 邮箱服务（mail.tm / 自建邮箱）
│   └── config.py               # 配置管理
├── services/
│   ├── __init__.py
│   ├── registration.py         # 注册流程核心
│   ├── verification.py         # 邮箱验证处理
│   └── api_key_manager.py      # API Key 申请管理
├── utils/
│   ├── __init__.py
│   ├── logger.py               # 日志工具
│   ├── helpers.py              # 通用工具函数
│   └── validators.py           # 数据验证
├── tests/
│   └── test_flows.py           # 自动化测试用例
├── main.py                     # 主入口
└── requirements.txt
```

---

## 4. 页面元素分析

### 4.1 登录/注册入口

| 页面 | URL |
|------|-----|
| 登录页 | `https://app.fireworks.ai/login` |
| 注册页 | `https://app.fireworks.ai/signup` |

### 4.2 Signup 页面

**URL**: `https://app.fireworks.ai/signup`

#### 4.2.1 邮箱输入框
```html
<input type="email" 
       id="email-display" 
       name="email"
       class="focus:ring-input-active focus:border-input-active ..."
       data-sentry-element="InputWithLabel"
       data-sentry-source-file="SignupSection.tsx">
```

**定位策略**:
- 首选: `#email-display`
- 备选: `input[name="email"]`
- XPath: `//input[@id='email-display']`

#### 4.2.2 Next 按钮
```html
<button type="submit"
        class="font-bold whitespace-nowrap rounded cursor-pointer ..."
        data-sentry-component="UnwrappedButton"
        data-sentry-source-file="Button.tsx">
    Next
</button>
```

**定位策略**:
- 首选: `button[type="submit"]`
- 备选: `//button[contains(text(), 'Next')]`

### 4.3 密码设置页

**URL**: `https://app.fireworks.ai/login/email?redirectURI=%2Faccount%2Fhome`

**特点**: 邮箱从 signup 页面带入，不可编辑

#### 4.3.1 邮箱显示框（只读）
```html
<input id="email" 
       name="email" 
       disabled
       data-testid="login-form-email">
```

#### 4.3.2 密码输入框
```html
<input id="password" 
       type="password" 
       name="password"
       autocomplete="off"
       data-testid="login-form-password">
```

**定位策略**:
- CSS: `#password`
- XPath: `//input[@id='password']`

### 4.4 完整注册表单

**URL**: `https://app.fireworks.ai/signup`（后续步骤）

#### 4.4.1 邮箱显示（禁用状态）
```html
<input type="email" 
       id="email-display" 
       name="email" 
       disabled>
```

#### 4.4.2 密码输入
```html
<input id="password" 
       type="password" 
       name="password"
       placeholder="Enter your password">
```

#### 4.4.3 确认密码
```html
<input id="confirm-password" 
       type="password" 
       name="confirmPassword"
       placeholder="Re-enter your password">
```

#### 4.4.4 密码规范要求
- ✅ 至少 8 个字符
- ✅ 包含小写字母
- ✅ 包含大写字母
- ✅ 包含数字
- ✅ 包含特殊字符
- ✅ 两次输入一致

#### 4.4.5 Create Account 按钮
```html
<button type="submit"
        class="font-bold whitespace-nowrap rounded cursor-pointer ...">
    Create Account
</button>
```

### 4.5 邮箱验证页面

**页面提示**: 
> "A verification email has been sent to c***@1***. Please check your email..."

#### 4.5.1 验证邮件处理
- 从邮箱服务获取最新邮件
- 解析 HTML 内容，正则匹配验证链接
- 模拟点击验证链接

#### 4.5.2 Continue 按钮
```html
<button type="button"
        class="font-bold whitespace-nowrap rounded cursor-pointer ...">
    Continue
</button>
```

**定位策略**:
- CSS: `button:has-text('Continue')`
- XPath: `//button[contains(text(), 'Continue')]`

### 4.6 入门引导页面 (Onboarding)

**URL**: `https://app.fireworks.ai/onboarding`

#### 4.6.1 账号信息填写
```html
<input id="account-id" value="afeja25e-dncn0biea67" disabled>
<input id="first-name" placeholder="First Name">
<input id="last-name" placeholder="Last Name">
```

**定位策略**:
- First Name: `input[placeholder="First Name"]` 或 `//input[@id="first-name"]`
- Last Name: `input[placeholder="Last Name"]` 或 `//input[@id="last-name"]`
- Continue 按钮: `button:has-text('Continue')`

#### 4.6.2 问卷页面（领取 $5 奖励）
**⚠️ 重要：必须完成问卷才能领取 $5 免费额度**

页面标题: "Want free $5 credit? Answer 2 questions"

**问题 1**: "What are your goals for using Fireworks?"
选项（多选）：
- Prototype with open models
- Flexible capacity for experimentation
- Flexible capacity for production
- Faster speeds or lower costs
- Fine-tune models for quality
- High reliability inference for production
- Migrate from closed to open models
- Migrate from self-hosting to third-party
- Other

**问题 2**: "What are your primary use cases?"
选项（多选）：
- Code Assistance
- Conversational AI
- Agentic AI
- Search
- Multimedia RAG
- Other

**元素定位**:
```python
# 问卷选项定位（示例）
goals_checkboxes = [
    "Prototype with open models",
    "Flexible capacity for experimentation",
    "Faster speeds or lower costs",
    # ... 其他选项
]

use_cases_checkboxes = [
    "Code Assistance",
    "Conversational AI",
    "Agentic AI",
    # ... 其他选项
]

# 提交按钮
submit_button = "button:has-text('Submit to get $5 Credits')"
```

**⚠️ 注意事项**:
- **不要点击 "Skip" 按钮**，否则无法领取 $5 奖励
- 必须随机选择至少一个选项（建议每个问题选择 2-3 个）
- 提交后等待页面跳转

### 4.7 API Key 管理页面

**URL**: `https://app.fireworks.ai/settings/users/api-keys`

### 4.6 API Key 管理页面

**URL**: `https://app.fireworks.ai/settings/users/api-keys`

#### 4.6.1 Create API Key 按钮
```html
<a href="/settings/users/api-keys"
   class="inline-flex content-center items-center ...">
    <span class="text-brand-primary">
        <svg>...</svg>
    </span>
    Create API Key
</a>
```

#### 4.6.2 弹窗内 Create API Key 按钮
```html
<button type="button"
        id="radix-_R_clfiv5ubtaknmfb_"
        aria-haspopup="menu"
        data-sentry-source-file="AddNewKeyModal.tsx">
    <svg>...</svg>
    Create API Key
    <svg>...</svg>
</button>
```

---

## 5. 核心流程设计

### 5.1 注册流程

```python
async def register_account():
    """
    完整的注册流程
    """
    # 1. 获取临时邮箱
    email_service = EmailService()
    email = await email_service.create_account()
    
    # 2. 启动浏览器
    browser = await BrowserManager.launch()
    
    try:
        # 3. 访问注册页面
        await browser.goto("https://app.fireworks.ai/signup")
        
        # 4. 输入邮箱并点击 Next
        await browser.fill("#email-display", email)
        await browser.click("button[type='submit']")
        
        # 5. 等待跳转到密码设置页
        await browser.wait_for_url("/login/email")
        
        # 6. 生成符合规范的密码
        password = generate_secure_password()
        
        # 7. 输入密码
        await browser.fill("#password", password)
        await browser.fill("#confirm-password", password)
        
        # 8. 提交注册
        await browser.click("button[type='submit']")
        
        # 9. 等待验证邮件
        await browser.wait_for_text("verification email has been sent")
        
        # 10. 获取并点击验证链接
        verification_link = await email_service.get_verification_link()
        await browser.goto(verification_link)
        
        # 11. 点击 Continue
        await browser.click("button:has-text('Continue')")
        
        # 12. 保存账号信息
        save_account_info(email, password)
        
        return {"email": email, "password": password, "success": True}
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return {"success": False, "error": str(e)}
    finally:
        await browser.close()
```

### 5.2 入门引导与问卷流程（领取 $5 奖励）

**⚠️ 重要提示**：必须完成问卷才能领取 $5 免费额度，**不要点击 Skip**！

```python
async def complete_onboarding(browser):
    """
    完成入门引导和问卷（领取 $5 奖励）
    
    页面流程：
    1. 填写 Account ID、First Name、Last Name
    2. 勾选同意条款
    3. 完成问卷（2个问题，随机选择选项）
    4. 提交获取 $5 Credits
    """
    # 1. 等待入门引导页面
    await browser.wait_for_text("Welcome to Fireworks")
    
    # 2. 填写个人信息
    await browser.fill('input[placeholder="First Name"]', generate_first_name())
    await browser.fill('input[placeholder="Last Name"]', generate_last_name())
    
    # 3. 勾选同意条款
    await browser.click('input[type="checkbox"]')  # 同意条款复选框
    
    # 4. 点击 Continue
    await browser.click('button:has-text("Continue")')
    
    # 5. 等待问卷页面（关键步骤！）
    await browser.wait_for_text("Want free $5 credit")
    
    # 6. 随机选择问卷选项（问题1：目标）
    goals_options = [
        "Prototype with open models",
        "Flexible capacity for experimentation",
        "Faster speeds or lower costs",
        "Fine-tune models for quality",
        "Code Assistance",
        "Conversational AI"
    ]
    # 随机选择 2-3 个选项
    selected_goals = random.sample(goals_options, random.randint(2, 3))
    for option in selected_goals:
        # 通过文本定位复选框
        checkbox = await browser.find_element(f'//label[contains(text(), "{option}")]')
        await checkbox.click()
        await asyncio.sleep(0.5)  # 模拟人类操作间隔
    
    # 7. 随机选择问卷选项（问题2：用例）
    use_cases_options = [
        "Code Assistance",
        "Conversational AI",
        "Agentic AI",
        "Search",
        "Multimedia RAG"
    ]
    # 随机选择 1-2 个选项
    selected_use_cases = random.sample(use_cases_options, random.randint(1, 2))
    for option in selected_use_cases:
        checkbox = await browser.find_element(f'//label[contains(text(), "{option}")]')
        await checkbox.click()
        await asyncio.sleep(0.5)
    
    # 8. 提交问卷（领取 $5）
    await browser.click('button:has-text("Submit to get $5 Credits")')
    
    # 9. 等待跳转到主页
    await browser.wait_for_url("/account/home")
    
    logger.info("Onboarding completed, $5 credits claimed!")
    return {"credits": "$5.00", "onboarding_completed": True}
```

**问卷选项完整列表**：

| 问题 | 可选值 |
|-----|-------|
| What are your goals for using Fireworks? | Prototype with open models, Flexible capacity for experimentation, Flexible capacity for production, Faster speeds or lower costs, Fine-tune models for quality, High reliability inference for production, Migrate from closed to open models, Migrate from self-hosting to third-party, Other |
| What are your primary use cases? | Code Assistance, Conversational AI, Agentic AI, Search, Multimedia RAG, Other |

**错误示范（不要这样做）**:
```python
# ❌ 错误：跳过问卷，无法领取 $5
await browser.click('button:has-text("Skip")')  # 不要这样做！
```

**正确做法**:
```python
# ✅ 正确：随机选择选项并提交
await browser.click('button:has-text("Submit to get $5 Credits")')
```

### 5.3 API Key 申请流程

```python
async def create_api_key(browser, key_name: str = None):
    """
    申请 API Key
    
    重要: API Key 只显示一次，必须立即保存
    """
    if not key_name:
        key_name = f"auto-gen-{uuid.uuid4().hex[:8]}"
    
    # 1. 访问 API Keys 页面
    await browser.goto("https://app.fireworks.ai/settings/users/api-keys")
    
    # 2. 点击 Create API Key
    await browser.click("button:has-text('Create API Key')")
    
    # 3. 等待弹窗
    await browser.wait_for_selector("[role='dialog']")
    
    # 4. 输入 Key 名称
    await browser.fill("input[placeholder*='name' i]", key_name)
    
    # 5. 点击 Generate Key
    await browser.click("button:has-text('Generate Key')")
    
    # 6. 等待 Key 生成（关键！只显示一次）
    await browser.wait_for_selector("code, input[type='text']")
    
    # 7. 捕获 API Key
    api_key = await browser.get_text("code") or \
              await browser.get_input_value("input[type='text']")
    
    # 8. 验证格式（fw_ 开头）
    if not api_key.startswith("fw_"):
        raise ValueError(f"Invalid API Key format: {api_key}")
    
    # 9. 立即保存（关键！）
    save_api_key(key_name, api_key)
    
    # 10. 点击复制（可选）
    await browser.click("button[aria-label*='copy' i]")
    
    # 11. 关闭弹窗
    await browser.click("button:has-text('Close')")
    
    return {"name": key_name, "key": api_key}
```

---

## 6. 异常处理设计

### 6.1 常见异常场景

| 异常类型 | 处理方式 | 重试策略 |
|---------|---------|---------|
| 页面加载超时 | 刷新页面，重新定位元素 | 3次，间隔2秒 |
| 元素未找到 | 切换定位策略（CSS → XPath） | 5次，间隔1秒 |
| 邮箱服务不可用 | 切换到备用邮箱服务 | 立即切换 |
| 验证码获取失败 | 等待后重试 | 10次，间隔3秒 |
| 密码不符合规范 | 重新生成密码 | 立即重试 |
| API Key 重名 | 添加随机后缀 | 立即重试 |
| 浏览器崩溃 | 重启浏览器，恢复状态 | 3次，暂停5分钟 |
| IP 限制 | 记录错误，暂停注册 | 人工介入 |

### 6.2 错误处理代码示例

```python
class RegistrationError(Exception):
    """注册过程错误基类"""
    pass

class EmailVerificationError(RegistrationError):
    """邮箱验证错误"""
    pass

class BrowserCrashError(RegistrationError):
    """浏览器崩溃错误"""
    pass

async def safe_execute(func, max_retries=3, delay=2):
    """带重试的安全执行器"""
    for attempt in range(max_retries):
        try:
            return await func()
        except BrowserCrashError:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Browser crashed, restarting... (attempt {attempt + 1})")
            await asyncio.sleep(delay * (attempt + 1))
        except EmailVerificationError:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Email verification failed, retrying...")
            await asyncio.sleep(delay)
```

---

## 7. 安全考虑

### 7.1 数据安全
- 密码使用强随机生成（16+ 字符，包含大小写、数字、特殊字符）
- 敏感信息存储使用加密
- 临时邮箱定期清理
- 日志中脱敏处理（隐藏邮箱、密码、API Key）

### 7.2 操作安全
- 添加随机延迟模拟真人操作
- 使用 undetected-chromedriver 避免检测
- 控制注册频率（间隔 15-30 秒）
- 浏览器指纹随机化

### 7.3 风控规避
```python
HUMAN_LIKE_DELAYS = {
    "typing_min": 0.05,      # 最小输入延迟
    "typing_max": 0.15,      # 最大输入延迟
    "click_delay": 0.5,      # 点击后等待
    "page_wait": (2, 5),     # 页面加载等待（随机范围）
    "between_accounts": 15   # 账号间间隔
}

def human_like_typing(element, text: str):
    """模拟人类输入"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(
            HUMAN_LIKE_DELAYS["typing_min"],
            HUMAN_LIKE_DELAYS["typing_max"]
        ))
```

---

## 8. 数据持久化

### 8.1 账号信息存储格式

```json
{
  "fireworks_accounts": [
    {
      "id": "uuid-v4",
      "email": "xxx@tempmail.com",
      "password_encrypted": "base64-encoded-encrypted-password",
      "api_keys": [
        {
          "name": "auto-gen-abc123",
          "key": "fw_xxxxxxxxxxxxxxxx",
          "created_at": "2026-02-28T12:00:00Z",
          "status": "active"
        }
      ],
      "registration_date": "2026-02-28T12:00:00Z",
      "email_service": "mail.tm",
      "status": "active",
      "metadata": {
        "browser_fingerprint": "...",
        "ip_address": "xxx.xxx.xxx.xxx"
      }
    }
  ]
}
```

### 8.2 输出文件结构

```
output/
├── accounts/
│   ├── account-{email}-{date}.json    # 单个账号详情
│   └── summary.json                    # 所有账号汇总
├── api_keys/
│   └── api_keys_{date}.csv             # API Key 列表
└── logs/
    └── registration_{date}.log         # 运行日志
```

---

## 9. 测试计划

### 9.1 单元测试

```python
# tests/test_password_generator.py
def test_password_meets_requirements():
    """测试密码生成器符合规范"""
    password = generate_secure_password()
    assert len(password) >= 8
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in "!@#$%^&*" for c in password)

# tests/test_email_service.py
async def test_email_verification_flow():
    """测试邮箱验证流程"""
    service = MailTMService()
    email = await service.create_account()
    # 发送测试邮件
    # 验证是否能正确获取
```

### 9.2 集成测试

```python
# tests/test_full_flow.py
async def test_complete_registration():
    """测试完整注册流程"""
    result = await register_account()
    assert result["success"] is True
    assert "email" in result
    assert "password" in result
    # 验证可以登录
    # 验证可以创建 API Key
```

### 9.3 测试检查清单

- [ ] 邮箱服务可用性测试
- [ ] 浏览器启动和关闭测试
- [ ] 页面元素定位测试
- [ ] 注册流程端到端测试
- [ ] 邮箱验证解析测试
- [ ] 入门引导页面测试（Onboarding）
- [ ] 问卷提交测试（随机勾选选项）
- [ ] $5 奖励领取验证测试
- [ ] API Key 创建和捕获测试
- [ ] 异常处理和重试测试
- [ ] 数据持久化测试

---

## 10. 运行和部署

### 10.1 环境要求

```bash
# Python 3.12+
python --version

# Chrome 浏览器
google-chrome --version

# 依赖安装
pip install -r requirements.txt
```

### 10.2 配置文件

```yaml
# config.yaml
browser:
  headless: false
  window_size: [1920, 1080]
  user_data_dir: "./browser_data"

email:
  primary_service: "mail.tm"
  fallback_service: "chatgpt.org.uk"
  timeout: 60

registration:
  max_retries: 3
  delay_between_accounts: 15
  human_like_typing: true

security:
  encrypt_passwords: true
  log_level: "INFO"
```

### 10.3 运行命令

```bash
# 注册 1 个账号（默认）
python main.py

# 注册 5 个账号
python main.py -n 5

# 注册并创建 API Key
python main.py -n 3 --create-api-key

# 调试模式（显示浏览器窗口）
python main.py --debug
```

---

## 11. 监控和日志

### 11.1 日志格式

```
[2026-02-28 12:00:01] [INFO] Starting registration process
[2026-02-28 12:00:02] [INFO] Created temp email: xxx@mail.tm
[2026-02-28 12:00:03] [INFO] Navigating to signup page
[2026-02-28 12:00:05] [INFO] Filled email field
[2026-02-28 12:00:06] [WARN] Primary email service failed, switching to fallback
[2026-02-28 12:00:10] [INFO] Verification email received
[2026-02-28 12:00:15] [INFO] Account created successfully: xxx@mail.tm
[2026-02-28 12:00:30] [INFO] API Key created: fw_*** (masked)
```

### 11.2 监控指标

| 指标 | 说明 |
|-----|------|
| 成功率 | 成功注册数 / 尝试次数 |
| 平均耗时 | 单次注册平均用时 |
| 邮箱服务可用性 | 各邮箱服务的成功率 |
| API Key 捕获率 | 成功获取 API Key 的比例 |

---

## 12. 参考资料

### 12.1 相关文档
- [Fireworks AI Documentation](https://docs.fireworks.ai/)
- [Selenium WebDriver Documentation](https://www.selenium.dev/documentation/)
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

### 12.2 学习资源
- 浏览器自动化最佳实践
- 反爬虫技术原理
- 自动化测试框架设计

---

## 13. 附录：元素速查表

### 13.1 CSS 选择器

| 元素 | 选择器 |
|-----|--------|
| 邮箱输入 | `#email-display` |
| 密码输入 | `#password` |
| 确认密码 | `#confirm-password` |
| Next 按钮 | `button[type="submit"]` |
| Create Account | `button:has-text('Create Account')` |
| Continue | `button:has-text('Continue')` |
| First Name | `input[placeholder="First Name"]` |
| Last Name | `input[placeholder="Last Name"]` |
| 条款复选框 | `input[type="checkbox"]` |
| Submit to get $5 Credits | `button:has-text('Submit to get $5 Credits')` |
| ❌ Skip 按钮（不要点） | `button:has-text('Skip')` |
| Create API Key | `button:has-text('Create API Key')` |
| API Key Name | `input[placeholder*="name" i]` |
| Generate Key | `button:has-text('Generate Key')` |
| Copy to clipboard | `button:has-text('Copy to clipboard')` |

### 13.2 XPath 选择器

| 元素 | XPath |
|-----|-------|
| 邮箱输入 | `//input[@id='email-display']` |
| Next 按钮 | `//button[contains(text(), 'Next')]` |
| 验证提示 | `//*[contains(text(), 'verification email')]` |
| 问卷选项（按文本） | `//label[contains(text(), '{option_text}')]` |
| Submit $5 Credits | `//button[contains(text(), 'Submit to get $5 Credits')]` |

### 13.3 问卷选项列表

**问题1: What are your goals for using Fireworks?**
```python
goals_options = [
    "Prototype with open models",
    "Flexible capacity for experimentation", 
    "Flexible capacity for production",
    "Faster speeds or lower costs",
    "Fine-tune models for quality",
    "High reliability inference for production",
    "Migrate from closed to open models",
    "Migrate from self-hosting to third-party",
    "Other"
]
```

**问题2: What are your primary use cases?**
```python
use_cases_options = [
    "Code Assistance",
    "Conversational AI",
    "Agentic AI",
    "Search",
    "Multimedia RAG",
    "Other"
]
```

---

**文档版本**: v1.1  
**最后更新**: 2026-02-28  
**更新内容**: 
- 添加入门引导（Onboarding）页面元素分析
- 添加问卷提交流程（领取 $5 奖励）
- 修正流程：必须随机勾选问卷选项提交，不能跳过
- 添加已验证的元素定位信息
**作者**: [Your Name]  
**用途**: 技术研究学习
