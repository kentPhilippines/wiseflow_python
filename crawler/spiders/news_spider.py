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
    
    # 爬取规则 - 更新规则以匹配更多的新闻链接
    rules = (
        # 新闻列表页规则 - 扩展匹配模式
        Rule(
            LinkExtractor(
                allow=(
                    r'news\.163\.com/\d+/\d+/\d+/.*\.html', 
                    r'news\.163\.com/.*\.html',
                    r'money\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'ent\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'sports\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'tech\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'house\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'auto\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'war\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'travel\.163\.com/\d+/\d+/\d+/.*\.html',
                    r'dy\.163\.com/article/.*\.html',
                    # 添加更多的新闻链接模式
                    r'news\.163\.com/.*/.*/.*\.html',
                    r'data\.163\.com/.*\.html',
                    r'gov\.163\.com/.*\.html',
                    r'edu\.163\.com/.*\.html',
                    r'jiankang\.163\.com/.*\.html',
                    r'caipiao\.163\.com/.*\.html',
                    r'lady\.163\.com/.*\.html',
                    r'mobile\.163\.com/.*\.html'
                ),
                deny=(
                    r'news\.163\.com/photo', 
                    r'news\.163\.com/special', 
                    r'news\.163\.com/video',
                    r'comment\.news\.163\.com',  # 添加评论页面到拒绝列表
                    r'live\.163\.com',  # 直播页面
                    r'v\.163\.com',  # 视频页面
                    r'data\.163\.com/special',  # 数据专题
                    r'temp\.163\.com'  # 临时页面
                )
            ),
            callback='parse_news',
            follow=True
        ),
        # 分页规则 - 更新以匹配更多的分页模式
        Rule(
            LinkExtractor(
                allow=(
                    r'news\.163\.com/.*_\d+\.html', 
                    r'news\.163\.com/.*\?page=\d+',
                    r'news\.163\.com/.*/\d+\.html',
                    r'money\.163\.com/.*/\d+\.html',
                    r'ent\.163\.com/.*/\d+\.html',
                    r'sports\.163\.com/.*/\d+\.html',
                    r'tech\.163\.com/.*/\d+\.html',
                    # 添加更多的分页模式
                    r'.*\.163\.com/.*[?&]page=\d+',
                    r'.*\.163\.com/.*/index_\d+\.html',
                    r'.*\.163\.com/.*_\d+\.html',
                    r'.*\.163\.com/.*/list_\d+\.html'
                )
            ),
            follow=True
        ),
        # 添加新的规则：专题页面规则
        Rule(
            LinkExtractor(
                allow=(
                    r'news\.163\.com/special/.*',
                    r'.*\.163\.com/special/.*'
                ),
                deny=(
                    r'.*\.163\.com/special/.*/photo',
                    r'.*\.163\.com/special/.*/video'
                )
            ),
            callback='parse_special_page',
            follow=True
        ),
    )
    
    def __init__(self, *args, **kwargs):
        super(NeteaseNewsSpider, self).__init__(*args, **kwargs)
        self.crawl_time = datetime.datetime.now()
        # 添加计数器以跟踪处理的页面和新闻
        self.pages_processed = 0
        self.news_found = 0
        self.news_processed = 0
        # 添加已处理URL集合，避免重复处理
        self.processed_urls = set()
    
    def start_requests(self):
        """开始请求"""
        logger.info(f"开始爬取，起始URL数量: {len(self.start_urls)}")
        for url in self.start_urls:
            logger.info(f"请求起始URL: {url}")
            yield scrapy.Request(url, dont_filter=True)
    
    def parse(self, response):
        """解析首页和分类页面，提取新闻链接"""
        self.pages_processed += 1
        logger.info(f"正在解析页面[{self.pages_processed}]: {response.url}")
        
        # 提取新闻链接 - 更新选择器以匹配当前网站结构
        news_links = response.css('a.news-item-title::attr(href), a.news-title::attr(href), a.title::attr(href), a.data-title::attr(href), div.news_title a::attr(href), h3.title a::attr(href), div.titleBar a::attr(href), a.article-link::attr(href), div.news_item a::attr(href), div.ndi_main a::attr(href), div.news_title h3 a::attr(href), div.item_top h2 a::attr(href), div.news-item h3 a::attr(href), ul.cm_ul li a::attr(href), div.data_row a::attr(href), div.news_hot_list a::attr(href), div.hot_list a::attr(href), div.news-list a::attr(href), div.list-item a::attr(href), div.item h2 a::attr(href), div.content a::attr(href)').getall()
        logger.info(f"使用主选择器找到 {len(news_links)} 个链接")
        
        # 如果没有找到链接，尝试其他选择器
        if not news_links:
            all_links = response.css('a::attr(href)').getall()
            logger.info(f"找到 {len(all_links)} 个所有链接")
            # 过滤链接，只保留可能是新闻的链接
            news_links = [link for link in all_links if re.search(r'(news|money|ent|sports|tech|house|auto|war|travel|gov|edu|jiankang|caipiao|lady|mobile|data)\.163\.com/.*\.html', link) or re.search(r'dy\.163\.com/article/.*\.html', link)]
            logger.info(f"过滤后找到 {len(news_links)} 个可能的新闻链接")
        
        # 处理提取到的链接
        for link in news_links:
            # 处理相对URL
            if not link.startswith(('http://', 'https://')):
                link = urljoin(response.url, link)
            
            # 过滤链接
            if any(domain in link for domain in self.allowed_domains) and link not in self.processed_urls:
                self.processed_urls.add(link)
                self.news_found += 1
                logger.info(f"发现有效新闻链接[{self.news_found}]: {link}")
                yield scrapy.Request(link, callback=self.parse_news)
        
        # 提取下一页链接 - 增强下一页链接的提取能力
        next_page = response.css('a.next::attr(href), a.pagination_next::attr(href), a.js-next::attr(href), div.pagination a:contains("下一页")::attr(href), a.nxt::attr(href), a.nexta::attr(href), a[rel="next"]::attr(href), a.load-more::attr(href), a.more::attr(href), a.page-next::attr(href), a.next-page::attr(href)').get()
        if next_page:
            if not next_page.startswith(('http://', 'https://')):
                next_page = urljoin(response.url, next_page)
            logger.info(f"发现下一页链接: {next_page}")
            yield scrapy.Request(next_page, callback=self.parse)
        
        # 尝试从页面中提取更多的新闻列表页链接
        list_page_links = response.css('div.channel a::attr(href), div.category a::attr(href), div.nav a::attr(href), div.subnav a::attr(href), div.menu a::attr(href), div.submenu a::attr(href), div.tabs a::attr(href), div.tab a::attr(href), div.more a::attr(href)').getall()
        for link in list_page_links:
            if not link.startswith(('http://', 'https://')):
                link = urljoin(response.url, link)
            
            # 过滤链接，只保留网易域名下的链接
            if any(domain in link for domain in self.allowed_domains) and link not in self.processed_urls:
                self.processed_urls.add(link)
                logger.info(f"发现新闻列表页链接: {link}")
                yield scrapy.Request(link, callback=self.parse)
    
    def parse_special_page(self, response):
        """解析专题页面，提取新闻链接"""
        logger.info(f"正在解析专题页面: {response.url}")
        
        # 提取专题页面中的新闻链接
        news_links = response.css('a::attr(href)').getall()
        news_links = [link for link in news_links if re.search(r'.*\.163\.com/.*\.html', link)]
        
        for link in news_links:
            if not link.startswith(('http://', 'https://')):
                link = urljoin(response.url, link)
            
            if any(domain in link for domain in self.allowed_domains) and link not in self.processed_urls:
                self.processed_urls.add(link)
                self.news_found += 1
                logger.info(f"从专题页面发现新闻链接[{self.news_found}]: {link}")
                yield scrapy.Request(link, callback=self.parse_news)
    
    def parse_news(self, response):
        """解析新闻页面"""
        self.news_processed += 1
        logger.info(f"正在解析新闻页面[{self.news_processed}]: {response.url}")
        
        # 创建新闻项
        news_item = NewsItem()
        news_item['url'] = response.url
        news_item['crawl_time'] = self.crawl_time
        news_item['spider_name'] = self.name
        
        # 解析标题 - 更新选择器以匹配当前网站结构
        title = response.css('h1.post_title::text, h1.title::text, h1.article-title::text, h1.main-title::text, div.article-header h1::text, h1.headline::text, h1.news_title::text, h1.art_tit::text, h1.main_title::text, h1.page_title::text').get()
        if not title:
            title = response.xpath('//h1[contains(@class, "title") or contains(@class, "post_title") or contains(@class, "headline") or contains(@class, "news_title")]/text()').get()
        news_item['title'] = title.strip() if title else ''
        logger.info(f"解析到标题: {news_item['title']}")
        
        # 如果没有找到标题，可能不是新闻页面，跳过处理
        if not news_item['title']:
            logger.warning(f"未找到标题，可能不是新闻页面: {response.url}")
            return
        
        # 解析副标题
        subtitle = response.css('div.post_subtitle::text, div.sub-title::text, div.article-subtitle::text, div.sub_title::text, div.subtitle::text, p.summary::text').get()
        news_item['subtitle'] = subtitle.strip() if subtitle else ''
        
        # 解析来源
        source = response.css('div.post_info a.source::text, div.post_info span.source::text, div.article-source a::text, span.source::text, a.source::text, div.info a.source::text, div.info span.source::text, div.from a::text, div.from span::text, div.article_info span.source::text, div.article_info a.source::text').get()
        news_item['source'] = source.strip() if source else ''
        
        # 解析作者
        author = response.css('div.post_author::text, div.author::text, span.author::text, div.article-author::text, div.info span.author::text, div.info a.author::text, div.article_info span.author::text, div.article_info a.author::text').get()
        news_item['author'] = author.strip() if author else ''
        
        # 解析发布时间
        publish_time = response.css('div.post_info span.post_time::text, div.post_info time::text, span.time::text, span.publish-time::text, div.article-info span.date::text, div.info span.time::text, div.info time::text, div.from span.time::text, div.from time::text, div.article_info span.time::text, div.article_info time::text').get()
        if publish_time:
            try:
                # 尝试多种日期格式
                for date_format in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y年%m月%d日 %H:%M:%S', '%Y年%m月%d日 %H:%M']:
                    try:
                        news_item['publish_time'] = datetime.datetime.strptime(publish_time.strip(), date_format)
                        break
                    except ValueError:
                        continue
                if 'publish_time' not in news_item:
                    news_item['publish_time'] = self.crawl_time
            except Exception as e:
                logger.error(f"解析发布时间失败: {str(e)}")
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
            # 尝试从URL中提取分类
            url_parts = urlparse(response.url).netloc.split('.')
            if len(url_parts) > 0 and url_parts[0] != 'www' and url_parts[0] != 'news':
                category_name = url_parts[0]
                # 映射常见分类
                category_map = {
                    'money': '财经',
                    'ent': '娱乐',
                    'sports': '体育',
                    'tech': '科技',
                    'house': '房产',
                    'auto': '汽车',
                    'war': '军事',
                    'travel': '旅游',
                    'dy': '订阅',
                    'gov': '政务',
                    'edu': '教育',
                    'jiankang': '健康',
                    'caipiao': '彩票',
                    'lady': '女性',
                    'mobile': '手机',
                    'data': '数据'
                }
                if category_name in category_map:
                    category_name = category_map[category_name]
                    # 查找对应的分类ID
                    for category in NEWS_CATEGORIES:
                        if category['name'] == category_name:
                            news_item['category_id'] = category['id']
                            news_item['category_name'] = category_name
                            break
                    if 'category_id' not in news_item:
                        news_item['category_id'] = 99  # 其他分类
                        news_item['category_name'] = category_name
            
            # 如果仍未找到分类，设为默认
            if 'category_id' not in news_item:
                news_item['category_id'] = 1
                news_item['category_name'] = '头条'
        
        # 解析内容 - 更新选择器以匹配当前网站结构
        content_html = response.css('div.post_body, div.post_text, div.article-content, div.main-content, article.article-content, div.content, div.article, div.news_txt, div.article_content, div.main_content, div.end_content').get()
        
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
                
                # 创建图片项（只保存基本信息，不下载）
                image_info = {
                    'url': img_url,
                    'news_url': response.url,
                    'title': img.get('alt', ''),
                    'description': img.get('title', ''),
                    'is_cover': (i == 0),  # 第一张图片作为封面
                    'position': i
                }
                
                images.append(image_info)
            
            news_item['images'] = images
            logger.info(f"解析到 {len(images)} 张图片")
            
            # 提取相关新闻链接
            related_links = []
            related_elements = soup.select('div.related_news a, div.related a, div.relative_news a, div.relevant a, div.correlation a, div.related-news a, div.news-related a')
            for related in related_elements:
                related_link = related.get('href', '')
                if not related_link:
                    continue
                
                # 处理相对URL
                if not related_link.startswith(('http://', 'https://')):
                    related_link = urljoin(response.url, related_link)
                
                # 过滤链接
                if any(domain in related_link for domain in self.allowed_domains) and related_link not in self.processed_urls:
                    related_links.append(related_link)
                    self.processed_urls.add(related_link)
                    self.news_found += 1
                    logger.info(f"发现相关新闻链接[{self.news_found}]: {related_link}")
                    yield scrapy.Request(related_link, callback=self.parse_news)
        else:
            logger.warning(f"未找到内容: {response.url}")
            # 如果没有找到内容，但有标题，仍然处理这条新闻
            news_item['content'] = ''
            news_item['content_html'] = ''
            news_item['summary'] = ''
            news_item['keywords'] = ''
            news_item['images'] = []
        
        # 解析标签
        tags = []
        tag_elements = response.css('div.post_tags a::text, div.article-tags a::text, div.tags a::text, div.tag a::text, div.keywords a::text, div.key_word a::text').getall()
        if tag_elements:
            for tag_name in tag_elements:
                tag_name = tag_name.strip()
                if tag_name:
                    # 创建标签项
                    tag_item = TagItem()
                    tag_item['name'] = tag_name
                    tag_item['news_urls'] = [response.url]
                    
                    tags.append(tag_name)
        
        news_item['tags'] = tags
        
        # 解析统计信息
        view_count_text = response.css('div.post_info span.post_view::text, span.view-count::text, span.views::text, span.view::text, span.read::text, span.read-count::text').get()
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
        
        # 直接输出新闻项
        logger.info(f"成功解析新闻: {news_item['title']}")
        yield news_item
    
    def closed(self, reason):
        """爬虫关闭时的回调"""
        logger.info(f"爬虫关闭，原因: {reason}")
        logger.info(f"页面处理数: {self.pages_processed}, 发现新闻链接数: {self.news_found}, 处理新闻数: {self.news_processed}")
        end_time = datetime.datetime.now()
        duration = (end_time - self.crawl_time).total_seconds()
        logger.info(f"爬虫运行时间: {duration}秒") 