# 微信公众号发布套件（WeChat Publisher Suite）

🚀 全链路微信公众号内容生产和发布工具，实现从主题到草稿的一键式体验。

## ✨ 特性
- **🔍 智能选题**：自动搜索热点和行业数据，推荐优质选题
- **✍️ 内容生成**：双模式支持（技术文章/热点文章），自动生成高质量内容
- **🎨 格式优化**：自动适配微信公众号排版规范，生成标准HTML格式
- **🖼️ 智能配图**：优先搜索真实图片，文生图补充，自动上传到微信素材库
- **🚀 一键发布**：直接发布到公众号草稿箱，无需手动操作
- **🛡️ 内置校验**：自动检查格式错误、图片链接、内容合规性

## 🚀 快速开始
### 方式一：一键安装（推荐，1分钟搞定）
```bash
# 直接运行此命令即可完成全部安装配置
bash <(curl -fsSL https://raw.githubusercontent.com/your-repo/wechat-publisher-suite/main/install.sh)
```

安装脚本会自动完成：
1. 检查系统环境和Python版本
2. 克隆项目到本地
3. 安装所有依赖包
4. 引导输入API Key并配置环境
5. 添加命令别名到系统
6. 测试配置有效性

### 方式二：运行配置向导
```bash
# 克隆项目后运行配置向导
python scripts/setup.py
```

配置向导会一步步引导你：
1. 检查Python版本
2. 自动安装依赖包
3. 引导输入API Key并生成.env文件
4. 测试配置有效性
5. 显示使用说明

### 方式二：手动配置
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制环境变量模板
cp .env.example .env

# 3. 编辑.env文件，填入你的API Key
# TAVILY_API_KEY: https://tavily.com/ 获取
# WECHAT_API_KEY: https://wx.limyai.com/ 获取
# OPENAI_API_KEY: 可选，用于内容生成

# 4. 加载环境变量
source .env  # Linux/macOS
# 或 .\.env  # Windows
```

### 3. 一键发布
```bash
# 自动搜索热点并生成文章发布到草稿箱
python scripts/publish.py

# 指定主题生成文章
python scripts/publish.py --topic "智能座舱大模型应用"

# 指定文章类型（tech/hot）
python scripts/publish.py --topic "AI大模型最新进展" --type tech

# 仅生成内容不发布
python scripts/publish.py --topic "自动驾驶技术" --output ./article.html
```

## 📖 使用文档
### 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--topic <主题>` | 文章主题，不指定则自动搜索热点 | 自动搜索 |
| `--type <类型>` | 文章类型：`tech`(技术文章)/`hot`(热点文章)/`auto`(自动识别) | auto |
| `--output <路径>` | 文章保存路径，不指定则直接发布 | 直接发布 |
| `--images <数量>` | 配图数量 | 3 |
| `--appid <appid>` | 指定公众号APPID，不指定则使用第一个账号 | 自动选择 |
| `--draft` | 仅保存到草稿，不自动发布 | true |

### 文章类型说明
- **tech（技术文章）**：适合技术类公众号，结构包含背景、原理、实践、分析、趋势
- **hot（热点文章）**：适合资讯类公众号，结构包含事件回顾、分析、启示、观点
- **auto**：自动根据主题判断类型

## 🏗️ 项目结构
```
wechat-publisher-suite/
├── SKILL.md                    # AgentSkill 技能定义
├── README.md                   # 用户文档
├── .env.example                # 环境变量模板
├── scripts/
│   ├── setup.py                # 一键配置向导
│   ├── publish.py              # 主入口：一键发布全流程
│   ├── content_generator.py    # 内容生成模块
│   ├── format_converter.py     # 格式转换模块
│   ├── image_processor.py      # 图片处理模块
│   └── wechat_api.py           # 微信API封装
├── references/
│   ├── wechat-format-spec.md   # 微信格式规范
│   ├── content-templates.md    # 文章模板
│   └── api-docs.md             # API文档
└── assets/
    ├── default-styles.css      # 默认排版样式
    └── template.html           # HTML模板
```

## 🔧 技术栈
- **Python 3.8+**：核心开发语言
- **Tavily API**：网络搜索和图片搜索
- **OpenAI API**：内容生成（可选，可替换为其他大模型）
- **微信开放平台API**：公众号发布能力

## 🤝 贡献
欢迎提交Issue和Pull Request！

### 开发环境搭建
```bash
# 克隆项目
git clone https://github.com/your-repo/wechat-publisher-suite.git

# 安装依赖
pip install -r requirements.txt

# 运行测试
python scripts/publish.py --topic "测试主题" --output test.html
```

## 📄 许可证
MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙋 FAQ
### Q: 如何获取WECHAT_API_KEY？
A: 访问 https://wx.limyai.com/ 注册并授权你的公众号，即可获得API Key。

### Q: 可以不用OpenAI API吗？
A: 可以，如果你使用的是支持AgentSkill的AI助手（如OpenClaw/Claude），系统会自动使用内置的大模型能力生成内容。

### Q: 生成的文章需要修改吗？
A: 建议发布前预览一下内容，AI生成的内容可能需要根据你的账号风格进行微调。

### Q: 支持多公众号吗？
A: 支持，使用`--appid`参数指定要发布的公众号即可。

## 📞 交流
有问题欢迎提交Issue，或加入交流群讨论。
