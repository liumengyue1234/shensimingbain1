"""
腾讯混元大模型客户端封装
"""
import os
import json
import requests
from typing import Generator


class HunyuanClient:
    """腾讯混元大模型 / 腾讯元器智能体客户端"""

    YUANQI_URL = "https://yuanqi.tencent.com/openapi/v1/agent/chat/completions"

    def __init__(self):
        self.app_id = os.getenv("YUANQI_APP_ID", "")
        self.app_key = os.getenv("YUANQI_APP_KEY", "")

    def chat(
        self,
        message: str,
        user_id: str = "user_001",
        history: list = None,
        stream: bool = False
    ) -> dict | Generator:
        """
        与腾讯元器智能体对话
        :param message: 用户消息
        :param user_id: 用户 ID
        :param history: 历史消息列表
        :param stream: 是否流式返回
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.app_key}"
        }
        messages = history or []
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": message}]
        })

        payload = {
            "assistant_id": self.app_id,
            "user_id": user_id,
            "stream": stream,
            "messages": messages
        }

        if stream:
            return self._stream_chat(headers, payload)
        else:
            response = requests.post(
                self.YUANQI_URL, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()
            return response.json()

    def _stream_chat(self, headers: dict, payload: dict) -> Generator:
        """流式对话生成器"""
        with requests.post(
            self.YUANQI_URL, headers=headers, json=payload, stream=True, timeout=60
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

    def extract_content(self, response: dict) -> str:
        """从响应中提取文本内容"""
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return ""
