#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML解析工具模块
"""

import re
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HtmlParser:
    """HTML解析器"""
    
    def __init__(self, html, base_url=None):
        """
        初始化
        
        Args:
            html: HTML内容
            base_url: 基础URL，用于处理相对URL
        """
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'lxml')
    
    def get_title(self):
        """
        获取标题
        
        Returns:
            str: 标题
        """
        title_tag = self.soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        h1_tag = self.soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return ''
    
    def get_meta_description(self):
        """
        获取meta描述
        
        Returns:
            str: meta描述
        """
        meta_tag = self.soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            return meta_tag.get('content', '')
        return ''
    
    def get_meta_keywords(self):
        """
        获取meta关键词
        
        Returns:
            str: meta关键词
        """
        meta_tag = self.soup.find('meta', attrs={'name': 'keywords'})
        if meta_tag:
            return meta_tag.get('content', '')
        return ''
    
    def get_text(self, selector=None):
        """
        获取文本内容
        
        Args:
            selector: CSS选择器
            
        Returns:
            str: 文本内容
        """
        if selector:
            elements = self.soup.select(selector)
            if elements:
                return ' '.join([elem.get_text(strip=True) for elem in elements])
        
        return self.soup.get_text(strip=True)
    
    def get_element_text(self, selector):
        """
        获取元素文本
        
        Args:
            selector: CSS选择器
            
        Returns:
            str: 元素文本
        """
        element = self.soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        return ''
    
    def get_elements_text(self, selector):
        """
        获取多个元素文本
        
        Args:
            selector: CSS选择器
            
        Returns:
            list: 元素文本列表
        """
        elements = self.soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]
    
    def get_attribute(self, selector, attribute):
        """
        获取元素属性
        
        Args:
            selector: CSS选择器
            attribute: 属性名
            
        Returns:
            str: 属性值
        """
        element = self.soup.select_one(selector)
        if element:
            return element.get(attribute, '')
        return ''
    
    def get_attributes(self, selector, attribute):
        """
        获取多个元素属性
        
        Args:
            selector: CSS选择器
            attribute: 属性名
            
        Returns:
            list: 属性值列表
        """
        elements = self.soup.select(selector)
        return [elem.get(attribute, '') for elem in elements]
    
    def get_links(self, selector=None):
        """
        获取链接
        
        Args:
            selector: CSS选择器
            
        Returns:
            list: 链接列表
        """
        if selector:
            elements = self.soup.select(selector)
        else:
            elements = self.soup.find_all('a')
        
        links = []
        for elem in elements:
            href = elem.get('href', '')
            if href and not href.startswith(('#', 'javascript:')):
                # 处理相对URL
                if self.base_url and not href.startswith(('http://', 'https://')):
                    href = urljoin(self.base_url, href)
                links.append(href)
        
        return links
    
    def get_images(self, selector=None):
        """
        获取图片
        
        Args:
            selector: CSS选择器
            
        Returns:
            list: 图片信息列表
        """
        if selector:
            elements = self.soup.select(selector)
        else:
            elements = self.soup.find_all('img')
        
        images = []
        for i, elem in enumerate(elements):
            src = elem.get('src', '')
            if not src:
                # 尝试获取data-src属性
                src = elem.get('data-src', '')
                if not src:
                    continue
            
            # 处理相对URL
            if self.base_url and not src.startswith(('http://', 'https://')):
                src = urljoin(self.base_url, src)
            
            # 图片信息
            image_info = {
                'url': src,
                'title': elem.get('alt', ''),
                'description': elem.get('title', ''),
                'is_cover': (i == 0),  # 第一张图片作为封面
                'position': i
            }
            
            images.append(image_info)
        
        return images
    
    def get_tables(self, selector=None):
        """
        获取表格
        
        Args:
            selector: CSS选择器
            
        Returns:
            list: 表格数据列表
        """
        if selector:
            tables = self.soup.select(selector)
        else:
            tables = self.soup.find_all('table')
        
        result = []
        for table in tables:
            rows = table.find_all('tr')
            table_data = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    table_data.append(row_data)
            
            if table_data:
                result.append(table_data)
        
        return result
    
    def remove_elements(self, selector):
        """
        移除元素
        
        Args:
            selector: CSS选择器
            
        Returns:
            HtmlParser: 当前实例
        """
        for element in self.soup.select(selector):
            element.decompose()
        
        self.html = str(self.soup)
        return self
    
    def extract_content(self, content_selectors=None):
        """
        提取正文内容
        
        Args:
            content_selectors: 正文选择器列表
            
        Returns:
            dict: 正文内容
        """
        # 默认正文选择器
        if not content_selectors:
            content_selectors = [
                'div.post_body',
                'div.post_text',
                'div.article-content',
                'div.content',
                'article',
                'div.main-content'
            ]
        
        # 尝试使用选择器提取正文
        content_html = None
        for selector in content_selectors:
            element = self.soup.select_one(selector)
            if element:
                content_html = str(element)
                content_text = element.get_text(strip=True)
                break
        
        # 如果没有找到正文，尝试使用启发式方法
        if not content_html:
            # 移除无用元素
            for selector in ['script', 'style', 'nav', 'header', 'footer', 'aside']:
                for element in self.soup.find_all(selector):
                    element.decompose()
            
            # 查找最可能是正文的元素
            paragraphs = self.soup.find_all('p')
            if paragraphs:
                # 找到包含最多段落的父元素
                parent_counts = {}
                for p in paragraphs:
                    parent = p.parent
                    if parent not in parent_counts:
                        parent_counts[parent] = 0
                    parent_counts[parent] += 1
                
                # 选择包含最多段落的父元素
                max_parent = max(parent_counts.items(), key=lambda x: x[1])[0]
                content_html = str(max_parent)
                content_text = max_parent.get_text(strip=True)
            else:
                # 如果没有段落，使用body内容
                body = self.soup.find('body')
                if body:
                    content_html = str(body)
                    content_text = body.get_text(strip=True)
                else:
                    content_html = self.html
                    content_text = self.soup.get_text(strip=True)
        
        # 提取图片
        images = []
        if content_html:
            content_soup = BeautifulSoup(content_html, 'lxml')
            for i, img in enumerate(content_soup.find_all('img')):
                src = img.get('src', '')
                if not src:
                    src = img.get('data-src', '')
                    if not src:
                        continue
                
                # 处理相对URL
                if self.base_url and not src.startswith(('http://', 'https://')):
                    src = urljoin(self.base_url, src)
                
                # 图片信息
                image_info = {
                    'url': src,
                    'title': img.get('alt', ''),
                    'description': img.get('title', ''),
                    'is_cover': (i == 0),  # 第一张图片作为封面
                    'position': i
                }
                
                images.append(image_info)
        
        # 提取标签
        tags = []
        tag_elements = self.soup.select('div.post_tags a, div.tags a, div.article-tags a')
        for tag in tag_elements:
            tag_text = tag.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
        
        # 提取发布时间
        publish_time = ''
        time_elements = self.soup.select('div.post_info span.post_time, div.article-info span.time, time')
        for time_elem in time_elements:
            time_text = time_elem.get_text(strip=True)
            if time_text:
                # 尝试匹配常见的时间格式
                if re.search(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', time_text):
                    publish_time = time_text
                    break
        
        # 提取作者
        author = ''
        author_elements = self.soup.select('div.post_author, div.article-info span.author, span.byline')
        for author_elem in author_elements:
            author_text = author_elem.get_text(strip=True)
            if author_text:
                author = author_text
                break
        
        # 提取来源
        source = ''
        source_elements = self.soup.select('div.post_info a.source, div.post_info span.source, div.article-info span.source')
        for source_elem in source_elements:
            source_text = source_elem.get_text(strip=True)
            if source_text:
                source = source_text
                break
        
        # 返回结果
        return {
            'title': self.get_title(),
            'content': content_text,
            'content_html': content_html,
            'images': images,
            'tags': tags,
            'publish_time': publish_time,
            'author': author,
            'source': source,
            'description': self.get_meta_description(),
            'keywords': self.get_meta_keywords()
        }
    
    def to_html(self):
        """
        转换为HTML
        
        Returns:
            str: HTML内容
        """
        return str(self.soup)
    
    def to_text(self):
        """
        转换为文本
        
        Returns:
            str: 文本内容
        """
        return self.soup.get_text(strip=True) 