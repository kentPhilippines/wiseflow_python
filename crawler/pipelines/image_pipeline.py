#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片处理管道
"""

import os
import hashlib
import logging
from urllib.parse import urlparse
from datetime import datetime

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from PIL import Image

from config.settings import IMAGE_SETTINGS

logger = logging.getLogger(__name__)


class NeteaseImagePipeline(ImagesPipeline):
    """网易新闻图片处理管道"""
    
    def __init__(self, store_uri, download_func=None, settings=None):
        super(NeteaseImagePipeline, self).__init__(store_uri, download_func, settings)
        # 图片存储路径
        self.store_path = IMAGE_SETTINGS['store_path']
        # 是否调整图片大小
        self.resize_enabled = IMAGE_SETTINGS['resize_enabled']
        # 最大宽度
        self.max_width = IMAGE_SETTINGS['max_width']
        # 最大高度
        self.max_height = IMAGE_SETTINGS['max_height']
        # 图片质量
        self.quality = IMAGE_SETTINGS['quality']
        # 是否保留原始图片
        self.keep_original = IMAGE_SETTINGS['keep_original']
        # 允许的图片类型
        self.allowed_types = IMAGE_SETTINGS['allowed_types']
        # 图片大小限制
        self.size_limit = IMAGE_SETTINGS['size_limit']
    
    def get_media_requests(self, item, info):
        """获取媒体请求"""
        if not isinstance(item, dict) and hasattr(item, 'get'):
            item = dict(item)
            
        if 'url' in item and item['url']:
            # 检查URL是否有效
            url = item['url']
            if not url.startswith(('http://', 'https://')):
                return
                
            # 检查图片类型
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()
            if not any(path.endswith(f'.{ext}') for ext in self.allowed_types):
                return
                
            # 创建请求
            headers = {
                'Referer': item.get('news_url', ''),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            yield scrapy.Request(url, headers=headers, meta={'item': item})
    
    def file_path(self, request, response=None, info=None, *, item=None):
        """生成文件路径"""
        if item is None:
            item = request.meta.get('item', {})
            
        # 生成文件名
        url = request.url
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # 获取文件扩展名
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        ext = os.path.splitext(path)[1]
        if not ext or ext == '.':
            ext = '.jpg'  # 默认扩展名
        
        # 生成目录结构：年/月/日/
        now = datetime.now()
        date_path = now.strftime('%Y/%m/%d')
        
        # 最终路径
        file_path = f'{date_path}/{url_hash}{ext}'
        
        return file_path
    
    def item_completed(self, results, item, info):
        """项目完成处理"""
        if not isinstance(item, dict) and hasattr(item, 'get'):
            item = dict(item)
            
        # 收集成功下载的图片信息
        image_paths = []
        for ok, image_info in results:
            if ok:
                # 更新图片信息
                image_path = image_info['path']
                image_paths.append(image_path)
                
                # 处理图片（调整大小等）
                if self.resize_enabled:
                    self._process_image(image_path)
                
                # 更新项目信息
                item['local_path'] = image_path
                item['checksum'] = image_info.get('checksum', '')
                
                # 获取图片尺寸和大小
                try:
                    full_path = os.path.join(self.store_path, image_path)
                    if os.path.exists(full_path):
                        with Image.open(full_path) as img:
                            item['width'] = img.width
                            item['height'] = img.height
                            item['format'] = img.format.lower() if img.format else ''
                        item['size'] = os.path.getsize(full_path)
                except Exception as e:
                    logger.error(f"获取图片信息失败: {str(e)}")
        
        # 如果没有成功下载的图片，则丢弃该项
        if not image_paths and 'url' in item:
            raise DropItem(f"图片下载失败: {item['url']}")
            
        return item
    
    def _process_image(self, image_path):
        """处理图片（调整大小等）"""
        try:
            full_path = os.path.join(self.store_path, image_path)
            if not os.path.exists(full_path):
                return
                
            # 打开图片
            with Image.open(full_path) as img:
                # 检查是否需要调整大小
                width, height = img.size
                if width > self.max_width or height > self.max_height:
                    # 计算新尺寸
                    ratio = min(self.max_width / width, self.max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    
                    # 调整大小
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # 保存原始图片
                    if self.keep_original:
                        original_path = f"{os.path.splitext(full_path)[0]}_original{os.path.splitext(full_path)[1]}"
                        img.save(original_path)
                    
                    # 保存调整后的图片
                    resized_img.save(full_path, quality=self.quality)
                    logger.info(f"图片调整大小成功: {image_path}, {width}x{height} -> {new_width}x{new_height}")
        except Exception as e:
            logger.error(f"处理图片失败: {str(e)}")
    
    def open_spider(self, spider):
        """爬虫开始时的回调"""
        super(NeteaseImagePipeline, self).open_spider(spider)
        # 确保存储目录存在
        os.makedirs(self.store_path, exist_ok=True)
        logger.info(f"图片存储路径: {self.store_path}")
    
    def close_spider(self, spider):
        """爬虫结束时的回调"""
        super(NeteaseImagePipeline, self).close_spider(spider)
        logger.info("图片处理管道关闭") 