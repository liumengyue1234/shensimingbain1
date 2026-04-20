"""
API 路由定义
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


# ===== 请求/响应模型 =====

class QueryRequest(BaseModel):
    query: str
    page_size: Optional[int] = 5


class LawQueryRequest(BaseModel):
    query: str
    field_name: Optional[str] = "semantic"
    page_size: Optional[int] = 5
    with_detail: Optional[bool] = True


class ComplaintRequest(BaseModel):
    case_content: str


# ===== 类案检索接口 =====

@router.post("/cases/search")
async def search_cases(req: QueryRequest):
    """类案检索接口"""
    try:
        result = case_engine.search_and_analyze(
            query=req.query,
            page_size=req.page_size
        )
        return {"code": 0, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 法规检索接口 =====

@router.post("/laws/search")
async def search_laws(req: LawQueryRequest):
    """法规检索接口"""
    try:
        result = law_engine.search_and_analyze(
            query=req.query,
            field_name=req.field_name,
            page_size=req.page_size,
            with_detail=req.with_detail
        )
        return {"code": 0, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 诉讼策略推演接口 =====

@router.post("/strategy/analyze")
async def analyze_strategy(req: ComplaintRequest):
    """
    诉讼策略推演接口
    上传起诉状或案情，生成对方律师视角的策略报告
    """
    try:
        result = strategy_engine.analyze_complaint(req.case_content)
        return {"code": 0, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
