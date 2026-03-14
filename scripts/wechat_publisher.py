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
        response.encoding = 'utf-8'
        result = response.json()
        if 'access_token' not in result:
            raise Exception(f'获取access_token失败: {result}')
        return result['access_token']
    
    def upload_image(self, image_path: str) -> str:
        """上传图片到微信素材库，返回media_id"""
        url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image'
        files = {'media': open(image_path, 'rb')}
        data = {'description': json.dumps({'title': '图片', 'introduction': '文章图片'}, ensure_ascii=False)}
        response = requests.post(url, files=files, data=data, timeout=30)
        response.encoding = 'utf-8'
        result = response.json()
        if 'media_id' not in result:
            raise Exception(f'上传图片失败: {result}')
        return result['media_id']
    
    def get_default_thumb_media_id(self) -> str:
        """获取默认的封面图media_id"""
        url = f'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={self.access_token}'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {"type": "image", "offset": 0, "count": 1}
        response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), timeout=10)
        response.encoding = 'utf-8'
        result = response.json()
        if result.get('item'):
            return result['item'][0]['media_id']
        raise Exception('素材库中没有图片，请先上传至少一张图片作为封面')
    
    def markdown_to_wechat_html(self, markdown_content: str) -> str:
        """将Markdown转换为微信公众号兼容的HTML格式"""
        html_lines = []
        
        # 处理代码块
        in_code_block = False
        code_lines = []
        code_lang = ""
        
        lines = markdown_content.split('\n')
        for line in lines:
            # 处理代码块边界
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_lang = line[3:].strip()
                    code_lines = []
                else:
                    in_code_block = False
                    # 格式化代码块
                    code_content = '<br>'.join([line.replace(' ', '&nbsp;') for line in code_lines])
                    html_lines.append(f'<pre style="background-color: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; font-family: Consolas, monospace; font-size: 14px; line-height: 1.6;">{code_content}</pre>')
                continue
                
            if in_code_block:
                code_lines.append(line)
                continue
                
            if not line.strip():
                continue
                
            # 处理标题
            if line.startswith('# '):
                html_lines.append(f'<h1 style="font-size: 24px; font-weight: bold; color: #333; margin: 30px 0 15px 0; text-align: center;">{line[2:].strip()}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2 style="font-size: 20px; font-weight: bold; color: #2c3e50; margin: 25px 0 12px 0; padding-bottom: 5px; border-bottom: 2px solid #3498db;">{line[3:].strip()}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3 style="font-size: 17px; font-weight: bold; color: #34495e; margin: 20px 0 10px 0;">{line[4:].strip()}</h3>')
            # 处理无序列表
            elif line.startswith('- '):
                content = line[2:].strip()
                # 处理行内格式
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight: bold;">\1</strong>', content)
                content = re.sub(r'`(.*?)`', r'<code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 13px; color: #e74c3c;">\1</code>', content)
                html_lines.append(f'<p style="margin: 8px 0 8px 20px; text-indent: -1em;">•&nbsp;&nbsp;{content}</p>')
            # 处理有序列表
            elif re.match(r'^(\d+)\. ', line):
                match = re.match(r'^(\d+)\. (.*)$', line)
                if match:
                    num = match.group(1)
                    content = match.group(2).strip()
                    # 处理行内格式
                    content = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight: bold;">\1</strong>', content)
                    content = re.sub(r'`(.*?)`', r'<code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 13px; color: #e74c3c;">\1</code>', content)
                    html_lines.append(f'<p style="margin: 8px 0 8px 20px; text-indent: -1.5em;">{num}.&nbsp;&nbsp;{content}</p>')
            # 处理引用
            elif line.startswith('> '):
                content = line[2:].strip()
                html_lines.append(f'<blockquote style="border-left: 4px solid #3498db; padding: 10px 15px; margin: 15px 0; background-color: #f8f9fa; color: #666; font-style: italic;">{content}</blockquote>')
            # 处理普通段落
            else:
                # 处理行内格式
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong style="font-weight: bold;">\1</strong>', line)
                line = re.sub(r'`(.*?)`', r'<code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 13px; color: #e74c3c;">\1</code>', line)
                line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #3498db; text-decoration: none;">\1</a>', line)
                html_lines.append(f'<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-align: justify;">{line}</p>')
        
        # 合并内容，确保没有Unicode转义
        html = '\n'.join(html_lines)
        return html
    
    def publish_draft(self, title: str, content: str, thumb_media_id: str = "") -> str:
        """发布文章到草稿箱，返回media_id"""
        # 标题最多64字
        title = title[:64] if len(title) > 64 else title
        
        # 如果没有提供封面图，使用默认的第一张图片
        if not thumb_media_id:
            thumb_media_id = self.get_default_thumb_media_id()
        
        url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            "articles": [
                {
                    "title": title,
                    "content": content,
                    "thumb_media_id": thumb_media_id
                }
            ]
        }
        # 关键：使用ensure_ascii=False确保中文不被转义，然后编码为utf-8
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        response = requests.post(url, headers=headers, data=json_data, timeout=30)
        response.encoding = 'utf-8'
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
    print(f'HTML预览: {html_content[:300]}...')
    
    print('🚀 正在发布到草稿箱...')
    media_id = publisher.publish_draft(
        title="OpenClaw技能开发最佳实践",
        content=html_content
    )
    
    print(f'🎉 发布成功！草稿ID: {media_id}')
    print('📝 你可以在微信公众平台的"素材管理"->"草稿箱"中查看这篇文章')

if __name__ == "__main__":
    main()
