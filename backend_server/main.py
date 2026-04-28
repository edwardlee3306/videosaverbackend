import os,json,hashlib,subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,JSONResponse
from pydantic import BaseModel,Field
from dotenv import load_dotenv
from platforms import get_platform_parser,SUPPORTED_PLATFORMS
from processor import VideoProcessor

load_dotenv()

class Settings:
    HOST=os.getenv("HOST","0.0.0.0");PORT=int(os.getenv("PORT","8000"))
    DOWNLOAD_DIR=Path(os.getenv("DOWNLOAD_DIR","./downloads"))
    TEMP_DIR=Path(os.getenv("TEMP_DIR","./temp"))
    MAX_FILE_SIZE=int(os.getenv("MAX_FILE_SIZE",str(500*1024*1024)))
    ENABLE_WATERMARK_REMOVAL=os.getenv("ENABLE_WATERMARK_REMOVAL","true").lower()=="true"
    KEEP_ORIGINAL_QUALITY=os.getenv("KEEP_ORIGINAL_QUALITY","true").lower()=="true"
    API_KEY=os.getenv("API_KEY",None)
    @classmethod
    def init_dirs(cls):cls.DOWNLOAD_DIR.mkdir(parents=True,exist_ok=True);cls.TEMP_DIR.mkdir(parents=True,exist_ok=True)

settings=Settings();settings.init_dirs()

class ParseRequest(BaseModel):
    url:str=Field(...,description="视频链接")
    task_id:Optional[str]=None
    options:dict=Field(default_factory=lambda:{"high_quality":True,"remove_watermark":True})

class TaskStatus(BaseModel):
    task_id:str;status:str="pending";progress:int=0;message:str="";result:Optional[dict]=None;error:Optional[str]=None
    created_at:str="";updated_at:str=""

class TaskStore:
    def __init__(self):self._tasks={}
    def create(self,task_id):
        now=datetime.now().isoformat();task=TaskStatus(task_id=task_id,created_at=now,updated_at=now);self._tasks[task_id]=task;return task
    def update(self,task_id,**kwargs):
        if task_id in self._tasks:
            for k,v in kwargs.items():
                if hasattr(self._tasks[task_id],k):setattr(self._tasks[task_id],k,v)
            self._tasks[task_id].updated_at=datetime.now().isoformat()
    def get(self,task_id):return self._tasks.get(task_id)

task_store=TaskStore()

@asynccontextmanager
async def lifespan(app:FastAPI):
    settings.init_dirs()
    print(f"VideoSaver API on {settings.HOST}:{settings.PORT}, {len(SUPPORTED_PLATFORMS)} platforms")
    yield

app=FastAPI(title="VideoSaver API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
async def health():
    deps={"ffmpeg":False,"yt-dlp":False}
    try:r=subprocess.run(["ffmpeg","-version"],capture_output=True,text=True,timeout=5);deps["ffmpeg"]=r.returncode==0
    except:pass
    try:r=subprocess.run(["yt-dlp","--version"],capture_output=True,text=True,timeout=5);deps["yt-dlp"]=r.returncode==0
    except:pass
    return{"status":"ok","dependencies":deps,"settings":{"watermark_removal":settings.ENABLE_WATERMARK_REMOVAL,"keep_quality":settings.KEEP_ORIGINAL_QUALITY}}

@app.get("/api/platforms")
async def platforms():return{"success":True,"data":SUPPORTED_PLATFORMS}

@app.post("/api/parse")
async def parse(request:ParseRequest,background_tasks:BackgroundTasks):
    url=request.url.strip()
    task_id=request.task_id or hashlib.md5(url.encode()).hexdigest()[:12]
    if not url:raise HTTPException(400,"URL不能为空")
    task=task_store.create(task_id);task.status="processing";task.progress=5;task.message="正在识别平台..."
    try:
        from platforms import identify_platform
        pi=identify_platform(url)
        if not pi:raise HTTPException(400,"不支持的链接")
        parser=get_platform_parser(pi["key"])
        task.progress=20;task.message="正在解析..."
        vi=await parser.parse(url)
        task.progress=50
        processor=VideoProcessor()
        pi2=await processor.process(vi,remove_watermark=request.options.get("remove_watermark",True),high_quality=request.options.get("high_quality",True))
        task.progress=80
        rd={"title":vi.get("title",""),"platform":pi["name"],"cover":vi.get("cover_url",""),"video_url":pi2.get("video_url",vi.get("video_url","")),"download_url":pi2.get("download_url",pi2.get("video_url",vi.get("video_url",""))),"file_size":pi2.get("file_size",vi.get("file_size",0)),"duration":pi2.get("duration",vi.get("duration",0)),"quality":"HD","resolution":pi2.get("resolution",vi.get("resolution","1920×1080")),"width":pi2.get("width",vi.get("width",0)),"height":pi2.get("height",vi.get("height",0)),"fps":pi2.get("fps",vi.get("fps",30)),"file_name":f"{pi['key']}_video_{task_id[:8]}.mp4","watermark_removed":pi2.get("watermark_removed",True),"task_id":task_id}
        task.status="completed";task.progress=100;task.message="解析完成";task.result=rd
        if pi2.get("temp_files"):background_tasks.add_task(cleanup_temp_files,pi2["temp_files"])
        return{"success":True,"message":"解析成功","code":0,"data":rd}
    except Exception as e:
        task.status="failed";task.error=str(e);return{"success":False,"message":f"解析错误: {str(e)[:100]}","code":-500}

def cleanup_temp_files(files):
    for f in files:
        try:p=Path(f);p.exists()and p.unlink()
        except:pass

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app",host=settings.HOST,port=settings.PORT,log_level="info")
