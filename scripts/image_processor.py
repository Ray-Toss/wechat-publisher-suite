#!/usr/bin/env python3
"""
图片处理模块：搜索、生成、上传图片
"""

import os
import requests
from typing import List, Dict, Any, Optional
import subprocess
import json

class ImageProcessor:
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")

    def search_images(self, keyword: str, count: int = 3) -> List[str]:
        """使用Tavily搜索相关图片"""
        url = "https://api.tavily.com/search"
        payload = {
            "query": keyword,
            "search_depth": "basic",
            "include_images": True,
            "max_results": count
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.tavily_api_key}"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            images = data.get("images", [])
            return [img.get("url") for img in images if img.get("url")]
        except Exception as e:
            print(f"图片搜索失败: {e}")
            return []

    def generate_image(self, prompt: str) -> Optional[str]:
        """使用内置image-generate技能生成图片"""
        try:
            # 调用image-generate技能
            result = subprocess.run(
                ["python", "~/.openclaw/workspace/skills/image-generate/scripts/generate.py", prompt],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                # 解析生成的图片URL
                if output.startswith("http"):
                    return output
            return None
        except Exception as e:
            print(f"图片生成失败: {e}")
            return None

    def get_images(self, topic: str, count: int = 3) -> List[str]:
        """获取图片，优先搜索，搜索不到则生成"""
        # 先搜索图片
        images = self.search_images(topic, count)
        
        # 如果搜索结果不足，生成补充
        if len(images) < count:
            needed = count - len(images)
            for i in range(needed):
                img = self.generate_image(f"{topic} 相关的专业图片，适合技术文章配图，清晰专业，无版权问题")
                if img:
                    images.append(img)
        
        return images[:count]

    def format_image_html(self, image_url: str, alt_text: str = "图片") -> str:
        """格式化为微信公众号兼容的图片HTML"""
        return f'''<p style="text-align: center; margin: 20px 0;">
  <img src="{image_url}" 
       style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);" 
       alt="{alt_text}"/>
</p>'''

if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) == 2:
        processor = ImageProcessor()
        images = processor.get_images(sys.argv[1], 2)
        print("找到图片:", images)
