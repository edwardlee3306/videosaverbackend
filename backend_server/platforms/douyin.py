import re,json
import httpx
from .base import BaseParser
class DouyinParser(BaseParser):
    def __init__(self,platform_key="douyin",platform_name="抖音"):
        super().__init__(platform_key,platform_name)
        self._h={"User-Agent":"Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36","Referer":"https://www.douyin.com/"}
    async def parse(self,url):
        try:
            vid=None
            if "v.douyin.com"in url:
                async with httpx.AsyncClient(headers=self._h,follow_redirects=True,timeout=10)as c:r=await c.get(url);url=str(r.url)
            m=re.search(r'douyin\.com/video/(\d+)',url)
            if m:vid=m.group(1)
            if vid:
                async with httpx.AsyncClient(headers=self._h,timeout=15)as c:
                    r=await c.get(f"https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id={vid}")
                    if r.status_code==200:
                        d=r.json().get("aweme_detail",{})
                        if d:
                            v=d.get("video",{});u=(v.get("play_addr",{}).get("url_list",[""])[0]).replace("playwm","play")or v.get("play","")or ""
                            cv=(v.get("cover",{}).get("url_list",[""])[0])or(v.get("origin_cover",{}).get("url_list",[""])[0])or ""
                            du=d.get("duration",0)/1000;w=v.get("width",0);ht=v.get("height",0);br=v.get("bit_rate",[{}])[0].get("bit_rate",0)if v.get("bit_rate")else 0
                            fs=int(br*du/8)if(br and du)else 0;res=f"{w}x{ht}"if(w and ht)else"1080x1920"
                            return{"title":d.get("desc",""),"video_url":u,"cover_url":cv,"duration":int(du),"file_size":fs,"width":w,"height":ht,"resolution":res,"fps":v.get("fps",30),"ext":"mp4","extractor":"douyin_api","watermark":False}
            return await self._parse_with_ytdlp(url)
        except Exception:
            return await self._parse_with_ytdlp(url)
