import re
import httpx
from .base import BaseParser

class TikTokParser(BaseParser):
    def __init__(self, platform_key="tiktok", platform_name="TikTok"):
        super().__init__(platform_key, platform_name)
        self._h = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def parse(self, url):
        try:
            vid = None
            m = re.search(r'tiktok\.com/@[\w.-]+/video/(\d+)', url)
            if m:
                vid = m.group(1)
            if not vid:
                m = re.search(r'tiktok\.com/(?:t/|v/)?(\d+)', url)
                if m:
                    vid = m.group(1)

            if vid:
                try:
                    async with httpx.AsyncClient(headers=self._h, timeout=15) as c:
                        r = await c.get(f"https://www.tikwm.com/api/?url=https://www.tiktok.com/@i/video/{vid}")
                        if r.status_code == 200:
                            d = r.json()
                            if d.get("code") == 0 and d.get("data"):
                                dd = d["data"]
                                vu = dd.get("play", "") or dd.get("hdplay", "") or dd.get("wmplay", "")
                                if vu:
                                    return {
                                        "title": dd.get("title", ""),
                                        "video_url": vu,
                                        "cover_url": dd.get("cover", ""),
                                        "duration": dd.get("duration", 0),
                                        "file_size": dd.get("size", 0) or 0,
                                        "width": dd.get("w", 0),
                                        "height": dd.get("h", 0),
                                        "resolution": f"{dd.get('w',0)}x{dd.get('h',0)}" if dd.get('w') and dd.get('h') else "",
                                        "fps": 30,
                                        "ext": "mp4",
                                        "extractor": "tikwm_api",
                                        "watermark": False,
                                    }
                except Exception:
                    pass

            d = await self._parse_with_ytdlp(url)
            d["watermark"] = False
            return d

        except Exception as e:
            try:
                d = await self._parse_with_ytdlp(url)
                d["watermark"] = False
                return d
            except Exception as e2:
                raise RuntimeError(f"TikTok解析失败: {e2}")
