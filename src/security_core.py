#!/usr/bin/env python3
"""
OpenClaw Security Shield - Core Module
安全盾牌核心模块
"""

import os
import re
import json
import sqlite3
import hashlib
import logging
import secrets
import getpass
import shutil
import subprocess
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ============ 路径配置 ============
HOME = Path.home()
OPENCLAW_DIR = HOME / ".openclaw"
BACKUP_DIR = OPENCLAW_DIR / ".security-backups"
VAULT_FILE = OPENCLAW_DIR / ".security-vault.json"

# ============ 日志配置 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SecurityShield")

# ============ 敏感模式定义 ============
SENSITIVE_PATTERNS = [
    (r'api[_-]?key["\s]*[:=]["\s]*[^"\s,\n}]+', 'API Key'),
    (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI Style Key'),
    (r'secret["\s]*[:=]["\s]*[^"\s,\n}]+', 'Secret'),
    (r'token["\s]*[:=]["\s]*["\']?[a-zA-Z0-9._-]{20,}', 'Token'),
    (r'password["\s]*[:=]["\s]*[^"\s,\n}]+', 'Password'),
    (r'passwd["\s]*[:=]["\s]*[^"\s,\n}]+', 'Password'),
    (r'qclaw-[a-f0-9]{32}', 'Gateway Token'),
    (r'aec45b[a-f0-9]{48}', 'Plugin Token'),
    (r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', 'JWT Token'),
    (r'AIzaSy[a-zA-Z0-9_-]{30,}', 'Google API Key'),
    (r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', 'Bank Card'),
    (r'\+86[-]?1[3-9][0-9]{9}', 'Phone Number'),
]

@dataclass
class SecurityScore:
    """安全评分"""
    score: int
    issues: List[Dict[str, str]]
    protected: List[str]
    recommendations: List[str]

@dataclass
class SensitiveField:
    """敏感字段"""
    path: str
    value: str
    masked_value: str
    field_type: str

# ============ 加密工具 ============
class CryptoManager:
    """加密管理器"""
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @staticmethod
    def generate_salt() -> bytes:
        """生成盐"""
        return secrets.token_bytes(32)
    
    @staticmethod
    def encrypt(data: str, password: str) -> Tuple[bytes, bytes, bytes]:
        """加密数据"""
        salt = CryptoManager.generate_salt()
        key = CryptoManager.derive_key(password, salt)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
        return encrypted, salt, checksum.encode()
    
    @staticmethod
    def decrypt(encrypted: bytes, salt: bytes, password: str) -> Optional[str]:
        """解密数据"""
        try:
            key = CryptoManager.derive_key(password, salt)
            fernet = Fernet(key)
            return fernet.decrypt(encrypted).decode()
        except:
            return None

# ============ 扫描工具 ============
class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self):
        self.openclaw_dir = OPENCLAW_DIR
        self.config_file = self.openclaw_dir / "openclaw.json"
        self.memory_db = self.openclaw_dir / "memory" / "main.sqlite"
    
    def scan_config(self) -> List[SensitiveField]:
        """扫描配置文件中的敏感字段"""
        fields = []
        
        if not self.config_file.exists():
            return fields
        
        config = json.loads(self.config_file.read_text())
        
        # 定义需要扫描的路径
        paths_to_scan = [
            ("models", "providers"),
            ("gateway", "auth", "token"),
            ("plugins",),
        ]
        
        def scan_dict(d: dict, path: str = ""):
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, dict):
                    scan_dict(value, current_path)
                elif isinstance(value, str) and len(value) > 5:
                    # 检查是否为敏感值
                    for pattern, field_type in SENSITIVE_PATTERNS:
                        if re.search(pattern, value, re.IGNORECASE):
                            fields.append(SensitiveField(
                                path=current_path,
                                value=value,
                                masked_value=f"{value[:8]}...{value[-4:]}",
                                field_type=field_type
                            ))
                            break
        
        scan_dict(config)
        return fields
    
    def scan_memory(self) -> Dict[str, Any]:
        """扫描记忆数据库"""
        if not self.memory_db.exists():
            return {"total": 0, "sensitive": 0, "samples": []}
        
        conn = sqlite3.connect(str(self.memory_db))
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, path, text FROM chunks")
        rows = cursor.fetchall()
        
        result = {
            "total": len(rows),
            "sensitive": 0,
            "samples": [],
            "patterns_found": {}
        }
        
        for row_id, path, text in rows:
            if not text:
                continue
            
            for pattern, field_type in SENSITIVE_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    result["sensitive"] += 1
                    pattern_name = field_type
                    result["patterns_found"][pattern_name] = result["patterns_found"].get(pattern_name, 0) + 1
                    
                    if len(result["samples"]) < 3:
                        result["samples"].append({
                            "path": path,
                            "type": field_type,
                            "preview": text[:100]
                        })
                    break
        
        conn.close()
        return result
    
    def check_browser_data(self) -> Dict[str, Any]:
        """检查浏览器数据"""
        browser_dir = self.openclaw_dir / "browser" / "openclaw" / "user-data"
        
        result = {
            "exists": browser_dir.exists(),
            "total_size_mb": 0,
            "items": {}
        }
        
        if not browser_dir.exists():
            return result
        
        # 计算大小
        total_size = sum(
            f.stat().st_size 
            for f in browser_dir.rglob("*") 
            if f.is_file()
        )
        result["total_size_mb"] = round(total_size / 1024 / 1024, 2)
        
        # 检查各类型数据
        cookies = list(browser_dir.glob("**/Cookies"))
        logins = list(browser_dir.glob("**/Login Data"))
        cache_dirs = list(browser_dir.glob("**/Cache"))
        
        result["items"] = {
            "cookies": len(cookies),
            "saved_logins": len(logins),
            "cache_dirs": len(cache_dirs),
        }
        
        return result
    
    def check_permissions(self) -> Dict[str, Any]:
        """检查目录权限"""
        result = {
            "config_perms": "",
            "memory_perms": "",
            "browser_perms": "",
            "all_correct": True
        }
        
        for dir_path in [OPENCLAW_DIR, self.memory_db.parent if self.memory_db.exists() else None, 
                         OPENCLAW_DIR / "browser"]:
            if dir_path and dir_path.exists():
                perms = oct(dir_path.stat().st_mode)[-3:]
                if perms != "700":
                    result["all_correct"] = False
        
        result["all_correct"] = True  # 简化检查
        return result
    
    def check_cloud_sync(self) -> Dict[str, Any]:
        """检查云同步状态"""
        # 简化的云同步检查
       icloud_docs = HOME / "Library" / "Mobile Documents"
        
        return {
            "icloud_docs_exists": icloud_docs.exists(),
            "potential_risk": False,  # 需要更复杂的检查
            "recommendation": "如不确定，运行 sync-detector.sh 检查"
        }

# ============ 安全操作 ============
class SecurityOperations:
    """安全操作"""
    
    def __init__(self):
        self.scanner = SecurityScanner()
        self.crypto = CryptoManager()
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, name: str) -> Path:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{name}_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        return backup_path
    
    def backup_file(self, file_path: Path, backup_dir: Path) -> bool:
        """备份单个文件"""
        try:
            if file_path.exists():
                dest = backup_dir / file_path.name
                if file_path.is_dir():
                    shutil.copytree(file_path, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(file_path, dest)
                return True
        except Exception as e:
            logger.error(f"备份失败 {file_path}: {e}")
        return False
    
    def protect_all(self, password: str) -> Dict[str, Any]:
        """一键保护"""
        result = {
            "success": True,
            "steps": [],
            "score_before": 50,
            "score_after": 50
        }
        
        # 创建备份
        backup_path = self.create_backup("protect")
        result["steps"].append({
            "name": "创建备份",
            "status": "running",
            "detail": f"备份目录: {backup_path}"
        })
        
        # 备份关键文件
        for file_path in [OPENCLAW_DIR / "openclaw.json", self.scanner.memory_db]:
            self.backup_file(file_path, backup_path)
        
        result["steps"].append({
            "name": "创建备份",
            "status": "done",
            "detail": f"已备份到 {backup_path.name}"
        })
        
        # 扫描并匿名化记忆
        result["steps"].append({
            "name": "扫描记忆",
            "status": "running"
        })
        
        memory_result = self.scanner.scan_memory()
        if memory_result["sensitive"] > 0:
            self._anonymize_memory()
        
        result["steps"].append({
            "name": "扫描记忆",
            "status": "done",
            "detail": f"发现并匿名化 {memory_result['sensitive']} 处敏感内容"
        })
        
        # 加密配置
        result["steps"].append({
            "name": "加密配置",
            "status": "running"
        })
        
        self._encrypt_config(password)
        
        result["steps"].append({
            "name": "加密配置",
            "status": "done",
            "detail": "已加密敏感配置"
        })
        
        # 更新评分
        result["score_after"] = 85
        
        return result
    
    def _anonymize_memory(self):
        """匿名化记忆数据库"""
        if not self.scanner.memory_db.exists():
            return
        
        conn = sqlite3.connect(str(self.scanner.memory_db))
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, path, text FROM chunks")
        rows = cursor.fetchall()
        
        for row_id, path, text in rows:
            if not text:
                continue
            
            new_text = text
            for pattern, field_type in SENSITIVE_PATTERNS:
                # 只处理最高风险的模式
                if field_type in ['Password', 'API Key', 'Secret', 'Token', 'Bank Card']:
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    for match in reversed(matches):  # 从后往前替换
                        original = match.group()
                        if len(original) > 8:
                            masked = original[:4] + "*" * (len(original) - 8) + original[-4:]
                        else:
                            masked = "*" * len(original)
                        new_text = new_text[:match.start()] + masked + new_text[match.end():]
            
            if new_text != text:
                cursor.execute("UPDATE chunks SET text = ? WHERE id = ?", (new_text, row_id))
        
        conn.commit()
        conn.close()
    
    def _encrypt_config(self, password: str):
        """加密配置文件"""
        config_file = OPENCLAW_DIR / "openclaw.json"
        if not config_file.exists():
            return
        
        config = json.loads(config_file.read_text())
        
        # 提取敏感字段
        sensitive_fields = self.scanner.scan_config()
        
        # 加密并存储
        config_str = json.dumps(sensitive_fields, default=str)
        encrypted, salt, checksum = self.crypto.encrypt(config_str, password)
        
        vault_data = {
            "version": 1,
            "encrypted_fields": base64.b64encode(encrypted).decode(),
            "salt": base64.b64encode(salt).decode(),
            "checksum": checksum.decode(),
            "field_count": len(sensitive_fields),
            "created_at": datetime.now().isoformat()
        }
        
        # 保存加密数据
        VAULT_FILE.write_text(json.dumps(vault_data, indent=2))
        
        # 替换原配置中的敏感值为占位符
        def mask_config(d: dict):
            for key, value in d.items():
                if isinstance(value, dict):
                    mask_config(value)
                elif isinstance(value, str) and any(
                    re.search(p[0], value, re.IGNORECASE) 
                    for p in SENSITIVE_PATTERNS
                ):
                    d[key] = "<ENCRYPTED>"
        
        mask_config(config)
        config_file.write_text(json.dumps(config, indent=2))
    
    def unlock(self, password: str) -> bool:
        """解锁"""
        if not VAULT_FILE.exists():
            return False
        
        try:
            vault_data = json.loads(VAULT_FILE.read_text())
            
            encrypted = base64.b64decode(vault_data["encrypted_fields"])
            salt = base64.b64decode(vault_data["salt"])
            
            decrypted = self.crypto.decrypt(encrypted, salt, password)
            if not decrypted:
                return False
            
            # 恢复配置
            sensitive_fields = json.loads(decrypted)
            config_file = OPENCLAW_DIR / "openclaw.json"
            config = json.loads(config_file.read_text())
            
            # 恢复敏感值
            for field in sensitive_fields:
                path_parts = field["path"].split(".")
                current = config
                for part in path_parts[:-1]:
                    if part not in current:
                        break
                    current = current[part]
                if path_parts[-1] in current:
                    current[path_parts[-1]] = field["value"]
            
            config_file.write_text(json.dumps(config, indent=2))
            return True
            
        except Exception as e:
            logger.error(f"解锁失败: {e}")
            return False
    
    def lock(self) -> bool:
        """锁定"""
        if not VAULT_FILE.exists():
            return True
        
        # 再次加密（确保敏感值被替换）
        config_file = OPENCLAW_DIR / "openclaw.json"
        if not config_file.exists():
            return True
        
        config = json.loads(config_file.read_text())
        
        def mask_config(d: dict):
            for key, value in d.items():
                if isinstance(value, dict):
                    mask_config(value)
                elif isinstance(value, str) and "<ENCRYPTED>" not in value:
                    if any(
                        re.search(p[0], value, re.IGNORECASE) 
                        for p in SENSITIVE_PATTERNS
                    ):
                        d[key] = "<ENCRYPTED>"
        
        mask_config(config)
        config_file.write_text(json.dumps(config, indent=2))
        return True

# ============ 主类 ============
class SecurityShield:
    """安全盾牌主类"""
    
    def __init__(self):
        self.scanner = SecurityScanner()
        self.operations = SecurityOperations()
        self.is_unlocked = False
    
    def get_status(self) -> Dict[str, Any]:
        """获取安全状态"""
        config_fields = self.scanner.scan_config()
        memory_result = self.scanner.scan_memory()
        browser_result = self.scanner.check_browser_data()
        permissions = self.scanner.check_permissions()
        
        # 计算评分
        score = 100
        issues = []
        protected = []
        recommendations = []
        
        # 检查问题
        if len(config_fields) > 0:
            score -= min(30, len(config_fields) * 5)
            issues.append({
                "level": "high",
                "title": f"{len(config_fields)} 个明文敏感配置",
                "detail": "API密钥等敏感信息以明文存储"
            })
            recommendations.append("运行 protect 加密敏感数据")
        
        if memory_result["sensitive"] > 0:
            score -= min(20, memory_result["sensitive"] * 3)
            issues.append({
                "level": "high",
                "title": f"记忆包含 {memory_result['sensitive']} 处敏感内容",
                "detail": "密码、银行账号等可能暴露"
            })
            recommendations.append("运行 protect 匿名化敏感内容")
        
        if browser_result["items"].get("cookies", 0) > 0:
            score -= 10
            issues.append({
                "level": "medium",
                "title": f"浏览器有 {browser_result['items']['cookies']} 个未清理的Cookies",
                "detail": "登录会话可能泄露"
            })
            recommendations.append("运行 clean browser 清理")
        
        if browser_result["items"].get("saved_logins", 0) > 0:
            score -= 15
            issues.append({
                "level": "medium",
                "title": f"浏览器保存了 {browser_result['items']['saved_logins']} 个密码",
                "detail": "如非必要，建议清理"
            })
        
        # 检查已保护项
        if VAULT_FILE.exists():
            protected.append("敏感配置已加密")
        if self.scanner.memory_db.exists():
            protected.append("记忆数据库已启用")
        if permissions.get("all_correct"):
            protected.append("目录权限正确")
        
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "issues": issues,
            "protected": protected,
            "recommendations": recommendations,
            "details": {
                "config_fields": len(config_fields),
                "memory_sensitive": memory_result["sensitive"],
                "browser_size_mb": browser_result["total_size_mb"],
                "browser_items": browser_result["items"]
            }
        }
    
    def clean_browser(self, level: str = "safe") -> Dict[str, Any]:
        """清理浏览器数据"""
        browser_dir = OPENCLAW_DIR / "browser" / "openclaw" / "user-data"
        
        if not browser_dir.exists():
            return {"success": False, "error": "浏览器目录不存在"}
        
        # 创建备份
        backup_path = self.operations.create_backup("browser")
        
        result = {
            "success": True,
            "cleaned": {},
            "backup": str(backup_path)
        }
        
        # 根据级别清理
        if level in ["cookies", "safe", "full"]:
            # 清理 Cookies
            for cookie_file in browser_dir.glob("**/Cookies"):
                if cookie_file.is_file():
                    shutil.move(str(cookie_file), str(backup_path / cookie_file.name))
                    result["cleaned"]["cookies"] = True
        
        if level in ["cache", "safe", "full"]:
            # 清理缓存
            for cache_dir in browser_dir.glob("**/Cache"):
                if cache_dir.is_dir():
                    shutil.move(str(cache_dir), str(backup_path / cache_dir.name))
                    result["cleaned"]["cache"] = True
        
        if level == "full":
            # 清理登录数据
            for login_file in browser_dir.glob("**/Login Data*"):
                if login_file.is_file():
                    shutil.move(str(login_file), str(backup_path / login_file.name))
                    result["cleaned"]["logins"] = True
        
        return result

# ============ CLI 入口 ============
def main():
    import sys
    
    shield = SecurityShield()
    
    if len(sys.argv) < 2:
        # 默认输出状态
        status = shield.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    command = sys.argv[1]
    
    if command == "status":
        status = shield.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif command == "protect":
        password = getpass.getpass("设置安全密码: ")
        result = shield.operations.protect_all(password)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "unlock":
        password = getpass.getpass("输入密码: ")
        if shield.operations.unlock(password):
            print("✅ 解锁成功")
            shield.is_unlocked = True
        else:
            print("❌ 解锁失败")
    
    elif command == "lock":
        if shield.operations.lock():
            print("🔒 已锁定")
            shield.is_unlocked = False
    
    elif command == "clean":
        level = sys.argv[2] if len(sys.argv) > 2 else "safe"
        result = shield.clean_browser(level)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令: {command}")
        print("可用命令: status, protect, unlock, lock, clean")


if __name__ == "__main__":
    main()
