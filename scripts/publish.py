#!/usr/bin/env python3
"""
主入口脚本：一键发布公众号文章
"""

import os
import argparse
import sys
from typing import Optional
from content_generator import ContentGenerator
from format_converter import FormatConverter
from image_processor import ImageProcessor
from wechat_api import WeChatAPI

def main():
    parser = argparse.ArgumentParser(description='微信公众号一键发布工具')
    parser.add_argument('--topic', type=str, help='文章主题，不指定则自动搜索热点')
    parser.add_argument('--type', type=str, choices=['tech', 'hot', 'auto'], default='auto', help='文章类型')
    parser.add_argument('--output', type=str, help='文章保存路径，不指定则直接发布')
    parser.add_argument('--images', type=int, default=3, help='配图数量')
    parser.add_argument('--appid', type=str, help='指定公众号APPID')
    parser.add_argument('--draft', action='store_true', default=True, help='仅保存到草稿')
    
    args = parser.parse_args()
    
    # 检查环境变量
    required_env = ['TAVILY_API_KEY', 'WECHAT_API_KEY']
    missing = [env for env in required_env if not os.getenv(env)]
    if missing:
        print(f"错误：缺少必要的环境变量: {', '.join(missing)}")
        print("请先配置以下环境变量：")
        print("export TAVILY_API_KEY='your-tavily-api-key'")
        print("export WECHAT_API_KEY='your-wechat-api-key'")
        sys.exit(1)
    
    try:
        # 步骤1：生成内容
        print("🔍 正在搜索信息并生成内容...")
        content_generator = ContentGenerator()
        
        if not args.topic:
            # 自动搜索热点
            print("📰 未指定主题，正在搜索最新热点...")
            hot_topics = content_generator.search_information("最新科技热点 2026", 5)
            if hot_topics:
                args.topic = hot_topics[0].get('title', '科技热点分析')
                print(f"✅ 自动选择热点主题: {args.topic}")
            else:
                print("❌ 无法获取热点，请指定--topic参数")
                sys.exit(1)
        
        article = content_generator.generate_article(args.topic, args.type)
        print(f"✅ 内容生成完成，标题: {article['title']}")
        print(f"📝 文章类型: {article['type']}, 长度: {len(article['content'])} 字")
        
        # 步骤2：获取图片
        print("🖼️  正在搜索相关图片...")
        image_processor = ImageProcessor()
        images = image_processor.get_images(args.topic, args.images)
        print(f"✅ 找到 {len(images)} 张图片")
        
        # 步骤3：格式转换
        print("🎨 正在转换为公众号格式...")
        converter = FormatConverter()
        markdown_content = article['content']
        html_content = converter.markdown_to_html(markdown_content)
        final_html = converter.optimize_for_wechat(html_content, article['title'], images)
        summary = converter.generate_summary(final_html)
        print(f"✅ 格式转换完成")
        
        # 步骤4：保存到文件（如果指定output）
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_html)
            print(f"💾 文章已保存到: {args.output}")
            
            # 同时保存元数据
            meta_file = args.output + '.meta.json'
            meta = {
                "title": article['title'],
                "summary": summary,
                "topic": args.topic,
                "type": article['type'],
                "images": images
            }
            with open(meta_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(meta, f, ensure_ascii=False, indent=2)
            print(f"💾 元数据已保存到: {meta_file}")
            
            if not args.appid:
                # 仅保存不发布
                print("🎉 任务完成！文章已生成，如需发布请指定--appid参数")
                return
        
        # 步骤5：发布到公众号
        print("🚀 正在发布到公众号草稿箱...")
        wechat_api = WeChatAPI()
        
        # 获取账号列表
        accounts = wechat_api.list_accounts()
        if not accounts:
            print("❌ 没有找到已授权的公众号账号，请先在wx.limyai.com授权")
            sys.exit(1)
        
        # 选择账号
        if args.appid:
            selected_account = next((acc for acc in accounts if acc['wechatAppid'] == args.appid), None)
            if not selected_account:
                print(f"❌ 未找到APPID为 {args.appid} 的账号")
                print(f"可用账号: {[acc['name'] + '(' + acc['wechatAppid'] + ')' for acc in accounts]}")
                sys.exit(1)
        else:
            selected_account = accounts[0]
            print(f"ℹ️  自动选择账号: {selected_account['name']} ({selected_account['wechatAppid']})")
        
        # 上传图片到微信素材库
        print("📤 正在上传图片到微信素材库...")
        cover_media_id = None
        if images:
            try:
                cover_media_id = wechat_api.upload_image(selected_account['wechatAppid'], images[0])
                print(f"✅ 封面图上传成功，media_id: {cover_media_id}")
            except Exception as e:
                print(f"⚠️  封面图上传失败: {e}，将使用默认封面")
        
        # 发布文章
        result = wechat_api.publish_article(
            appid=selected_account['wechatAppid'],
            title=article['title'],
            content=final_html,
            summary=summary,
            cover_media_id=cover_media_id,
            article_type="news"
        )
        
        draft_url = wechat_api.get_draft_url(result['publicationId'])
        print(f"🎉 发布成功！草稿已创建")
        print(f"📄 文章标题: {article['title']}")
        print(f"🔗 预览链接: {draft_url}")
        print(f"💡 请登录微信公众平台预览并发布")
        
    except KeyboardInterrupt:
        print("\n⚠️  操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
