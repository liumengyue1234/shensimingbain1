"""
法规检索核心模块（优化版）
- 默认不拉法规全文，减少等待时间
- 大模型调用改为可选，先快速返回列表
"""
from utils.deli_client import DeliClient
from utils.hunyuan_client import HunyuanClient


class LawRetrievalEngine:
    """法规检索引擎"""

    def __init__(self):
        self.deli = DeliClient()
        self.hunyuan = HunyuanClient()

    def search_and_analyze(
        self,
        query: str,
        field_name: str = "semantic",
        page_size: int = 5,
        with_detail: bool = False,   # ★ 默认关闭全文拉取，大幅提速
        with_ai_analysis: bool = True
    ) -> dict:
        """
        检索法规并生成分析报告
        :param query: 用户查询文本
        :param field_name: 检索模式 semantic|title
        :param page_size: 返回法规数量
        :param with_detail: 是否拉取法规全文（默认关闭，按需开启）
        :param with_ai_analysis: 是否调用大模型生成分析（默认开启）
        """
        # 1. 法规列表检索
        result = self.deli.search_laws(
            keywords=[query],
            field_name=field_name,
            page_size=page_size
        )
        laws = result.get("body", {}).get("data", [])
        if not laws:
            return {
                "query": query,
                "laws": [],
                "analysis": "暂未检索到相关法规，请调整关键词后重试。"
            }

        # 2. 按需拉取全文（并发）
        if with_detail:
            laws_data = self.deli.get_laws_detail_batch(laws)
        else:
            laws_data = laws

        analysis_text = ""
        # 3. 按需调用大模型
        if with_ai_analysis and self.hunyuan.app_key:
            law_text = self._format_laws(laws_data, with_detail)
            prompt = f"""
            用户问题：{query}

            相关法规列表：
            {law_text}

            请以专业律师视角，简要分析：
            1. 各法规与用户问题的关联性
            2. 核心法律要点
            3. 实操建议

            要求：语言专业，条理清晰，控制在300字以内。
            """
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
            "laws": laws_data,
            "analysis": analysis_text
        }

    def get_law_detail_by_id(self, law_id: str) -> dict:
        """按需获取单条法规全文"""
        return self.deli.get_law_detail(law_id)

    def _format_laws(self, laws: list, with_detail: bool = False) -> str:
        """格式化法规列表"""
        formatted = []
        for i, law in enumerate(laws, 1):
            if with_detail and "body" in law:
                body = law["body"].get("body", {})
                content = body.get("lawDetailContent", "")[:500]  # ★ 截短，减少大模型输入 token
                formatted.append(
                    f"{i}. 《{body.get('title', '未知法规')}》"
                    f"（{body.get('publisherName', '')} {body.get('publishDate', '')} {body.get('timelinessName', '')}）\n"
                    f"   摘录：{content}..."
                )
            else:
                formatted.append(
                    f"{i}. {law.get('title', '未知法规')}"
                    f"（{law.get('publishDate', '')}）"
                )
        return "\n".join(formatted)
