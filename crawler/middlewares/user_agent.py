#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User-Agent中间件
"""

import logging
import random
from collections import defaultdict
from scrapy import signals
from scrapy.exceptions import IgnoreRequest

from config.settings import USER_AGENT_SETTINGS

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware:
    """随机User-Agent中间件"""
    
    def __init__(self):
        """初始化"""
        self.enabled = USER_AGENT_SETTINGS['enabled']
        self.user_agents = USER_AGENT_SETTINGS['user_agents']
        self.count = 0
        # 添加URL计数器，记录每个URL的尝试次数
        self.url_attempts = defaultdict(int)
        # 设置最大尝试次数
        self.max_attempts_per_url = 20
        logger.info(f"随机User-Agent中间件初始化，启用状态: {self.enabled}，每个URL最大尝试次数: {self.max_attempts_per_url}")
    
    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫创建中间件"""
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def process_request(self, request, spider):
        """处理请求"""
        if not self.enabled or not self.user_agents:
            return None
            
        # 获取请求URL
        url = request.url
        
        # 增加URL尝试次数
        self.url_attempts[url] += 1
        
        # 如果超过最大尝试次数，放弃请求
        if self.url_attempts[url] > self.max_attempts_per_url:
            logger.warning(f"URL {url} 已尝试 {self.url_attempts[url]-1} 次，超过最大尝试次数，放弃请求")
            raise IgnoreRequest(f"超过最大尝试次数 {self.max_attempts_per_url}")
            
        # 随机选择一个User-Agent
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        self.count += 1
        
        if self.count % 100 == 0:
            logger.info(f"已切换User-Agent {self.count} 次")
        
        return None
    
    def spider_opened(self, spider):
        """爬虫开始时的回调"""
        logger.info("随机User-Agent中间件启动")
    
    def spider_closed(self, spider):
        """爬虫结束时的回调"""
        logger.info(f"随机User-Agent中间件关闭，共切换User-Agent {self.count} 次，处理URL数: {len(self.url_attempts)}") 