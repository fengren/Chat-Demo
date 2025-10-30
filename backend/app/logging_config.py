import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 配置根日志记录器
def setup_logging(level: str = "INFO"):
    """设置日志配置"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # 设置日志级别
    root_logger.setLevel(log_level)
    
    # 控制台处理器（输出到终端）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（输出到文件）
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 为特定模块设置更详细的日志级别
    logging.getLogger("app.services.memory").setLevel(logging.DEBUG)
    logging.getLogger("app.lang.graph").setLevel(logging.DEBUG)
    logging.getLogger("app.routes.chat").setLevel(logging.DEBUG)
    
    logging.info(f"Logging configured: level={level}, log_dir={LOG_DIR}")

