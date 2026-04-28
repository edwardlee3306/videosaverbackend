import os,re
def sanitize_filename(fn):fn=re.sub(r'[\\/:*?"<>|]','_',fn);return fn[:100]if len(fn)>100else fn
def format_size(b):
    if not b:return"未知"
    u=['B','KB','MB','GB'];i=0;s=float(b)
    while s>=1024 and i<3:s/=1024;i+=1
    return f"{s:.1f} {u[i]}"
def format_duration(s):
    if not s:return"0:00"
    m=s//60;sec=s%60
    if m>=60:h,m_=m//60,m%60;return f"{h}:{m_:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"
def is_valid_url(url):return bool(re.match(r'^https?://[^\s/$.?#][^\s]*$',url,re.I))if url and len(url)>=10 else False
