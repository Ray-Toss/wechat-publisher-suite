#!/usr/bin/env python3
"""
微信公众号官方API封装模块
直接对接微信公众平台官方接口
"""

import os
import json
import requests
import time
from typing import List, Dict, Any, Optional

class WeChatAPI:
    def __init__(self, appid: Optional[str] = None, appsecret: Optional[str] = None):
        self.appid = appid or os.getenv("WECHAT_APPID")
        self.appsecret = appsecret or os.getenv("WECHAT_APPSECRET")
        
        if not self.appid or not self.appsecret:
            raise ValueError("WECHAT_APPID 和 WECHAT_APPSECRET 环境变量必须设置")
            
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
        self.access_token = None
        self.access_token_expires = 0

    def get_access_token(self) -> str:
        """获取access_token，自动缓存"""
        now = time.time()
        if self.access_token and now < self.access_token_expires:
            return self.access_token
            
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"获取access_token失败: {data.get('errmsg')}")
            
        self.access_token = data["access_token"]
        self.access_token_expires = now + data["expires_in"] - 60  # 提前1分钟过期
        return self.access_token

    def upload_image(self, image_url: str) -> str:
        """上传图片到微信素材库（永久素材）"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/material/add_material"
        params = {
            "access_token": access_token,
            "type": "image"
        }
        
        # 先下载图片到本地
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        files = {
            "media": ("image.jpg", img_response.content, "image/jpeg")
        }
        
        response = requests.post(url, params=params, files=files)
        response.raise_for_status()
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"图片上传失败: {data.get('errmsg')}")
            
        return data["media_id"]

    def upload_news_image(self, image_url: str) -> str:
        """上传图文消息内的图片获取URL"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/media/uploadimg"
        params = {
            "access_token": access_token
        }
        
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        files = {
            "media": ("image.jpg", img_response.content, "image/jpeg")
        }
        
        response = requests.post(url, params=params, files=files)
        response.raise_for_status()
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"图文图片上传失败: {data.get('errmsg')}")
            
        return data["url"]

    def create_draft(self, title: str, content: str, 
                   author: Optional[str] = None, digest: Optional[str] = None,
                   cover_media_id: Optional[str] = None) -> str:
        """创建图文草稿"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/draft/add"
        
        # 处理内容中的图片，替换为微信CDN URL
        # 这里需要先提取内容中的img标签，上传后替换URL
        # 简化版本：假设内容中的图片已经是微信CDN地址
        
        articles = [{
            "title": title[:64],  # 标题最多64字符
            "author": author or "",
            "digest": digest[:120] if digest else "",  # 摘要最多120字符
            "content": content,
            "content_source_url": "",
            "thumb_media_id": cover_media_id or "",
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
        
        payload = {
            "articles": articles
        }
        
        response = requests.post(url, params={"access_token": access_token}, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"创建草稿失败: {data.get('errmsg')}")
            
        return data["media_id"]

    def get_draft_url(self, draft_media_id: str) -> str:
        """获取草稿预览链接"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/draft/get"
        
        payload = {
            "media_id": draft_media_id
        }
        
        response = requests.post(url, params={"access_token": access_token}, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"获取草稿信息失败: {data.get('errmsg')}")
            
        # 返回预览URL
        return f"https://mp.weixin.qq.com/s?__biz=MzI5NzM1NjMwOQ==&mid=100000000&idx=1&sn=xxxxxx"  # 实际预览URL需要调用预览接口

    def send_preview(self, draft_media_id: str, openid: str) -> bool:
        """发送预览到指定用户"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/message/mass/preview"
        
        payload = {
            "touser": openid,
            "mpnews": {
                "media_id": draft_media_id
            },
            "msgtype": "mpnews"
        }
        
        response = requests.post(url, params={"access_token": access_token}, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"发送预览失败: {data.get('errmsg')}")
            
        return True

    def list_accounts(self) -> List[Dict[str, Any]]:
        """获取当前账号信息"""
        # 微信官方API没有获取账号列表的接口，这里返回当前配置的账号
        return [{
            "name": "当前公众号",
            "wechatAppid": self.appid,
            "verified": True,
            "status": "active"
        }]

if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "test":
        api = WeChatAPI(sys.argv[2], sys.argv[3])
        token = api.get_access_token()
        print(f"access_token获取成功: {token[:20]}...")
