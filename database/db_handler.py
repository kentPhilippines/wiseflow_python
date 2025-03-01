#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库处理模块
"""

import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from config.db_config import (
    SQLALCHEMY_DATABASE_URI,
    POOL_SIZE,
    MAX_OVERFLOW,
    POOL_RECYCLE,
    POOL_TIMEOUT,
    ECHO_SQL
)
from database.models import Base

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """数据库处理类"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(DatabaseHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化数据库连接"""
        if self._initialized:
            return
            
        try:
            self.engine = create_engine(
                SQLALCHEMY_DATABASE_URI,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_recycle=POOL_RECYCLE,
                pool_timeout=POOL_TIMEOUT,
                echo=ECHO_SQL
            )
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            self._initialized = True
            logger.info("数据库连接初始化成功")
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {str(e)}")
            raise
    
    def create_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("数据库表创建成功")
        except SQLAlchemyError as e:
            logger.error(f"数据库表创建失败: {str(e)}")
            raise
    
    def drop_tables(self):
        """删除所有表"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("数据库表删除成功")
        except SQLAlchemyError as e:
            logger.error(f"数据库表删除失败: {str(e)}")
            raise
    
    @contextmanager
    def session_scope(self):
        """提供事务范围的会话"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库事务失败: {str(e)}")
            raise
        finally:
            session.close()
    
    def add(self, obj):
        """添加对象"""
        with self.session_scope() as session:
            session.add(obj)
            return obj
    
    def add_all(self, objs):
        """批量添加对象"""
        with self.session_scope() as session:
            session.add_all(objs)
            return objs
    
    def delete(self, obj):
        """删除对象"""
        with self.session_scope() as session:
            session.delete(obj)
    
    def query(self, model):
        """查询模型"""
        with self.session_scope() as session:
            return session.query(model)
    
    def get_by_id(self, model, id):
        """根据ID获取对象"""
        with self.session_scope() as session:
            return session.query(model).get(id)
    
    def get_by_field(self, model, field, value):
        """根据字段获取对象"""
        with self.session_scope() as session:
            return session.query(model).filter(getattr(model, field) == value).first()
    
    def get_all(self, model):
        """获取所有对象"""
        with self.session_scope() as session:
            return session.query(model).all()
    
    def execute(self, sql, params=None):
        """执行原生SQL"""
        with self.engine.connect() as conn:
            if params:
                return conn.execute(text(sql), params)
            return conn.execute(text(sql))
    
    def check_connection(self):
        """检查数据库连接"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"数据库连接检查失败: {str(e)}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("数据库连接已关闭")


# 创建数据库处理实例
db_handler = DatabaseHandler()


def init_db():
    """初始化数据库"""
    db_handler.create_tables()
    logger.info("数据库初始化完成")


def get_session():
    """获取数据库会话"""
    return db_handler.Session()


@contextmanager
def session_scope():
    """提供事务范围的会话"""
    with db_handler.session_scope() as session:
        yield session 