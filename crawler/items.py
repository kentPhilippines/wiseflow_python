#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫数据项定义
"""

import scrapy


class NewsItem(scrapy.Item):
    """新闻数据项"""
    # 基本信息
    title = scrapy.Field()  # 标题
    subtitle = scrapy.Field()  # 副标题
    url = scrapy.Field()  # 新闻URL
    source = scrapy.Field()  # 来源
    author = scrapy.Field()  # 作者
    publish_time = scrapy.Field()  # 发布时间
    category_id = scrapy.Field()  # 分类ID
    category_name = scrapy.Field()  # 分类名称
    
    # 内容信息
    content = scrapy.Field()  # 纯文本内容
    content_html = scrapy.Field()  # HTML内容
    summary = scrapy.Field()  # 摘要
    keywords = scrapy.Field()  # 关键词
    
    # 统计信息
    view_count = scrapy.Field()  # 浏览量
    comment_count = scrapy.Field()  # 评论数
    like_count = scrapy.Field()  # 点赞数
    
    # 标记信息
    is_top = scrapy.Field()  # 是否置顶
    is_hot = scrapy.Field()  # 是否热门
    is_recommend = scrapy.Field()  # 是否推荐
    
    # 爬虫信息
    crawl_time = scrapy.Field()  # 爬取时间
    spider_name = scrapy.Field()  # 爬虫名称
    
    # 其他信息
    tags = scrapy.Field()  # 标签列表
    images = scrapy.Field()  # 图片列表
    status = scrapy.Field()  # 状态


class ImageItem(scrapy.Item):
    """图片数据项"""
    url = scrapy.Field()  # 图片URL
    news_url = scrapy.Field()  # 所属新闻URL
    title = scrapy.Field()  # 图片标题
    description = scrapy.Field()  # 图片描述
    width = scrapy.Field()  # 宽度
    height = scrapy.Field()  # 高度
    size = scrapy.Field()  # 大小
    format = scrapy.Field()  # 格式
    is_cover = scrapy.Field()  # 是否为封面
    position = scrapy.Field()  # 位置顺序
    local_path = scrapy.Field()  # 本地存储路径
    checksum = scrapy.Field()  # 校验和
    status = scrapy.Field()  # 状态
    crawl_time = scrapy.Field()  # 爬取时间


class TagItem(scrapy.Item):
    """标签数据项"""
    name = scrapy.Field()  # 标签名称
    frequency = scrapy.Field()  # 使用频率
    news_urls = scrapy.Field()  # 关联的新闻URL列表


class CategoryItem(scrapy.Item):
    """分类数据项"""
    id = scrapy.Field()  # 分类ID
    name = scrapy.Field()  # 分类名称
    code = scrapy.Field()  # 分类代码
    url = scrapy.Field()  # 分类URL
    parent_id = scrapy.Field()  # 父分类ID
    level = scrapy.Field()  # 分类层级
    sort = scrapy.Field()  # 排序
    description = scrapy.Field()  # 分类描述
    status = scrapy.Field()  # 状态 