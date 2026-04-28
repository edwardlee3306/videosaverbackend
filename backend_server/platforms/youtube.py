from .base import BaseParser
class YouTubeParser(BaseParser):
    def __init__(self,platform_key="youtube",platform_name="YouTube"):
        super().__init__(platform_key,platform_name)
    async def parse(self,url):
        try:
            d=await self._parse_with_ytdlp(url);d["watermark"]=False
            t=d.get("title","")
            if t.endswith(" - YouTube"):d["title"]=t[:-10]
            return d
        except Exception as e:raise RuntimeError(f"YouTube解析失败: {e}")
