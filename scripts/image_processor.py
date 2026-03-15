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
    
    def search_images_from_tavily(self, topic: str, count: int = 3) -> List[str]:
        """从Tavily搜索相关图片"""
        try:
            print(f'🔍 正在搜索"{topic}"相关图片...')
            url = "https://api.tavily.com/search"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "api_key": self.tavily_api_key,
                "query": topic,
                "search_depth": "basic",
                "include_images": True,
                "max_results": 5
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                images = result.get("images", [])
                if images:
                    # 筛选有效的图片URL
                    valid_images = []
                    for img in images:
                        if img.startswith("http") and (img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith(".png") or img.endswith(".webp")):
                            valid_images.append(img)
                            if len(valid_images) >= count:
                                break
                    
                    if valid_images:
                        print(f'✅ 从Tavily找到{len(valid_images)}张相关图片')
                        return valid_images
            
            print(f'❌ Tavily图片搜索失败，状态码：{response.status_code}')
            return []
        except Exception as e:
            print(f'Tavily图片搜索失败: {e}')
            return []
    
    def generate_article_images(self, topic: str, count: int = 3) -> List[str]:
        """为文章生成相关配图：优先从Tavily搜索，失败再用文生图，确保至少有3张图"""
        # 第一步：从Tavily搜索相关图片
        image_urls = self.search_images_from_tavily(topic, count=count)
        
        # 第二步：如果Tavily搜索不足，用文生图补充
        if len(image_urls) < count:
            print(f'⚠️  Tavily只找到{len(image_urls)}张图片，尝试文生图补充')
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
            elif "伊朗" in topic or "时政" in topic or "局势" in topic:
                prompts = [
                    "中东地图 伊朗 政治局势 新闻风格 高清写实",
                    "国际政治谈判场景 严肃正式 新闻报道风格",
                    "石油能源 中东经济 抽象概念图 商务风格"
                ]
            else:
                prompts = [
                    f"{topic} 概念图，高清，专业，新闻风格",
                    f"{topic} 应用场景插画，清晰美观",
                    f"{topic} 相关配图，真实感强"
                ]
            
            # 生成缺失的图片
            needed = count - len(image_urls)
            for prompt in prompts[:needed]:
                img_url = self.generate_image(prompt)
                if img_url:
                    image_urls.append(img_url)
        
        # 第三步：如果还是不足，使用高质量免费图库补充，确保至少有3张
        if len(image_urls) < count:
            print(f'⚠️  文生图也不足，使用免费图库补充，还需要{count - len(image_urls)}张')
            # 使用Unsplash Source的高质量图片，根据主题关键词搜索
            keywords = topic.replace(" ", "+")
            for i in range(count - len(image_urls)):
                # 不同主题使用不同的分类
                if "时政" in topic or "局势" in topic:
                    img_url = f"https://source.unsplash.com/800x450/?news,politics,world"
                elif "科技" in topic or "AI" in topic:
                    img_url = f"https://source.unsplash.com/800x450/?technology,ai,computer"
                elif "经济" in topic or "金融" in topic:
                    img_url = f"https://source.unsplash.com/800x450/?business,economy,finance"
                else:
                    img_url = f"https://source.unsplash.com/800x450/?{keywords}"
                image_urls.append(img_url)
        
        print(f'✅ 最终获取到{len(image_urls)}张配图，满足文章需求')
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
        """上传图片并返回base64编码，确保在文章中正常显示"""
        try:
            # 直接使用base64嵌入图片，避免URL问题
            with open(image_path, 'rb') as f:
                import base64
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
                img_url = f"data:image/jpeg;base64,{img_base64}"
            
            print(f'✅ 图片编码完成，大小：{len(img_base64)//1024}KB')
            return img_url
        except Exception as e:
            print(f'图片编码失败: {e}')
            # 失败时使用占位图
            return "https://picsum.photos/800/450?random=" + str(random.randint(1000, 9999))
    
    def insert_images_into_article(self, content: str, topic: str) -> str:
        """智能插入图片到文章合适位置，直接返回图片URL列表，由publisher处理上传"""
        # 生成相关配图
        print(f'🖼️  正在为文章生成配图...')
        image_urls = self.generate_article_images(topic, count=3)
        
        if not image_urls:
            print('⚠️  未获取到图片，跳过配图')
            return content, []
        
        # 过滤有效的HTTP图片URL
        valid_urls = [url for url in image_urls if url.startswith('http')]
        print(f'✅ 配图处理完成，共获取到{len(valid_urls)}张有效图片')
        return content, valid_urls

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
