"""
诉讼策略推演引擎
切换"对方律师"视角，生成质证意见与风险提示报告
"""
from utils.deli_client import DeliClient
from utils.hunyuan_client import HunyuanClient


class StrategyEngine:
    """诉讼策略推演引擎"""

    OPPONENT_LAWYER_PROMPT = """
    你现在扮演一名经验丰富的资深律师，代表本案的对方当事人。
    请基于以下案情材料，以对方律师视角进行全面分析：
    
    {case_content}
    
    请生成一份完整的【质证意见与诉讼风险报告】，包含以下部分：
    
    ## 一、我方（对方）核心主张
    简述对方当事人的核心诉求与法律依据
    
    ## 二、质证意见
    针对起诉方提交的证据逐一进行质证，指出其证明力不足之处
    
    ## 三、抗辩策略
    列举 3-5 个可供采用的抗辩理由，并引用支撑法条
    
    ## 四、风险提示
    客观评估本案的胜诉概率及主要风险点（高/中/低）
    
    ## 五、建议措施
    提出具体的应诉建议与下一步行动计划
    
    注意：保持专业、客观、全面，所有法律引用须准确。
    """

    def __init__(self):
        self.deli = DeliClient()
        self.hunyuan = HunyuanClient()

    def analyze_complaint(self, case_content: str) -> dict:
        """
        分析起诉状，生成对方律师视角的策略报告
        :param case_content: 起诉状或案情描述文本
        """
        # 1. 检索相关案例作为参考
        case_result = self.deli.search_cases(
            keywords=[case_content[:200]],
            page_size=3
        )
        related_cases = case_result.get("body", {}).get("data", [])

        # 2. 检索相关法规
        law_result = self.deli.search_laws(
            keywords=[case_content[:200]],
            field_name="semantic",
            page_size=3
        )
        related_laws = law_result.get("body", {}).get("data", [])

        # 3. 构建增强后的案情文本
        enhanced_content = self._build_enhanced_content(
            case_content, related_cases, related_laws
        )

        # 4. 生成对方律师视角报告
        prompt = self.OPPONENT_LAWYER_PROMPT.format(case_content=enhanced_content)
        response = self.hunyuan.chat(prompt)
        report = self.hunyuan.extract_content(response)

        return {
            "original_complaint": case_content,
            "related_cases_count": len(related_cases),
            "related_laws_count": len(related_laws),
            "strategy_report": report
        }

    def _build_enhanced_content(
        self, case_content: str, cases: list, laws: list
    ) -> str:
        """构建增强案情文本"""
        content = f"【案情描述】\n{case_content}\n\n"
        if cases:
            content += "【参考类案】\n"
            for i, case in enumerate(cases, 1):
                content += f"{i}. {case.get('caseName', '')} - {case.get('abstract', '')[:200]}\n"
        if laws:
            content += "\n【相关法规】\n"
            for i, law in enumerate(laws, 1):
                content += f"{i}. {law.get('title', '')}\n"
        return content
