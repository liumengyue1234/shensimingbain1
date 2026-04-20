"""
得理开放平台 API 客户端封装
支持类案检索与法规检索
"""
import os
import requests
from typing import Optional


class DeliClient:
    """得理开放平台 API 客户端"""

    BASE_URL = "https://openapi.delilegal.com"

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
        keywords: list[str],
        page_no: int = 1,
        page_size: int = 5,
        sort_field: str = "correlation",
        sort_order: str = "desc",
        court_levels: Optional[list[str]] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None
    ) -> dict:
        """
        类案检索
        :param keywords: 关键词数组
        :param page_no: 页码
        :param page_size: 每页条数
        :param sort_field: 排序字段 correlation|time
        :param sort_order: 排序方向 asc|desc
        :param court_levels: 法院层级 ["0"最高法,"1"高院,"2"中院,"3"基层]
        :param year_start: 裁判年份起始
        :param year_end: 裁判年份结束
        """
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
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def search_laws(
        self,
        keywords: list[str],
        field_name: str = "semantic",
        page_no: int = 1,
        page_size: int = 5,
        sort_field: str = "correlation",
        sort_order: str = "desc"
    ) -> dict:
        """
        法规检索
        :param keywords: 查询关键词或语义查询文字
        :param field_name: 检索方式 title(关键词)|semantic(语义)
        :param page_no: 页码
        :param page_size: 每页条数
        :param sort_field: 排序字段
        :param sort_order: 排序方向
        """
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
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_law_detail(self, law_id: str) -> dict:
        """
        获取法规详情
        :param law_id: 法规 ID（来自法规检索结果）
        """
        url = f"{self.BASE_URL}/api/qa/v3/search/lawInfo"
        params = {"lawId": law_id, "merge": "true"}
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_laws_detail_batch(self, laws: list[dict]) -> list[dict]:
        """
        批量获取法规详情
        :param laws: 法规列表（包含 id 字段）
        """
        results = []
        for law in laws:
            law_id = law.get("id") or law.get("lawsId")
            if not law_id:
                continue
            try:
                detail = self.get_law_detail(law_id)
                results.append({"id": law_id, "body": detail})
            except Exception as e:
                results.append({"id": law_id, "body": {}, "error": str(e)})
        return results
