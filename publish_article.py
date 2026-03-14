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
from scripts.image_processor import ImageProcessor

def main():
    if len(sys.argv) < 2:
        print("使用方式：python publish_article.py \"文章主题\"")
        print("示例：python publish_article.py \"OpenClaw技能开发最佳实践\"")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    print(f'🎯 开始生成文章：{topic}')
    
    # 初始化组件
    generator = ContentGenerator()
    publisher = WeChatPublisher()
    image_processor = ImageProcessor(wechat_publisher=publisher)
    
    # 1. 生成文章内容（纯文本，不含图片）
    title, md_content = generator.generate_article(topic)
    print(f'✅ 内容生成完成，标题：{title}')
    
    # 2. 生成配图
    print('🖼️  正在生成配图...')
    image_paths = image_processor.generate_article_images(topic, count=3)
    
    # 3. 转换为HTML并插入图片（自动上传到微信素材库获取URL）
    print('🔄 正在转换格式并插入配图...')
    html_content = publisher.markdown_to_wechat_html(md_content, image_paths)
    
    # 4. 发布到草稿箱
    print('🚀 正在发布到微信公众号草稿箱...')
    media_id = publisher.publish_draft(title, html_content)
    
    # 清理临时图片
    for img_path in image_paths:
        if os.path.exists(img_path):
            os.remove(img_path)
    
    print(f'🎉 发布成功！')
    print(f'📄 草稿ID：{media_id}')
    print('📝 你可以在微信公众平台的"素材管理"->"草稿箱"中查看这篇文章')

if __name__ == "__main__":
    main()
