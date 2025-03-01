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
        log_warn "Python版本需要 >= 3.8，当前版本: $python_version"
        log_info "尝试安装更高版本的Python..."
        
        OS=$(detect_os)
        if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
            log_info "在Ubuntu/Debian上安装Python 3.8..."
            apt update -y
            apt install -y software-properties-common
            add-apt-repository -y ppa:deadsnakes/ppa
            apt update -y
            apt install -y python3.8 python3.8-dev python3.8-venv python3.8-distutils
            
            # 创建软链接
            update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
            
            # 安装pip
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python3.8 get-pip.py
            rm get-pip.py
            
            # 检查安装结果
            python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            if [[ $(echo "$python_version < 3.8" | bc) -eq 1 ]]; then
                log_error "Python 3.8安装失败，请手动安装"
                exit 1
            fi
            log_info "Python 3.8安装成功，当前版本: $python_version"
            
        elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]] || [[ $OS == *"Fedora"* ]]; then
            log_info "在CentOS/RHEL上安装Python 3.8..."
            
            # 安装开发工具
            yum groupinstall -y "Development Tools"
            yum install -y openssl-devel bzip2-devel libffi-devel
            
            # 下载并编译Python 3.8
            cd /tmp
            curl -O https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
            tar -xzf Python-3.8.12.tgz
            cd Python-3.8.12
            ./configure --enable-optimizations
            make altinstall
            
            # 创建软链接
            ln -sf /usr/local/bin/python3.8 /usr/bin/python3
            ln -sf /usr/local/bin/pip3.8 /usr/bin/pip3
            
            # 返回原目录
            cd -
            
            # 检查安装结果
            python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            if [[ $(echo "$python_version < 3.8" | bc) -eq 1 ]]; then
                log_error "Python 3.8安装失败，请手动安装"
                exit 1
            fi
            log_info "Python 3.8安装成功，当前版本: $python_version"
            
        else
            log_error "不支持的操作系统: $OS，请手动安装Python 3.8或更高版本"
            exit 1
        fi
    else
        log_info "Python版本检查通过: $python_version"
    fi
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    
    if [ -d "$ABSOLUTE_PATH/venv" ]; then
        log_warn "虚拟环境已存在，跳过创建"
    else
        python3 -m venv $ABSOLUTE_PATH/venv
        if [ $? -ne 0 ]; then
            log_error "创建虚拟环境失败"
            exit 1
        fi
        log_info "虚拟环境创建成功: $ABSOLUTE_PATH/venv"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    
    source $ABSOLUTE_PATH/venv/bin/activate
    if [ $? -ne 0 ]; then
        log_error "激活虚拟环境失败"
        exit 1
    fi
    log_info "虚拟环境激活成功"
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."
    
    # 确保在正确的项目目录中
    if [ ! -d "config" ] || [ ! -d "database" ] || [ ! -d "scripts" ]; then
        log_warn "当前不在项目根目录，尝试查找项目目录..."
        
        # 检查是否在wiseflow_python-main目录下
        if [ -d "wiseflow_python-main" ]; then
            log_info "找到项目目录: wiseflow_python-main"
            cd wiseflow_python-main
        # 检查是否在wiseflow_python目录下
        elif [ -d "wiseflow_python" ]; then
            log_info "找到项目目录: wiseflow_python"
            cd wiseflow_python
        # 检查是否在/tmp/wiseflow_python目录下
        elif [ -d "/tmp/wiseflow_python" ]; then
            log_info "找到项目目录: /tmp/wiseflow_python"
            cd /tmp/wiseflow_python
            
            # 检查子目录
            if [ -d "wiseflow_python-main" ]; then
                cd wiseflow_python-main
            elif [ -d "wiseflow_python" ]; then
                cd wiseflow_python
            fi
        else
            log_error "无法找到项目目录，请确保已下载项目"
            exit 1
        fi
    fi
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    log_info "当前工作目录: $ABSOLUTE_PATH"
    
    # 检查requirements.txt是否存在
    if [ ! -f "requirements.txt" ]; then
        log_warn "requirements.txt文件不存在，创建基本依赖文件..."
        cat > requirements.txt << EOF
scrapy==2.8.0
pymysql==1.0.3
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
pillow==10.0.0
lxml==4.9.3
fake-useragent==1.1.3
schedule==1.2.0
EOF
        log_info "已创建基本的requirements.txt文件"
    else
        # 检查并移除concurrent-futures依赖
        if grep -q "concurrent-futures" requirements.txt; then
            log_warn "发现concurrent-futures依赖，这在Python 3.x中是不需要的，正在移除..."
            sed -i '/concurrent-futures/d' requirements.txt
            log_info "已移除concurrent-futures依赖"
        fi
    fi
    
    # 升级pip
    log_info "升级pip到最新版本..."
    $ABSOLUTE_PATH/venv/bin/pip install --upgrade pip
    
    # 确保pip可用
    if ! $ABSOLUTE_PATH/venv/bin/pip --version &> /dev/null; then
        log_warn "pip可能不可用，尝试重新安装..."
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $ABSOLUTE_PATH/venv/bin/python get-pip.py
        rm get-pip.py
    fi
    
    # 先安装核心依赖
    log_info "安装核心依赖..."
    CORE_DEPS=("pymysql" "python-dotenv" "requests")
    
    for dep in "${CORE_DEPS[@]}"; do
        log_info "安装核心依赖: $dep"
        # 尝试多次安装
        for i in {1..3}; do
            log_info "尝试安装 $dep (尝试 $i/3)..."
            $ABSOLUTE_PATH/venv/bin/pip install $dep -i https://pypi.org/simple
            
            if $ABSOLUTE_PATH/venv/bin/python -c "import $dep" &> /dev/null; then
                log_info "核心依赖 $dep 安装成功"
                break
            else
                if [ $i -eq 3 ]; then
                    log_error "核心依赖 $dep 安装失败，尝试使用其他源..."
                    # 尝试使用其他源
                    $ABSOLUTE_PATH/venv/bin/pip install $dep -i https://mirrors.aliyun.com/pypi/simple/
                    
                    if ! $ABSOLUTE_PATH/venv/bin/python -c "import $dep" &> /dev/null; then
                        log_error "核心依赖 $dep 安装失败，请检查网络连接或手动安装"
                    else
                        log_info "使用备用源安装 $dep 成功"
                    fi
                fi
            fi
        done
    done
    
    # 安装其他依赖
    log_info "安装其他依赖..."
    while IFS= read -r package || [[ -n "$package" ]]; do
        # 跳过注释、空行和核心依赖
        if [[ $package == \#* ]] || [[ -z "${package// }" ]] || [[ " ${CORE_DEPS[@]} " =~ " ${package%%==*} " ]]; then
            continue
        fi
        
        log_info "安装: $package"
        $ABSOLUTE_PATH/venv/bin/pip install $package
        
        if [ $? -ne 0 ]; then
            log_warn "安装 $package 失败，尝试继续安装其他依赖..."
        fi
    done < requirements.txt
    
    # 检查核心依赖是否安装成功
    log_info "检查核心依赖..."
    MISSING_DEPS=()
    
    for dep in "${CORE_DEPS[@]}"; do
        if ! $ABSOLUTE_PATH/venv/bin/python -c "import $dep" &> /dev/null; then
            MISSING_DEPS+=("$dep")
        fi
    done
    
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        log_error "以下核心依赖安装失败: ${MISSING_DEPS[*]}"
        log_error "尝试手动安装这些依赖..."
        
        # 尝试使用系统包管理器安装
        OS=$(detect_os)
        if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
            for dep in "${MISSING_DEPS[@]}"; do
                log_info "尝试使用apt安装 python3-$dep..."
                apt install -y python3-$dep
            done
        elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]] || [[ $OS == *"Fedora"* ]]; then
            for dep in "${MISSING_DEPS[@]}"; do
                log_info "尝试使用yum安装 python3-$dep..."
                yum install -y python3-$dep
            done
        fi

        
        # 再次检查
        MISSING_DEPS=()
        for dep in "${CORE_DEPS[@]}"; do
            if ! $ABSOLUTE_PATH/venv/bin/python -c "import $dep" &> /dev/null; then
                MISSING_DEPS+=("$dep")
            fi
        done
        
        if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
            log_error "仍然无法安装以下核心依赖: ${MISSING_DEPS[*]}"
            log_error "请手动安装这些依赖后继续"
            log_info "您可以尝试以下命令手动安装:"
            for dep in "${MISSING_DEPS[@]}"; do
                echo "$ABSOLUTE_PATH/venv/bin/pip install $dep -i https://pypi.org/simple"
            done
            exit 1
        fi
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
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    
    $ABSOLUTE_PATH/venv/bin/python -c "from database.db_handler import init_db; init_db()"
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
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    
    # 询问是否需要设置定时任务
    read -p "是否需要设置定时任务? (y/n): " setup_cron
    if [[ $setup_cron == "y" || $setup_cron == "Y" ]]; then
        read -p "定时任务执行时间 (crontab格式，默认: 0 2 * * * 每天凌晨2点): " cron_time
        cron_time=${cron_time:-"0 2 * * *"}
        
        # 创建临时crontab文件
        crontab -l > crontab_temp 2>/dev/null || true
        
        # 检查是否已存在相同的定时任务
        if grep -q "$ABSOLUTE_PATH/scripts/run_crawler.py" crontab_temp; then
            log_warn "定时任务已存在，跳过设置"
        else
            # 添加新的定时任务
            echo "$cron_time cd $ABSOLUTE_PATH && $ABSOLUTE_PATH/venv/bin/python $ABSOLUTE_PATH/scripts/run_crawler.py --once >> $ABSOLUTE_PATH/logs/cron.log 2>&1" >> crontab_temp
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
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    
    cat > start.sh << EOF
#!/bin/bash
cd $ABSOLUTE_PATH
source $ABSOLUTE_PATH/venv/bin/activate
$ABSOLUTE_PATH/venv/bin/python $ABSOLUTE_PATH/scripts/run_crawler.py \$@
EOF
    
    chmod +x start.sh
    log_info "启动脚本创建成功: $ABSOLUTE_PATH/start.sh"
}

# 测试运行
test_run() {
    log_info "测试运行爬虫..."
    
    # 获取当前目录的绝对路径
    ABSOLUTE_PATH=$(pwd)
    
    # 询问是否需要测试运行
    read -p "是否需要测试运行爬虫? (y/n): " test_run
    if [[ $test_run == "y" || $test_run == "Y" ]]; then
        log_info "开始测试运行爬虫..."
        $ABSOLUTE_PATH/venv/bin/python $ABSOLUTE_PATH/scripts/run_crawler.py --once
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
    if [ ! -f "README.md" ] || ! grep -q "网易新闻爬虫系统" "README.md" 2>/dev/null; then
        log_info "下载项目文件..."
        
        # 创建临时工作目录
        WORK_DIR="/tmp/wiseflow_python"
        mkdir -p $WORK_DIR
        cd $WORK_DIR
        
        # 检查并安装curl
        check_command curl curl
        
        # 检查并安装unzip
        check_command unzip unzip
        
        # 下载项目
        curl -L https://github.com/kentPhilippines/wiseflow_python/archive/refs/heads/main.zip -o wiseflow_python.zip
        
        # 解压项目
        unzip -o wiseflow_python.zip
        
        # 进入项目目录
        cd wiseflow_python-main || {
            # 如果目录不存在，创建基本项目结构
            log_warn "无法进入项目目录，创建基本项目结构..."
            mkdir -p wiseflow_python
            cd wiseflow_python
            
            # 创建基本项目结构
            mkdir -p config database scripts data/exports data/images logs
            
            # 创建README文件
            cat > README.md << EOF
# 网易新闻爬虫系统

这是一个用于抓取网易新闻数据的爬虫系统。

## 功能特点

- 抓取网易新闻数据，包括标题、内容、图片和标签
- 数据存储到MySQL数据库
- 支持数据导出为JSON和CSV格式
- 支持定时抓取
- 支持断点续爬
- 多线程抓取
- IP和User-Agent轮换

## 使用方法

1. 运行一次爬虫: \${INSTALL_PATH}/start.sh --once
2. 按计划运行爬虫: \${INSTALL_PATH}/start.sh --schedule
3. 导出数据: \${INSTALL_PATH}/venv/bin/python \${INSTALL_PATH}/scripts/export_data.py --format json

## 部署方法

使用一键部署脚本:

\`\`\`bash
curl -s -L https://raw.githubusercontent.com/kentPhilippines/wiseflow_python/main/scripts/deploy.sh | bash
\`\`\`
EOF

            # 替换README中的安装路径变量
            sed -i "s|\\\${INSTALL_PATH}|$ABSOLUTE_PATH|g" README.md
        }
        
        # 设置部署脚本可执行权限
        chmod +x scripts/deploy.sh 2>/dev/null || true
        
        log_info "项目下载完成，开始部署..."
    fi
}





# 主函数
main() {
    log_info "开始部署网易新闻爬虫系统..."
    
    # 下载项目（如果需要）
    download_project
    
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
    
    # 获取当前目录的绝对路径（确保在最后输出时也有）
    ABSOLUTE_PATH=$(pwd)
    
    log_info "网易新闻爬虫系统部署完成!"
    log_info "使用方法:"
    log_info "1. 运行一次爬虫: $ABSOLUTE_PATH/start.sh --once"
    log_info "2. 按计划运行爬虫: $ABSOLUTE_PATH/start.sh --schedule"
    log_info "3. 导出数据: $ABSOLUTE_PATH/venv/bin/python $ABSOLUTE_PATH/scripts/export_data.py"
}

# 检查是否是通过curl直接执行的脚本
if [[ "$0" == "bash" ]] || [[ "$0" == "/bin/bash" ]] || [[ "$0" == "-bash" ]] || [[ "$0" == "/usr/bin/bash" ]]; then
    # 通过curl执行的情况
    download_project
else
    # 如果不是通过curl执行，也需要确保项目已下载
    download_project
fi

# 执行主函数
main 