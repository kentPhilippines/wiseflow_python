#!/bin/bash

# 网易新闻爬虫系统一键部署脚本
# 作者: wiseflow_python
# 日期: $(date +%Y-%m-%d)

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
    elif [ -f /etc/debian_version ]; then
        OS="Debian"
    elif [ -f /etc/redhat-release ]; then
        OS="CentOS"
    else
        OS=$(uname -s)
    fi
    
    echo $OS
}

# 安装基础依赖
install_base_dependencies() {
    OS=$(detect_os)
    log_info "检测到系统: $OS"
    
    # 检查是否有root权限
    if [ "$(id -u)" != "0" ]; then
        log_warn "当前不是root用户，可能无法安装某些依赖"
        read -p "是否继续? (y/n): " continue_install
        if [[ $continue_install != "y" && $continue_install != "Y" ]]; then
            log_info "安装已取消"
            exit 0
        fi
    fi
    
    if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
        log_info "使用apt安装基础依赖..."
        apt update -y
        apt install -y python3 python3-dev python3-pip python3-venv libmysqlclient-dev build-essential bc
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]] || [[ $OS == *"Fedora"* ]]; then
        log_info "使用yum安装基础依赖..."
        yum update -y
        yum install -y python3 python3-devel python3-pip mysql-devel gcc bc
    else
        log_warn "未识别的操作系统: $OS，请手动安装依赖"
    fi
}

# 检查并安装命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_warn "$1 命令未找到，尝试安装..."
        
        OS=$(detect_os)
        if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
            apt install -y $2
        elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]] || [[ $OS == *"Fedora"* ]]; then
            yum install -y $2
        else
            log_error "$1 命令未找到，请手动安装"
            exit 1
        fi
        
        if ! command -v $1 &> /dev/null; then
            log_error "$1 安装失败"
            exit 1
        fi
        
        log_info "$1 安装成功"
    fi
}

# 检查Python版本
check_python_version() {
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$python_version < 3.8" | bc) -eq 1 ]]; then
        log_error "Python版本需要 >= 3.8，当前版本: $python_version"
        exit 1
    fi
    log_info "Python版本检查通过: $python_version"
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    if [ -d "venv" ]; then
        log_warn "虚拟环境已存在，跳过创建"
    else
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            log_error "创建虚拟环境失败"
            exit 1
        fi
        log_info "虚拟环境创建成功"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        log_error "激活虚拟环境失败"
        exit 1
    fi
    log_info "虚拟环境激活成功"
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        log_error "安装依赖失败"
        exit 1
    fi
    log_info "依赖安装成功"
}

# 配置数据库
configure_database() {
    log_info "配置数据库连接..."
    
    # 检查数据库配置文件是否存在
    if [ ! -f "config/db_config.py" ]; then
        log_error "数据库配置文件不存在: config/db_config.py"
        exit 1
    fi
    
    # 询问是否需要修改数据库配置
    read -p "是否需要修改数据库配置? (y/n): " modify_db
    if [[ $modify_db == "y" || $modify_db == "Y" ]]; then
        read -p "数据库主机 (默认: 103.112.99.20): " db_host
        read -p "数据库端口 (默认: 3306): " db_port
        read -p "数据库用户名 (默认: wiseflow_python): " db_user
        read -s -p "数据库密码 (默认: aY7YjpJY4JxEYAG2): " db_password
        echo
        read -p "数据库名称 (默认: wiseflow_python): " db_name
        
        # 设置默认值
        db_host=${db_host:-"103.112.99.20"}
        db_port=${db_port:-"3306"}
        db_user=${db_user:-"wiseflow_python"}
        db_password=${db_password:-"aY7YjpJY4JxEYAG2"}
        db_name=${db_name:-"wiseflow_python"}
        
        # 创建.env文件
        cat > .env << EOF
DB_HOST=$db_host
DB_PORT=$db_port
DB_USER=$db_user
DB_PASSWORD=$db_password
DB_NAME=$db_name
EOF
        log_info "数据库配置已更新"
    else
        log_info "使用默认数据库配置"
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    python -c "from database.db_handler import init_db; init_db()"
    if [ $? -ne 0 ]; then
        log_error "数据库初始化失败"
        exit 1
    fi
    log_info "数据库初始化成功"
}

# 创建目录
create_directories() {
    log_info "创建必要目录..."
    mkdir -p logs
    mkdir -p data/images
    mkdir -p data/exports
    log_info "目录创建成功"
}

# 设置定时任务
setup_cron() {
    log_info "设置定时任务..."
    
    # 询问是否需要设置定时任务
    read -p "是否需要设置定时任务? (y/n): " setup_cron
    if [[ $setup_cron == "y" || $setup_cron == "Y" ]]; then
        read -p "定时任务执行时间 (crontab格式，默认: 0 2 * * * 每天凌晨2点): " cron_time
        cron_time=${cron_time:-"0 2 * * *"}
        
        # 获取当前目录的绝对路径
        current_dir=$(pwd)
        
        # 创建临时crontab文件
        crontab -l > crontab_temp 2>/dev/null || true
        
        # 检查是否已存在相同的定时任务
        if grep -q "$current_dir/scripts/run_crawler.py" crontab_temp; then
            log_warn "定时任务已存在，跳过设置"
        else
            # 添加新的定时任务
            echo "$cron_time cd $current_dir && $current_dir/venv/bin/python $current_dir/scripts/run_crawler.py --once >> $current_dir/logs/cron.log 2>&1" >> crontab_temp
            crontab crontab_temp
            rm crontab_temp
            log_info "定时任务设置成功: $cron_time"
        fi
    else
        log_info "跳过设置定时任务"
    fi
}

# 创建启动脚本
create_start_script() {
    log_info "创建启动脚本..."
    
    cat > start.sh << EOF
#!/bin/bash
cd $(pwd)
source venv/bin/activate
python scripts/run_crawler.py \$@
EOF
    
    chmod +x start.sh
    log_info "启动脚本创建成功: start.sh"
}

# 测试运行
test_run() {
    log_info "测试运行爬虫..."
    
    # 询问是否需要测试运行
    read -p "是否需要测试运行爬虫? (y/n): " test_run
    if [[ $test_run == "y" || $test_run == "Y" ]]; then
        log_info "开始测试运行爬虫..."
        python scripts/run_crawler.py --once
        if [ $? -ne 0 ]; then
            log_error "爬虫测试运行失败"
            exit 1
        fi
        log_info "爬虫测试运行成功"
    else
        log_info "跳过测试运行"
    fi
}

# 下载项目函数
download_project() {
    # 如果当前目录不是项目目录，则下载项目
    if [ ! -f "README.md" ] || ! grep -q "网易新闻爬虫系统" "README.md"; then
        log_info "下载项目文件..."
        
        # 检查并安装curl
        check_command curl curl
        
        # 检查并安装unzip
        check_command unzip unzip
        
        # 下载项目
        curl -L https://github.com/kentPhilippines/wiseflow_python/archive/refs/heads/main.zip -o wiseflow_python.zip
        
        # 解压项目
        unzip -o wiseflow_python.zip
        
        # 进入项目目录
        cd wiseflow_python-main
        
        # 设置部署脚本可执行权限
        chmod +x scripts/deploy.sh
        
        log_info "项目下载完成，开始部署..."
    fi
}

# 主函数
main() {
    log_info "开始部署网易新闻爬虫系统..."
    
    # 安装基础依赖
    install_base_dependencies
    
    # 检查并安装必要命令
    check_command python3 python3
    check_command pip3 python3-pip
    check_command bc bc
    
    # 检查Python版本
    check_python_version
    
    # 创建并激活虚拟环境
    create_venv
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    # 创建目录
    create_directories
    
    # 配置数据库
    configure_database
    
    # 初始化数据库
    init_database
    
    # 设置定时任务
    setup_cron
    
    # 创建启动脚本
    create_start_script
    
    # 测试运行
    test_run
    
    log_info "网易新闻爬虫系统部署完成!"
    log_info "使用方法:"
    log_info "1. 运行一次爬虫: ./start.sh --once"
    log_info "2. 按计划运行爬虫: ./start.sh --schedule"
    log_info "3. 导出数据: python scripts/export_data.py"
}

# 检查是否是通过curl直接执行的脚本
if [[ "$0" == "bash" ]] || [[ "$0" == "/bin/bash" ]] || [[ "$0" == "-bash" ]] || [[ "$0" == "/usr/bin/bash" ]]; then
    # 通过curl执行的情况
    download_project
fi

# 执行主函数
main 