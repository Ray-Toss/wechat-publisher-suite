#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号内容生成器
完全动态生成，根据任意主题生成高质量公众号文章
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
    
    def search_related_info(self, topic: str, max_results: int = 10) -> List[Dict]:
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
            print(f'✅ 找到{len(results)}篇相关资讯')
            return results, answer
        except Exception as e:
            print(f'搜索信息失败: {e}')
            return [], ''
    
    def generate_title(self, topic: str) -> str:
        """生成爆款标题"""
        topic_lower = topic.lower()
        
        # 经济/财经类标题
        if "经济" in topic_lower or "财经" in topic_lower or "金融" in topic_lower:
            if "热点" in topic_lower or "新闻" in topic_lower:
                return "今日经济热点：8个重要事件，第3个直接影响你的钱袋子"
            elif "趋势" in topic_lower or "未来" in topic_lower:
                return "2026年经济趋势分析：5个核心信号，看懂未来3年财富方向"
            else:
                return "经济趋势深度解析：普通人如何抓住这波财富机遇"
        
        # 科技/AI类标题
        elif "科技" in topic_lower or "ai" in topic_lower or "大模型" in topic_lower or "人工智能" in topic_lower:
            if "热点" in topic_lower or "新闻" in topic_lower:
                return "今日科技热点：7个重磅消息，最后一个颠覆整个行业"
            elif "应用" in topic_lower or "落地" in topic_lower:
                return "AI大模型落地的5个核心场景，2026年行业爆发点分析"
            else:
                return f"{topic}最新进展：7个颠覆性应用，普通人的机会在哪里？"
        
        # 汽车/智能座舱类标题
        elif "汽车" in topic_lower or "智能座舱" in topic_lower or "新能源" in topic_lower:
            return "智能座舱2026年演进：AI大模型重构人车交互的3个核心方向"
        
        # 创业/副业类标题
        elif "创业" in topic_lower or "副业" in topic_lower or "赚钱" in topic_lower or "机会" in topic_lower:
            return "2026年低风险创业方向：5个小成本项目，普通人也能做"
        
        # OpenClaw/Agent类标题
        elif "openclaw" in topic_lower or "agent" in topic_lower or "技能开发" in topic_lower:
            return "OpenClaw技能开发最佳实践：7个秘诀让你的AI Agent效率提升300%"
        
        # 热点/新闻类通用标题
        elif "热点" in topic_lower or "新闻" in topic_lower:
            hot_type = topic.split(' ')[-1] if ' ' in topic else "热点"
            return f"今日{hot_type}热点：8个重要事件，第3个和你息息相关"
        
        # 通用爆款标题
        else:
            return f"{topic}深度解析：行业专家不会告诉你的10个秘密"
    
    def generate_dynamic_article(self, topic: str, search_results: List[Dict], search_answer: str) -> tuple:
        """根据搜索结果完全动态生成文章"""
        print('🤖 正在动态生成文章内容...')
        
        # 生成爆款标题
        title = self.generate_title(topic)
        
        # 构建文章结构
        article_parts = []
        
        # 开头部分：钩子+痛点
        article_parts.append(f"""
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
最近关于<strong style="font-weight: bold;">{topic}</strong>的讨论越来越多，很多人还没意识到这波浪潮带来的机会和挑战。
</p>
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
今天这篇文章我们结合最新的行业数据和真实案例，把这个话题说透，看完你不仅能搞懂背后的逻辑，更能找到适合自己的机会。
</p>
        """)
        
        # 核心内容部分：根据搜索结果动态生成
        article_parts.append(f"""
<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">一、核心要点：你需要知道的{min(len(search_results), 8)}个关键信息</h2>
        """)
        
        # 动态生成要点列表
        for i, res in enumerate(search_results[:min(len(search_results), 8)]):
            point_title = res.get('title', f'要点{i+1}')
            # 清理标题中的特殊字符
            point_title = re.sub(r'\[PDF\]|\[DOC\]|\[网页\]', '', point_title).strip()
            point_title = point_title.split(' - ')[0].strip()  # 去掉来源后缀
            content = res.get('content', '')[:200] + "..."
            article_parts.append(f"""
<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">{i+1}.&nbsp;&nbsp;<strong style="font-weight: bold;">{point_title}</strong><br>
<span style="margin-left: 1.5em;">{content}</span>
</p>
            """)
        
        # 趋势分析部分
        article_parts.append(f"""
<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">二、趋势分析：未来发展的3个核心方向</h2>
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
结合最新的行业动态，我们判断这个领域未来会朝着这三个方向发展：
</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1em;">🔹&nbsp;&nbsp;<strong style="font-weight: bold;">技术落地加速</strong>：从概念验证到规模化商用，成本会快速下降，普及率大幅提升</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1em;">🔹&nbsp;&nbsp;<strong style="font-weight: bold;">场景更加细分</strong>：从通用场景到垂直行业深度定制，专业领域机会更多</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1em;">🔹&nbsp;&nbsp;<strong style="font-weight: bold;">生态逐步完善</strong>：平台、工具、服务、内容的完整产业链正在形成</p>
        """)
        
        # 机遇与挑战部分
        article_parts.append(f"""
<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">三、机会分析：普通人能抓住的4个机遇</h2>
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
任何行业变革都会带来新的机会，这几个方向普通人也可以参与：
</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">1.&nbsp;&nbsp;<strong style="font-weight: bold;">技能升级</strong>：学习相关工具的使用，成为第一批吃螃蟹的人</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">2.&nbsp;&nbsp;<strong style="font-weight: bold;">内容创作</strong>：分享行业知识、经验、案例，打造个人IP</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">3.&nbsp;&nbsp;<strong style="font-weight: bold;">服务提供商</strong>：为企业和个人提供配套服务，比如咨询、培训、定制开发</p>
<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">4.&nbsp;&nbsp;<strong style="font-weight: bold;">资源整合</strong>：连接供需双方，做信息和资源的中介</p>
        """)
        
        # 案例部分（如果有搜索到案例）
        if search_answer and len(search_answer) > 100:
            article_parts.append(f"""
<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">四、真实案例：先行者已经拿到结果</h2>
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
{search_answer[:300]}...
</p>
            """)
        
        # 结尾部分：总结+互动
        article_parts.append(f"""
<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">最后总结</h2>
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
每一次技术变革都会淘汰一批人，也会成就一批人。与其焦虑会不会被取代，不如主动拥抱变化，成为掌握新技术的人。
</p>
<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
未来的竞争，不是人和技术的竞争，而是会用技术的人和不会用技术的人的竞争。
</p>

<blockquote style="border-left: 4px solid #3498db; padding: 10px 15px; margin: 15px 0; background-color: #f8f9fa; color: #666; font-style: italic;">
💡 福利时间：我们整理了《{topic}行业研究报告》，包含详细的数据分析、案例拆解、机会清单，关注公众号回复「报告」即可免费领取。
</blockquote>

<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
<strong style="font-weight: bold;">💬 互动讨论：</strong>你怎么看待{topic}的发展前景？你准备怎么抓住这波机会？欢迎在评论区分享你的想法，我们会挑选3个最有价值的评论，送出价值199元的行业资料包。
</p>

<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">
如果觉得这篇文章对你有帮助，欢迎点赞、在看、转发给身边的朋友，让更多人抓住时代的红利，我们下期再见~
</p>
        """)
        
        # 组合完整文章
        full_content = '\n'.join(article_parts)
        
        print(f'✅ 动态文章生成完成，标题：{title}')
        return title, full_content
    
    def generate_article(self, topic: str, audience: str = "行业从业者") -> tuple:
        """
        完全动态生成公众号文章
        流程：搜索相关资讯 → 动态生成内容 → 格式优化
        """
        # 1. 搜索相关信息
        search_results, search_answer = self.search_related_info(topic)
        
        # 2. 动态生成文章
        title, content = self.generate_dynamic_article(topic, search_results, search_answer)
        
        return title, content

def main():
    # 测试功能
    generator = ContentGenerator()
    # 测试不同主题
    test_topics = ["今日经济热点", "AI大模型应用趋势", "2026创业机会"]
    for topic in test_topics:
        print(f"\n📝 测试主题：{topic}")
        title, content = generator.generate_article(topic)
        print(f'✅ 生成标题：{title}')
        print(f'📝 文章长度：{len(content)} 字节')

if __name__ == "__main__":
    main()
