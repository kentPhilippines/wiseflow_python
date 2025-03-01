# 网易新闻爬虫系统架构文档

## 1. 项目概述

本项目是一个用于爬取网易新闻(https://news.163.com/)数据的爬虫系统。系统会抓取新闻内容、图片、标签等信息，并将数据存储到MySQL数据库中，为SEO前端站点提供数据支持。

### 1.1 项目目标

- 爬取网易新闻网站的新闻数据，包括标题、内容、图片、标签等
- 对爬取的数据进行清洗和处理
- 将数据存储到MySQL数据库中
- 提供数据导出功能，支持多种格式
- 支持定时任务，定期更新数据
- 支持断点续爬，避免重复爬取
- 支持多线程并发爬取，提高效率
- 支持代理IP轮换，避免被封IP
- 支持User-Agent轮换，模拟不同浏览器

### 1.2 技术栈

- 编程语言: Python 3.8+
- 爬虫框架: Scrapy
- 数据库: MySQL 8.4.0
- 图片处理: Pillow
- 数据解析: BeautifulSoup4, lxml
- 请求库: Requests
- 浏览器自动化: Selenium (用于处理动态加载内容)
- 定时任务: Schedule
- ORM框架: SQLAlchemy
- 日志: Logging

## 2. 系统架构

### 2.1 整体架构

系统采用分层架构设计，主要分为以下几层：

1. **爬虫层**：负责爬取网页数据，包括爬虫脚本、中间件等
2. **数据处理层**：负责对爬取的数据进行清洗、处理和存储
3. **数据存储层**：负责将处理后的数据存储到数据库中
4. **数据导出层**：负责将数据导出为多种格式，供前端使用
5. **调度层**：负责调度爬虫任务，支持定时任务和手动触发
6. **工具层**：提供各种工具函数，如日志、HTML解析、文本清洗等

### 2.2 模块划分

系统主要包含以下模块：

1. **配置模块**：管理系统配置，包括数据库配置、爬虫设置等
2. **爬虫模块**：实现爬虫功能，包括爬虫脚本、中间件、管道等
3. **数据库模块**：实现数据库操作，包括模型定义、数据库连接等
4. **工具模块**：提供各种工具函数，如日志、HTML解析、文本清洗等
5. **脚本模块**：提供各种脚本，如运行爬虫、导出数据等

### 2.3 数据流

系统的数据流如下：

1. 爬虫从网易新闻网站爬取数据
2. 数据经过中间件处理（如User-Agent轮换、代理IP轮换等）
3. 数据经过管道处理（如数据清洗、图片下载等）
4. 处理后的数据存储到MySQL数据库中
5. 数据可以通过导出脚本导出为多种格式，供前端使用

## 3. 数据库设计

### 3.1 数据库表设计

系统使用MySQL数据库存储爬取的新闻数据，主要包含以下表：

#### 3.1.1 新闻表 (wf_news)

存储新闻基本信息

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| title | VARCHAR(255) | 新闻标题 |
| subtitle | VARCHAR(255) | 新闻副标题 |
| source | VARCHAR(100) | 新闻来源 |
| author | VARCHAR(100) | 作者 |
| url | VARCHAR(255) | 新闻URL |
| category_id | INT | 分类ID，外键 |
| publish_time | DATETIME | 发布时间 |
| crawl_time | DATETIME | 爬取时间 |
| update_time | DATETIME | 更新时间 |
| is_top | BOOLEAN | 是否置顶 |
| is_hot | BOOLEAN | 是否热门 |
| is_recommend | BOOLEAN | 是否推荐 |
| view_count | INT | 浏览量 |
| comment_count | INT | 评论数 |
| like_count | INT | 点赞数 |
| status | INT | 状态：0-禁用，1-启用 |

#### 3.1.2 新闻内容表 (wf_news_content)

存储新闻内容

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| news_id | INT | 新闻ID，外键 |
| content | TEXT | 新闻内容 |
| content_html | TEXT | HTML格式内容 |
| summary | VARCHAR(500) | 摘要 |
| keywords | VARCHAR(255) | 关键词，逗号分隔 |

#### 3.1.3 新闻图片表 (wf_news_image)

存储新闻图片

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| news_id | INT | 新闻ID，外键 |
| url | VARCHAR(255) | 原始图片URL |
| local_path | VARCHAR(255) | 本地存储路径 |
| title | VARCHAR(255) | 图片标题 |
| description | VARCHAR(500) | 图片描述 |
| width | INT | 图片宽度 |
| height | INT | 图片高度 |
| size | INT | 图片大小(字节) |
| format | VARCHAR(10) | 图片格式 |
| is_cover | BOOLEAN | 是否为封面图 |
| position | INT | 图片位置顺序 |
| status | INT | 状态：0-禁用，1-启用 |
| create_time | DATETIME | 创建时间 |

#### 3.1.4 分类表 (wf_category)

存储新闻分类

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| name | VARCHAR(50) | 分类名称 |
| code | VARCHAR(50) | 分类代码 |
| url | VARCHAR(255) | 分类URL |
| parent_id | INT | 父分类ID |
| level | INT | 分类层级 |
| sort | INT | 排序 |
| description | VARCHAR(255) | 分类描述 |
| status | INT | 状态：0-禁用，1-启用 |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

#### 3.1.5 标签表 (wf_tag)

存储新闻标签

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| name | VARCHAR(50) | 标签名称 |
| frequency | INT | 使用频率 |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

#### 3.1.6 新闻-标签关联表 (wf_news_tag_association)

存储新闻和标签的多对多关系

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| news_id | INT | 新闻ID，外键 |
| tag_id | INT | 标签ID，外键 |

#### 3.1.7 爬虫日志表 (wf_crawl_log)

存储爬虫运行日志

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| spider_name | VARCHAR(50) | 爬虫名称 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| duration | FLOAT | 持续时间(秒) |
| status | INT | 状态：0-进行中，1-成功，2-失败 |
| url_count | INT | URL数量 |
| success_count | INT | 成功数量 |
| fail_count | INT | 失败数量 |
| error_message | TEXT | 错误信息 |

#### 3.1.8 失败URL表 (wf_failed_url)

存储爬取失败的URL

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | INT | 主键，自增 |
| url | VARCHAR(255) | URL |
| spider_name | VARCHAR(50) | 爬虫名称 |
| error_message | TEXT | 错误信息 |
| retry_count | INT | 重试次数 |
| status | INT | 状态：0-未处理，1-已处理 |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

### 3.2 数据库关系图

```
+---------------+       +-------------------+       +----------------+
|   wf_news     |       |  wf_news_content  |       |  wf_news_image |
+---------------+       +-------------------+       +----------------+
| id            |<----->| news_id           |       | news_id        |
| title         |       | content           |       | url            |
| ...           |       | ...               |       | ...            |
+---------------+       +-------------------+       +----------------+
       ^                                                    ^
       |                                                    |
       |                                                    |
       v                                                    v
+---------------+       +------------------------+       +----------------+
|  wf_category  |       | wf_news_tag_association|       |    wf_tag     |
+---------------+       +------------------------+       +----------------+
| id            |       | news_id                |<----->| id             |
| name          |       | tag_id                 |       | name           |
| ...           |       |                        |       | ...            |
+---------------+       +------------------------+       +----------------+
```

## 4. 爬虫设计

### 4.1 爬虫流程

1. 从网易新闻首页和各个分类页面开始爬取
2. 提取新闻链接，并过滤掉不需要的链接（如图片新闻、专题等）
3. 对每个新闻链接发起请求，获取新闻页面内容
4. 解析新闻页面，提取标题、内容、图片、标签等信息
5. 将提取的数据经过清洗和处理后，存储到数据库中
6. 对于新闻中的图片，下载并保存到本地，同时记录图片信息

### 4.2 爬虫组件

#### 4.2.1 爬虫脚本

- `NeteaseNewsSpider`：网易新闻爬虫，负责爬取新闻数据

#### 4.2.2 中间件

- `RandomUserAgentMiddleware`：随机User-Agent中间件，负责随机切换User-Agent
- `RandomProxyMiddleware`：随机代理中间件，负责随机切换代理IP

#### 4.2.3 管道

- `NeteaseNewsPipeline`：新闻数据处理管道，负责处理和存储新闻数据
- `NeteaseImagePipeline`：图片处理管道，负责下载和处理图片

### 4.3 数据项

- `NewsItem`：新闻数据项，包含新闻的各种信息
- `ImageItem`：图片数据项，包含图片的各种信息
- `TagItem`：标签数据项，包含标签的各种信息
- `CategoryItem`：分类数据项，包含分类的各种信息

## 5. 工具设计

### 5.1 日志工具

- `setup_logger`：设置日志记录器
- `setup_daily_logger`：设置按天轮转的日志记录器
- `get_logger`：获取日志记录器

### 5.2 HTML解析工具

- `HtmlParser`：HTML解析器，提供各种HTML解析方法
  - `get_title`：获取标题
  - `get_meta_description`：获取meta描述
  - `get_meta_keywords`：获取meta关键词
  - `get_text`：获取文本内容
  - `get_links`：获取链接
  - `get_images`：获取图片
  - `extract_content`：提取正文内容
  - ...

### 5.3 文本清洗工具

- `TextCleaner`：文本清洗器，提供各种文本清洗方法
  - `clean_html`：清除HTML标签
  - `clean_spaces`：清除多余空白字符
  - `clean_special_chars`：清除特殊字符
  - `clean_urls`：清除URL
  - `extract_keywords`：提取关键词
  - `extract_summary`：提取摘要
  - ...

## 6. 脚本设计

### 6.1 运行爬虫脚本

- `run_crawler.py`：运行爬虫脚本，支持一次性运行和定时任务
  - `run_spider`：运行爬虫
  - `run_scheduled_task`：运行定时任务
  - `schedule_task`：调度定时任务
  - ...

### 6.2 数据导出脚本

- `export_data.py`：数据导出脚本，支持导出为多种格式
  - `export_to_json`：导出为JSON格式
  - `export_to_xml`：导出为XML格式
  - `export_to_csv`：导出为CSV格式
  - ...

## 7. 配置设计

### 7.1 数据库配置

- `db_config.py`：数据库配置文件，包含数据库连接信息
  - `DB_CONFIG`：数据库配置
  - `SQLALCHEMY_DATABASE_URI`：SQLAlchemy连接字符串
  - `POOL_SIZE`：连接池大小
  - ...

### 7.2 爬虫设置

- `settings.py`：爬虫设置文件，包含爬虫的各种配置参数
  - `CRAWLER_SETTINGS`：爬虫设置
  - `IMAGE_SETTINGS`：图片设置
  - `PROXY_SETTINGS`：代理设置
  - `USER_AGENT_SETTINGS`：User-Agent设置
  - `SELENIUM_SETTINGS`：Selenium设置
  - `SCHEDULE_SETTINGS`：定时任务设置
  - `EXPORT_SETTINGS`：导出设置
  - `NEWS_CATEGORIES`：新闻分类
  - ...

## 8. 部署方案

### 8.1 环境要求

- Python 3.8+
- MySQL 8.4.0
- Chrome浏览器（用于Selenium）
- ChromeDriver（用于Selenium）

### 8.2 安装步骤

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

4. 初始化数据库
```bash
python -c "from database.db_handler import init_db; init_db()"
```

5. 运行爬虫
```bash
python scripts/run_crawler.py
```

### 8.3 定时任务

可以使用crontab设置定时任务，定期运行爬虫：

```bash
# 每天凌晨2点运行爬虫
0 2 * * * cd /path/to/wiseflow_python && python scripts/run_crawler.py --once
```

或者使用内置的定时任务功能：

```bash
python scripts/run_crawler.py --schedule
```

### 8.4 数据导出

可以使用导出脚本导出数据：

```bash
python scripts/export_data.py --format json
```

## 9. 扩展性设计

### 9.1 添加新的爬虫

1. 在 `crawler/spiders/` 目录下创建新的爬虫脚本
2. 在 `scripts/run_crawler.py` 中添加新的爬虫
3. 根据需要修改数据库模型和数据项

### 9.2 添加新的数据源

1. 在 `config/settings.py` 中添加新的数据源配置
2. 创建新的爬虫脚本
3. 根据需要修改数据库模型和数据项

### 9.3 添加新的导出格式

1. 在 `scripts/export_data.py` 中添加新的导出函数
2. 在 `export_data` 函数中添加新的导出格式处理

## 10. 安全性设计

### 10.1 数据库安全

- 使用参数化查询，防止SQL注入
- 使用连接池，避免连接泄漏
- 定期备份数据库

### 10.2 爬虫安全

- 使用User-Agent轮换，避免被识别为爬虫
- 使用代理IP轮换，避免被封IP
- 设置下载延迟，避免请求过于频繁
- 遵循robots.txt规则

### 10.3 数据安全

- 对敏感数据进行加密存储
- 定期清理过期数据
- 控制数据访问权限

## 11. 监控与维护

### 11.1 日志监控

- 使用日志记录爬虫运行状态
- 定期检查日志，发现异常情况
- 设置日志轮转，避免日志文件过大

### 11.2 性能监控

- 监控数据库性能
- 监控爬虫性能
- 监控服务器资源使用情况

### 11.3 异常处理

- 捕获并记录异常
- 自动重试失败的请求
- 发送告警通知

## 12. 前端对接

### 12.1 数据接口

前端PHP站点可以通过以下方式获取数据：

1. 直接访问MySQL数据库
2. 使用导出的JSON/XML/CSV文件
3. 开发API接口，提供数据访问服务

### 12.2 数据格式

导出的数据格式如下：

#### JSON格式

```json
[
  {
    "id": 1,
    "title": "新闻标题",
    "subtitle": "新闻副标题",
    "url": "新闻URL",
    "source": "新闻来源",
    "author": "作者",
    "publish_time": "2023-01-01 12:00:00",
    "category": {
      "id": 1,
      "name": "头条"
    },
    "content": {
      "text": "新闻内容",
      "html": "<p>新闻内容</p>",
      "summary": "摘要",
      "keywords": "关键词"
    },
    "images": [
      {
        "id": 1,
        "url": "图片URL",
        "local_path": "本地路径",
        "is_cover": true
      }
    ],
    "tags": [
      {
        "id": 1,
        "name": "标签名称"
      }
    ]
  }
]
```

#### XML格式

```xml
<news_data>
  <news>
    <id>1</id>
    <title>新闻标题</title>
    <subtitle>新闻副标题</subtitle>
    <url>新闻URL</url>
    <source>新闻来源</source>
    <author>作者</author>
    <publish_time>2023-01-01 12:00:00</publish_time>
    <category>
      <id>1</id>
      <name>头条</name>
    </category>
    <content>
      <text>新闻内容</text>
      <html><![CDATA[<p>新闻内容</p>]]></html>
      <summary>摘要</summary>
      <keywords>关键词</keywords>
    </content>
    <images>
      <image>
        <id>1</id>
        <url>图片URL</url>
        <local_path>本地路径</local_path>
        <is_cover>true</is_cover>
      </image>
    </images>
    <tags>
      <tag>
        <id>1</id>
        <name>标签名称</name>
      </tag>
    </tags>
  </news>
</news_data>
```

#### CSV格式

```
id,title,subtitle,url,source,author,publish_time,category_id,category_name,content_summary,content_keywords,tags,cover_image
1,新闻标题,新闻副标题,新闻URL,新闻来源,作者,2023-01-01 12:00:00,1,头条,摘要,关键词,标签1|标签2,图片URL
```

### 12.3 多模板多域名支持

前端PHP站点可以根据不同的模板和域名，从数据库中获取不同的数据：

1. 根据分类获取不同的新闻数据
2. 根据标签获取不同的新闻数据
3. 根据时间获取不同的新闻数据
4. 根据热度获取不同的新闻数据

## 13. 总结

本项目是一个完整的网易新闻爬虫系统，包含爬虫、数据处理、数据存储、数据导出等功能。系统采用分层架构设计，各模块职责明确，易于扩展和维护。系统支持多线程并发爬取、代理IP轮换、User-Agent轮换、定时任务等功能，能够高效地爬取网易新闻数据，为SEO前端站点提供数据支持。 