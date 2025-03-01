#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行爬虫脚本
"""

import os
import sys
import time
import logging
import argparse
import datetime
import schedule
from pathlib import Path

# 添加项目根目录到系统路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings

from config.settings import CRAWLER_SETTINGS, SCHEDULE_SETTINGS
from database.db_handler import init_db
from utils.logger import setup_logger
from crawler.spiders.news_spider import NeteaseNewsSpider

# 设置日志
logger = setup_logger(
    name='run_crawler',
    level=CRAWLER_SETTINGS.get('log_level', 'INFO'),
    log_file=os.path.join(BASE_DIR, 'logs', 'run_crawler.log')
)

# 设置Scrapy日志输出到文件而不是控制台
import logging
# 移除这行代码，不再将scrapy日志传播到控制台
# logging.getLogger('scrapy').propagate = True


def get_scrapy_settings():
    """获取Scrapy设置"""
    settings = Settings()
    
    # 爬虫设置
    settings.set('BOT_NAME', CRAWLER_SETTINGS['name'])
    settings.set('CONCURRENT_REQUESTS', CRAWLER_SETTINGS['concurrent_requests'])
    settings.set('DOWNLOAD_DELAY', CRAWLER_SETTINGS['download_delay'])
    settings.set('RANDOMIZE_DOWNLOAD_DELAY', CRAWLER_SETTINGS['randomize_download_delay'])
    settings.set('DOWNLOAD_TIMEOUT', CRAWLER_SETTINGS['download_timeout'])
    settings.set('RETRY_TIMES', CRAWLER_SETTINGS['retry_times'])
    settings.set('RETRY_HTTP_CODES', CRAWLER_SETTINGS['retry_http_codes'])
    settings.set('ROBOTSTXT_OBEY', CRAWLER_SETTINGS['robotstxt_obey'])
    settings.set('DEFAULT_REQUEST_HEADERS', CRAWLER_SETTINGS['default_headers'])
    settings.set('COOKIES_ENABLED', CRAWLER_SETTINGS['cookies_enabled'])
    settings.set('TELNETCONSOLE_ENABLED', CRAWLER_SETTINGS['telnetconsole_enabled'])
    settings.set('LOG_LEVEL', CRAWLER_SETTINGS['log_level'])
    # 恢复LOG_FILE设置，使日志输出到文件
    settings.set('LOG_FILE', CRAWLER_SETTINGS['log_file'])
    # 禁用日志到控制台
    settings.set('LOG_STDOUT', False)
    
    # 自动限速设置
    settings.set('AUTOTHROTTLE_ENABLED', CRAWLER_SETTINGS['autothrottle_enabled'])
    settings.set('AUTOTHROTTLE_START_DELAY', CRAWLER_SETTINGS['autothrottle_start_delay'])
    settings.set('AUTOTHROTTLE_MAX_DELAY', CRAWLER_SETTINGS['autothrottle_max_delay'])
    settings.set('AUTOTHROTTLE_TARGET_CONCURRENCY', CRAWLER_SETTINGS['autothrottle_target_concurrency'])
    settings.set('AUTOTHROTTLE_DEBUG', CRAWLER_SETTINGS['autothrottle_debug'])
    
    # 中间件设置
    settings.set('DOWNLOADER_MIDDLEWARES', {
        'crawler.middlewares.user_agent.RandomUserAgentMiddleware': 400,
        'crawler.middlewares.proxy.RandomProxyMiddleware': 410,
    })
    
    # 管道设置
    settings.set('ITEM_PIPELINES', {
        'crawler.pipelines.news_pipeline.NeteaseNewsPipeline': 300,
        # 禁用图片下载管道
        # 'crawler.pipelines.image_pipeline.NeteaseImagePipeline': 200,
    })
    
    # 图片设置
    settings.set('IMAGES_STORE', os.path.join(BASE_DIR, 'data', 'images'))
    
    return settings


def run_spider():
    """运行爬虫"""
    try:
        logger.info("开始运行爬虫")
        
        # 初始化数据库
        init_db()
        
        # 获取Scrapy设置
        settings = get_scrapy_settings()
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        # 添加爬虫
        process.crawl(NeteaseNewsSpider)
        
        # 启动爬虫
        process.start()
        
        logger.info("爬虫运行完成")
        return True
    except Exception as e:
        logger.error(f"爬虫运行失败: {str(e)}")
        return False


def run_scheduled_task():
    """运行定时任务"""
    logger.info(f"定时任务开始执行，当前时间: {datetime.datetime.now()}")
    success = run_spider()
    logger.info(f"定时任务执行{'成功' if success else '失败'}，当前时间: {datetime.datetime.now()}")


def schedule_task():
    """调度定时任务"""
    if not SCHEDULE_SETTINGS['enabled']:
        logger.info("定时任务未启用")
        return
    
    # 设置定时任务
    interval_hours = SCHEDULE_SETTINGS['interval']
    logger.info(f"设置定时任务，间隔: {interval_hours}小时")
    
    # 每隔N小时运行一次
    schedule.every(interval_hours).hours.do(run_scheduled_task)
    
    # 如果设置了立即运行
    if SCHEDULE_SETTINGS['run_on_start']:
        logger.info("立即运行一次爬虫")
        run_scheduled_task()
    
    # 运行定时任务
    logger.info("开始运行定时任务")
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行网易新闻爬虫')
    parser.add_argument('--once', action='store_true', help='只运行一次爬虫')
    parser.add_argument('--schedule', action='store_true', help='按计划运行爬虫')
    args = parser.parse_args()
    
    # 创建日志目录
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
    
    # 创建数据目录
    os.makedirs(os.path.join(BASE_DIR, 'data', 'images'), exist_ok=True)
    
    if args.once:
        # 只运行一次
        run_spider()
    elif args.schedule:
        # 按计划运行
        schedule_task()
    else:
        # 默认只运行一次
        run_spider()


if __name__ == '__main__':
    main() 