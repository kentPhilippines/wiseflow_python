#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫设置模块
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 目标网站
TARGET_URL = 'https://news.163.com/'

# 爬虫设置
CRAWLER_SETTINGS = {
    # 爬虫名称
    'name': 'netease_news_spider',
    
    # 并发请求数
    'concurrent_requests': 32,
    
    # 下载延迟（秒）
    'download_delay': 1.0,
    
    # 随机下载延迟
    'randomize_download_delay': True,
    
    # 请求超时（秒）
    'download_timeout': 30,
    
    # 重试次数
    'retry_times': 3,
    
    # 重试HTTP状态码
    'retry_http_codes': [500, 502, 503, 504, 408, 429],
    
    # 是否遵循robots.txt规则
    'robotstxt_obey': True,
    
    # 默认请求头
    'default_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    },
    
    # 是否启用cookies
    'cookies_enabled': True,
    
    # 是否启用telnet控制台
    'telnetconsole_enabled': False,
    
    # 日志级别
    'log_level': 'INFO',
    
    # 日志文件
    'log_file': os.path.join(BASE_DIR, 'logs', 'spider.log'),
    
    # 是否启用内存调试
    'memdebug_enabled': False,
    
    # 是否启用自动限速
    'autothrottle_enabled': True,
    
    # 自动限速初始延迟
    'autothrottle_start_delay': 3,
    
    # 自动限速最大延迟
    'autothrottle_max_delay': 30,
    
    # 自动限速目标并发数
    'autothrottle_target_concurrency': 2.0,
    
    # 是否显示限速统计
    'autothrottle_debug': False,
}

# 图片设置
IMAGE_SETTINGS = {
    # 图片存储路径
    'store_path': os.path.join(BASE_DIR, 'data', 'images'),
    
    # 图片大小限制（字节）
    'size_limit': 10 * 1024 * 1024,  # 10MB
    
    # 图片类型
    'allowed_types': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    
    # 是否调整图片大小
    'resize_enabled': True,
    
    # 调整后的最大宽度
    'max_width': 1200,
    
    # 调整后的最大高度
    'max_height': 1200,
    
    # 图片质量（1-100）
    'quality': 85,
    
    # 是否保留原始图片
    'keep_original': True,
}

# 代理设置
PROXY_SETTINGS = {
    # 是否启用代理
    'enabled': False,
    
    # 代理类型（http, https, socks5）
    'type': 'http',
    
    # 代理地址列表
    'proxies': [
        # 'http://user:pass@host:port',
    ],
    
    # 代理API地址
    'proxy_api': '',
    
    # 代理API密钥
    'proxy_api_key': '',
    
    # 代理检查超时（秒）
    'check_timeout': 10,
    
    # 代理最大失败次数
    'max_fail_times': 3,
}

# User-Agent设置
USER_AGENT_SETTINGS = {
    # 是否启用User-Agent轮换
    'enabled': True,
    
    # User-Agent列表
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux i686; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    ],
}

# Selenium设置
SELENIUM_SETTINGS = {
    # 是否启用Selenium
    'enabled': True,
    
    # 浏览器类型（chrome, firefox, edge）
    'browser': 'chrome',
    
    # 是否使用无头模式
    'headless': True,
    
    # 窗口大小
    'window_size': (1920, 1080),
    
    # 页面加载超时（秒）
    'page_load_timeout': 30,
    
    # 等待元素超时（秒）
    'implicit_wait': 10,
    
    # 是否禁用图片加载
    'disable_images': True,
    
    # 是否禁用JavaScript
    'disable_javascript': False,
    
    # 是否禁用CSS
    'disable_css': False,
    
    # 是否禁用cookies
    'disable_cookies': False,
    
    # 是否启用代理
    'use_proxy': False,
    
    # 代理地址
    'proxy': '',
    
    # WebDriver路径
    'webdriver_path': '',
}

# 定时任务设置
SCHEDULE_SETTINGS = {
    # 是否启用定时任务
    'enabled': True,
    
    # 任务间隔（小时）
    'interval': 6,
    
    # 开始时间（24小时制）
    'start_time': '00:00',
    
    # 结束时间（24小时制）
    'end_time': '23:59',
    
    # 是否在启动时立即运行
    'run_on_start': True,
}

# 导出设置
EXPORT_SETTINGS = {
    # 导出格式（json, xml, csv）
    'formats': ['json', 'xml', 'csv'],
    
    # 导出路径
    'export_path': os.path.join(BASE_DIR, 'data', 'exports'),
    
    # 是否压缩导出文件
    'compress': True,
    
    # 压缩格式（zip, gz, bz2）
    'compress_format': 'zip',
    
    # 是否包含时间戳
    'include_timestamp': True,
    
    # 导出文件编码
    'encoding': 'utf-8',
    
    # CSV分隔符
    'csv_delimiter': ',',
    
    # 是否包含表头
    'include_header': True,
}

# 新闻分类
NEWS_CATEGORIES = [
    {'id': 1, 'name': '头条', 'url': 'https://news.163.com/'},
    {'id': 2, 'name': '国内', 'url': 'https://news.163.com/domestic/'},
    {'id': 3, 'name': '国际', 'url': 'https://news.163.com/world/'},
    {'id': 4, 'name': '军事', 'url': 'https://news.163.com/military/'},
    {'id': 5, 'name': '财经', 'url': 'https://money.163.com/'},
    {'id': 6, 'name': '科技', 'url': 'https://tech.163.com/'},
    {'id': 7, 'name': '体育', 'url': 'https://sports.163.com/'},
    {'id': 8, 'name': '娱乐', 'url': 'https://ent.163.com/'},
    {'id': 9, 'name': '汽车', 'url': 'https://auto.163.com/'},
    {'id': 10, 'name': '房产', 'url': 'https://house.163.com/'},
    # 添加更多分类
    {'id': 11, 'name': '教育', 'url': 'https://edu.163.com/'},
    {'id': 12, 'name': '健康', 'url': 'https://jiankang.163.com/'},
    {'id': 13, 'name': '旅游', 'url': 'https://travel.163.com/'},
    {'id': 14, 'name': '政务', 'url': 'https://gov.163.com/'},
    {'id': 15, 'name': '数据', 'url': 'https://data.163.com/'},
    {'id': 16, 'name': '女性', 'url': 'https://lady.163.com/'},
    {'id': 17, 'name': '手机', 'url': 'https://mobile.163.com/'},
    {'id': 18, 'name': '彩票', 'url': 'https://caipiao.163.com/'},
    {'id': 19, 'name': '直播', 'url': 'https://live.163.com/'},
    {'id': 20, 'name': '本地', 'url': 'https://news.163.com/local/'},
    {'id': 21, 'name': '热点', 'url': 'https://news.163.com/hot/'},
    {'id': 22, 'name': '排行', 'url': 'https://news.163.com/rank/'},
    {'id': 23, 'name': '专题', 'url': 'https://news.163.com/special/'},
    {'id': 24, 'name': '订阅', 'url': 'https://dy.163.com/'},
] 