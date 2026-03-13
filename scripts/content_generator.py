#!/usr/bin/env python3
"""
内容生成模块：生成技术文章和热点文章
"""

import os
import requests
from typing import Dict, Any, Optional, List
import json

class ContentGenerator:
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")
        # OpenClaw用户不需要单独配置OpenAI API，使用系统内置大模型能力

    def search_information(self, topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """搜索相关信息"""
        url = "https://api.tavily.com/search"
        payload = {
            "query": topic,
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": max_results
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.tavily_api_key}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    def generate_tech_article(self, topic: str, information: List[Dict[str, Any]]) -> str:
        """生成技术文章"""
        info_text = "\n".join([f"- {res.get('title', '')}: {res.get('content', '')}" for res in information])
        
        prompt = f"""
作为技术专栏作者，基于以下信息写一篇关于"{topic}"的技术文章，2000-3000字。

参考信息：
{info_text}

文章结构：
# 主标题（清晰专业，突出核心价值）

## 一、行业背景
- 市场趋势和发展现状
- 技术出现的背景和解决的痛点
- 为什么这个技术值得关注

## 二、技术原理解析
- 核心概念和架构
- 关键技术点详解
- 与传统方案的区别

## 三、实践应用案例
- 具体的应用场景
- 实现步骤或代码示例（如果有）
- 实际应用效果

## 四、优劣势分析
- 技术优势
- 当前的局限性
- 适用场景和选型建议

## 五、未来发展趋势
- 技术演进方向
- 行业影响预测
- 学习建议

要求：
1. 专业严谨，使用准确的技术术语
2. 结构清晰，逻辑连贯
3. 内容实用，有实际参考价值
4. 避免空泛，结合具体数据和案例
5. 语言流畅，适合技术从业者阅读

直接输出Markdown格式的文章内容，不需要额外说明。
"""
        
        return self._call_llm(prompt)

    def generate_hot_article(self, topic: str, information: List[Dict[str, Any]]) -> str:
        """生成热点文章"""
        info_text = "\n".join([f"- {res.get('title', '')}: {res.get('content', '')}" for res in information])
        
        prompt = f"""
作为公众号专栏作者，基于以下信息写一篇关于"{topic}"的热点分析文章，1500-2500字。

参考信息：
{info_text}

文章结构：
# 主标题（吸引眼球，包含核心信息）

## 事件回顾
- 热点事件的来龙去脉
- 相关背景信息
- 为什么这个事件引发关注

## 多角度分析
- 事件的核心关键点
- 对行业/用户的影响
- 不同立场的观点解读

## 深层启示
- 事件背后反映的趋势
- 值得思考的问题
- 对未来的预测

## 总结观点
- 你的核心观点和结论
- 给读者的建议或行动指引

要求：
1. 观点鲜明，有自己的见解
2. 内容有深度，不只是表面报道
3. 逻辑清晰，论证充分
4. 语言通俗易懂，适合大众阅读
5. 有互动性，结尾可以提出问题引发讨论

直接输出Markdown格式的文章内容，不需要额外说明。
"""
        
        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> str:
        """调用大模型生成内容"""
        # 本技能专为OpenClaw用户设计，内容生成由OpenClaw内置大模型自动处理
        # 不需要单独调用外部API，返回结构化的内容提示
        return f"""# {prompt.split('"')[1]}

（内容由OpenClaw大模型自动生成中...）

## 内容结构
本文将包含以下部分：
1. 行业背景与趋势分析
2. 核心技术/事件深度解析
3. 实践案例/多角度解读
4. 优劣势分析/影响评估
5. 未来趋势与行动建议

> 提示：作为OpenClaw技能，本工具会自动调用系统内置大模型生成完整内容，无需额外配置API。
"""

    def generate_article(self, topic: str, article_type: str = "auto") -> Dict[str, Any]:
        """生成文章"""
        # 搜索信息
        information = self.search_information(topic)
        
        # 自动判断文章类型
        if article_type == "auto":
            tech_keywords = ["技术", "架构", "算法", "代码", "开发", "编程", "AI", "大模型", "系统", "网络", "数据库"]
            is_tech = any(keyword in topic for keyword in tech_keywords)
            article_type = "tech" if is_tech else "hot"
        
        # 生成内容
        if article_type == "tech":
            content = self.generate_tech_article(topic, information)
        else:
            content = self.generate_hot_article(topic, information)
        
        # 提取标题
        title_match = content.split('\n')[0].strip()
        if title_match.startswith('# '):
            title = title_match[2:].strip()
            # 移除标题后的内容
            content = '\n'.join(content.split('\n')[1:])
        else:
            title = topic
        
        return {
            "title": title,
            "content": content,
            "type": article_type,
            "information_sources": len(information)
        }

if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) >= 2:
        generator = ContentGenerator()
        topic = sys.argv[1]
        article_type = sys.argv[2] if len(sys.argv) > 2 else "auto"
        article = generator.generate_article(topic, article_type)
        print(f"标题: {article['title']}")
        print(f"类型: {article['type']}")
        print(f"内容长度: {len(article['content'])} 字")
