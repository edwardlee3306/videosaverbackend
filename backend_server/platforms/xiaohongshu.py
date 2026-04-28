from .base import BaseParser
class XiaohongshuParser(BaseParser):
    def __init__(self,platform_key="xiaohongshu",platform_name="小红书"):
        super().__init__(platform_key,platform_name)
    async def parse(self,url):
        try:
            d=await self._parse_with_ytdlp(url);d["watermark"]=False;return d
        except Exception as e:raise RuntimeError(f"小红书解析失败: {e}")
