from .base import BaseParser,identify_platform
from .douyin import DouyinParser,TikTokParser
from .bilibili import BilibiliParser
from .youtube import YouTubeParser
from .kuaishou import KuaishouParser
from .xiaohongshu import XiaohongshuParser
from .instagram import InstagramParser
from .twitter import TwitterParser
from .facebook import FacebookParser

SUPPORTED_PLATFORMS=[
    {"name":"抖音","key":"douyin","icon":"🎵","enabled":True,"example":"https://v.douyin.com/xxxxx/"},
    {"name":"TikTok","key":"tiktok","icon":"🎶","enabled":True,"example":"https://www.tiktok.com/@user/video/xxxxx"},
    {"name":"快手","key":"kuaishou","icon":"🎬","enabled":True,"example":"https://v.kuaishou.com/xxxxx"},
    {"name":"B站","key":"bilibili","icon":"📺","enabled":True,"example":"https://www.bilibili.com/video/BVxxxxx"},
    {"name":"小红书","key":"xiaohongshu","icon":"📕","enabled":True,"example":"https://www.xiaohongshu.com/explore/xxxxx"},
    {"name":"Instagram","key":"instagram","icon":"📸","enabled":True,"example":"https://www.instagram.com/reel/xxxxx/"},
    {"name":"YouTube","key":"youtube","icon":"▶️","enabled":True,"example":"https://www.youtube.com/watch?v=xxxxx"},
    {"name":"Twitter/X","key":"twitter","icon":"🐦","enabled":True,"example":"https://x.com/user/status/xxxxx"},
    {"name":"Facebook","key":"facebook","icon":"👤","enabled":True,"example":"https://www.facebook.com/watch/?v=xxxxx"},
    {"name":"微博","key":"weibo","icon":"💬","enabled":True,"example":"https://weibo.com/xxxxx"},
]

PARSER_REGISTRY={"douyin":DouyinParser,"tiktok":TikTokParser,"kuaishou":KuaishouParser,"bilibili":BilibiliParser,"xiaohongshu":XiaohongshuParser,"instagram":InstagramParser,"youtube":YouTubeParser,"twitter":TwitterParser,"facebook":FacebookParser,"default":BaseParser}
def get_platform_parser(key):cls=PARSER_REGISTRY.get(key,BaseParser);return cls(key,key)
