"""
审思明辨——智判法案双擎系统
主应用入口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
async def root():
    return {
        "name": "审思明辨——智判法案双擎系统",
        "version": "1.0.0",
        "status": "running",
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
    uvicorn.run(
        "app:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "False") == "True"
    )
