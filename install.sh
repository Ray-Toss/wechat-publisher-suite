#!/bin/bash
# 微信公众号发布套件 一键安装脚本
# 使用方式: bash <(curl -fsSL https://raw.githubusercontent.com/your-repo/wechat-publisher-suite/main/install.sh)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║               微信公众号发布套件                 ║"
echo "║               一键安装脚本 v1.0.0                ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    echo -e "${RED}❌ 不支持的操作系统: $OSTYPE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 检测到操作系统: $OS${NC}"

# 检查Python版本
echo -e "\n${YELLOW}🔍 检查Python版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到Python3，请先安装Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python版本过低: $PYTHON_VERSION，需要Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python版本符合要求: $PYTHON_VERSION${NC}"

# 检查Git
echo -e "\n${YELLOW}🔍 检查Git...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 未找到Git，请先安装Git${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git已安装${NC}"

# 克隆仓库
echo -e "\n${YELLOW}📥 正在克隆项目...${NC}"
INSTALL_DIR="$HOME/wechat-publisher-suite"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  检测到已存在安装目录，是否覆盖？(y/N)${NC}"
    read -r OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 安装已取消${NC}"
        exit 0
    fi
    rm -rf "$INSTALL_DIR"
fi

git clone https://github.com/your-repo/wechat-publisher-suite.git "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}✅ 项目已克隆到: $INSTALL_DIR${NC}"

# 安装依赖
echo -e "\n${YELLOW}📦 正在安装Python依赖...${NC}"
pip3 install -r requirements.txt
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 配置环境变量
echo -e "\n${YELLOW}⚙️  开始配置环境变量...${NC}"
echo ""
echo "请准备好以下配置信息："
echo "1. Tavily API Key (https://tavily.com/) - 用于搜索热点和图片"
echo "2. 微信公众号APPID - 在微信公众平台后台获取：开发 -> 基本配置"
echo "3. 微信公众号APPSECRET - 在微信公众平台后台获取：开发 -> 基本配置"
echo ""
echo "⚠️  重要提示：请先在微信公众平台后台配置IP白名单"
echo "   路径：开发 -> 基本配置 -> IP白名单，添加你服务器的公网IP"
echo ""

read -p "请输入Tavily API Key: " TAVILY_KEY
while [ -z "$TAVILY_KEY" ]; do
    read -p "Tavily API Key不能为空，请重新输入: " TAVILY_KEY
done

read -p "请输入微信公众号APPID: " WECHAT_APPID
while [ -z "$WECHAT_APPID" ]; do
    read -p "微信公众号APPID不能为空，请重新输入: " WECHAT_APPID
done

read -p "请输入微信公众号APPSECRET: " WECHAT_APPSECRET
while [ -z "$WECHAT_APPSECRET" ]; do
    read -p "微信公众号APPSECRET不能为空，请重新输入: " WECHAT_APPSECRET
done

# 生成.env文件
cat > .env << EOF
# 微信公众号发布套件环境变量配置
# 配置时间: $(date)

# Tavily API Key - 用于搜索热点和图片
# 申请地址: https://tavily.com/
export TAVILY_API_KEY="$TAVILY_KEY"

# 微信公众号配置
# 在微信公众平台后台获取：开发 -> 基本配置
export WECHAT_APPID="$WECHAT_APPID"
export WECHAT_APPSECRET="$WECHAT_APPSECRET"

# ⚠️ 重要提示：必须在微信公众平台后台配置IP白名单
# 路径：开发 -> 基本配置 -> IP白名单，添加你服务器的公网IP
EOF

echo -e "${GREEN}✅ 环境变量已保存到 $INSTALL_DIR/.env${NC}"

# 添加到PATH
echo -e "\n${YELLOW}🔧 正在配置环境变量...${NC}"
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# 添加别名
if ! grep -q "wechat-publisher-suite" "$SHELL_CONFIG"; then
    cat >> "$SHELL_CONFIG" << EOF

# 微信公众号发布套件
export PATH="$INSTALL_DIR/scripts:\$PATH"
alias wechat-publish="cd $INSTALL_DIR && source .env && python3 scripts/publish.py"
alias wechat-setup="cd $INSTALL_DIR && python3 scripts/setup.py"
EOF
    echo -e "${GREEN}✅ 已添加到PATH和别名${NC}"
    echo -e "${YELLOW}💡 请运行以下命令生效配置:${NC}"
    echo -e "  source $SHELL_CONFIG"
fi

# 测试配置
echo -e "\n${YELLOW}🧪 正在测试配置...${NC}"
source .env

# 测试Tavily API
echo -e "  测试Tavily API..."
TEST_RESULT=$(python3 -c "
import requests
try:
    response = requests.post('https://api.tavily.com/search', 
        json={'query': 'test', 'max_results': 1},
        headers={'Authorization': 'Bearer $TAVILY_KEY'})
    print('success' if response.status_code == 200 else 'failed')
except Exception as e:
    print('failed')
")
if [ "$TEST_RESULT" = "success" ]; then
    echo -e "${GREEN}  ✅ Tavily API 配置有效${NC}"
else
    echo -e "${YELLOW}  ⚠️  Tavily API 测试失败，请检查API Key是否正确${NC}"
fi

# 测试微信API
echo -e "  测试微信API..."
TEST_RESULT=$(python3 -c "
import requests
try:
    response = requests.get('https://api.weixin.qq.com/cgi-bin/token',
        params={
            'grant_type': 'client_credential',
            'appid': '$WECHAT_APPID',
            'secret': '$WECHAT_APPSECRET'
        })
    data = response.json()
    print('success' if 'access_token' in data else 'failed:' + str(data.get('errmsg')))
except Exception as e:
    print('failed:' + str(e))
")
if [[ "$TEST_RESULT" == success* ]]; then
    echo -e "${GREEN}  ✅ 微信API 配置有效${NC}"
    echo -e "${GREEN}  📋 公众号APPID: $WECHAT_APPID${NC}"
else
    echo -e "${YELLOW}  ⚠️  微信API 测试失败: ${TEST_RESULT#failed:}${NC}"
    echo -e "${YELLOW}  💡 请检查：${NC}"
    echo -e "     1. APPID和APPSECRET是否正确"
    echo -e "     2. 公众号后台是否配置了IP白名单"
    echo -e "     3. 公众号是否是认证的服务号/订阅号"
fi

# 安装完成
echo -e "\n${GREEN}🎉 安装完成！🎉${NC}"
echo ""
echo -e "${YELLOW}🚀 使用方式:${NC}"
echo "  1. 生效配置: source $SHELL_CONFIG"
echo "  2. 一键发布: wechat-publish --topic \"你的文章主题\""
echo "  3. 自动热点: wechat-publish"
echo "  4. 更多帮助: wechat-publish --help"
echo ""
echo -e "${YELLOW}📖 完整文档:${NC}"
echo "  $INSTALL_DIR/README.md"
echo ""
echo -e "${GREEN}💡 现在你可以开始使用微信公众号发布套件了！${NC}"
