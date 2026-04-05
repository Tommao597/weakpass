from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import detector, dict_manage, report
from app.api.generate_smart import router as generate_smart_dict_router
from app.api.asset_routes import router as asset_router
from app.api import password_dict



import uvicorn

app = FastAPI(title="弱口令检测系统")


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
     ],  # Vue开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(detector.router, prefix="/api/detector", tags=["弱口令检测"])
app.include_router(asset_router, prefix="/api/asset", tags=["资产识别"])
app.include_router(dict_manage.router, prefix="/api/dict", tags=["字典"])
app.include_router(password_dict.router, prefix="/api/password", tags=["ai密码字典"])
app.include_router(generate_smart_dict_router, prefix="/api/smart_dict", tags=["智能字典生成"])
app.include_router(report.router, prefix="/api/report", tags=["报告"])

@app.get("/")
async def root():
    return {"message": "弱口令检测系统API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

