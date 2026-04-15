# MLA vs GQA：为什么 DeepSeek 选了一条更难的路？

**写于 2026-04-15 | 大模型架构 | 阅读约 5 分钟**

---

## 结论先行

MLA（Multi-Head Latent Attention）在 KV Cache 压缩率和建模精度上同时优于 GQA，代价是实现复杂度显著上升。DeepSeek 选择 MLA 不是因为它更简单，而是因为在极大规模模型中，KV Cache 的内存墙问题比实现复杂度更致命。

---

## 问题背景：KV Cache 是推理的瓶颈

自回归生成的本质是：每生成一个 token，都要重新访问之前所有 token 的 Key 和 Value。序列越长，存储这些 KV 的内存开销越大。

对于 671B 的 DeepSeek V3，如果用标准 MHA：
- 每个 token 需要存储 `num_heads × head_dim × 2`（K + V）个浮点数
- 128K 上下文 × 大 batch size = 内存爆炸

这是模型无法服务长上下文的根本原因，不是算力不够，是内存放不下。

---

## GQA 的解法：共享 Key/Value

GQA（Grouped Query Attention）的思路很直接：**让多个 Query Head 共用一套 K/V**。

比如 64 个 Query Head 分成 8 组，每组共享 1 套 K/V，KV Cache 直接缩小 8 倍。

**代价**：多个 Query Head 用同一套 K/V 做 attention，表达能力有损耗。消融实验显示 GQA 相比 MHA 有轻微的精度下降，但工业界普遍接受这个 tradeoff（Llama 2/3 都用 GQA）。

---

## MLA 的解法：低秩压缩 KV 投影

MLA 的思路更激进：**不共享，而是压缩**。

具体做法：
1. 训练时，把 K/V 投影到一个低维潜空间（latent space），维度远小于原始 head_dim
2. 推理时，KV Cache 只存储这个压缩后的低维向量
3. 计算 attention 时，临时解压（多一次矩阵乘法）

这意味着：
- **KV Cache 大小**：取决于潜空间维度，可以压缩到 MHA 的 1/10 甚至更小
- **精度**：低秩压缩不等于随机降维，通过训练学习到的压缩矩阵能够保留最重要的信息

DeepSeek-V2 的消融实验是关键数据点：在相同参数量下，**MLA 的困惑度（perplexity）比 GQA 更低，比 MHA 也略低**。这个结果让人意外——压缩反而提升了建模能力？

可能的解释：低秩分解本身起到了一种正则化效果，迫使模型学习更紧凑的注意力表示。

---

## 我的判断

GQA 是工程妥协，MLA 是架构创新。

对于需要在单机服务超长上下文的场景（如 128K+ 的代码 Agent），MLA 的内存效率优势会被充分放大。GQA 适合快速工程落地，MLA 适合追求极限性能的旗舰模型。

2026 年的趋势已经明确：Kimi K2（1T 参数）沿用 MLA，说明这个架构在超大规模下也经受住了验证。GQA 不会消失，但 MLA 会成为旗舰模型的标配。

---

**参考来源**
- DeepSeek-V2 技术报告（arxiv.org/abs/2405.04434）
- The Big LLM Architecture Comparison — Sebastian Raschka（2026-04-02）
- DeepSeek-V3 Explained: Multi-head Latent Attention — Medium（2025-01-31）
