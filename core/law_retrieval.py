"""
法规检索核心模块
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
        with_detail: bool = True
    ) -> dict:
        """
        检索法规并生成分析报告
        :param query: 用户查询文本
        :param field_name: 检索模式 semantic|title
        :param page_size: 返回法规数量
        :param with_detail: 是否获取法规全文
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

        # 2. 可选：获取法规全文
        if with_detail:
            laws_with_detail = self.deli.get_laws_detail_batch(laws)
        else:
            laws_with_detail = laws

        # 3. 调用大模型生成法规分析
        law_text = self._format_laws(laws_with_detail, with_detail)
        prompt = f"""
        用户问题：{query}
        
        相关法规内容：
        {law_text}
        
        请以专业律师视角，对上述法规进行分析解读：
        1. 简要说明各法规与用户问题的关联性
        2. 提炼核心法律要点
        3. 给出实操建议
        
        要求：语言专业准确，条理清晰，仅基于检索结果作答。
        """
        analysis = self.hunyuan.chat(prompt)
        analysis_text = self.hunyuan.extract_content(analysis)

        return {
            "query": query,
            "total": result.get("body", {}).get("total", 0),
            "laws": laws_with_detail,
            "analysis": analysis_text
        }

    def _format_laws(self, laws: list, with_detail: bool = False) -> str:
        """格式化法规列表为文本"""
        formatted = []
        for i, law in enumerate(laws, 1):
            if with_detail and "body" in law:
                body = law["body"].get("body", {})
                content = body.get("lawDetailContent", "")[:2000]
                formatted.append(
                    f"{i}. 《{body.get('title', '未知法规')}》\n"
                    f"   发布机构：{body.get('publisherName', '未知')}\n"
                    f"   发布时间：{body.get('publishDate', '未知')}\n"
                    f"   时效状态：{body.get('timelinessName', '未知')}\n"
                    f"   内容摘录：{content}..."
                )
            else:
                formatted.append(
                    f"{i}. {law.get('title', '未知法规')}\n"
                    f"   发布时间：{law.get('publishDate', '未知')}"
                )
        return "\n\n".join(formatted)
