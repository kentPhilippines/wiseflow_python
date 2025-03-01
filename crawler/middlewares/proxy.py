#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代理中间件
"""

import logging
import random
import requests
import json
from urllib.parse import urlparse
from scrapy import signals
from scrapy.exceptions import IgnoreRequest

from config.settings import PROXY_SETTINGS

logger = logging.getLogger(__name__)


class RandomProxyMiddleware:
    """随机代理中间件"""
    
    def __init__(self):
        """初始化"""
        self.enabled = PROXY_SETTINGS['enabled']
        self.proxy_type = PROXY_SETTINGS['type']
        self.proxies = PROXY_SETTINGS['proxies']
        self.proxy_api = PROXY_SETTINGS['proxy_api']
        self.proxy_api_key = PROXY_SETTINGS['proxy_api_key']
        self.check_timeout = PROXY_SETTINGS['check_timeout']
        self.max_fail_times = PROXY_SETTINGS['max_fail_times']
        
        # 代理状态
        self.proxy_stats = {}
        self.count = 0
        
        logger.info(f"随机代理中间件初始化，启用状态: {self.enabled}")
        
        # 如果启用了代理API，则从API获取代理列表
        if self.enabled and self.proxy_api:
            self._fetch_proxies_from_api()
    
    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫创建中间件"""
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def process_request(self, request, spider):
        """处理请求"""
        if not self.enabled or not self.proxies:
            return None
            
        # 随机选择一个代理
        proxy = self._get_random_proxy()
        if not proxy:
            logger.warning("没有可用的代理")
            return None
            
        # 设置代理
        request.meta['proxy'] = proxy
        self.count += 1
        
        if self.count % 50 == 0:
            logger.info(f"已使用代理 {self.count} 次")
        
        return None
    
    def process_response(self, request, response, spider):
        """处理响应"""
        if not self.enabled or 'proxy' not in request.meta:
            return response
            
        proxy = request.meta['proxy']
        
        # 检查响应状态
        if response.status >= 400:
            self._mark_proxy_fail(proxy)
            logger.warning(f"代理 {proxy} 返回状态码 {response.status}")
        else:
            self._mark_proxy_success(proxy)
        
        return response
    
    def process_exception(self, request, exception, spider):
        """处理异常"""
        if not self.enabled or 'proxy' not in request.meta:
            return None
            
        proxy = request.meta['proxy']
        self._mark_proxy_fail(proxy)
        logger.warning(f"代理 {proxy} 发生异常: {str(exception)}")
        
        # 如果代理失败次数过多，则从列表中移除
        if self.proxy_stats.get(proxy, {}).get('fail_times', 0) >= self.max_fail_times:
            self._remove_proxy(proxy)
            logger.warning(f"代理 {proxy} 失败次数过多，已移除")
            
            # 如果没有可用代理，则尝试重新获取
            if not self.proxies and self.proxy_api:
                self._fetch_proxies_from_api()
        
        return None
    
    def _get_random_proxy(self):
        """获取随机代理"""
        if not self.proxies:
            return None
            
        # 按照成功率排序，优先选择成功率高的代理
        sorted_proxies = sorted(
            self.proxies,
            key=lambda p: self.proxy_stats.get(p, {}).get('success_rate', 0),
            reverse=True
        )
        
        # 从前80%的代理中随机选择
        top_count = max(1, int(len(sorted_proxies) * 0.8))
        return random.choice(sorted_proxies[:top_count])
    
    def _mark_proxy_success(self, proxy):
        """标记代理成功"""
        if proxy not in self.proxy_stats:
            self.proxy_stats[proxy] = {'success': 0, 'fail': 0, 'success_rate': 0, 'fail_times': 0}
            
        self.proxy_stats[proxy]['success'] += 1
        self.proxy_stats[proxy]['fail_times'] = 0
        
        # 计算成功率
        total = self.proxy_stats[proxy]['success'] + self.proxy_stats[proxy]['fail']
        self.proxy_stats[proxy]['success_rate'] = self.proxy_stats[proxy]['success'] / total if total > 0 else 0
    
    def _mark_proxy_fail(self, proxy):
        """标记代理失败"""
        if proxy not in self.proxy_stats:
            self.proxy_stats[proxy] = {'success': 0, 'fail': 0, 'success_rate': 0, 'fail_times': 0}
            
        self.proxy_stats[proxy]['fail'] += 1
        self.proxy_stats[proxy]['fail_times'] += 1
        
        # 计算成功率
        total = self.proxy_stats[proxy]['success'] + self.proxy_stats[proxy]['fail']
        self.proxy_stats[proxy]['success_rate'] = self.proxy_stats[proxy]['success'] / total if total > 0 else 0
    
    def _remove_proxy(self, proxy):
        """移除代理"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
        if proxy in self.proxy_stats:
            del self.proxy_stats[proxy]
    
    def _fetch_proxies_from_api(self):
        """从API获取代理列表"""
        if not self.proxy_api:
            return
            
        try:
            # 构建API请求
            params = {}
            if self.proxy_api_key:
                params['key'] = self.proxy_api_key
            
            # 发送请求
            response = requests.get(self.proxy_api, params=params, timeout=self.check_timeout)
            if response.status_code != 200:
                logger.error(f"获取代理API返回状态码 {response.status_code}")
                return
                
            # 解析响应
            try:
                data = response.json()
                if isinstance(data, list):
                    self.proxies = data
                elif isinstance(data, dict) and 'data' in data:
                    self.proxies = data['data']
                else:
                    logger.error(f"无法解析代理API响应: {response.text}")
                    return
            except json.JSONDecodeError:
                # 尝试按行解析
                self.proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
            
            # 格式化代理
            self.proxies = [self._format_proxy(p) for p in self.proxies if p]
            logger.info(f"从API获取到 {len(self.proxies)} 个代理")
        except Exception as e:
            logger.error(f"获取代理API异常: {str(e)}")
    
    def _format_proxy(self, proxy):
        """格式化代理"""
        if isinstance(proxy, dict):
            # 如果是字典格式，提取IP和端口
            ip = proxy.get('ip', '')
            port = proxy.get('port', '')
            username = proxy.get('username', '')
            password = proxy.get('password', '')
            
            if not ip or not port:
                return None
                
            # 构建代理字符串
            if username and password:
                return f"{self.proxy_type}://{username}:{password}@{ip}:{port}"
            else:
                return f"{self.proxy_type}://{ip}:{port}"
        elif isinstance(proxy, str):
            # 如果是字符串格式，检查是否包含协议
            if '://' in proxy:
                return proxy
            else:
                return f"{self.proxy_type}://{proxy}"
        
        return None
    
    def _check_proxy(self, proxy):
        """检查代理是否可用"""
        try:
            # 构建测试URL
            test_url = 'http://httpbin.org/ip'
            
            # 设置代理
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            # 发送请求
            response = requests.get(test_url, proxies=proxies, timeout=self.check_timeout)
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False
    
    def spider_opened(self, spider):
        """爬虫开始时的回调"""
        logger.info("随机代理中间件启动")
        
        # 检查代理可用性
        if self.enabled and self.proxies:
            valid_proxies = []
            for proxy in self.proxies:
                if self._check_proxy(proxy):
                    valid_proxies.append(proxy)
                    logger.info(f"代理 {proxy} 可用")
                else:
                    logger.warning(f"代理 {proxy} 不可用")
            
            self.proxies = valid_proxies
            logger.info(f"检查完成，共有 {len(self.proxies)} 个可用代理")
    
    def spider_closed(self, spider):
        """爬虫结束时的回调"""
        logger.info(f"随机代理中间件关闭，共使用代理 {self.count} 次") 