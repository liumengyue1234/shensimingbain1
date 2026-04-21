"""
审思明辨——智判法案双擎系统
主应用入口（完善版）
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="审思明辨——智判法案双擎系统",
    description="面向法律从业者的智能辅助平台",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
from api.routes import router
app.include_router(router)

# 托管前端静态文件
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """返回前端页面"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "name": "审思明辨——智判法案双擎系统",
        "version": "1.0.0",
        "status": "running",
        "message": "Frontend not found. Please ensure static/index.html exists.",
        "capabilities": [
            "对话式法律问答",
            "精准法条检索",
            "相似案例匹配",
            "诉讼策略推演"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  审思明辨——智判法案双擎系统")
    print("  http://localhost:8000")
    print("=" * 50)
    uvicorn.run(
        "app:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True
    )
