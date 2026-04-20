"""
类案检索核心模块
"""
from utils.deli_client import DeliClient
from utils.hunyuan_client import HunyuanClient


class CaseRetrievalEngine:
    """类案检索引擎"""

    def __init__(self):
        self.deli = DeliClient()
        self.hunyuan = HunyuanClient()

    def search_and_analyze(self, query: str, page_size: int = 5) -> dict:
        """
        检索类案并生成分析报告
        :param query: 用户查询文本
        :param page_size: 返回案例数量
        """
        # 1. 调用得理 API 检索类案
        result = self.deli.search_cases(
            keywords=[query],
            page_size=page_size,
            sort_field="correlation"
        )

        cases = result.get("body", {}).get("data", [])
        if not cases:
            return {
                "query": query,
                "cases": [],
                "analysis": "暂未检索到相关案例，请调整关键词后重试。"
            }

        # 2. 调用混元大模型生成类案分析报告
        case_text = self._format_cases(cases)
        prompt = f"""
        #用户输入的问题：{query}
        #检索出的类案列表：{case_text}
        
        你是一名经验丰富的律师，擅长基于用户输入问题检索出的类案（即与用户问题高度相关的相似案例）进行分析，
        并生成一份结构清晰、内容详实的类案检索报告。
        
        要求：
        1. 报告整体结构须采用"总分总"结构：先概述，再分述类案要点，最后总结归纳。
        2. 仅可使用通过用户问题检索得出的类案列表中的案例，严禁引用类案列表之外的任何案例。
        3. 每个案例须包含：案件名称、裁判法院、裁判时间、核心争议、裁判要旨。
        """
        analysis = self.hunyuan.chat(prompt)
        analysis_text = self.hunyuan.extract_content(analysis)

        return {
            "query": query,
            "total": result.get("body", {}).get("total", 0),
            "cases": cases,
            "analysis": analysis_text
        }

    def _format_cases(self, cases: list) -> str:
        """格式化案例列表为文本"""
        formatted = []
        for i, case in enumerate(cases, 1):
            formatted.append(
                f"{i}. 案件名称：{case.get('caseName', '未知')}\n"
                f"   法院：{case.get('courtName', '未知')}\n"
                f"   裁判时间：{case.get('judgeDate', '未知')}\n"
                f"   摘要：{case.get('abstract', '暂无摘要')}"
            )
        return "\n\n".join(formatted)
