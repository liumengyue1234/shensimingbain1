"""
类案检索核心模块（优化版）
- 大模型调用改为可选
- 截短 prompt 减少 token 消耗
"""
from utils.deli_client import DeliClient
from utils.hunyuan_client import HunyuanClient


class CaseRetrievalEngine:
    """类案检索引擎"""

    def __init__(self):
        self.deli = DeliClient()
        self.hunyuan = HunyuanClient()

    def search_and_analyze(
        self,
        query: str,
        page_size: int = 5,
        with_ai_analysis: bool = True
    ) -> dict:
        """
        检索类案并生成分析报告
        :param query: 用户查询文本
        :param page_size: 返回案例数量
        :param with_ai_analysis: 是否调用大模型生成分析
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

        analysis_text = ""
        # 2. 按需调用大模型生成类案分析报告
        if with_ai_analysis and self.hunyuan.app_key:
            case_text = self._format_cases(cases)
            prompt = (
                f"用户问题：{query}\n\n"
                f"检索到的类案（共{len(cases)}个）：\n{case_text}\n\n"
                "请以律师视角，用总-分-总结构，"
                "简要生成类案检索报告（每个案例说明裁判要旨，总结控制在400字内）。"
                "仅使用上述案例，不得引用其他案例。"
            )
            try:
                analysis = self.hunyuan.chat(prompt)
                analysis_text = self.hunyuan.extract_content(analysis)
            except Exception:
                analysis_text = "AI 分析暂时不可用，请检查元器配置。"
        else:
            analysis_text = "（未配置腾讯元器，仅展示检索结果）"

        return {
            "query": query,
            "total": result.get("body", {}).get("total", 0),
            "cases": cases,
            "analysis": analysis_text
        }

    def _format_cases(self, cases: list) -> str:
        """格式化案例列表（精简版，减少 token）"""
        formatted = []
        for i, case in enumerate(cases, 1):
            abstract = case.get("abstract", "暂无摘要")
            if abstract:
                abstract = abstract[:200]  # ★ 截短摘要，减少 token
            formatted.append(
                f"{i}. {case.get('caseName', '未知案件')}"
                f"｜{case.get('courtName', '')} {case.get('judgeDate', '')}\n"
                f"   摘要：{abstract}"
            )
        return "\n\n".join(formatted)
