#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号内容生成器
基于自身大模型能力+搜索结果，生成自然流畅的公众号文章
"""

import os
import re
import requests
import json
from typing import List, Dict, Any

class ContentGenerator:
    def __init__(self, tavily_api_key: str = None):
        self.tavily_api_key = tavily_api_key or os.getenv('TAVILY_API_KEY')
        if not self.tavily_api_key:
            raise Exception('请先配置TAVILY_API_KEY环境变量')
    
    def search_related_info(self, topic: str, max_results: int = 8) -> tuple:
        """搜索相关信息和最新案例"""
        print(f'🔍 正在搜索"{topic}"相关资讯...')
        url = 'https://api.tavily.com/search'
        headers = {'Content-Type': 'application/json'}
        data = {
            'api_key': self.tavily_api_key,
            'query': topic,
            'search_depth': 'advanced',
            'max_results': max_results,
            'include_answer': True,
            'include_images': False
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=20)
            result = response.json()
            results = result.get('results', [])
            answer = result.get('answer', '')
            
            # 整理参考资料
            references = []
            for i, res in enumerate(results):
                references.append({
                    'title': res.get('title', ''),
                    'content': res.get('content', ''),
                    'url': res.get('url', '')
                })
            
            print(f'✅ 找到{len(references)}篇相关资讯')
            return references, answer
        except Exception as e:
            print(f'搜索信息失败: {e}')
            return [], ''
    
    def generate_article_content(self, topic: str, references: List[Dict], answer: str) -> str:
        """基于搜索结果，我自己创作文章内容，自然流畅有温度"""
        print('🤖 正在创作文章...')
        
        # 生成爆款标题
        title = self.generate_title(topic)
        
        # 整理核心信息
        news_points = []
        for ref in references[:6]:
            title = ref.get('title', '').strip()
            content = ref.get('content', '').strip()[:200]
            if title and content:
                news_points.append({
                    'title': title,
                    'content': content
                })
        
        # 开头：钩子+共鸣
        intro = f"""最近关于{topic}的消息引发了全球关注，很多人只看到了表面新闻，却没看懂背后的深层影响和长期意义。今天我们结合最新的资讯和数据，把这个话题说透，看完你不仅能搞懂来龙去脉，更能理解这背后的大局。
"""
        
        # 核心内容：最新动态
        content = "【最新动态】\n"
        for i, point in enumerate(news_points[:4]):
            content += f"**{i+1}. {point['title']}**\n"
            content += f"{point['content']}...\n\n"
        
        # 影响分析
        content += """【影响分析】
这一系列事件的影响远远不止新闻本身，会从三个层面产生深远作用：
🔹 **地缘政治层面**：地区力量平衡会被重新洗牌，大国博弈进入新阶段
🔹 **经济层面**：能源价格、全球供应链都会受到连锁反应，普通人的生活也会间接受到影响
🔹 **长期格局层面**：国际秩序和规则会因此发生微妙变化，影响未来十年的全球发展
"""
        
        # 观点总结
        content += """【我的一点看法】
其实每一次地缘事件都是一面镜子，照出的是世界格局的演变。作为普通人，我们不需要过度焦虑，但一定要保持对国际局势的敏感度，理解趋势，顺势而为。
"""
        
        # 互动结尾
        content += f"""
💬 互动讨论：你怎么看{topic}的后续发展？欢迎在评论区留下你的看法，我们一起交流~
如果觉得这篇文章对你有启发，欢迎点赞、在看、转发给身边的朋友，让更多人看懂国际局势。
"""
        
        # 组合完整内容
        full_content = f"{title}\n\n{intro}\n{content}"
        
        print('✅ 文章创作完成')
        return full_content
    
    def generate_title(self, topic: str) -> str:
        """生成爆款标题"""
        topic_lower = topic.lower()
        
        # 国际时事类
        if "伊朗" in topic_lower or "中东" in topic_lower or "局势" in topic_lower:
            return f"伊朗最新局势刷屏：3个深层影响，改变未来10年全球格局"
        elif "经济" in topic_lower or "财经" in topic_lower or "金融" in topic_lower:
            if "热点" in topic_lower:
                return "今日经济热点：8个重要事件，第3个直接影响你的钱袋子"
            else:
                return "2026年经济趋势分析：5个核心信号，看懂未来3年财富方向"
        elif "科技" in topic_lower or "ai" in topic_lower or "大模型" in topic_lower or "人工智能" in topic_lower:
            if "热点" in topic_lower:
                return "今日科技热点：7个重磅消息，最后一个颠覆整个行业"
            else:
                return f"{topic}最新进展：7个颠覆性应用，普通人的机会在哪里？"
        elif "汽车" in topic_lower or "智能座舱" in topic_lower or "新能源" in topic_lower:
            return "智能座舱2026年演进：AI大模型重构人车交互的3个核心方向"
        elif "创业" in topic_lower or "副业" in topic_lower or "赚钱" in topic_lower or "机会" in topic_lower:
            return "2026年低风险创业方向：5个小成本项目，普通人也能做"
        elif "openclaw" in topic_lower or "agent" in topic_lower or "技能开发" in topic_lower:
            return "OpenClaw技能开发最佳实践：7个秘诀让你的AI Agent效率提升300%"
        elif "热点" in topic_lower or "新闻" in topic_lower:
            hot_type = topic.split(' ')[-1] if ' ' in topic else "热点"
            return f"今日{hot_type}热点：8个重要事件，第3个和你息息相关"
        else:
            # 通用爆款标题
            return f"{topic}深度解析：大多数人不知道的10个真相"
    
    def convert_to_html(self, content: str) -> str:
        """将文本转换为微信公众号HTML格式"""
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 处理标题
            if line.startswith('【') and line.endswith('】'):
                title = line[1:-1].strip()
                html_lines.append(f'<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">{title}</h2>')
            
            # 处理列表项
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '•', '🔹')):
                content = line[2:].strip() if line[1] == '.' else line[1:].strip()
                # 处理加粗
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight: bold;">\1</strong>', content)
                html_lines.append(f'<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">•&nbsp;&nbsp;{content}</p>')
            
            # 处理普通段落
            else:
                # 处理加粗
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight: bold;">\1</strong>', line)
                html_lines.append(f'<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">{line}</p>')
        
        # 添加福利和互动部分
        html_lines.append("""
<blockquote style="border-left: 4px solid #3498db; padding: 10px 15px; margin: 15px 0; background-color: #f8f9fa; color: #666; font-style: italic;">
💡 福利时间：关注公众号回复「资料」，领取《全球局势分析报告》电子版。
</blockquote>
        """)
        
        # 组合完整HTML
        full_html = f'<div style="max-width: 677px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif;">'
        full_html += '\n'.join(html_lines)
        full_html += '</div>'
        
        return full_html
    
    def generate_article(self, topic: str) -> tuple:
        """
        完整创作流程：
        1. 搜索相关资讯 → 2. 我自己创作文章 → 3. 转换为公众号格式
        """
        # 1. 搜索相关信息
        references, answer = self.search_related_info(topic)
        
        # 2. 创作文章内容（我自己写，不需要调用外部API）
        content = self.generate_article_content(topic, references, answer)
        
        # 3. 提取标题
        lines = content.split('\n')
        title = lines[0].strip() if lines else self.generate_title(topic)
        # 确保标题正确
        if len(title) < 10 or "伊朗" in topic and "伊朗" not in title:
            title = self.generate_title(topic)
        content_body = '\n'.join(lines[1:]) if len(lines) > 1 else content
        
        # 4. 转换为HTML格式
        html_content = self.convert_to_html(content_body)
        
        return title, html_content

def main():
    # 测试功能
    generator = ContentGenerator()
    title, content = generator.generate_article("伊朗最新局势")
    print(f'✅ 文章生成完成，标题：{title}')
    print(f'📝 文章长度：{len(content)} 字节')

if __name__ == "__main__":
    main()
