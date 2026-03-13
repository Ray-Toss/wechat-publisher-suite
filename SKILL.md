---
name: wechat-publisher-suite
description: 微信公众号全链路发布套件 - 从主题选题、内容生成、格式优化到一键发布到草稿箱的完整工作流，支持技术文章和热点文章双模式，自动配图、自动排版，开箱即用。Use when: 用户需要发布微信公众号文章、创建公众号内容、一键生成公众号草稿。
---

# 微信公众号发布套件（WeChat Publisher Suite）

全链路微信公众号内容生产和发布工具，实现从主题到草稿的一键式体验。

## 核心能力
- 🔍 **智能选题**：自动搜索热点和行业数据，推荐优质选题
- ✍️ **内容生成**：双模式支持（技术文章/热点文章），自动生成高质量内容
- 🎨 **格式优化**：自动适配微信公众号排版规范，生成标准HTML格式
- 🖼️ **智能配图**：优先搜索真实图片，文生图补充，自动上传到微信素材库
- 🚀 **一键发布**：直接发布到公众号草稿箱，无需手动操作

## 触发场景
- "帮我写一篇关于XX的公众号文章"
- "发布这篇文章到微信公众号"
- "生成一个公众号热点文章"
- "公众号一键发布"

## 环境配置
### 必需的环境变量
```bash
# Tavily API 用于搜索热点和图片
export TAVILY_API_KEY="your-tavily-api-key"

# 微信API Key 用于公众号发布
export WECHAT_API_KEY="your-wechat-api-key"

# OpenAI API 用于内容生成（可选，使用系统默认时不需要）
export OPENAI_API_KEY="your-openai-api-key"
```

### 获取API Key
- Tavily API: https://tavily.com/
- 微信API: https://wx.limyai.com/

## 使用方法
### 首次使用：一键配置
```bash
# 运行配置向导，自动完成环境配置
python scripts/setup.py
```

### 基础用法（一键发布）
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

### 完整参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--topic <主题>` | 文章主题，不指定则自动搜索热点 | 自动搜索 |
| `--type <类型>` | 文章类型：`tech`(技术文章)/`hot`(热点文章) | 自动识别 |
| `--output <路径>` | 文章保存路径，不指定则直接发布 | 直接发布 |
| `--images <数量>` | 配图数量 | 3 |
| `--appid <appid>` | 指定公众号APPID，不指定则使用第一个账号 | 自动选择 |
| `--draft` | 仅保存到草稿，不自动发布 | true |

## 工作流程
```
1. 选题阶段：搜索相关资讯、数据、案例
2. 内容生成：根据类型选择对应模板生成文章
3. 配图阶段：搜索相关图片，自动上传到微信素材库
4. 格式转换：转换为公众号兼容的HTML格式，优化排版
5. 发布阶段：调用微信API创建草稿，返回预览链接
```

## 文章结构
### 技术文章模式
- 行业背景与趋势
- 技术原理解析
- 实践案例与代码示例
- 竞品分析对比
- 未来趋势展望
- 总结与互动

### 热点文章模式
- 热点事件回顾
- 多角度分析解读
- 行业影响与启示
- 观点总结与评论
- 互动提问

## 格式规范
自动遵循微信公众号排版要求：
- 使用HTML标签，不使用Markdown语法
- 图片使用带样式的HTML标签，自动居中、圆角、阴影
- 段落间距、字体大小、行高优化，适合手机阅读
- 重要内容自动加粗突出
- 自动生成分隔线、引用块等元素

## 最佳实践
1. 技术类文章建议使用`--type tech`获得更专业的内容
2. 热点类文章建议使用`--type hot`获得更时效性的内容
3. 发布前可以使用`--output`参数先预览内容
4. 配图优先使用搜索到的真实图片，更有说服力

## 相关脚本
- `scripts/content_generator.py` - 内容生成模块
- `scripts/format_converter.py` - 格式转换模块
- `scripts/image_processor.py` - 图片处理模块
- `scripts/wechat_api.py` - 微信API封装

## 错误处理
- API_KEY未配置：提示用户设置环境变量
- 公众号未授权：提示用户在wx.limyai.com授权账号
- 图片上传失败：自动重试，或跳过图片使用默认配图
- 内容生成失败：降级使用简化模式生成内容

## 开源地址
GitHub: https://github.com/your-repo/wechat-publisher-suite
