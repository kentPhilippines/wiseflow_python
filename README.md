# 网易新闻爬虫系统

## 项目概述
本项目是一个用于爬取网易新闻(https://news.163.com/)数据的爬虫系统。系统会抓取新闻内容、图片、标签等信息，并将数据存储到MySQL数据库中，为SEO前端站点提供数据支持。

## 技术栈
- 编程语言: Python 3.8+
- 爬虫框架: Scrapy
- 数据库: MySQL 8.4.0
- 图片处理: Pillow
- 数据解析: BeautifulSoup4, lxml
- 请求库: Requests
- 浏览器自动化: Selenium (用于处理动态加载内容)

## 项目结构
```
wiseflow_python/
├── config/                  # 配置文件目录
│   ├── db_config.py         # 数据库配置
│   └── settings.py          # 爬虫设置
├── crawler/                 # 爬虫模块
│   ├── spiders/             # 爬虫脚本
│   │   ├── news_spider.py   # 新闻爬虫
│   │   └── image_spider.py  # 图片爬虫
│   ├── middlewares/         # 中间件
│   │   ├── user_agent.py    # User-Agent中间件
│   │   └── proxy.py         # 代理中间件
│   ├── pipelines/           # 数据处理管道
│   │   ├── news_pipeline.py # 新闻数据处理
│   │   └── image_pipeline.py# 图片处理管道
│   └── items.py             # 数据项定义
├── database/                # 数据库模块
│   ├── models.py            # 数据模型
│   └── db_handler.py        # 数据库操作
├── utils/                   # 工具函数
│   ├── html_parser.py       # HTML解析工具
│   ├── text_cleaner.py      # 文本清洗工具
│   └── logger.py            # 日志工具
├── tests/                   # 测试模块
│   ├── test_spider.py       # 爬虫测试
│   └── test_db.py           # 数据库测试
├── logs/                    # 日志目录
├── data/                    # 数据存储目录
│   └── images/              # 图片存储目录
├── scripts/                 # 脚本目录
│   ├── run_crawler.py       # 运行爬虫脚本
│   └── export_data.py       # 数据导出脚本
├── requirements.txt         # 依赖包列表
├── setup.py                 # 安装脚本
└── README.md                # 项目说明
```

## 安装与配置
1. 克隆项目
```bash
git clone [项目地址]
cd wiseflow_python
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
编辑 `config/db_config.py` 文件，设置数据库连接信息。

4. 运行爬虫
```bash
python scripts/run_crawler.py
```

## 数据库设计
系统使用MySQL数据库存储爬取的新闻数据，主要包含以下表：
- news: 存储新闻基本信息
- news_content: 存储新闻内容
- news_image: 存储新闻图片
- news_tag: 存储新闻标签
- news_category: 存储新闻分类

## 爬虫功能
- 支持增量爬取，避免重复数据
- 支持多线程并发爬取
- 支持图片下载与处理
- 支持代理IP轮换
- 支持User-Agent轮换
- 支持定时任务
- 支持断点续爬
- 支持日志记录与监控

## 数据导出
系统支持将数据导出为多种格式，便于前端PHP站点使用：
- JSON格式
- XML格式
- CSV格式

## 维护与监控
- 日志系统：记录爬虫运行状态和错误信息
- 监控系统：监控爬虫运行状态和数据库状态
- 告警系统：当爬虫异常或数据库异常时发送告警

## 许可证
[许可证信息] 