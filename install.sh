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

# 交互式配置
echo -e "\n${YELLOW}⚙️  配置API密钥（可直接回车跳过，后续再配置）${NC}"
echo ""

# 检查bashrc文件
BASHRC_FILE="$HOME/.bashrc"
if [ ! -f "$BASHRC_FILE" ]; then
    touch "$BASHRC_FILE"
fi

# 询问是否现在配置
echo -e "${YELLOW}🤔 是否现在配置API密钥？(Y/n)${NC}"
read -r CONFIG_NOW
if [[ "$CONFIG_NOW" =~ ^[Yy]$ ]] || [[ -z "$CONFIG_NOW" ]]; then
    # 收集配置信息
    echo ""
    echo -e "${YELLOW}🔑 请输入 Tavily API Key (申请地址: https://tavily.com/):${NC}"
    read -r TAVILY_API_KEY
    
    echo ""
    echo -e "${YELLOW}💬 请输入微信公众号 AppID:${NC}"
    read -r WECHAT_APPID
    
    echo ""
    echo -e "${YELLOW}🔒 请输入微信公众号 AppSecret:${NC}"
    read -r WECHAT_APPSECRET
    
    # 写入配置到bashrc
    echo ""
    echo -e "${YELLOW}📝 正在写入配置到 ~/.bashrc...${NC}"
    
    # 移除旧配置
    sed -i '/# 微信公众号发布技能配置/d' "$BASHRC_FILE"
    sed -i '/export TAVILY_API_KEY=/d' "$BASHRC_FILE"
    sed -i '/export WECHAT_APPID=/d' "$BASHRC_FILE"
    sed -i '/export WECHAT_APPSECRET=/d' "$BASHRC_FILE"
    
    # 添加新配置
    if [ -n "$TAVILY_API_KEY" ]; then
        echo "" >> "$BASHRC_FILE"
        echo "# 微信公众号发布技能配置" >> "$BASHRC_FILE"
        echo "export TAVILY_API_KEY=\"$TAVILY_API_KEY\"" >> "$BASHRC_FILE"
        if [ -n "$WECHAT_APPID" ]; then
            echo "export WECHAT_APPID=\"$WECHAT_APPID\"" >> "$BASHRC_FILE"
        fi
        if [ -n "$WECHAT_APPSECRET" ]; then
            echo "export WECHAT_APPSECRET=\"$WECHAT_APPSECRET\"" >> "$BASHRC_FILE"
        fi
        echo -e "${GREEN}✅ 配置已保存到 ~/.bashrc${NC}"
        echo ""
        echo -e "${YELLOW}💡 请运行以下命令使配置生效：${NC}"
        echo "   source ~/.bashrc"
    else
        echo -e "${YELLOW}⚠️  未输入Tavily API Key，已跳过配置写入${NC}"
    fi
else
    # 显示手动配置说明
    echo ""
    echo -e "${YELLOW}📝 手动配置方法：${NC}"
    echo ""
    echo "请在 ~/.bashrc 文件中添加以下配置："
    echo ""
    echo "# 微信公众号发布技能配置"
    echo "# Tavily API Key - 用于搜索热点和图片，申请地址: https://tavily.com/"
    echo "export TAVILY_API_KEY=\"your-tavily-api-key\""
    echo ""
    echo "# 微信公众号配置（在微信公众平台开发者后台获取）"
    echo "export WECHAT_APPID=\"your-wechat-appid\""
    echo "export WECHAT_APPSECRET=\"your-wechat-appsecret\""
    echo ""
    echo "配置完成后运行：source ~/.bashrc"
fi

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
