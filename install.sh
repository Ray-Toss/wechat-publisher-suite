#!/bin/bash
# OpenClaw 微信公众号发布技能 一键安装脚本
# 使用方式: bash <(curl -fsSL https://raw.githubusercontent.com/Ray-Toss/wechat-publisher-suite/main/install.sh)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║        微信公众号发布技能 一键安装脚本           ║"
echo "║               专为 OpenClaw 设计                ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查OpenClaw目录
echo -e "\n${YELLOW}🔍 检查OpenClaw工作目录...${NC}"
OPENCLAW_DIR="$HOME/.openclaw/workspace/skills"
if [ ! -d "$OPENCLAW_DIR" ]; then
    echo -e "${RED}❌ 未找到OpenClaw技能目录: $OPENCLAW_DIR${NC}"
    echo -e "${YELLOW}💡 请确认已正确安装OpenClaw${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 找到OpenClaw技能目录: $OPENCLAW_DIR${NC}"

# 克隆仓库
echo -e "\n${YELLOW}📥 正在下载技能...${NC}"
TEMP_DIR=$(mktemp -d)
git clone https://github.com/Ray-Toss/wechat-publisher-suite.git "$TEMP_DIR/wechat-publisher-suite"
echo -e "${GREEN}✅ 技能下载完成${NC}"

# 安装到技能目录
echo -e "\n${YELLOW}📦 正在安装到OpenClaw技能目录...${NC}"
TARGET_DIR="$OPENCLAW_DIR/wechat-publisher-suite"
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  检测到已存在同名技能目录，是否覆盖？(y/N)${NC}"
    read -r OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 安装已取消${NC}"
        rm -rf "$TEMP_DIR"
        exit 0
    fi
    rm -rf "$TARGET_DIR"
fi

mv "$TEMP_DIR/wechat-publisher-suite" "$TARGET_DIR"
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✅ 技能已安装到: $TARGET_DIR${NC}"

# 配置提示
echo -e "\n${YELLOW}⚙️  下一步配置${NC}"
echo ""
echo "请在OpenClaw的环境变量中添加以下配置："
echo ""
echo "# Tavily API Key - 用于搜索热点和图片"
echo "# 申请地址: https://tavily.com/"
echo "export TAVILY_API_KEY=\"your-tavily-api-key\""
echo ""
echo "# 微信公众号配置"
echo "# 在微信公众平台开发者后台获取：https://mp.weixin.qq.com/"
echo "# 路径：开发 -> 基本配置 -> 开发者ID(AppID)和开发者密码(AppSecret)"
echo "export WECHAT_APPID=\"your-wechat-appid\""
echo "export WECHAT_APPSECRET=\"your-wechat-appsecret\""
echo ""
echo -e "${YELLOW}⚠️  重要提示：必须在微信公众平台后台配置IP白名单${NC}"
echo "   路径：开发 -> 基本配置 -> IP白名单，添加运行OpenClaw的服务器公网IP"
echo ""

# 使用说明
echo -e "\n${GREEN}🎉 安装完成！🎉${NC}"
echo ""
echo -e "${YELLOW}🚀 使用方式：${NC}"
echo "  直接和OpenClaw对话即可，不需要运行任何命令："
echo ""
echo "  示例："
echo "  \"帮我写一篇关于智能座舱大模型应用的公众号文章\""
echo "  \"生成一篇关于AI大模型的技术文章，发布到公众号\""
echo "  \"找一下本周的科技热点，写一篇公众号文章\""
echo ""
echo -e "${GREEN}💡 技能会自动完成从选题到发布的全流程！${NC}"
