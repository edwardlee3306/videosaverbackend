from .base import BaseParser
class FacebookParser(BaseParser):
    def __init__(self,platform_key="facebook",platform_name="Facebook"):
        super().__init__(platform_key,platform_name)
    async def parse(self,url):
        try:
            d=await self._parse_with_ytdlp(url);d["watermark"]=False;return d
        except Exception as e:raise RuntimeError(f"Facebook解析失败: {e}")
