"""
API 路由定义（优化版）
- 法规检索新增 /laws/detail 按需获取全文接口
- 所有接口统一异常处理
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.case_retrieval import CaseRetrievalEngine
from core.law_retrieval import LawRetrievalEngine
from core.strategy_engine import StrategyEngine

router = APIRouter(prefix="/api/v1")

case_engine = CaseRetrievalEngine()
law_engine = LawRetrievalEngine()
strategy_engine = StrategyEngine()


# ===== 请求模型 =====

class QueryRequest(BaseModel):
    query: str
    page_size: Optional[int] = 5
    with_ai: Optional[bool] = True  # 是否调用大模型分析


class LawQueryRequest(BaseModel):
    query: str
    field_name: Optional[str] = "semantic"
    page_size: Optional[int] = 5
    with_detail: Optional[bool] = False  # ★ 默认不拉全文
    with_ai: Optional[bool] = True


class LawDetailRequest(BaseModel):
    law_id: str


class ComplaintRequest(BaseModel):
    case_content: str


# ===== 类案检索 =====

@router.post("/cases/search")
async def search_cases(req: QueryRequest):
    """类案检索接口"""
    try:
        result = case_engine.search_and_analyze(
            query=req.query,
            page_size=req.page_size,
            with_ai_analysis=req.with_ai
        )
        return {"code": 0, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 法规检索 =====

@router.post("/laws/search")
async def search_laws(req: LawQueryRequest):
    """法规检索接口（快速返回列表）"""
    try:
        result = law_engine.search_and_analyze(
            query=req.query,
            field_name=req.field_name,
            page_size=req.page_size,
            with_detail=req.with_detail,
            with_ai_analysis=req.with_ai
        )
        return {"code": 0, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/laws/detail")
async def get_law_detail(req: LawDetailRequest):
    """按需获取法规全文（点击展开时调用）"""
    try:
        detail = law_engine.get_law_detail_by_id(req.law_id)
        return {"code": 0, "msg": "success", "data": detail}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 诉讼策略推演 =====

@router.post("/strategy/analyze")
async def analyze_strategy(req: ComplaintRequest):
    """诉讼策略推演接口"""
    try:
        result = strategy_engine.analyze_complaint(req.case_content)
        return {"code": 0, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
