#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
网易新闻爬虫
"""

import re
import json
import logging
import datetime
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup

from config.settings import NEWS_CATEGORIES, CRAWLER_SETTINGS
from crawler.items import NewsItem, ImageItem, TagItem

logger = logging.getLogger(__name__)


class NeteaseNewsSpider(CrawlSpider):
    """网易新闻爬虫"""
    name = CRAWLER_SETTINGS['name']
    allowed_domains = ['163.com']
    start_urls = [category['url'] for category in NEWS_CATEGORIES]
    
    # 爬取规则
    rules = (
        # 新闻列表页规则
        Rule(
            LinkExtractor(
                allow=(r'news\.163\.com/\d+/\d+/\d+/.*\.html', r'news\.163\.com/.*\.html'),
                deny=(r'news\.163\.com/photo', r'news\.163\.com/special', r'news\.163\.com/video')
            ),
            callback='parse_news',
            follow=True
        ),
        # 分页规则
        Rule(
            LinkExtractor(
                allow=(r'news\.163\.com/.*_\d+\.html', r'news\.163\.com/.*\?page=\d+')
            ),
            follow=True
        ),
    )
    
    def __init__(self, *args, **kwargs):
        super(NeteaseNewsSpider, self).__init__(*args, **kwargs)
        self.crawl_time = datetime.datetime.now()
    
    def start_requests(self):
        """开始请求"""
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)
    
    def parse_news(self, response):
        """解析新闻页面"""
        logger.info(f"正在解析新闻页面: {response.url}")
        
        # 创建新闻项
        news_item = NewsItem()
        news_item['url'] = response.url
        news_item['crawl_time'] = self.crawl_time
        news_item['spider_name'] = self.name
        
        # 解析标题
        title = response.css('h1.post_title::text').get()
        if not title:
            title = response.css('h1.title::text').get()
        news_item['title'] = title.strip() if title else ''
        
        # 解析副标题
        subtitle = response.css('div.post_subtitle::text').get()
        news_item['subtitle'] = subtitle.strip() if subtitle else ''
        
        # 解析来源
        source = response.css('div.post_info a.source::text').get()
        if not source:
            source = response.css('div.post_info span.source::text').get()
        news_item['source'] = source.strip() if source else ''
        
        # 解析作者
        author = response.css('div.post_author::text').get()
        news_item['author'] = author.strip() if author else ''
        
        # 解析发布时间
        publish_time = response.css('div.post_info span.post_time::text').get()
        if publish_time:
            try:
                news_item['publish_time'] = datetime.datetime.strptime(
                    publish_time.strip(), '%Y-%m-%d %H:%M:%S'
                )
            except ValueError:
                news_item['publish_time'] = self.crawl_time
        else:
            news_item['publish_time'] = self.crawl_time
        
        # 解析分类
        category_name = None
        for category in NEWS_CATEGORIES:
            if category['url'] in response.url:
                news_item['category_id'] = category['id']
                news_item['category_name'] = category['name']
                category_name = category['name']
                break
        
        if not category_name:
            # 默认分类为头条
            news_item['category_id'] = 1
            news_item['category_name'] = '头条'
        
        # 解析内容
        content_html = response.css('div.post_body').get()
        if not content_html:
            content_html = response.css('div.post_text').get()
        
        if content_html:
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(content_html, 'lxml')
            
            # 提取纯文本内容
            content = soup.get_text(strip=True)
            news_item['content'] = content
            news_item['content_html'] = content_html
            
            # 提取摘要
            summary = content[:200] + '...' if len(content) > 200 else content
            news_item['summary'] = summary
            
            # 提取关键词
            keywords = response.css('meta[name="keywords"]::attr(content)').get()
            news_item['keywords'] = keywords if keywords else ''
            
            # 提取图片
            images = []
            img_tags = soup.find_all('img')
            for i, img in enumerate(img_tags):
                img_url = img.get('src', '')
                if not img_url:
                    continue
                
                # 处理相对URL
                if not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(response.url, img_url)
                
                # 创建图片项
                image_item = ImageItem()
                image_item['url'] = img_url
                image_item['news_url'] = response.url
                image_item['title'] = img.get('alt', '')
                image_item['description'] = img.get('title', '')
                image_item['is_cover'] = (i == 0)  # 第一张图片作为封面
                image_item['position'] = i
                image_item['crawl_time'] = self.crawl_time
                
                images.append(dict(image_item))
                
                # 单独提交图片项
                yield image_item
            
            news_item['images'] = images
        
        # 解析标签
        tags = []
        tag_elements = response.css('div.post_tags a::text').getall()
        if tag_elements:
            for tag_name in tag_elements:
                tag_name = tag_name.strip()
                if tag_name:
                    # 创建标签项
                    tag_item = TagItem()
                    tag_item['name'] = tag_name
                    tag_item['news_urls'] = [response.url]
                    
                    tags.append(tag_name)
                    
                    # 单独提交标签项
                    yield tag_item
        
        news_item['tags'] = tags
        
        # 解析统计信息
        view_count_text = response.css('div.post_info span.post_view::text').get()
        if view_count_text:
            view_count_match = re.search(r'\d+', view_count_text)
            if view_count_match:
                news_item['view_count'] = int(view_count_match.group())
        
        # 设置默认值
        news_item.setdefault('view_count', 0)
        news_item.setdefault('comment_count', 0)
        news_item.setdefault('like_count', 0)
        news_item.setdefault('is_top', False)
        news_item.setdefault('is_hot', False)
        news_item.setdefault('is_recommend', False)
        news_item.setdefault('status', 1)
        
        # 尝试从JavaScript中提取更多信息
        script_text = response.xpath('//script[contains(text(), "window.NTES")]/text()').get()
        if script_text:
            try:
                # 提取JSON数据
                json_match = re.search(r'window\.NTES\s*=\s*(\{.*?\});', script_text, re.DOTALL)
                if json_match:
                    json_data = json.loads(json_match.group(1))
                    
                    # 提取评论数
                    if 'commentCount' in json_data:
                        news_item['comment_count'] = int(json_data['commentCount'])
                    
                    # 提取点赞数
                    if 'likeCount' in json_data:
                        news_item['like_count'] = int(json_data['likeCount'])
            except Exception as e:
                logger.error(f"解析JavaScript数据失败: {str(e)}")
        
        yield news_item
    
    def closed(self, reason):
        """爬虫关闭时的回调"""
        logger.info(f"爬虫关闭，原因: {reason}")
        end_time = datetime.datetime.now()
        duration = (end_time - self.crawl_time).total_seconds()
        logger.info(f"爬虫运行时间: {duration}秒") 