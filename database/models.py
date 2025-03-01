#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库模型模块
"""

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from config.db_config import TABLE_PREFIX

Base = declarative_base()

# 新闻-标签关联表
news_tag_association = Table(
    f'{TABLE_PREFIX}news_tag_association',
    Base.metadata,
    Column('news_id', Integer, ForeignKey(f'{TABLE_PREFIX}news.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey(f'{TABLE_PREFIX}tag.id'), primary_key=True)
)


class News(Base):
    """新闻表"""
    __tablename__ = f'{TABLE_PREFIX}news'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='新闻ID')
    title = Column(String(255), nullable=False, comment='新闻标题')
    subtitle = Column(String(255), nullable=True, comment='新闻副标题')
    source = Column(String(100), nullable=True, comment='新闻来源')
    author = Column(String(100), nullable=True, comment='作者')
    url = Column(String(255), nullable=False, unique=True, comment='新闻URL')
    category_id = Column(Integer, ForeignKey(f'{TABLE_PREFIX}category.id'), nullable=False, comment='分类ID')
    publish_time = Column(DateTime, nullable=True, comment='发布时间')
    crawl_time = Column(DateTime, default=datetime.datetime.now, comment='爬取时间')
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='更新时间')
    is_top = Column(Boolean, default=False, comment='是否置顶')
    is_hot = Column(Boolean, default=False, comment='是否热门')
    is_recommend = Column(Boolean, default=False, comment='是否推荐')
    view_count = Column(Integer, default=0, comment='浏览量')
    comment_count = Column(Integer, default=0, comment='评论数')
    like_count = Column(Integer, default=0, comment='点赞数')
    status = Column(Integer, default=1, comment='状态：0-禁用，1-启用')
    
    # 关联关系
    category = relationship('Category', back_populates='news')
    content = relationship('NewsContent', uselist=False, back_populates='news', cascade='all, delete-orphan')
    images = relationship('NewsImage', back_populates='news', cascade='all, delete-orphan')
    tags = relationship('Tag', secondary=news_tag_association, back_populates='news')
    
    def __repr__(self):
        return f'<News {self.id}: {self.title}>'


class NewsContent(Base):
    """新闻内容表"""
    __tablename__ = f'{TABLE_PREFIX}news_content'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='内容ID')
    news_id = Column(Integer, ForeignKey(f'{TABLE_PREFIX}news.id'), nullable=False, unique=True, comment='新闻ID')
    content = Column(Text, nullable=False, comment='新闻内容')
    content_html = Column(Text, nullable=False, comment='HTML格式内容')
    summary = Column(String(500), nullable=True, comment='摘要')
    keywords = Column(String(255), nullable=True, comment='关键词，逗号分隔')
    
    # 关联关系
    news = relationship('News', back_populates='content')
    
    def __repr__(self):
        return f'<NewsContent {self.id} for News {self.news_id}>'


class NewsImage(Base):
    """新闻图片表"""
    __tablename__ = f'{TABLE_PREFIX}news_image'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='图片ID')
    news_id = Column(Integer, ForeignKey(f'{TABLE_PREFIX}news.id'), nullable=False, comment='新闻ID')
    url = Column(String(255), nullable=False, comment='原始图片URL')
    local_path = Column(String(255), nullable=True, comment='本地存储路径')
    title = Column(String(255), nullable=True, comment='图片标题')
    description = Column(String(500), nullable=True, comment='图片描述')
    width = Column(Integer, nullable=True, comment='图片宽度')
    height = Column(Integer, nullable=True, comment='图片高度')
    size = Column(Integer, nullable=True, comment='图片大小(字节)')
    format = Column(String(10), nullable=True, comment='图片格式')
    is_cover = Column(Boolean, default=False, comment='是否为封面图')
    position = Column(Integer, default=0, comment='图片位置顺序')
    status = Column(Integer, default=1, comment='状态：0-禁用，1-启用')
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    
    # 关联关系
    news = relationship('News', back_populates='images')
    
    def __repr__(self):
        return f'<NewsImage {self.id} for News {self.news_id}>'


class Category(Base):
    """新闻分类表"""
    __tablename__ = f'{TABLE_PREFIX}category'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='分类ID')
    name = Column(String(50), nullable=False, comment='分类名称')
    code = Column(String(50), nullable=True, comment='分类代码')
    url = Column(String(255), nullable=True, comment='分类URL')
    parent_id = Column(Integer, ForeignKey(f'{TABLE_PREFIX}category.id'), nullable=True, comment='父分类ID')
    level = Column(Integer, default=1, comment='分类层级')
    sort = Column(Integer, default=0, comment='排序')
    description = Column(String(255), nullable=True, comment='分类描述')
    status = Column(Integer, default=1, comment='状态：0-禁用，1-启用')
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='更新时间')
    
    # 关联关系
    news = relationship('News', back_populates='category')
    children = relationship('Category', backref=ForeignKey('parent'))
    
    def __repr__(self):
        return f'<Category {self.id}: {self.name}>'


class Tag(Base):
    """标签表"""
    __tablename__ = f'{TABLE_PREFIX}tag'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='标签ID')
    name = Column(String(50), nullable=False, unique=True, comment='标签名称')
    frequency = Column(Integer, default=0, comment='使用频率')
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='更新时间')
    
    # 关联关系
    news = relationship('News', secondary=news_tag_association, back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.id}: {self.name}>'


class CrawlLog(Base):
    """爬虫日志表"""
    __tablename__ = f'{TABLE_PREFIX}crawl_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='日志ID')
    spider_name = Column(String(50), nullable=False, comment='爬虫名称')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=True, comment='结束时间')
    duration = Column(Float, nullable=True, comment='持续时间(秒)')
    status = Column(Integer, default=0, comment='状态：0-进行中，1-成功，2-失败')
    url_count = Column(Integer, default=0, comment='URL数量')
    success_count = Column(Integer, default=0, comment='成功数量')
    fail_count = Column(Integer, default=0, comment='失败数量')
    error_message = Column(Text, nullable=True, comment='错误信息')
    
    def __repr__(self):
        return f'<CrawlLog {self.id}: {self.spider_name}>'


class FailedUrl(Base):
    """失败URL表"""
    __tablename__ = f'{TABLE_PREFIX}failed_url'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    url = Column(String(255), nullable=False, comment='URL')
    spider_name = Column(String(50), nullable=False, comment='爬虫名称')
    error_message = Column(Text, nullable=True, comment='错误信息')
    retry_count = Column(Integer, default=0, comment='重试次数')
    status = Column(Integer, default=0, comment='状态：0-未处理，1-已处理')
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<FailedUrl {self.id}: {self.url}>' 