import re,json,subprocess
from pathlib import Path
from typing import Optional
from abc import ABC,abstractmethod
PLATFORM_PATTERNS=[(r'douyin\.com|iesdouyin\.com','douyin'),(r'tiktok\.com','tiktok'),(r'kuaishou\.com|kwai\.com','kuaishou'),(r'bilibili\.com|b23\.tv','bilibili'),(r'xiaohongshu\.com|xhslink\.com','xiaohongshu'),(r'instagram\.com|ig\.me','instagram'),(r'youtube\.com|youtu\.be','youtube'),(r'twitter\.com|x\.com','twitter'),(r'facebook\.com|fb\.com|fb\.watch','facebook'),(r'weibo\.com','weibo')]
def identify_platform(url):
    for p,k in PLATFORM_PATTERNS:
        if re.search(p,url,re.I):return{"key":k,"name":{"douyin":"抖音","tiktok":"TikTok","kuaishou":"快手","bilibili":"B站","xiaohongshu":"小红书","instagram":"Instagram","youtube":"YouTube","twitter":"Twitter/X","facebook":"Facebook","weibo":"微博"}.get(k,k.capitalize())}
    return None
class BaseParser(ABC):
    def __init__(self,platform_key,platform_name):self.platform_key=platform_key;self.platform_name=platform_name;self._headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36","Accept":"text/html,application/json,*/*","Accept-Language":"zh-CN,zh;q=0.9"}
    async def parse(self,url):return await self._parse_with_ytdlp(url)
    async def _parse_with_ytdlp(self,url):
        try:
            r=subprocess.run(["yt-dlp","--get-url","--format","best[ext=mp4]/best","--no-warnings","--user-agent",self._headers["User-Agent"],url],capture_output=True,text=True,timeout=30)
            vu=(r.stdout.strip().split('\n')[0])if r.returncode==0 else""
            if not vu:
                r=subprocess.run(["yt-dlp","--dump-json","--format","best[ext=mp4]/best","--no-warnings","--user-agent",self._headers["User-Agent"],url],capture_output=True,text=True,timeout=30)
                if r.returncode!=0:raise RuntimeError(r.stderr[:200])
                d=json.loads(r.stdout.strip().split('\n')[0])
                vu=d.get("url","")or self._best_url(d)
            else:
                r2=subprocess.run(["yt-dlp","--dump-json","--no-warnings","--user-agent",self._headers["User-Agent"],url],capture_output=True,text=True,timeout=15)
                d=json.loads(r2.stdout.strip().split('\n')[0])if r2.returncode==0 else{}
            return {"title":d.get("title","")if d else"","video_url":vu,"cover_url":d.get("thumbnail","")or(d.get("thumbnails",[{}])[0].get("url","")if d.get("thumbnails")else""),"duration":d.get("duration",0),"file_size":d.get("filesize",d.get("filesize_approx",0)),"width":d.get("width",0),"height":d.get("height",0),"resolution":d.get("resolution",""),"fps":d.get("fps",30),"ext":"mp4","extractor":"yt-dlp","watermark":"unknown"}
        except subprocess.TimeoutExpired:raise RuntimeError("解析超时")
        except FileNotFoundError:raise RuntimeError("请安装 yt-dlp: pip install yt-dlp")
        except Exception as e:raise RuntimeError(f"解析失败: {e}")
    def _best_url(self,info):
        fmts=info.get("formats",[])
        best=None
        for f in fmts:
            if f.get("vcodec")!="none":
                if best is None or f.get("height",0)>best.get("height",0):best=f
        if best:return best.get("url","")
        for f in fmts:
            if f.get("url"):return f.get("url","")
        return info.get("url","")
