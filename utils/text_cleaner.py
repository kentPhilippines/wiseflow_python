#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本清洗工具模块
"""

import re
import html
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """文本清洗器"""
    
    @staticmethod
    def clean_html(text):
        """
        清除HTML标签
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 解码HTML实体
        text = html.unescape(text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    @staticmethod
    def clean_spaces(text):
        """
        清除多余空白字符
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 替换多个空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def clean_special_chars(text):
        """
        清除特殊字符
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 替换特殊字符为空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff,.，。!?！？:：;；""''()（）\[\]【】]', ' ', text)
        
        # 替换多个空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def clean_urls(text):
        """
        清除URL
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        
        return text.strip()
    
    @staticmethod
    def clean_emails(text):
        """
        清除邮箱地址
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 移除邮箱地址
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        return text.strip()
    
    @staticmethod
    def clean_phone_numbers(text):
        """
        清除电话号码
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 移除电话号码
        text = re.sub(r'1[3-9]\d{9}', '', text)  # 移除手机号
        text = re.sub(r'\d{3,4}-\d{7,8}', '', text)  # 移除座机号
        
        return text.strip()
    
    @staticmethod
    def clean_id_numbers(text):
        """
        清除身份证号
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 移除身份证号
        text = re.sub(r'\d{17}[\dXx]', '', text)
        
        return text.strip()
    
    @staticmethod
    def clean_punctuation(text):
        """
        清除标点符号
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 移除标点符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        return text.strip()
    
    @staticmethod
    def clean_numbers(text):
        """
        清除数字
        
        Args:
            text: 待清洗文本
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 移除数字
        text = re.sub(r'\d+', '', text)
        
        return text.strip()
    
    @staticmethod
    def clean_stopwords(text, stopwords=None):
        """
        清除停用词
        
        Args:
            text: 待清洗文本
            stopwords: 停用词列表
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        if not stopwords:
            return text
            
        # 分词
        words = text.split()
        
        # 移除停用词
        words = [word for word in words if word not in stopwords]
        
        return ' '.join(words)
    
    @staticmethod
    def extract_keywords(text, top_n=10):
        """
        提取关键词
        
        Args:
            text: 待处理文本
            top_n: 提取关键词数量
            
        Returns:
            list: 关键词列表
        """
        if not text:
            return []
            
        # 分词
        words = text.split()
        
        # 统计词频
        word_freq = {}
        for word in words:
            if len(word) > 1:  # 忽略单字词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按词频排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 提取前N个关键词
        keywords = [word for word, freq in sorted_words[:top_n]]
        
        return keywords
    
    @staticmethod
    def extract_summary(text, max_length=200):
        """
        提取摘要
        
        Args:
            text: 待处理文本
            max_length: 最大长度
            
        Returns:
            str: 摘要
        """
        if not text:
            return ''
            
        # 清洗文本
        text = TextCleaner.clean_html(text)
        text = TextCleaner.clean_spaces(text)
        
        # 截取摘要
        if len(text) <= max_length:
            return text
        
        # 尝试在句子边界截断
        sentences = re.split(r'[。！？!?]', text)
        summary = ''
        for sentence in sentences:
            if len(summary) + len(sentence) + 1 <= max_length:
                summary += sentence + '。'
            else:
                break
        
        # 如果没有找到合适的句子边界，直接截断
        if not summary:
            summary = text[:max_length] + '...'
        
        return summary
    
    @staticmethod
    def clean_all(text, stopwords=None):
        """
        综合清洗
        
        Args:
            text: 待清洗文本
            stopwords: 停用词列表
            
        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ''
            
        # 解码HTML实体
        text = html.unescape(text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        
        # 移除邮箱地址
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # 移除电话号码
        text = re.sub(r'1[3-9]\d{9}', '', text)
        text = re.sub(r'\d{3,4}-\d{7,8}', '', text)
        
        # 移除身份证号
        text = re.sub(r'\d{17}[\dXx]', '', text)
        
        # 替换多个空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除停用词
        if stopwords:
            words = text.split()
            words = [word for word in words if word not in stopwords]
            text = ' '.join(words)
        
        return text.strip() 