from .base import BaseParser
class InstagramParser(BaseParser):
    def __init__(self,platform_key="instagram",platform_name="Instagram"):
        super().__init__(platform_key,platform_name)
    async def parse(self,url):
        try:
            d=await self._parse_with_ytdlp(url);d["watermark"]=False;return d
        except Exception as e:raise RuntimeError(f"Instagram解析失败: {e}")
