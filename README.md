# 审思明辨——智判法案双擎系统

> 面向法律从业者的智能辅助平台，融合对话式问答、精准法条检索、相似案例匹配与诉讼策略推演四大核心能力。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/platform-腾讯云-orange.svg)

---

## 📖 项目简介

**审思明辨** 是一款深度整合腾讯生态的法律智能辅助平台，以腾讯混元大模型为认知引擎，借助腾讯云向量数据库构建高质量法律知识库，实现"法条 + 案例"双擎驱动的智能问答与深度推理。

### 核心能力

| 能力模块 | 描述 |
|---|---|
| 🗣️ 对话式法律问答 | 自然语言咨询法律问题，实时推送相关法条与司法解释 |
| 🔍 精准法条检索 | 基于语义检索的法规定位，支持关键词与语义双模式 |
| 📚 相似案例匹配 | 类案智能匹配，生成结构化类案检索报告 |
| ⚖️ 诉讼策略推演 | 上传案情后，智能体切换"对方律师"视角，生成质证意见与风险提示 |

---

## 🏗️ 系统架构

```
审思明辨系统
├── 认知引擎层        腾讯混元大模型 (Hunyuan)
├── 知识库层          腾讯云向量数据库 + 得理开放平台
│   ├── 法规知识库    法律法规、司法解释语义索引
│   └── 案例知识库    判决书、裁决书等类案语料
├── 智能体编排层      腾讯元器工作流编排
│   ├── 意图识别      识别用户请求类型
│   ├── 法条检索流    调用得理法规检索 API
│   ├── 类案检索流    调用得理案例检索 API
│   └── 策略推演流    对方律师视角生成报告
└── 应用服务层
    ├── Web 前端      React 交互界面
    ├── API 网关      RESTful / WebSocket 接口
    └── 导出服务      一键导出至腾讯文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- 腾讯云账号（混元大模型 + 向量数据库）
- 腾讯元器账号

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/liumengyue1234/shensi-mingbian.git
cd shensi-mingbian

# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下配置：

```env
# 腾讯混元大模型
HUNYUAN_SECRET_ID=your_secret_id
HUNYUAN_SECRET_KEY=your_secret_key

# 腾讯云向量数据库
VECTOR_DB_URL=your_vector_db_url
VECTOR_DB_KEY=your_vector_db_key

# 腾讯元器智能体
YUANQI_APP_ID=your_app_id
YUANQI_APP_KEY=your_app_key

# 得理开放平台
DELI_APP_ID=QthdBErlyaYvyXul
DELI_SECRET=EC5D455E6BD348CE8E18BE05926D2EBE
```

### 运行服务

```bash
# 启动后端 API 服务
python app.py

# 启动前端（另开终端）
cd frontend
npm run dev
```

访问 `http://localhost:3000` 即可使用。

---

## 🔌 API 集成

### 得理开放平台

本项目调用得理开放平台提供的两大核心 API：

#### 类案检索

```python
import requests

url = "https://openapi.delilegal.com/api/qa/v3/search/queryListCase"
headers = {
    "appid": "QthdBErlyaYvyXul",
    "secret": "EC5D455E6BD348CE8E18BE05926D2EBE"
}
payload = {
    "pageNo": 1,
    "pageSize": 5,
    "sortField": "correlation",
    "sortOrder": "desc",
    "condition": {
        "keywordArr": ["劳动合同纠纷"]
    }
}
response = requests.post(url, headers=headers, json=payload)
```

#### 法规检索

```python
url = "https://openapi.delilegal.com/api/qa/v3/search/queryListLaw"
payload = {
    "pageNo": 1,
    "pageSize": 5,
    "sortField": "correlation",
    "sortOrder": "desc",
    "condition": {
        "keywords": ["劳动合同解除的法律规定"],
        "fieldName": "semantic"
    }
}
response = requests.post(url, headers=headers, json=payload)
```

### 腾讯元器智能体 API

```python
url = "https://yuanqi.tencent.com/openapi/v1/agent/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {APP_KEY}"
}
payload = {
    "assistant_id": APP_ID,
    "user_id": "user_001",
    "stream": False,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": "帮我分析这份起诉状的风险"}]
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
```

---

## 📂 项目结构

```
shensi-mingbian/
├── README.md                   项目说明
├── requirements.txt            Python 依赖
├── .env.example                环境变量模板
├── app.py                      Flask/FastAPI 主服务
├── config/
│   └── settings.py             全局配置
├── core/
│   ├── case_retrieval.py       类案检索模块
│   ├── law_retrieval.py        法规检索模块
│   ├── strategy_engine.py      诉讼策略推演引擎
│   └── qa_engine.py            对话式问答引擎
├── api/
│   ├── routes.py               API 路由
│   └── schemas.py              请求/响应 Schema
├── agents/
│   ├── lawyer_agent.py         法律顾问智能体
│   └── opponent_agent.py       对方律师视角智能体
├── utils/
│   ├── deli_client.py          得理 API 客户端封装
│   ├── hunyuan_client.py       混元大模型客户端封装
│   └── export.py               腾讯文档导出工具
├── frontend/                   React 前端应用
│   ├── src/
│   │   ├── components/         UI 组件
│   │   ├── pages/              页面
│   │   └── services/           API 服务调用
│   └── package.json
├── docs/
│   ├── architecture.md         架构设计文档
│   ├── api_reference.md        API 接口文档
│   └── demo.md                 演示说明
└── tests/
    ├── test_case_retrieval.py
    └── test_law_retrieval.py
```

---

## 🎯 使用场景

### 场景一：法律咨询

用户输入：「我在上班途中发生车祸，能认定为工伤吗？」

系统响应：
1. 检索相关工伤认定法条（《工伤保险条例》第 14 条等）
2. 匹配 5 个类似案例，展示裁判要旨
3. 给出综合法律意见

### 场景二：诉讼策略推演

用户上传起诉状后，系统：
1. 解析案情要素与争议焦点
2. 切换"对方律师"视角
3. 生成质证意见清单
4. 输出风险提示报告
5. 支持一键导出至腾讯文档

---

## 🏆 参赛信息

- **赛事**：腾讯开悟 服创赛 D06 赛道
- **作品名称**：审思明辨——智判法案双擎系统
- **核心技术栈**：腾讯混元大模型 · 腾讯云向量数据库 · 腾讯元器 · 得理开放平台

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- [腾讯混元大模型](https://hunyuan.tencent.com/)
- [腾讯元器](https://yuanqi.tencent.com/)
- [腾讯云向量数据库](https://cloud.tencent.com/product/vdb)
- [得理开放平台](https://open.delilegal.com/)
