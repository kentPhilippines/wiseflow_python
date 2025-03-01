# 网易新闻爬虫系统部署文档

本文档详细说明了如何在服务器上部署网易新闻爬虫系统。

## 1. 系统要求

### 1.1 硬件要求
- CPU: 2核心以上
- 内存: 4GB以上
- 硬盘: 50GB以上（取决于爬取数据量）
- 带宽: 5Mbps以上

### 1.2 软件要求
- 操作系统: CentOS 7+/Ubuntu 18.04+/Debian 10+
- Python: 3.8+
- MySQL: 8.0+
- Git: 2.0+

## 2. 部署方式

### 2.1 一键部署（推荐）

一键部署脚本会自动完成环境配置、依赖安装、数据库初始化等操作，是最简单的部署方式。

#### 步骤：

1. 安装基础软件
```bash
# CentOS
sudo yum update -y
sudo yum install -y git python3 python3-devel python3-pip mysql-devel gcc bc

# Ubuntu/Debian
sudo apt update
sudo apt install -y git python3 python3-dev python3-pip python3-venv libmysqlclient-dev build-essential bc
```

2. 克隆代码仓库
```bash
git clone https://github.com/yourusername/wiseflow_python.git
cd wiseflow_python
```

3. 运行部署脚本
```bash
bash scripts/deploy.sh
```

4. 按照提示完成配置
   - 数据库配置：输入数据库主机、端口、用户名、密码和数据库名
   - 定时任务配置：选择是否设置定时任务及运行时间
   - 测试运行：选择是否立即测试运行爬虫

### 2.2 手动部署

如果您需要更精细地控制部署过程，可以选择手动部署。

#### 步骤：

1. 安装基础软件（同上）

2. 克隆代码仓库
```bash
git clone https://github.com/yourusername/wiseflow_python.git
cd wiseflow_python
```

3. 创建并激活虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 创建必要目录
```bash
mkdir -p logs
mkdir -p data/images
mkdir -p data/exports
```

6. 配置数据库
   - 编辑 `config/db_config.py` 文件，设置数据库连接信息
   - 或者创建 `.env` 文件，设置环境变量

7. 初始化数据库
```bash
python -c "from database.db_handler import init_db; init_db()"
```

8. 设置定时任务（可选）
```bash
crontab -e
```
添加以下内容：
```
0 2 * * * cd /path/to/wiseflow_python && /path/to/wiseflow_python/venv/bin/python /path/to/wiseflow_python/scripts/run_crawler.py --once >> /path/to/wiseflow_python/logs/cron.log 2>&1
```

9. 创建启动脚本
```bash
cat > start.sh << EOF
#!/bin/bash
cd $(pwd)
source venv/bin/activate
python scripts/run_crawler.py \$@
EOF
chmod +x start.sh
```

## 3. 运行爬虫

### 3.1 运行模式

爬虫系统支持以下运行模式：

1. 单次运行模式
```bash
./start.sh --once
```

2. 定时任务模式
```bash
./start.sh --schedule
```

### 3.2 导出数据

可以使用以下命令导出爬取的数据：

```bash
# 激活虚拟环境
source venv/bin/activate

# 导出所有格式
python scripts/export_data.py

# 导出特定格式
python scripts/export_data.py --json
python scripts/export_data.py --xml
python scripts/export_data.py --csv
```

## 4. 系统维护

### 4.1 日志查看

爬虫运行日志存储在 `logs` 目录下：
```bash
# 查看爬虫日志
cat logs/spider.log

# 查看定时任务日志
cat logs/cron.log
```

### 4.2 数据备份

建议定期备份MySQL数据库：
```bash
# 备份数据库
mysqldump -h <host> -u <user> -p<password> wiseflow_python > backup_$(date +%Y%m%d).sql
```

### 4.3 系统更新

当代码仓库有更新时，可以按以下步骤更新系统：

```bash
# 进入项目目录
cd /path/to/wiseflow_python

# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重新初始化数据库（如有必要）
python -c "from database.db_handler import init_db; init_db()"
```

## 5. 故障排除

### 5.1 常见问题

1. **数据库连接失败**
   - 检查数据库配置是否正确
   - 确认MySQL服务是否运行
   - 检查防火墙设置是否允许数据库连接

2. **爬虫运行失败**
   - 检查日志文件了解具体错误
   - 确认网络连接是否正常
   - 检查目标网站是否可访问

3. **定时任务未执行**
   - 检查crontab配置是否正确
   - 确认cron服务是否运行
   - 检查日志文件了解具体错误

### 5.2 联系支持

如遇到无法解决的问题，请联系作者
 
## 6. 附录

### 6.1 环境变量说明

可以通过创建 `.env` 文件设置以下环境变量：

```
DB_HOST=数据库主机
DB_PORT=数据库端口
DB_USER=数据库用户名
DB_PASSWORD=数据库密码
DB_NAME=数据库名称
```

### 6.2 配置文件说明

主要配置文件及其作用：

- `config/db_config.py`: 数据库配置
- `config/settings.py`: 爬虫设置，包括并发数、延迟、代理等

### 6.3 命令参考

```bash
# 运行爬虫（单次）
./start.sh --once

# 运行爬虫（定时）
./start.sh --schedule

# 导出数据
python scripts/export_data.py [--json] [--xml] [--csv]

# 初始化数据库
python -c "from database.db_handler import init_db; init_db()"
``` 