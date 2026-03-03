# Fireworks AI 自动注册工具

> **版本**: v1.0.0  
> **用途**: Fireworks AI 账号自动注册，支持邮箱验证、入门引导和 API Key 创建

---

## ✨ 特性

- **多源邮箱自动切换** - SamfunAsia → Primary → Mail.tm，失败自动切换
- **浏览器自动化** - ChromeDriver 145 适配，支持本地缓存和自动下载
- **完整注册流程** - 注册 → 验证 → 入门引导 → API Key 创建
- **人机模拟** - 随机延迟、自然输入，降低风控检测
- **错误重试** - 浏览器崩溃自动重启，网络错误自动重试
- **结果保存** - 自动保存账号信息，支持增量写入

---

## 📦 安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd fireworks_auto_register
```

### 2. 安装依赖

#### 方法 A: 使用 pip（标准方式）
```bash
pip install -r requirements.txt
```

#### 方法 B: 使用 uv（推荐，速度极快）
```bash
# 创建虚拟环境（Python 3.12）
uv venv --python python3.12

# 激活环境
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

**uv 优势**: 比 pip 快 10-100 倍，支持全局缓存

### 依赖列表
- `undetected-chromedriver>=3.5.0` - 浏览器自动化
- `selenium>=4.15.0` - WebDriver 支持
- `requests>=2.31.0` - HTTP 请求
- `python-dotenv>=1.0.0` - 环境变量（可选）

### 3. 准备 ChromeDriver（可选）
项目已内置 ChromeDriver 145 缓存，位于 `.chromedriver_cache/`。

如需手动下载：
```bash
# 检查 Chrome 版本
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# 下载对应版本 ChromeDriver
# https://chromedriver.chromium.org/downloads
```

---

## 🚀 使用方法

### 快速开始
```bash
# 注册 1 个账号
python main.py -n 1

# 注册 5 个账号
python main.py -n 5

# 无头模式（不显示浏览器窗口）
python main.py -n 3 --headless
```

### 命令行选项
```bash
python main.py --help
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-n, --count` | 注册账号数量 | 1 |
| `--retry` | 失败重试次数 | 3 |
| `--headless` | 无头模式 | False |
| `--skip-onboarding` | 跳过入门引导 | False |
| `--skip-apikey` | 跳过 API Key 创建 | False |
| `--primary-url` | 主邮箱服务 URL | "" |
| `--primary-key` | 主邮箱服务 API Key | "" |

### 示例

```bash
# 注册 10 个账号，失败重试 5 次
python main.py -n 10 --retry 5

# 仅注册，跳过问卷和 API Key
python main.py -n 1 --skip-onboarding --skip-apikey

# 使用自定义邮箱服务
python main.py -n 1 --primary-url "https://mail.example.com" --primary-key "xxx"
```

---

## 📁 项目结构

```
fireworks_auto_register/
├── core/                           # 核心模块
│   ├── __init__.py
│   ├── browser_manager.py          # 浏览器管理（ChromeDriver 145）
│   └── email_service.py            # 邮箱服务（多源自动切换）
│
├── services/                       # 业务服务
│   ├── __init__.py
│   ├── registration.py             # 注册流程
│   ├── onboarding.py               # 入门引导（问卷+$5奖励）
│   └── api_key_manager.py          # API Key 管理
│
├── utils/                          # 工具模块
│   ├── __init__.py
│   ├── config.py                   # 配置管理
│   ├── logger.py                   # 日志工具
│   ├── http_client.py              # HTTP 工具
│   └── file_handler.py             # 文件处理
│
├── tests/                          # 测试用例
│   ├── __init__.py
│   └── test_flows.py               # 单元测试
│
├── output/                         # 输出目录
│   └── fireworks_YYYYMMDD.txt      # 结果文件
│
├── .chromedriver_cache/            # ChromeDriver 缓存
│   └── chromedriver-145
│
├── main.py                         # 主入口
├── requirements.txt                # 依赖列表
├── README.md                       # 本文件
└── DEVELOPMENT_LOG.md              # 开发日志
```

---

## ⚙️ 配置说明

### 邮箱服务配置

编辑 `utils/config.py`：

```python
# SamfunAsia 配置（主要邮箱服务）
SAMFUN_ASIA_BASE = "https://cloudflare_temp_email.caiql20022000.workers.dev"
SAMFUN_ASIA_ADMIN_AUTH = "xiaoyibao@1234"

# Mail.tm 配置（备用邮箱服务）
MAIL_TM_BASE = "https://api.mail.tm"
```

### 浏览器配置

```python
BROWSER_HEADLESS = False      # 是否无头模式
BROWSER_WINDOW_SIZE = (1920, 1080)  # 窗口大小
PAGE_LOAD_TIMEOUT = 30        # 页面加载超时
IMPLICIT_WAIT = 10            # 隐式等待
```

### 人机模拟延迟

```python
TYPING_MIN_DELAY = 0.05       # 最小输入延迟（秒）
TYPING_MAX_DELAY = 0.15       # 最大输入延迟（秒）
CLICK_DELAY = 0.5             # 点击后延迟（秒）
BETWEEN_ACCOUNTS = 30         # 账号间间隔（秒）
```

---

## 📊 输出结果

注册成功后，结果保存到 `output/fireworks_YYYYMMDD.txt`：

```
Fireworks AI 账号注册结果
生成时间: 2026-02-28 18:37:12
==================================================

  项目         验证结果
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  邮箱         silverwave704@samfun.asia
  密码         abj!Lo8vU&bZA@1N
  API Key      fw_xxxxxxxxxxxxxxxx
  Account ID   silverwave704-xxxxx

  注册时间: 2026-02-28 18:37:12
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🧪 测试

### 运行单元测试
```bash
python -m pytest tests/test_flows.py -v
```

### 测试覆盖
- ✅ 密码生成器（符合复杂度要求）
- ✅ 邮箱服务（SamfunAsia、Mail.tm）
- ✅ 邮箱管理器（优先级切换）
- ✅ 姓名生成器
- ✅ 问卷选项
- ✅ 文件处理器
- ✅ 日志工具

---

## 🔧 常见问题

### Q: 浏览器无法启动？
```bash
# 检查 Chrome 版本
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# 确保 ChromeDriver 权限正确
chmod +x .chromedriver_cache/chromedriver-145
```

### Q: 邮箱服务不可用？
- 检查网络连接
- SamfunAsia 偶尔会有 SSL 问题，会自动切换到备用邮箱服务

### Q: 验证链接获取失败？
- 可能是邮件延迟，可以增加 `VERIFY_EMAIL_TIMEOUT`
- 检查邮箱服务是否正常

### Q: ModuleNotFoundError: No module named 'urllib3'?
系统有多个 Python 版本，请使用以下方法之一：

```bash
# 方法1: 使用 Python 3.10 明确运行
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 main.py -n 1

# 方法2: 为当前 Python 安装依赖
python3 -m pip install urllib3 selenium undetected-chromedriver requests

# 方法3: 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py -n 1
```

---

## 📝 更新日志

### v1.0.0 (2026-02-28)
- ✅ 完整注册流程实现
- ✅ 多源邮箱自动切换
- ✅ ChromeDriver 145 适配
- ✅ 入门引导和 API Key 创建
- ✅ 浏览器优雅退出
- ✅ 账号间隔默认 30s

---

## ⚠️ 免责声明

本项目仅用于自动化测试技术学习与研究，使用本工具必须遵守 Fireworks AI 的服务条款和相关法律法规。

- 仅供学习研究目的
- 不得用于批量注册恶意账号
- 不得用于绕过平台安全机制
- 妥善处理生成的测试数据

---

## 📄 许可证

MIT License

---

**作者**: AI Assistant  
**最后更新**: 2026-02-28
