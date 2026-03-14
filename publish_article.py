#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键发布公众号文章
使用方式：python publish_article.py "文章主题"
"""

import os
import sys
from scripts.content_generator import ContentGenerator
from scripts.wechat_publisher import WeChatPublisher

def main():
    if len(sys.argv) < 2:
        print("使用方式：python publish_article.py \"文章主题\"")
        print("示例：python publish_article.py \"OpenClaw技能开发最佳实践\"")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    print(f'🎯 开始生成文章：{topic}')
    
    # 生成内容
    generator = ContentGenerator()
    title, content = generator.generate_article(topic)
    print(f'✅ 内容生成完成，标题：{title}')
    
    # 发布到草稿箱
    publisher = WeChatPublisher()
    print('🚀 正在发布到微信公众号草稿箱...')
    media_id = publisher.publish_draft(title, content)
    
    print(f'🎉 发布成功！')
    print(f'📄 草稿ID：{media_id}')
    print('📝 你可以在微信公众平台的"素材管理"->"草稿箱"中查看这篇文章')

if __name__ == "__main__":
    main()
