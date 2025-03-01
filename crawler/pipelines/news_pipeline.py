#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻数据处理管道
"""

import logging
import datetime
from sqlalchemy.exc import SQLAlchemyError

from database.db_handler import session_scope
from database.models import News, NewsContent, NewsImage, Category, Tag
from crawler.items import NewsItem, ImageItem, TagItem

logger = logging.getLogger(__name__)


class NeteaseNewsPipeline:
    """网易新闻数据处理管道"""
    
    def __init__(self):
        """初始化"""
        self.items_count = 0
        self.success_count = 0
        self.fail_count = 0
    
    def process_item(self, item, spider):
        """处理数据项"""
        if isinstance(item, NewsItem):
            return self._process_news_item(item, spider)
        elif isinstance(item, ImageItem):
            return self._process_image_item(item, spider)
        elif isinstance(item, TagItem):
            return self._process_tag_item(item, spider)
        return item
    
    def _process_news_item(self, item, spider):
        """处理新闻数据项"""
        try:
            with session_scope() as session:
                # 检查新闻是否已存在
                existing_news = session.query(News).filter(News.url == item['url']).first()
                if existing_news:
                    logger.info(f"新闻已存在，更新数据: {item['url']}")
                    # 更新新闻基本信息
                    for key, value in item.items():
                        if key not in ['content', 'content_html', 'summary', 'keywords', 'images', 'tags']:
                            setattr(existing_news, key, value)
                    
                    # 更新新闻内容
                    if existing_news.content and all(k in item for k in ['content', 'content_html', 'summary', 'keywords']):
                        existing_news.content.content = item['content']
                        existing_news.content.content_html = item['content_html']
                        existing_news.content.summary = item['summary']
                        existing_news.content.keywords = item['keywords']
                    
                    # 处理标签
                    if 'tags' in item and item['tags']:
                        self._process_news_tags(session, existing_news, item['tags'])
                    
                    news = existing_news
                else:
                    logger.info(f"新增新闻: {item['url']}")
                    # 创建新闻对象
                    news = News(
                        title=item['title'],
                        subtitle=item.get('subtitle', ''),
                        url=item['url'],
                        source=item.get('source', ''),
                        author=item.get('author', ''),
                        category_id=item.get('category_id', 1),
                        publish_time=item.get('publish_time', datetime.datetime.now()),
                        crawl_time=item.get('crawl_time', datetime.datetime.now()),
                        is_top=item.get('is_top', False),
                        is_hot=item.get('is_hot', False),
                        is_recommend=item.get('is_recommend', False),
                        view_count=item.get('view_count', 0),
                        comment_count=item.get('comment_count', 0),
                        like_count=item.get('like_count', 0),
                        status=item.get('status', 1)
                    )
                    session.add(news)
                    session.flush()  # 获取新闻ID
                    
                    # 创建新闻内容
                    if all(k in item for k in ['content', 'content_html']):
                        news_content = NewsContent(
                            news_id=news.id,
                            content=item['content'],
                            content_html=item['content_html'],
                            summary=item.get('summary', ''),
                            keywords=item.get('keywords', '')
                        )
                        session.add(news_content)
                    
                    # 处理标签
                    if 'tags' in item and item['tags']:
                        self._process_news_tags(session, news, item['tags'])
                
                # 提交事务
                session.commit()
                self.success_count += 1
                self.items_count += 1
                return item
        except SQLAlchemyError as e:
            logger.error(f"处理新闻数据失败: {str(e)}")
            self.fail_count += 1
            self.items_count += 1
            return item
    
    def _process_image_item(self, item, spider):
        """处理图片数据项"""
        try:
            with session_scope() as session:
                # 查找对应的新闻
                news = session.query(News).filter(News.url == item['news_url']).first()
                if not news:
                    logger.warning(f"图片对应的新闻不存在: {item['news_url']}")
                    return item
                
                # 检查图片是否已存在
                existing_image = session.query(NewsImage).filter(
                    NewsImage.news_id == news.id,
                    NewsImage.url == item['url']
                ).first()
                
                if existing_image:
                    logger.info(f"图片已存在，更新数据: {item['url']}")
                    # 更新图片信息
                    for key, value in item.items():
                        if key != 'news_url':
                            setattr(existing_image, key, value)
                else:
                    logger.info(f"新增图片: {item['url']}")
                    # 创建图片对象
                    news_image = NewsImage(
                        news_id=news.id,
                        url=item['url'],
                        local_path=item.get('local_path', ''),
                        title=item.get('title', ''),
                        description=item.get('description', ''),
                        width=item.get('width', 0),
                        height=item.get('height', 0),
                        size=item.get('size', 0),
                        format=item.get('format', ''),
                        is_cover=item.get('is_cover', False),
                        position=item.get('position', 0),
                        status=item.get('status', 1),
                        create_time=item.get('crawl_time', datetime.datetime.now())
                    )
                    session.add(news_image)
                
                # 提交事务
                session.commit()
                self.success_count += 1
                self.items_count += 1
                return item
        except SQLAlchemyError as e:
            logger.error(f"处理图片数据失败: {str(e)}")
            self.fail_count += 1
            self.items_count += 1
            return item
    
    def _process_tag_item(self, item, spider):
        """处理标签数据项"""
        try:
            with session_scope() as session:
                # 检查标签是否已存在
                tag_name = item['name']
                existing_tag = session.query(Tag).filter(Tag.name == tag_name).first()
                
                if existing_tag:
                    logger.info(f"标签已存在，更新频率: {tag_name}")
                    # 更新标签频率
                    existing_tag.frequency += 1
                    existing_tag.update_time = datetime.datetime.now()
                else:
                    logger.info(f"新增标签: {tag_name}")
                    # 创建标签对象
                    tag = Tag(
                        name=tag_name,
                        frequency=1,
                        create_time=datetime.datetime.now(),
                        update_time=datetime.datetime.now()
                    )
                    session.add(tag)
                
                # 提交事务
                session.commit()
                self.success_count += 1
                self.items_count += 1
                return item
        except SQLAlchemyError as e:
            logger.error(f"处理标签数据失败: {str(e)}")
            self.fail_count += 1
            self.items_count += 1
            return item
    
    def _process_news_tags(self, session, news, tag_names):
        """处理新闻标签关联"""
        # 清空现有标签关联
        news.tags = []
        
        # 添加新标签关联
        for tag_name in tag_names:
            # 查找或创建标签
            tag = session.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(
                    name=tag_name,
                    frequency=1,
                    create_time=datetime.datetime.now(),
                    update_time=datetime.datetime.now()
                )
                session.add(tag)
                session.flush()
            else:
                # 更新标签频率
                tag.frequency += 1
                tag.update_time = datetime.datetime.now()
            
            # 添加关联
            news.tags.append(tag)
    
    def open_spider(self, spider):
        """爬虫开始时的回调"""
        logger.info("新闻数据处理管道启动")
        self.start_time = datetime.datetime.now()
    
    def close_spider(self, spider):
        """爬虫结束时的回调"""
        end_time = datetime.datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        logger.info(f"新闻数据处理管道关闭，处理项目数: {self.items_count}，成功: {self.success_count}，失败: {self.fail_count}，耗时: {duration}秒") 