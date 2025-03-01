#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新闻API服务
提供新闻数据接口，供其他服务调用
"""

import os
import sys
import json
import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import desc, func, text

# 添加项目根目录到系统路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db_handler import DBHandler
from database.models import News, Content, Category, Tag
from config.db_config import TABLE_PREFIX

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 创建数据库处理器
db_handler = DBHandler()

# 自定义JSON编码器，处理日期时间格式
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

@app.route('/api/news', methods=['GET'])
def get_news_list():
    """获取新闻列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        category_id = request.args.get('category_id')
        keyword = request.args.get('keyword')
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        with db_handler.session_scope() as session:
            # 构建查询
            query = session.query(News)
            
            # 应用过滤条件
            if category_id:
                query = query.filter(News.category_id == category_id)
            
            if keyword:
                query = query.filter(News.title.like(f'%{keyword}%'))
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据
            news_list = query.order_by(desc(News.publish_time)).offset(offset).limit(page_size).all()
            
            # 转换为字典列表
            result = []
            for news in news_list:
                news_dict = {
                    'id': news.id,
                    'title': news.title,
                    'subtitle': news.subtitle,
                    'source': news.source,
                    'author': news.author,
                    'url': news.url,
                    'category_id': news.category_id,
                    'publish_time': news.publish_time,
                    'crawl_time': news.crawl_time,
                    'update_time': news.update_time,
                    'is_top': news.is_top,
                    'is_hot': news.is_hot,
                    'is_recommend': news.is_recommend,
                    'view_count': news.view_count,
                    'comment_count': news.comment_count,
                    'like_count': news.like_count,
                    'status': news.status
                }
                result.append(news_dict)
            
            # 返回结果
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'list': result
                }
            })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取新闻列表失败: {str(e)}',
            'data': None
        })

@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    """获取新闻详情"""
    try:
        with db_handler.session_scope() as session:
            # 查询新闻
            news = session.query(News).filter(News.id == news_id).first()
            
            if not news:
                return jsonify({
                    'code': 404,
                    'message': f'新闻不存在: {news_id}',
                    'data': None
                })
            
            # 查询内容
            content = session.query(Content).filter(Content.news_id == news_id).first()
            
            # 查询分类
            category = session.query(Category).filter(Category.id == news.category_id).first()
            
            # 转换为字典
            news_dict = {
                'id': news.id,
                'title': news.title,
                'subtitle': news.subtitle,
                'source': news.source,
                'author': news.author,
                'url': news.url,
                'category_id': news.category_id,
                'category_name': category.name if category else '',
                'publish_time': news.publish_time,
                'crawl_time': news.crawl_time,
                'update_time': news.update_time,
                'is_top': news.is_top,
                'is_hot': news.is_hot,
                'is_recommend': news.is_recommend,
                'view_count': news.view_count,
                'comment_count': news.comment_count,
                'like_count': news.like_count,
                'status': news.status
            }
            
            if content:
                news_dict['content'] = content.content
                news_dict['html_content'] = content.html_content
                news_dict['image_urls'] = json.loads(content.image_urls) if content.image_urls else []
            
            # 返回结果
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': news_dict
            })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取新闻详情失败: {str(e)}',
            'data': None
        })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        with db_handler.session_scope() as session:
            # 查询分类
            categories = session.query(Category).all()
            
            # 转换为字典列表
            result = []
            for category in categories:
                category_dict = {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'create_time': category.create_time,
                    'update_time': category.update_time
                }
                result.append(category_dict)
            
            # 返回结果
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': result
            })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分类列表失败: {str(e)}',
            'data': None
        })

@app.route('/api/news/search', methods=['GET'])
def search_news():
    """搜索新闻"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        with db_handler.session_scope() as session:
            # 构建查询
            query = session.query(News).filter(
                News.title.like(f'%{keyword}%') | 
                News.subtitle.like(f'%{keyword}%')
            )
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据
            news_list = query.order_by(desc(News.publish_time)).offset(offset).limit(page_size).all()
            
            # 转换为字典列表
            result = []
            for news in news_list:
                news_dict = {
                    'id': news.id,
                    'title': news.title,
                    'subtitle': news.subtitle,
                    'source': news.source,
                    'author': news.author,
                    'url': news.url,
                    'category_id': news.category_id,
                    'publish_time': news.publish_time,
                    'crawl_time': news.crawl_time,
                    'update_time': news.update_time,
                    'is_top': news.is_top,
                    'is_hot': news.is_hot,
                    'is_recommend': news.is_recommend,
                    'view_count': news.view_count,
                    'comment_count': news.comment_count,
                    'like_count': news.like_count,
                    'status': news.status
                }
                result.append(news_dict)
            
            # 返回结果
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'list': result
                }
            })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'搜索新闻失败: {str(e)}',
            'data': None
        })

@app.route('/api/news/stats', methods=['GET'])
def get_news_stats():
    """获取新闻统计信息"""
    try:
        with db_handler.session_scope() as session:
            # 查询总数
            total_count = session.query(func.count(News.id)).scalar()
            
            # 查询各分类数量
            category_stats = session.execute(text(f'''
                SELECT c.id, c.name, COUNT(n.id) as count
                FROM {TABLE_PREFIX}news n
                JOIN {TABLE_PREFIX}category c ON n.category_id = c.id
                GROUP BY n.category_id, c.id, c.name
            ''')).fetchall()
            
            # 查询今日新增
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = session.query(func.count(News.id)).filter(News.crawl_time >= today).scalar()
            
            # 查询热门新闻
            hot_news = session.query(News).filter(News.is_hot == True).count()
            
            # 返回结果
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'total_count': total_count,
                    'today_count': today_count,
                    'hot_count': hot_news,
                    'category_stats': [
                        {
                            'id': row[0],
                            'name': row[1],
                            'count': row[2]
                        } for row in category_stats
                    ]
                }
            })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取新闻统计信息失败: {str(e)}',
            'data': None
        })

def main():
    """主函数"""
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='新闻API服务')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听主机，默认为0.0.0.0')
    parser.add_argument('--port', type=int, default=5000, help='监听端口，默认为5000')
    parser.add_argument('--debug', action='store_true', help='是否启用调试模式')
    args = parser.parse_args()
    
    # 启动服务
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main() 