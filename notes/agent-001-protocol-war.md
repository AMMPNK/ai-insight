# Agent 协议战争：为什么 MCP 赢了，接下来谁会赢？

**写于 2026-04-15 | AI Agent | 阅读约 6 分钟**

---

## 结论先行

MCP 已经是事实标准，这场仗打完了。A2A 是下一个竞争点，但还没有决出胜负。真正没人关注但很重要的是 AP2——Agent 自主支付的授权机制，这是 Agentic Commerce 能否规模化的关键。

---

## 为什么 MCP 赢得如此彻底？

2024 年底 Anthropic 发布 MCP 时，市场上已经有很多「工具调用标准化」的尝试（OpenAI 的 Function Calling、LangChain 的 Tool 接口等）。MCP 赢的不是技术更先进，而是**生态策略**。

关键动作：
1. **开放协议而非私有 SDK**：任何人可以实现 MCP Server，不需要依赖 Anthropic 的 SDK
2. **Stdio + HTTP 双模式**：本地工具用 Stdio，远程服务用 HTTP SSE，覆盖了所有场景
3. **优先覆盖高价值服务器**：GitHub、Postgres、Notion、Filesystem——这些是开发者最常用的，先覆盖核心用户

6个月后，市场上已经有几百个 MCP Server。这时候再来一个竞争标准成本极高——要说服所有 Server 提供方重新实现一遍协议。网络效应形成壁垒。

**教训**：协议标准竞争不是技术竞争，是生态竞争，先覆盖核心节点者胜。

---

## A2A 还没有赢

A2A（Agent2Agent）解决的是不同 Agent 之间如何互相发现和通信的问题。Google 推的，方式是每个 Agent 在 `/.well-known/agent-card.json` 暴露自己的能力描述。

技术上很干净，逻辑也对。但有几个问题让我觉得 A2A 还没到「事实标准」的程度：

1. **企业内部 vs 互联网公开**：大多数真实场景的 Multi-Agent 是在企业内部，不需要公开发现。LangGraph、CrewAI 等框架已经有成熟的内部 Agent 编排方案，A2A 的价值在企业内部不明显
2. **安全机制还不成熟**：公开暴露 Agent 能力描述，意味着任何人都能调用你的 Agent。生产环境的认证、计费、访问控制怎么做？规范还不完整
3. **Google 自己在推**：标准的可信度有时候需要竞争对手共同背书，目前 Anthropic 没有明确支持 A2A

A2A 值得跟踪，但不值得现在就梭哈进去。

---

## AP2 是被低估的关键

AP2（Agent Payments Protocol）是整个 Agentic 生态里我认为最值得关注、但关注度最低的协议。

想象一个 Agent 能自动下单采购：它能调用工具（MCP）、能找到供应商 Agent（A2A）、能走完结账流程（UCP）——但最后谁来授权这笔支付？

没有 AP2 或类似机制，企业不敢让 Agent 真正自主执行带金融风险的操作。这是 Agentic Commerce 从「演示」到「生产」的最后一道门。

AP2 的设计思路很务实：
- IntentMandate：事前设定守卫（允许哪些商家、金额上限、是否需要人工确认）
- PaymentMandate：Agent 执行时生成绑定具体订单的授权凭证
- PaymentReceipt：事后形成不可抵赖的审计链

这套机制本质上是**把人类的授权意图用密码学固化下来**，让 Agent 的自主行为有法可依。

---

## 我的判断

2026 年 Agent 基础设施的演进顺序：MCP（已完成）→ A2A（进行中）→ AP2（2026-2027 关键期）→ A2UI/AG-UI（UI 层最后落地）。

作为产品经理，我更关注 AP2 和 AG-UI 这两层：AP2 决定 Agent 能做多大的事，AG-UI 决定用户怎么跟 Agent 交互。这两层打通了，Agentic 产品才能真正超越「聊天」范式。

---

**参考来源**
- Developer's Guide to AI Agent Protocols — Google Developer Blog
- MCP 官方规范（modelcontextprotocol.io）
- A2A 协议文档（a2a-protocol.org）
