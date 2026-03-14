#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号发布工具
功能：将Markdown文章转换为微信兼容的HTML格式并发布到草稿箱
"""

import os
import re
import requests
import json
from typing import List, Dict, Any

class WeChatPublisher:
    def __init__(self):
        self.appid = os.getenv('WECHAT_APPID')
        self.appsecret = os.getenv('WECHAT_APPSECRET')
        if not self.appid or not self.appsecret:
            raise Exception('请先配置WECHAT_APPID和WECHAT_APPSECRET环境变量')
        self.access_token = self._get_access_token()
        
    def _get_access_token(self) -> str:
        """获取access_token"""
        url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}'
        response = requests.get(url, timeout=10)
        result = response.json()
        if 'access_token' not in result:
            raise Exception(f'获取access_token失败: {result}')
        return result['access_token']
    
    def upload_image(self, image_path: str) -> str:
        """上传图片到微信素材库，返回media_id"""
        url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image'
        files = {'media': open(image_path, 'rb')}
        data = {'description': json.dumps({'title': '图片', 'introduction': '文章图片'})}
        response = requests.post(url, files=files, data=data, timeout=30)
        result = response.json()
        if 'media_id' not in result:
            raise Exception(f'上传图片失败: {result}')
        return result['media_id']
    
    def get_default_thumb_media_id(self) -> str:
        """获取默认的封面图media_id"""
        url = f'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={self.access_token}'
        data = {"type": "image", "offset": 0, "count": 1}
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        if result.get('item'):
            return result['item'][0]['media_id']
        raise Exception('素材库中没有图片，请先上传至少一张图片作为封面')
    
    def markdown_to_wechat_html(self, markdown_content: str) -> str:
        """将Markdown转换为微信公众号兼容的HTML格式"""
        # 处理代码块
        def replace_code_block(match):
            code = match.group(1).strip()
            code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            code = code.replace('\n', '<br>')
            return f'<pre><code>{code}</code></pre>'
        
        html = re.sub(r'```([\s\S]*?)```', replace_code_block, markdown_content)
        
        # 处理标题
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 处理行内代码
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # 处理链接
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        
        # 处理列表
        html = re.sub(r'^- (.*?)$', r'<p>• \1</p>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.*?)$', r'<p>\1. \2</p>', html, flags=re.MULTILINE)
        
        # 处理引用
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # 处理普通段落
        lines = html.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 已经是HTML标签的直接保留
            if line.startswith(('<h', '<p', '<pre', '<code', '<blockquote', '<strong', '<em', '<a')):
                processed_lines.append(line)
            else:
                processed_lines.append(f'<p>{line}</p>')
        
        html = '\n'.join(processed_lines)
        return html
    
    def publish_draft(self, title: str, content: str, thumb_media_id: str = "") -> str:
        """发布文章到草稿箱，返回media_id"""
        # 标题最多64字
        title = title[:64] if len(title) > 64 else title
        
        # 如果没有提供封面图，使用默认的第一张图片
        if not thumb_media_id:
            thumb_media_id = self.get_default_thumb_media_id()
        
        url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}'
        data = {
            "articles": [
                {
                    "title": title,
                    "content": content,
                    "thumb_media_id": thumb_media_id
                }
            ]
        }
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        if 'media_id' not in result:
            raise Exception(f'发布草稿失败: {result}')
        return result['media_id']

def main():
    # 测试功能
    publisher = WeChatPublisher()
    
    test_md = """# OpenClaw技能开发最佳实践

随着AI Agent技术的快速发展，OpenClaw作为开源的Agent运行框架，成为众多开发者构建智能助手的首选平台。

## 核心特性
- **完全开源**：所有代码开源，可自由定制
- **扩展性强**：通过Skill系统可以无限扩展功能
- **安全可靠**：内置多重安全机制，保障运行安全

## 最佳实践
1. 单一职责：每个Skill只做一件事
2. 无状态设计：避免在Skill中保存状态
3. 容错处理：优雅处理各种异常情况

### 代码示例
```python
def handle_request(params, context):
    # 业务逻辑处理
    return {"result": "success"}
```

> 本文由OpenClaw自动生成
"""
    
    print('🔄 正在转换Markdown到微信HTML格式...')
    html_content = publisher.markdown_to_wechat_html(test_md)
    print(f'✅ 转换完成，HTML长度: {len(html_content)}')
    
    print('🚀 正在发布到草稿箱...')
    media_id = publisher.publish_draft(
        title="OpenClaw技能开发最佳实践",
        content=html_content
    )
    
    print(f'🎉 发布成功！草稿ID: {media_id}')
    print('📝 你可以在微信公众平台的"素材管理"->"草稿箱"中查看这篇文章')

if __name__ == "__main__":
    main()
