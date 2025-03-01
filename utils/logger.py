#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具模块
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from config.settings import CRAWLER_SETTINGS


def setup_logger(name=None, level=None, log_file=None, max_bytes=10*1024*1024, backup_count=5):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        max_bytes: 单个日志文件最大字节数
        backup_count: 备份文件数量
        
    Returns:
        logger: 日志记录器
    """
    # 获取日志级别
    if level is None:
        level = CRAWLER_SETTINGS.get('log_level', 'INFO')
    
    level = getattr(logging, level) if isinstance(level, str) else level
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers = []
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建按大小轮转的文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_daily_logger(name=None, level=None, log_file=None, backup_count=30):
    """
    设置按天轮转的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        backup_count: 备份文件数量
        
    Returns:
        logger: 日志记录器
    """
    # 获取日志级别
    if level is None:
        level = CRAWLER_SETTINGS.get('log_level', 'INFO')
    
    level = getattr(logging, level) if isinstance(level, str) else level
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers = []
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建按天轮转的文件处理器
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.suffix = '%Y-%m-%d.log'
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 默认日志记录器
default_logger = setup_logger(
    name='wiseflow_python',
    level=CRAWLER_SETTINGS.get('log_level', 'INFO'),
    log_file=CRAWLER_SETTINGS.get('log_file')
)


def get_logger(name=None):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logger: 日志记录器
    """
    if name:
        return logging.getLogger(name)
    return default_logger 