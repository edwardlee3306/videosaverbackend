import os,re,json,subprocess
from pathlib import Path
from typing import Optional
WATERMARK_REGIONS={"douyin":{"top_right":{"x":0.85,"y":0.05,"w":0.12,"h":0.08},"bottom_center":{"x":0.3,"y":0.9,"w":0.4,"h":0.06}},"kuaishou":{"top_left":{"x":0.02,"y":0.02,"w":0.25,"h":0.06}},"tiktok":{"bottom_center":{"x":0.2,"y":0.92,"w":0.6,"h":0.05}}}
class VideoProcessor:
    def __init__(self,download_dir=None):self.download_dir=download_dir or Path("./downloads");self.download_dir.mkdir(parents=True,exist_ok=True)
    async def process(self,vi,remove_watermark=True,high_quality=True):
        pk=vi.get("extractor","").replace("_api","");vu=vi.get("video_url","");ws=vi.get("watermark","unknown")
        r={"video_url":vu,"download_url":vu,"file_size":vi.get("file_size",0),"quality":vi.get("resolution","HD"),"resolution":vi.get("resolution",""),"width":vi.get("width",0),"height":vi.get("height",0),"fps":vi.get("fps",30),"file_name":vi.get("file_name",f"video_{self._rid()}.mp4"),"watermark_removed":ws==False,"temp_files":[]}
        if not remove_watermark or ws==False or not vu:return r
        try:
            p=self._ffmpeg_delogo(vu,pk)
            if p:r["video_url"]=p.get("url",vu);r["download_url"]=p.get("url",vu);r["file_size"]=p.get("size",r["file_size"]);r["file_name"]=p.get("filename",r["file_name"]);r["watermark_removed"]=True;r["temp_files"]=p.get("temp_files",[])
        except Exception as e:print(f"水印处理跳过: {e}");r["watermark_removed"]=False
        return r
    def _ffmpeg_delogo(self,vu,pk):
        cfg=WATERMARK_REGIONS.get(pk,{})
        if not cfg:return None
        vi=self._probe(vu)
        if not vi:return None
        w=vi.get("width",0);h=vi.get("height",0)
        if w==0 or h==0:return None
        filters=[]
        for rn,rv in cfg.items():
            x=int(w*rv["x"]);y=int(h*rv["y"]);fw=int(w*rv["w"]);fh=int(h*rv["h"])
            filters.append(f"delogo=x={x}:y={y}:w={fw}:h={fh}:show=0")
        if not filters:return None
        fc=",".join(filters)
        fn=f"proc_{self._rid()}.mp4";op=self.download_dir/fn
        fps=vi.get("fps",30)
        cmd=["ffmpeg","-i",vu,"-vf",fc,"-c:v","libx264","-crf","18","-preset","slow","-c:a","copy","-r",str(fps),"-s",f"{w}x{h}","-pix_fmt","yuv420p","-y",str(op)]
        try:
            r=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
            if r.returncode!=0 or not op.exists():return None
            return{"url":str(op),"size":op.stat().st_size,"filename":fn,"temp_files":[str(op)]}
        except:return None
    def _probe(self,url):
        try:
            r=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_streams","-show_format",url],capture_output=True,text=True,timeout=15)
            if r.returncode!=0:return None
            d=json.loads(r.stdout);vs=None
            for s in d.get("streams",[]):
                if s.get("codec_type")=="video":vs=s;break
            if not vs:return None
            fps=30
            if"/"in vs.get("r_frame_rate","30"):
                n,d_=vs["r_frame_rate"].split("/");fps=round(float(n)/float(d_))if float(d_)!=0 else 30
            return{"width":int(vs.get("width",0)),"height":int(vs.get("height",0)),"fps":fps}
        except:return None
    def _rid(self):
        import hashlib,time;return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
