#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库配置模块
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '103.112.99.20'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'wiseflow_python'),
    'password': os.getenv('DB_PASSWORD', 'aY7YjpJY4JxEYAG2'),
    'database': os.getenv('DB_NAME', 'wiseflow_python'),
    'charset': 'utf8mb4',
}

# SQLAlchemy连接字符串
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}'.format(**DB_CONFIG)

# 数据库连接池配置
POOL_SIZE = 10
MAX_OVERFLOW = 20
POOL_RECYCLE = 3600
POOL_TIMEOUT = 30

# 表前缀
TABLE_PREFIX = 'wf_'

# 是否显示SQL语句
ECHO_SQL = False 