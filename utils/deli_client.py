"""
得理开放平台 API 客户端封装
支持类案检索与法规检索（并发优化版）
"""
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional


class DeliClient:
    """得理开放平台 API 客户端"""

    BASE_URL = "https://openapi.delilegal.com"
    TIMEOUT = 15  # 单次请求超时秒数

    def __init__(self):
        self.app_id = os.getenv("DELI_APP_ID", "QthdBErlyaYvyXul")
        self.secret = os.getenv("DELI_SECRET", "EC5D455E6BD348CE8E18BE05926D2EBE")
        self.headers = {
            "Content-Type": "application/json",
            "appid": self.app_id,
            "secret": self.secret
        }

    def search_cases(
        self,
        keywords: list,
        page_no: int = 1,
        page_size: int = 5,
        sort_field: str = "correlation",
        sort_order: str = "desc",
        court_levels: Optional[list] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None
    ) -> dict:
        """类案检索"""
        url = f"{self.BASE_URL}/api/qa/v3/search/queryListCase"
        condition = {"keywordArr": keywords}
        if court_levels:
            condition["courtLevelArr"] = court_levels
        if year_start:
            condition["caseYearStart"] = year_start
        if year_end:
            condition["caseYearEnd"] = year_end

        payload = {
            "pageNo": page_no,
            "pageSize": page_size,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "condition": condition
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=self.TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            return {"body": {"data": [], "total": 0}, "error": "请求超时，请稍后重试"}
        except Exception as e:
            return {"body": {"data": [], "total": 0}, "error": str(e)}

    def search_laws(
        self,
        keywords: list,
        field_name: str = "semantic",
        page_no: int = 1,
        page_size: int = 5,
        sort_field: str = "correlation",
        sort_order: str = "desc"
    ) -> dict:
        """法规检索"""
        url = f"{self.BASE_URL}/api/qa/v3/search/queryListLaw"
        payload = {
            "pageNo": page_no,
            "pageSize": page_size,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "condition": {
                "keywords": keywords,
                "fieldName": field_name
            }
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=self.TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            return {"body": {"data": [], "total": 0}, "error": "请求超时，请稍后重试"}
        except Exception as e:
            return {"body": {"data": [], "total": 0}, "error": str(e)}

    def get_law_detail(self, law_id: str) -> dict:
        """获取单条法规详情"""
        url = f"{self.BASE_URL}/api/qa/v3/search/lawInfo"
        params = {"lawId": law_id, "merge": "true"}
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=self.TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_laws_detail_batch(self, laws: list, max_workers: int = 5) -> list:
        """
        并发批量获取法规详情（核心优化：串行改并发）
        原来 5 条法规串行请求需要 5~10s，现在并发只需 1~2s
        """
        if not laws:
            return []

        def fetch_one(law):
            law_id = law.get("id") or law.get("lawsId")
            if not law_id:
                return {"original": law, "detail": {}}
            detail = self.get_law_detail(law_id)
            return {"id": law_id, "original": law, "body": detail}

        results = [None] * len(laws)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(fetch_one, law): i for i, law in enumerate(laws)}
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = {"id": None, "body": {}, "error": str(e)}

        return [r for r in results if r is not None]
