import logging
import os

_initialized = False

def get_logger(name: str) -> logging.Logger:
    """获取配置好的 logger 实例"""
    global _initialized
    
    if not _initialized:
        log_level = os.environ.get("LOG_LEVEL", "ERROR").strip().upper()
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        )
        _initialized = True
    
    logger = logging.getLogger(name)
    log_level = os.environ.get("LOG_LEVEL", "ERROR").strip().upper()
    logger.setLevel(log_level)
    return logger
