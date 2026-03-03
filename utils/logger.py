"""
日志工具模块
"""
import sys
from datetime import datetime


class Logger:
    """简单日志记录器"""
    
    def __init__(self, name: str = "FireworksAuto"):
        self.name = name
    
    def _log(self, level: str, message: str):
        """内部日志方法"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] [{self.name}] {message}"
        print(log_line, file=sys.stderr if level in ["ERROR", "WARN"] else sys.stdout)
    
    def info(self, message: str):
        """信息日志"""
        self._log("INFO", message)
    
    def error(self, message: str):
        """错误日志"""
        self._log("ERROR", message)
    
    def warning(self, message: str):
        """警告日志"""
        self._log("WARN", message)
    
    def debug(self, message: str):
        """调试日志"""
        self._log("DEBUG", message)
