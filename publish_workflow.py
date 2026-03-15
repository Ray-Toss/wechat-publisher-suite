#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号发布工作流
完全按照要求实现：搜索素材 → AI创作 → 生成配图 → 格式转换 → 发布草稿
"""

import os
import sys
from scripts.content_generator import ContentGenerator
from scripts.image_processor import ImageProcessor
from scripts.wechat_publisher import WeChatPublisher

def main():
    if len(sys.argv) < 2:
        print("使用方式：python publish_workflow.py \"文章主题\"")
        print("示例：python publish_workflow.py \"2026年AI大模型发展趋势\"")
        sys.exit(1)
    
    topic = sys.argv[1]
    print(f'🎯 启动公众号发布工作流：{topic}')
    
    # 初始化组件
    print('⚙️  初始化工作流组件...')
    generator = ContentGenerator()
    publisher = WeChatPublisher()
    image_processor = ImageProcessor(wechat_publisher=publisher)
    
    # 步骤1：搜索相关素材
    print('\n📚 步骤1/5：搜索相关素材')
    references, answer = generator.search_related_info(topic, max_results=8)
    if not references:
        print('❌ 未找到相关素材，请调整关键词重试')
        sys.exit(1)
    
    # 步骤2：AI创作原创文章
    print('\n✍️  步骤2/5：AI原创写作')
    title, md_content = generator.generate_article_content(topic, references, answer)
    print(f'✅ 文章创作完成，标题：{title}')
    print(f'✅ 文章字数：{len(md_content)} 字')
    
    # 步骤3：生成相关配图
    print('\n🖼️  步骤3/5：生成文章配图')
    image_urls = image_processor.generate_article_images(topic, count=3)
    print(f'✅ 获取到{len(image_urls)}张配图')
    
    # 步骤4：转换为微信公众号HTML格式
    print('\n🎨 步骤4/5：转换为公众号格式')
    html_content = publisher.markdown_to_wechat_html(md_content, [])
    
    # 手动插入图片到合适位置
    print('🔧 正在插入配图...')
    paragraphs = html_content.split('</p>')
    new_paragraphs = []
    img_idx = 0
    
    for i, para in enumerate(paragraphs):
        new_paragraphs.append(para + '</p>')
        # 每3个段落插入一张图片
        if (i + 1) % 3 == 0 and img_idx < len(image_urls) and img_idx < 3:
            img_url = image_urls[img_idx]
            img_html = f'''<p style="text-align: center; margin: 25px 0;">
<img src="{img_url}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
</p>'''
            new_paragraphs.append(img_html)
            img_idx += 1
            print(f'✅ 已插入第{img_idx}张配图')
    
    final_html = ''.join(new_paragraphs)
    print(f'✅ 格式转换完成，HTML大小：{len(final_html)} 字节')
    
    # 步骤5：发布到公众号草稿箱
    print('\n🚀 步骤5/5：发布到草稿箱')
    try:
        media_id = publisher.publish_draft(title, final_html)
        print(f'🎉 发布成功！')
        print(f'📄 草稿ID：{media_id}')
        print('📝 请登录微信公众平台，在"素材管理"->"草稿箱"中查看和发布')
    except Exception as e:
        print(f'❌ 发布失败：{e}')
        print('💡 建议：如果是内容审核问题，请手动调整敏感表述后再发布')
        # 保存生成的内容到本地，方便手动修改
        with open(f'/tmp/{title}.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
        with open(f'/tmp/{title}.html', 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f'💡 内容已保存到本地：/tmp/{title}.md 和 /tmp/{title}.html')
        sys.exit(1)

if __name__ == "__main__":
    main()
