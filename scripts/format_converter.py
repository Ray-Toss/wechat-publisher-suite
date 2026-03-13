#!/usr/bin/env python3
"""
格式转换模块：将内容转换为微信公众号兼容的HTML格式
"""

import re
from typing import Dict, Any, List

class FormatConverter:
    def __init__(self):
        self.styles = {
            "h1": "font-size: 22px; font-weight: bold; color: #333; margin: 30px 0 20px 0; text-align: center;",
            "h2": "font-size: 18px; font-weight: bold; color: #2c3e50; margin: 25px 0 15px 0; padding-left: 10px; border-left: 4px solid #3498db;",
            "h3": "font-size: 17px; font-weight: bold; color: #34495e; margin: 20px 0 10px 0;",
            "p": "font-size: 16px; line-height: 1.8; color: #333; margin: 15px 0; text-indent: 2em;",
            "blockquote": "background: #f8f9fa; border-left: 4px solid #ccc; padding: 15px; margin: 20px 0; color: #666; font-style: italic;",
            "hr": "border: none; border-top: 1px solid #eee; margin: 30px 0;",
            "strong": "font-weight: bold; color: #e74c3c;",
            "ul": "margin: 15px 0; padding-left: 2em;",
            "li": "font-size: 16px; line-height: 1.8; color: #333; margin: 8px 0;",
            "code": "background: #f7f7f7; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 14px;",
            "pre": "background: #282c34; color: #abb2bf; padding: 20px; border-radius: 8px; overflow-x: auto; margin: 20px 0;",
            "pre code": "background: none; padding: 0; color: inherit;"
        }

    def markdown_to_html(self, markdown: str) -> str:
        """将Markdown转换为微信公众号兼容的HTML"""
        html = markdown
        
        # 处理代码块
        html = re.sub(r'```([\s\S]*?)```', 
                     lambda m: f'<pre style="{self.styles["pre"]}"><code style="{self.styles["pre code"]}">{m.group(1).strip()}</code></pre>', 
                     html)
        
        # 处理行内代码
        html = re.sub(r'`([^`]+)`', 
                     lambda m: f'<code style="{self.styles["code"]}">{m.group(1)}</code>', 
                     html)
        
        # 处理标题
        html = re.sub(r'^# (.+)$', 
                     lambda m: f'<h1 style="{self.styles["h1"]}">{m.group(1)}</h1>', 
                     html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', 
                     lambda m: f'<h2 style="{self.styles["h2"]}">{m.group(1)}</h2>', 
                     html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', 
                     lambda m: f'<h3 style="{self.styles["h3"]}">{m.group(1)}</h3>', 
                     html, flags=re.MULTILINE)
        
        # 处理粗体
        html = re.sub(r'\*\*(.+?)\*\*', 
                     lambda m: f'<strong style="{self.styles["strong"]}">{m.group(1)}</strong>', 
                     html)
        
        # 处理斜体
        html = re.sub(r'\*(.+?)\*', 
                     lambda m: f'<em>{m.group(1)}</em>', 
                     html)
        
        # 处理引用
        html = re.sub(r'^> (.+)$', 
                     lambda m: f'<blockquote style="{self.styles["blockquote"]}">{m.group(1)}</blockquote>', 
                     html, flags=re.MULTILINE)
        
        # 处理无序列表
        html = re.sub(r'^- (.+)$', 
                     lambda m: f'<ul style="{self.styles["ul"]}"><li style="{self.styles["li"]}">{m.group(1)}</li></ul>', 
                     html, flags=re.MULTILINE)
        # 合并相邻的li
        html = re.sub(r'</ul>\s*<ul style="[^"]*">', '', html)
        
        # 处理有序列表
        html = re.sub(r'^\d+\. (.+)$', 
                     lambda m: f'<ol style="{self.styles["ul"]}"><li style="{self.styles["li"]}">{m.group(1)}</li></ol>', 
                     html, flags=re.MULTILINE)
        html = re.sub(r'</ol>\s*<ol style="[^"]*">', '', html)
        
        # 处理分隔线
        html = re.sub(r'^---$', 
                     f'<hr style="{self.styles["hr"]}">', 
                     html, flags=re.MULTILINE)
        
        # 处理段落（剩余的行）
        lines = html.split('\n')
        processed_lines = []
        in_block = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                processed_lines.append('')
                continue
                
            # 检查是否在块级元素中
            if (stripped.startswith('<h') or stripped.startswith('<p') or stripped.startswith('<blockquote') or 
                stripped.startswith('<pre') or stripped.startswith('<ul') or stripped.startswith('<ol') or 
                stripped.startswith('<hr') or stripped.startswith('</')):
                processed_lines.append(line)
                continue
                
            # 普通段落
            processed_lines.append(f'<p style="{self.styles["p"]}">{line}</p>')
        
        html = '\n'.join(processed_lines)
        
        # 清理多余的空行
        html = re.sub(r'\n\s*\n', '\n', html)
        
        return html

    def optimize_for_wechat(self, html: str, title: str, images: List[str] = None) -> str:
        """优化HTML为微信公众号格式"""
        # 添加标题
        full_html = f'<h1 style="{self.styles["h1"]}">{title}</h1>\n'
        
        # 添加开头导语
        full_html += f'<p style="{self.styles["p"]}">本文由AI助手自动生成，全文约{len(html) // 3}字，阅读需要{max(3, len(html) // 1000)}分钟。</p>\n'
        full_html += f'<hr style="{self.styles["hr"]}">\n'
        
        # 添加正文
        full_html += html
        
        # 插入图片（每800字插入一张）
        if images:
            paragraphs = re.split(r'(</p>|<h2|<h3|<hr)', full_html)
            char_count = 0
            image_index = 0
            new_content = []
            
            for part in paragraphs:
                new_content.append(part)
                char_count += len(part)
                
                if char_count > 800 and image_index < len(images) and part.endswith('</p>'):
                    # 插入图片
                    img_html = f'''<p style="text-align: center; margin: 20px 0;">
  <img src="{images[image_index]}" 
       style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);" 
       alt="配图{image_index + 1}"/>
</p>'''
                    new_content.append(img_html)
                    char_count = 0
                    image_index += 1
            
            full_html = ''.join(new_content)
        
        # 添加结尾
        full_html += f'\n<hr style="{self.styles["hr"]}">\n'
        full_html += f'<p style="{self.styles["p"]}"><strong style="{self.styles["strong"]}">写在最后</strong></p>\n'
        full_html += f'<p style="{self.styles["p"]}">如果这篇文章对你有帮助，欢迎转发给需要的朋友，也欢迎在评论区交流你的看法。</p>\n'
        full_html += f'<p style="{self.styles["p"]}">关注我，获取更多有深度的技术干货。</p>\n'
        
        return full_html

    def generate_summary(self, content: str, max_length: int = 120) -> str:
        """生成文章摘要"""
        # 提取前几段文本
        text = re.sub(r'<[^>]+>', '', content)
        text = re.sub(r'\s+', ' ', text).strip()
        summary = text[:max_length]
        if len(text) > max_length:
            summary += '...'
        return summary

if __name__ == "__main__":
    # 测试代码
    converter = FormatConverter()
    test_md = """# 测试文章

这是一篇测试文章。

## 第一个章节

**加粗文本**和*斜体文本*。

> 这是引用内容

- 列表项1
- 列表项2
- 列表项3

```python
print("Hello World")
```

---

这是第二段内容。
"""
    html = converter.markdown_to_html(test_md)
    print(html)
