from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.detector import router as detector_router
from app.api.dict_manage import router as dict_router
from app.api.report import router as report_router
from app.api.password_dict import router as password_router
from app.api.generate_smart import router as generate_smart_dict_router
from app.api.asset_routes import router as asset_router

import uvicorn

app = FastAPI(title="弱口令检测系统")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(detector_router, prefix="/api/detector", tags=["弱口令检测"])
app.include_router(asset_router, prefix="/api/asset", tags=["资产识别"])
app.include_router(dict_router, prefix="/api/dict", tags=["字典"])
app.include_router(password_router, prefix="/api/password", tags=["AI密码字典"])
app.include_router(generate_smart_dict_router, prefix="/api/smart_dict", tags=["智能字典生成"])
app.include_router(report_router, prefix="/api/report", tags=["报告"])


@app.get("/")
async def root():
    return {"message": "弱口令检测系统API"}



@app.on_event("startup")
async def print_routes():
    print("\n===== 已注册路由 =====")
    for route in app.routes:
        print(route.path)
    print("=====================\n")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  
    )