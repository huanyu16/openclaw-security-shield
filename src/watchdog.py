#!/usr/bin/env python3
"""
Security Shield - File Watchdog
文件监控模块
"""

import os
import sys
import time
import json
import hashlib
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# ============ 配置 ============
WATCH_DIR = Path.home() / ".openclaw"
ALERT_THRESHOLD = 5  # 5秒内超过10次访问触发告警
CHECK_INTERVAL = 2  # 检查间隔（秒）

# ============ 日志 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Watchdog")

# ============ 数据类 ============
@dataclass
class FileState:
    """文件状态"""
    path: str
    mtime: float
    size: int
    hash: str = ""
    last_access: float = 0
    access_count: int = 0

@dataclass
class AccessEvent:
    """访问事件"""
    timestamp: float
    path: str
    process_name: str = "unknown"
    event_type: str = "access"

@dataclass
class Alert:
    """告警"""
    timestamp: float
    alert_type: str
    message: str
    details: Dict = field(default_factory=dict)

# ============ 文件监控器 ============
class FileWatchdog:
    """文件监控器"""
    
    def __init__(self, watch_path: Path):
        self.watch_path = watch_path
        self.state_file = watch_path / ".watchdog_state.json"
        self.alert_file = watch_path / ".watchdog_alerts.jsonl"
        self.state: Dict[str, FileState] = {}
        self.access_log: List[AccessEvent] = []
        self.alerts: List[Alert] = []
        self.recent_access_times: List[float] = []
        
    def _compute_hash(self, filepath: Path) -> str:
        """计算文件hash"""
        try:
            return hashlib.sha256(filepath.read_bytes()).hexdigest()[:16]
        except:
            return ""
    
    def _scan_files(self) -> Dict[str, FileState]:
        """扫描文件"""
        state = {}
        
        if not self.watch_path.exists():
            return state
        
        for filepath in self.watch_path.rglob("*"):
            if not filepath.is_file():
                continue
            
            try:
                stat = filepath.stat()
                state[str(filepath)] = FileState(
                    path=str(filepath),
                    mtime=stat.st_mtime,
                    size=stat.st_size,
                    hash=self._compute_hash(filepath)
                )
            except:
                pass
        
        return state
    
    def _load_state(self) -> Dict[str, FileState]:
        """加载状态"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                return {k: FileState(**v) for k, v in data.items()}
            except:
                pass
        return {}
    
    def _save_state(self, state: Dict[str, FileState]):
        """保存状态"""
        data = {k: {
            "path": v.path,
            "mtime": v.mtime,
            "size": v.size,
            "hash": v.hash,
            "last_access": v.last_access,
            "access_count": v.access_count
        } for k, v in state.items()}
        self.state_file.write_text(json.dumps(data, indent=2))
    
    def _log_alert(self, alert: Alert):
        """记录告警"""
        self.alerts.append(alert)
        
        # 写入文件
        with open(self.alert_file, "a") as f:
            f.write(json.dumps({
                "timestamp": alert.timestamp,
                "type": alert.alert_type,
                "message": alert.message,
                "details": alert.details
            }, ensure_ascii=False) + "\n")
    
    def _check_access_pattern(self) -> Optional[Alert]:
        """检查访问模式"""
        now = time.time()
        
        # 只保留最近30秒的访问记录
        self.recent_access_times = [t for t in self.recent_access_times if now - t < 30]
        
        # 如果30秒内访问超过20次，认为是异常
        if len(self.recent_access_times) > 20:
            return Alert(
                timestamp=now,
                alert_type="high_frequency",
                message="检测到高频文件访问",
                details={"count": len(self.recent_access_times)}
            )
        
        return None
    
    def _detect_changes(self, old_state: Dict[str, FileState], new_state: Dict[str, FileState]) -> List[Alert]:
        """检测变化"""
        alerts = []
        
        # 新增文件
        for path in new_state:
            if path not in old_state:
                # 检查是否是敏感文件
                if any(s in path.lower() for s in ["key", "token", "secret", "password", "credential", "auth"]):
                    alerts.append(Alert(
                        timestamp=time.time(),
                        alert_type="new_sensitive_file",
                        message=f"检测到新敏感文件",
                        details={"path": path}
                    ))
        
        # 修改文件
        for path in new_state:
            if path in old_state:
                if new_state[path].hash != old_state[path].hash:
                    # 检查是否是敏感文件被修改
                    if any(s in path.lower() for s in ["config", "memory", "vault"]):
                        alerts.append(Alert(
                            timestamp=time.time(),
                            alert_type="sensitive_modified",
                            message=f"敏感文件被修改",
                            details={"path": path}
                        ))
        
        return alerts
    
    def check(self) -> List[Alert]:
        """执行一次检查"""
        old_state = self._load_state()
        new_state = self._scan_files()
        
        alerts = []
        
        # 检测变化
        alerts.extend(self._detect_changes(old_state, new_state))
        
        # 检查访问模式
        self.recent_access_times.append(time.time())
        pattern_alert = self._check_access_pattern()
        if pattern_alert:
            alerts.append(pattern_alert)
        
        # 保存状态
        self._save_state(new_state)
        
        # 记录告警
        for alert in alerts:
            self._log_alert(alert)
            self._notify(alert)
        
        return alerts
    
    def _notify(self, alert: Alert):
        """发送通知"""
        import subprocess
        
        message = alert.message
        if alert.details:
            details_str = " | ".join([f"{k}={v}" for k, v in alert.details.items()])
            message += f"\n{details_str}"
        
        try:
            # macOS 通知
            script = f'display notification "{message}" with title "🛡️ Security Shield Alert"'
            subprocess.run(["osascript", "-e", script], capture_output=True)
        except:
            pass
        
        # 同时打印到控制台
        timestamp = datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S")
        print(f"\n🚨 [{timestamp}] {alert.alert_type.upper()}: {alert.message}")
        if alert.details:
            for k, v in alert.details.items():
                print(f"   {k}: {v}")
    
    def run(self, interval: int = CHECK_INTERVAL):
        """持续监控"""
        print(f"👁️  启动文件监控")
        print(f"   监控目录: {self.watch_path}")
        print(f"   检查间隔: {interval}秒")
        print(f"   按 Ctrl+C 停止\n")
        
        print("状态: 🟢 运行中")
        print("\n最近活动:")
        
        while True:
            try:
                alerts = self.check()
                
                # 打印正常状态
                if not alerts:
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"\r[{now}] ✓ 正常", end="", flush=True)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\n👁️  监控已停止")
                break
            except Exception as e:
                logger.error(f"监控出错: {e}")
                time.sleep(interval)

# ============ CLI ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Shield File Watchdog")
    parser.add_argument("--path", type=str, default=str(WATCH_DIR), help="监控目录")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL, help="检查间隔(秒)")
    parser.add_argument("--once", action="store_true", help="单次检查")
    
    args = parser.parse_args()
    
    watchdog = FileWatchdog(Path(args.path))
    
    if args.once:
        alerts = watchdog.check()
        if alerts:
            print(f"发现 {len(alerts)} 个告警")
            for alert in alerts:
                print(f"  - {alert.alert_type}: {alert.message}")
            sys.exit(1)
        else:
            print("✓ 未检测到异常")
    else:
        watchdog.run(args.interval)

if __name__ == "__main__":
    main()
