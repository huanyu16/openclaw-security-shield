# 🛡️ OpenClaw Security Shield

<!-- Badges -->
<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-999999)
![Python](https://img.shields.io/badge/python-3.8+-orange)

</div>

---

<div align="center">

**[English](#english)** · **[中文](#中文)** · **[快速开始](#quick-start)** · **[功能](#功能)** · **[安全特性](#安全特性)**

</div>

---

# English

## 🛡️ One-Click Security Suite for OpenClaw

> *Your AI agent is powerful — but is it secure?*

Every OpenClaw installation contains a goldmine of sensitive data: API keys, conversation history, browser sessions, and everything you've ever told your agent. Most users don't realize their "personal AI assistant" is walking around naked on the internet.

**Security Shield** is the one-click solution that protects your OpenClaw from the ground up — no security expertise required.

### Why Security Shield?

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Without Security Shield:                                  │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  ~/.openclaw/                                       │  │
│   │  ├── openclaw.json     ← API keys in plain text    │  │
│   │  ├── memory/main.sqlite ← ALL your conversations    │  │
│   │  └── browser/         ← Your online sessions        │  │
│   │                                                     │  │
│   │  🔓 Exposed to: Cloud sync, GitHub leaks, malware  │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   With Security Shield:                                     │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  ~/.openclaw/                                       │  │
│   │  ├── openclaw.json     ← Encrypted                 │  │
│   │  ├── memory/main.sqlite ← Anonymized               │  │
│   │  └── browser/         ← Cleaned                    │  │
│   │                                                     │  │
│   │  🔒 Protected by: AES-256 + Real-time monitoring   │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### What It Protects

| Asset | Risk | Protection |
|-------|------|------------|
| **API Keys** | Cloud sync / GitHub leaks | PBKDF2 + AES-256 encryption |
| **Memory Database** | Contains all conversations | Auto-anonymization of passwords, bank cards |
| **Browser Data** | Saved logins, session cookies | One-click cleanup |
| **Files** | Malware / unauthorized access | Real-time monitoring + alerts |

### Features

- 🔐 **One-Click Protection** — Encrypt + anonymize everything in one command
- 👁️ **Real-Time Monitoring** — Detect abnormal file access patterns
- 🧹 **Smart Cleanup** — Remove browser data without breaking functionality  
- 🔍 **Leak Detection** — Scan for secrets exposed on GitHub
- 💾 **Safe Backups** — Every operation backs up before changing
- 🔓 **Simple Unlock** — Password-protected access when you need it

### Quick Start

```bash
# One-line install
curl -fsSL https://raw.githubusercontent.com/huanyu16/openclaw-security-shield/main/install.sh | bash

# Or clone and install
git clone https://github.com/huanyu16/openclaw-security-shield.git
cd openclaw-security-shield
bash install.sh

# Check security status
security-shield status

# One-click protect
security-shield protect

# Clean browser data
security-shield clean safe
```

### One Command = Complete Protection

```bash
$ security-shield protect

🛡️ One-Click Security Protection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/4] 🔐 Encrypting sensitive configuration...
       ✅ 4 API keys encrypted

[2/4] 🧹 Scanning memory for sensitive content...
       ⚠️ Found 12 instances
       ✅ Anonymized

[3/4] 📦 Backing up original data...
       ✅ Saved to ~/.openclaw/.security-backups/

[4/4] 👁️ Starting file monitoring...
       ✅ Monitor active (background)

🎉 Protection Complete!
   Security Score: 65 → 90/100

⚠️ Remember your password! Cannot be recovered.
```

### Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Security Shield Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Input                                                │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │            Command Layer (security-shield.sh)        │   │
│   └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│   ┌──────────────┬──────────────┬──────────────┐           │
│   │   Encrypt    │   Scan      │   Monitor    │           │
│   │   Module     │   Module    │   Module     │           │
│   └──────────────┴──────────────┴──────────────┘           │
│       │                │                │                   │
│       ▼                ▼                ▼                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Storage Layer                            │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐     │   │
│   │  │ vault   │  │ memory  │  │  file monitor   │     │   │
│   │  │ .enc    │  │ .db     │  │  logs          │     │   │
│   │  └─────────┘  └─────────┘  └─────────────────┘     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Comparison

| Feature | Without Shield | With Shield |
|---------|---------------|-------------|
| API Keys | Plain text | AES-256 encrypted |
| Memory | Full history | Passwords anonymized |
| Browser | Cookies + cache | Cleaned on demand |
| Monitoring | None | Real-time alerts |
| Backups | Manual | Automatic |

### Requirements

- macOS, Linux, or Windows
- Python 3.8+
- OpenClaw 2026.3+

---

<br>

---

# 中文

## 🛡️ OpenClaw 安全盾牌 — 一键守护你的智能体

> *你的 AI 智能体很强大——但它安全吗？*

每一次 OpenClaw 安装，都是一座敏感数据的金矿：API 密钥、对话历史、浏览器会话，以及你曾经告诉过智能体的所有事情。大多数用户没有意识到，他们的"私人 AI 助手"其实一直在互联网上**裸奔**。

**安全盾牌**是一个一键式安全套件，让你的 OpenClaw 从根本上得到保护——**无需任何安全知识**。

### 为什么需要安全盾牌？

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   没有安全盾牌时：                                          │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  ~/.openclaw/                                       │  │
│   │  ├── openclaw.json     ← API密钥明文存储           │  │
│   │  ├── memory/main.sqlite ← 你所有的对话记录         │  │
│   │  └── browser/         ← 你的在线会话               │  │
│   │                                                     │  │
│   │  🔓 暴露于：云同步、GitHub泄露、恶意软件          │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   有了安全盾牌后：                                         │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  ~/.openclaw/                                       │  │
│   │  ├── openclaw.json     ← 已加密                    │  │
│   │  ├── memory/main.sqlite ← 敏感内容已匿名化         │  │
│   │  └── browser/         ← 已清理                    │  │
│   │                                                     │  │
│   │  🔒 保护： AES-256加密 + 实时监控                 │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 保护什么？

| 资产 | 风险 | 保护措施 |
|------|------|----------|
| **API 密钥** | 云同步 / GitHub 泄露 | PBKDF2 + AES-256 加密 |
| **记忆数据库** | 包含所有对话 | 自动匿名化密码、银行卡 |
| **浏览器数据** | 保存的密码、会话 Cookies | 一键清理 |
| **文件目录** | 恶意软件 / 未授权访问 | 实时监控 + 告警 |

### 功能特性

- 🔐 **一键保护** — 一个命令完成加密 + 匿名化
- 👁️ **实时监控** — 检测异常文件访问模式
- 🧹 **智能清理** — 清理浏览器数据但不影响功能
- 🔍 **泄露检测** — 扫描 GitHub 上暴露的密钥
- 💾 **安全备份** — 每次操作前自动备份
- 🔓 **简单解锁** — 需要时输入密码即可访问

### 快速开始

```bash
# 一键安装
curl -fsSL https://raw.githubusercontent.com/huanyu16/openclaw-security-shield/main/install.sh | bash

# 或克隆安装
git clone https://github.com/huanyu16/openclaw-security-shield.git
cd openclaw-security-shield
bash install.sh

# 查看安全状态
security-shield status

# 一键保护
security-shield protect

# 清理浏览器数据
security-shield clean safe
```

### 一个命令 = 全面保护

```bash
$ security-shield protect

🛡️ 一键安全保护
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/4] 🔐 加密敏感配置...
       ✅ 4 个 API 密钥已加密

[2/4] 🧹 扫描记忆敏感内容...
       ⚠️ 发现 12 处敏感内容
       ✅ 已匿名化处理

[3/4] 📦 备份原始数据...
       ✅ 已保存到 ~/.openclaw/.security-backups/

[4/4] 👁️ 启动文件监控...
       ✅ 监控已启动（后台运行）

🎉 安全保护完成！
   安全评分: 65 → 90/100

⚠️ 记住你的密码！丢失后无法恢复。
```

### 安全架构

```
┌─────────────────────────────────────────────────────────────┐
│                   安全盾牌架构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用户输入                                                   │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              命令层 (security-shield.sh)             │   │
│   └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│   ┌──────────────┬──────────────┬──────────────┐           │
│   │   加密       │   扫描       │   监控       │           │
│   │   模块       │   模块       │   模块       │           │
│   └──────────────┴──────────────┴──────────────┘           │
│       │                │                │                   │
│       ▼                ▼                ▼                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    存储层                            │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐     │   │
│   │  │ 加密库  │  │ 记忆库  │  │  文件监控日志   │     │   │
│   │  │ .enc    │  │ .db     │  │                 │     │   │
│   │  └─────────┘  └─────────┘  └─────────────────┘     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 对比

| 功能 | 无盾牌 | 有盾牌 |
|------|--------|--------|
| API 密钥 | 明文存储 | AES-256 加密 |
| 记忆数据 | 完整历史 | 密码已匿名化 |
| 浏览器 | Cookies + 缓存 | 按需清理 |
| 监控 | 无 | 实时告警 |
| 备份 | 手动 | 自动 |

### 系统要求

- macOS、Linux 或 Windows
- Python 3.8+
- OpenClaw 2026.3+

---

<br>

## 📖 使用指南

### 查看安全状态

```bash
security-shield status
```

输出示例：
```
🛡️ Security Shield - 安全状态报告

📊 安全评分: 65/100 (需要改进)

🔴 高风险:
  • 4 个明文 API 密钥
  • 记忆数据库包含敏感对话

🟡 中风险:
  • 浏览器有未清理的 Cookies

✅ 已保护:
  • 目录权限正确

💡 建议: 运行 protect 进行安全保护
```

### 一键保护

```bash
security-shield protect
```

### 解锁使用

```bash
# 解锁（使用前）
security-shield unlock

# ... 使用 OpenClaw ...

# 重新锁定（使用后）
security-shield lock
```

### 清理浏览器

```bash
# 安全清理（Cookies + 缓存）
security-shield clean safe

# 仅清理 Cookies
security-shield clean cookies

# 全部清理（包含保存的密码）
security-shield clean full
```

### 启动监控

```bash
security-shield monitor
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

<div align="center">

**如果你觉得有用，请给个 ⭐**

</div>
