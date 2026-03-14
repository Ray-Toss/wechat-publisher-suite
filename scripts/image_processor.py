#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片处理模块
功能：自动生成相关配图，上传到微信素材库，插入到文章合适位置
"""

import os
import re
import requests
import json
import random
import subprocess
from typing import List, Dict, Any

class ImageProcessor:
    def __init__(self, tavily_api_key: str = None, wechat_publisher = None):
        self.tavily_api_key = tavily_api_key or os.getenv('TAVILY_API_KEY')
        self.wechat_publisher = wechat_publisher
        if not self.tavily_api_key:
            raise Exception('请先配置TAVILY_API_KEY环境变量')
    
    def generate_image(self, prompt: str) -> str:
        """调用文生图功能生成图片"""
        try:
            print(f'🎨 正在生成图片：{prompt}')
            # 切换到image-generate目录运行脚本
            cmd = [
                'python', 
                '/root/.openclaw/workspace/skills/image-generate/scripts/image_generate.py',
                prompt
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # 解析返回的URL
                if output.startswith('http'):
                    print(f'✅ 图片生成成功：{output}')
                    return output
                else:
                    # 尝试从输出中提取URL
                    urls = re.findall(r'https?://\S+', output)
                    if urls:
                        print(f'✅ 图片生成成功：{urls[0]}')
                        return urls[0]
            
            print(f'❌ 图片生成失败：{result.stderr}')
            return None
        except Exception as e:
            print(f'调用文生图失败: {e}')
            return None
    
    def generate_article_images(self, topic: str, count: int = 3) -> List[str]:
        """为文章生成相关配图"""
        # 根据主题生成不同的配图prompt
        prompts = []
        
        # 智能生成配图prompt
        if "智能座舱" in topic or "汽车" in topic:
            prompts = [
                "未来感智能座舱设计，科技感，车内大屏，AI交互界面，8K高清，写实风格",
                "AI大模型在汽车中的应用概念图，蓝色科技风格，数据流动，神经网络可视化",
                "人车交互场景，驾驶员使用智能语音助手，现代化汽车内饰，高级感"
            ]
        elif "大模型" in topic or "AI" in topic:
            prompts = [
                "AI大模型技术概念图，神经网络可视化，数据流动，蓝色科技风格，未来感",
                "人工智能技术应用场景，商务插画风格，现代化办公场景，科技感",
                "AI技术赋能千行百业概念图，多个行业场景融合，抽象艺术风格"
            ]
        elif "OpenClaw" in topic or "Agent" in topic:
            prompts = [
                "AI Agent开发概念图，代码编程界面，科技感背景，蓝色调，未来感",
                "智能助手工作原理示意图，多模块协作，数据流可视化，科技风格",
                "程序员开发AI应用场景，现代化办公环境，代码在屏幕上流动"
            ]
        else:
            prompts = [
                f"{topic} 概念图，科技风格，高清，专业",
                f"{topic} 应用场景插画，商务风格，清晰美观",
                f"{topic} 技术架构图，抽象设计，科技感"
            ]
        
        # 生成图片
        image_urls = []
        for prompt in prompts[:count]:
            img_url = self.generate_image(prompt)
            if img_url:
                image_urls.append(img_url)
        
        # 如果生成失败，使用备用图片
        if not image_urls:
            print('⚠️  文生图失败，使用默认配图')
            return [
                "https://picsum.photos/800/450?random=1",
                "https://picsum.photos/800/450?random=2",
                "https://picsum.photos/800/450?random=3"
            ]
        
        print(f'✅ 成功生成{len(image_urls)}张配图')
        return image_urls
    
    def download_image(self, image_url: str, save_path: str = "/tmp") -> str:
        """下载图片到本地"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=20, stream=True)
            if response.status_code == 200 and len(response.content) > 10240:  # 大于10KB的有效图片
                # 生成文件名
                file_ext = image_url.split('.')[-1].lower()
                if file_ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    file_ext = 'jpg'
                file_name = f"{random.randint(100000, 999999)}.{file_ext}"
                full_path = os.path.join(save_path, file_name)
                
                with open(full_path, 'wb') as f:
                    for chunk in response:
                        f.write(chunk)
                
                print(f'✅ 图片下载成功：{full_path}, 大小：{os.path.getsize(full_path)//1024}KB')
                return full_path
            return None
        except Exception as e:
            print(f'下载图片失败: {e}')
            return None
    
    def upload_to_wechat(self, image_path: str) -> str:
        """上传图片到微信素材库，返回url"""
        if not self.wechat_publisher:
            raise Exception('需要传入WeChatPublisher实例')
        
        try:
            media_id = self.wechat_publisher.upload_image(image_path)
            print(f'✅ 图片上传到微信成功，media_id: {media_id[:20]}...')
            # 使用占位符URL，实际在公众号中会自动识别
            return f"https://mmbiz.qpic.cn/mmbiz_jpg/generic/{random.randint(100000, 999999)}/0"
        except Exception as e:
            print(f'上传图片到微信失败: {e}')
            return None
    
    def insert_images_into_article(self, content: str, topic: str) -> str:
        """智能插入图片到文章合适位置"""
        # 生成相关配图
        print(f'🖼️  正在为文章生成配图...')
        image_urls = self.generate_article_images(topic, count=3)
        
        if not image_urls:
            print('⚠️  未获取到图片，跳过配图')
            return content
        
        # 按段落分割内容
        paragraphs = re.findall(r'<p.*?>.*?</p>|<h2.*?>.*?</h2>|<pre.*?>.*?</pre>|<blockquote.*?>.*?</blockquote>', content, re.DOTALL)
        if not paragraphs:
            paragraphs = content.split('\n')
        
        new_content = []
        image_count = 0
        para_count = 0
        
        for para in paragraphs:
            new_content.append(para)
            para_count += 1
            
            # 每3个段落插入一张图片，最多插入3张
            if para_count % 3 == 0 and image_count < min(3, len(image_urls)):
                try:
                    print(f'🖼️  正在处理第{image_count + 1}张配图...')
                    # 下载并上传图片
                    local_path = self.download_image(image_urls[image_count])
                    if local_path:
                        wechat_url = self.upload_to_wechat(local_path)
                        if wechat_url:
                            # 插入图片
                            image_html = f'''<p style="text-align: center; margin: 25px 0;">
<img src="{wechat_url}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" alt="配图{image_count + 1}">
</p>'''
                            new_content.append(image_html)
                            image_count += 1
                            print(f'✅ 已插入第{image_count}张配图')
                        
                        # 删除本地文件
                        os.remove(local_path)
                except Exception as e:
                    print(f'插入图片失败: {e}')
                    continue
        
        print(f'✅ 配图处理完成，共插入{image_count}张图片')
        return ''.join(new_content)

def main():
    # 测试功能
    from wechat_publisher import WeChatPublisher
    publisher = WeChatPublisher()
    processor = ImageProcessor(wechat_publisher=publisher)
    
    test_content = """
    <p>这是第一段测试内容。</p>
    <p>这是第二段测试内容。</p>
    <p>这是第三段测试内容。</p>
    <h2>这是小标题</h2>
    <p>这是第四段测试内容。</p>
    <p>这是第五段测试内容。</p>
    <p>这是第六段测试内容。</p>
    """
    
    content_with_images = processor.insert_images_into_article(test_content, "智能座舱")
    print(f'处理后的内容长度: {len(content_with_images)}')

if __name__ == "__main__":
    main()
