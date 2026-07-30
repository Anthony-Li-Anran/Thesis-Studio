"""结构化日志配置。"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """配置全局日志，输出到 stderr。"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )


def get_logger(name: str) -> logging.Logger:
    """获取模块日志器。"""
    return logging.getLogger(name)
