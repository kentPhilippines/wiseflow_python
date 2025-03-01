#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据导出脚本
"""

import os
import sys
import json
import csv
import time
import logging
import argparse
import datetime
import zipfile
import gzip
import bz2
from pathlib import Path
import xml.dom.minidom as md
from xml.etree import ElementTree as ET

# 添加项目根目录到系统路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db_handler import session_scope
from database.models import News, NewsContent, NewsImage, Category, Tag
from config.settings import EXPORT_SETTINGS
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(
    name='export_data',
    level='INFO',
    log_file=os.path.join(BASE_DIR, 'logs', 'export_data.log')
)


def get_export_path(format_name):
    """
    获取导出文件路径
    
    Args:
        format_name: 导出格式名称
        
    Returns:
        str: 导出文件路径
    """
    # 创建导出目录
    export_path = EXPORT_SETTINGS['export_path']
    os.makedirs(export_path, exist_ok=True)
    
    # 生成文件名
    timestamp = ''
    if EXPORT_SETTINGS['include_timestamp']:
        timestamp = f"_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    filename = f"news_data{timestamp}.{format_name}"
    
    # 完整路径
    return os.path.join(export_path, filename)


def compress_file(file_path, compress_format='zip'):
    """
    压缩文件
    
    Args:
        file_path: 文件路径
        compress_format: 压缩格式
        
    Returns:
        str: 压缩后的文件路径
    """
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return None
    
    try:
        if compress_format == 'zip':
            # ZIP压缩
            compressed_path = f"{file_path}.zip"
            with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
        elif compress_format == 'gz':
            # GZIP压缩
            compressed_path = f"{file_path}.gz"
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
        elif compress_format == 'bz2':
            # BZ2压缩
            compressed_path = f"{file_path}.bz2"
            with open(file_path, 'rb') as f_in:
                with bz2.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
        else:
            logger.error(f"不支持的压缩格式: {compress_format}")
            return None
        
        # 删除原始文件
        os.remove(file_path)
        
        logger.info(f"文件压缩成功: {compressed_path}")
        return compressed_path
    except Exception as e:
        logger.error(f"文件压缩失败: {str(e)}")
        return None


def fetch_news_data():
    """
    获取新闻数据
    
    Returns:
        list: 新闻数据列表
    """
    news_data = []
    
    try:
        with session_scope() as session:
            # 查询所有新闻
            news_list = session.query(News).filter(News.status == 1).all()
            
            for news in news_list:
                # 基本信息
                news_item = {
                    'id': news.id,
                    'title': news.title,
                    'subtitle': news.subtitle,
                    'url': news.url,
                    'source': news.source,
                    'author': news.author,
                    'publish_time': news.publish_time.strftime('%Y-%m-%d %H:%M:%S') if news.publish_time else '',
                    'crawl_time': news.crawl_time.strftime('%Y-%m-%d %H:%M:%S') if news.crawl_time else '',
                    'is_top': news.is_top,
                    'is_hot': news.is_hot,
                    'is_recommend': news.is_recommend,
                    'view_count': news.view_count,
                    'comment_count': news.comment_count,
                    'like_count': news.like_count,
                    'category': {
                        'id': news.category.id,
                        'name': news.category.name,
                        'code': news.category.code,
                    } if news.category else {},
                }
                
                # 内容信息
                if news.content:
                    news_item['content'] = {
                        'text': news.content.content,
                        'html': news.content.content_html,
                        'summary': news.content.summary,
                        'keywords': news.content.keywords,
                    }
                else:
                    news_item['content'] = {}
                
                # 图片信息
                news_item['images'] = []
                for image in news.images:
                    image_item = {
                        'id': image.id,
                        'url': image.url,
                        'local_path': image.local_path,
                        'title': image.title,
                        'description': image.description,
                        'width': image.width,
                        'height': image.height,
                        'size': image.size,
                        'format': image.format,
                        'is_cover': image.is_cover,
                    }
                    news_item['images'].append(image_item)
                
                # 标签信息
                news_item['tags'] = [{'id': tag.id, 'name': tag.name} for tag in news.tags]
                
                news_data.append(news_item)
        
        logger.info(f"获取到 {len(news_data)} 条新闻数据")
        return news_data
    except Exception as e:
        logger.error(f"获取新闻数据失败: {str(e)}")
        return []


def export_to_json(news_data):
    """
    导出为JSON格式
    
    Args:
        news_data: 新闻数据列表
        
    Returns:
        str: 导出文件路径
    """
    try:
        # 获取导出路径
        file_path = get_export_path('json')
        
        # 写入JSON文件
        with open(file_path, 'w', encoding=EXPORT_SETTINGS['encoding']) as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"导出JSON成功: {file_path}")
        
        # 压缩文件
        if EXPORT_SETTINGS['compress']:
            file_path = compress_file(file_path, EXPORT_SETTINGS['compress_format'])
        
        return file_path
    except Exception as e:
        logger.error(f"导出JSON失败: {str(e)}")
        return None


def export_to_xml(news_data):
    """
    导出为XML格式
    
    Args:
        news_data: 新闻数据列表
        
    Returns:
        str: 导出文件路径
    """
    try:
        # 获取导出路径
        file_path = get_export_path('xml')
        
        # 创建XML根元素
        root = ET.Element('news_data')
        
        # 添加新闻元素
        for news in news_data:
            news_elem = ET.SubElement(root, 'news')
            
            # 添加基本信息
            for key, value in news.items():
                if key not in ['content', 'images', 'tags', 'category']:
                    elem = ET.SubElement(news_elem, key)
                    elem.text = str(value)
            
            # 添加分类信息
            if news.get('category'):
                category_elem = ET.SubElement(news_elem, 'category')
                for key, value in news['category'].items():
                    elem = ET.SubElement(category_elem, key)
                    elem.text = str(value)
            
            # 添加内容信息
            if news.get('content'):
                content_elem = ET.SubElement(news_elem, 'content')
                for key, value in news['content'].items():
                    elem = ET.SubElement(content_elem, key)
                    elem.text = str(value)
            
            # 添加图片信息
            images_elem = ET.SubElement(news_elem, 'images')
            for image in news.get('images', []):
                image_elem = ET.SubElement(images_elem, 'image')
                for key, value in image.items():
                    elem = ET.SubElement(image_elem, key)
                    elem.text = str(value)
            
            # 添加标签信息
            tags_elem = ET.SubElement(news_elem, 'tags')
            for tag in news.get('tags', []):
                tag_elem = ET.SubElement(tags_elem, 'tag')
                for key, value in tag.items():
                    elem = ET.SubElement(tag_elem, key)
                    elem.text = str(value)
        
        # 格式化XML
        xml_str = ET.tostring(root, encoding=EXPORT_SETTINGS['encoding'])
        dom = md.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ', encoding=EXPORT_SETTINGS['encoding'])
        
        # 写入XML文件
        with open(file_path, 'wb') as f:
            f.write(pretty_xml)
        
        logger.info(f"导出XML成功: {file_path}")
        
        # 压缩文件
        if EXPORT_SETTINGS['compress']:
            file_path = compress_file(file_path, EXPORT_SETTINGS['compress_format'])
        
        return file_path
    except Exception as e:
        logger.error(f"导出XML失败: {str(e)}")
        return None


def export_to_csv(news_data):
    """
    导出为CSV格式
    
    Args:
        news_data: 新闻数据列表
        
    Returns:
        str: 导出文件路径
    """
    try:
        # 获取导出路径
        file_path = get_export_path('csv')
        
        # 定义CSV表头
        fieldnames = [
            'id', 'title', 'subtitle', 'url', 'source', 'author', 'publish_time', 'crawl_time',
            'is_top', 'is_hot', 'is_recommend', 'view_count', 'comment_count', 'like_count',
            'category_id', 'category_name', 'content_summary', 'content_keywords', 'tags', 'cover_image'
        ]
        
        # 写入CSV文件
        with open(file_path, 'w', encoding=EXPORT_SETTINGS['encoding'], newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=EXPORT_SETTINGS['csv_delimiter'])
            
            # 写入表头
            if EXPORT_SETTINGS['include_header']:
                writer.writeheader()
            
            # 写入数据
            for news in news_data:
                # 处理标签
                tags = ','.join([tag['name'] for tag in news.get('tags', [])])
                
                # 处理封面图
                cover_image = ''
                for image in news.get('images', []):
                    if image.get('is_cover'):
                        cover_image = image.get('url', '')
                        break
                
                # 写入行
                writer.writerow({
                    'id': news.get('id', ''),
                    'title': news.get('title', ''),
                    'subtitle': news.get('subtitle', ''),
                    'url': news.get('url', ''),
                    'source': news.get('source', ''),
                    'author': news.get('author', ''),
                    'publish_time': news.get('publish_time', ''),
                    'crawl_time': news.get('crawl_time', ''),
                    'is_top': news.get('is_top', ''),
                    'is_hot': news.get('is_hot', ''),
                    'is_recommend': news.get('is_recommend', ''),
                    'view_count': news.get('view_count', ''),
                    'comment_count': news.get('comment_count', ''),
                    'like_count': news.get('like_count', ''),
                    'category_id': news.get('category', {}).get('id', ''),
                    'category_name': news.get('category', {}).get('name', ''),
                    'content_summary': news.get('content', {}).get('summary', ''),
                    'content_keywords': news.get('content', {}).get('keywords', ''),
                    'tags': tags,
                    'cover_image': cover_image
                })
        
        logger.info(f"导出CSV成功: {file_path}")
        
        # 压缩文件
        if EXPORT_SETTINGS['compress']:
            file_path = compress_file(file_path, EXPORT_SETTINGS['compress_format'])
        
        return file_path
    except Exception as e:
        logger.error(f"导出CSV失败: {str(e)}")
        return None


def export_data(formats=None):
    """
    导出数据
    
    Args:
        formats: 导出格式列表
        
    Returns:
        dict: 导出结果
    """
    # 获取导出格式
    if not formats:
        formats = EXPORT_SETTINGS['formats']
    
    # 获取新闻数据
    news_data = fetch_news_data()
    if not news_data:
        logger.error("没有可导出的数据")
        return {'success': False, 'message': '没有可导出的数据'}
    
    # 导出结果
    result = {
        'success': True,
        'message': '导出成功',
        'files': {}
    }
    
    # 导出数据
    for format_name in formats:
        if format_name == 'json':
            file_path = export_to_json(news_data)
            if file_path:
                result['files']['json'] = file_path
        elif format_name == 'xml':
            file_path = export_to_xml(news_data)
            if file_path:
                result['files']['xml'] = file_path
        elif format_name == 'csv':
            file_path = export_to_csv(news_data)
            if file_path:
                result['files']['csv'] = file_path
        else:
            logger.warning(f"不支持的导出格式: {format_name}")
    
    # 检查是否有成功导出的文件
    if not result['files']:
        result['success'] = False
        result['message'] = '导出失败'
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='导出网易新闻数据')
    parser.add_argument('--format', choices=['json', 'xml', 'csv', 'all'], default='all', help='导出格式')
    args = parser.parse_args()
    
    # 创建导出目录
    os.makedirs(EXPORT_SETTINGS['export_path'], exist_ok=True)
    
    # 确定导出格式
    if args.format == 'all':
        formats = EXPORT_SETTINGS['formats']
    else:
        formats = [args.format]
    
    # 导出数据
    start_time = time.time()
    result = export_data(formats)
    end_time = time.time()
    
    # 输出结果
    if result['success']:
        logger.info(f"数据导出成功，耗时: {end_time - start_time:.2f}秒")
        for format_name, file_path in result['files'].items():
            logger.info(f"- {format_name}: {file_path}")
    else:
        logger.error(f"数据导出失败: {result['message']}")


if __name__ == '__main__':
    main() 