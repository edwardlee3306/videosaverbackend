import re,json
import httpx
from .base import BaseParser
class BilibiliParser(BaseParser):
    def __init__(self,platform_key="bilibili",platform_name="B站"):
        super().__init__(platform_key,platform_name)
        self._h={"User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36","Referer":"https://www.bilibili.com/"}
    async def parse(self,url):
        try:
            if "b23.tv"in url:
                async with httpx.AsyncClient(headers=self._h,follow_redirects=True,timeout=10)as c:url=str((await c.get(url)).url)
            m=re.search(r'(BV[a-zA-Z0-9]{10,12})',url)or re.search(r'av(\d+)',url,re.I)
            if not m:return await self._parse_with_ytdlp(url)
            vid=m.group(1)
            async with httpx.AsyncClient(headers=self._h,timeout=15)as c:
                r=await c.get(f"https://api.bilibili.com/x/web-interface/view?bvid={vid}")
                data=r.json()
                if data.get("code")!=0:return await self._parse_with_ytdlp(url)
                vi=data["data"];title=vi.get("title","");cv=vi.get("pic","");du=vi.get("duration",0);dm=vi.get("dimension",{});w=dm.get("width",0);ht=dm.get("height",0)
                vu=""
                for qn in[116,112,80,74,64]:
                    r2=await c.get(f"https://api.bilibili.com/x/player/playurl?bvid={vid}&qn={qn}")
                    d2=r2.json()
                    if d2.get("code")==0and d2.get("data",{}).get("durl"):vu=d2["data"]["durl"][0].get("url","")or d2["data"]["durl"][0].get("backup_url",[""])[0];break
                if not vu:return await self._parse_with_ytdlp(url)
                return{"title":title,"video_url":vu,"cover_url":cv,"duration":du,"file_size":0,"width":w,"height":ht,"resolution":f"{w}x{ht}"if w and ht else"","fps":30,"ext":"mp4","extractor":"bilibili_api","watermark":False}
        except Exception as e:
            return await self._parse_with_ytdlp(url)
