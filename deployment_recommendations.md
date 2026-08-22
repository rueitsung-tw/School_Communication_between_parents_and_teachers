# 💻 專案硬體部署與模型選擇建議

根據專案需求（台灣教育情境繁中處理、心理學/NVC 架構、RAG 檢索生成與法律規範遵循），針對四種硬體層級的模型選擇與輸出品質差異分析如下：

### 硬體模型選擇建議

* **最低單機門檻：GTX 1650（4GB VRAM / 16GB RAM / LM Studio 或 Ollama）**
  * **推薦模型**：`gemma-2:2b` / `gemma-3:4b-instruct-q4_K_M` 或 `qwen2.5:3b-instruct-q4_K_M`
  * **配置與多模型考量**：
    * 扣除系統後可用 VRAM 約 2.5–3GB，4B `Q4_K_M` 模型大小約 3.0–3.4GB，需開啟 CPU RAM 卸載（Offload）支援。
    * **LM Studio 載入注意事項**：在 4GB VRAM 顯卡上，**不建議同時在 LM Studio 顯存中載入兩個模型**（如 LLM + `nomic-embed-text`）。建議將 `nomic-embed-text` Embedding 模型設定為 **純 CPU 執行**（或由 Python 端經由 `sentence-transformers` / CPU 直接計算向量），將有限的 4GB 顯存完全留給 LLM 主模型。
    * **Context Window**：建議限制在 **2K ~ 4K**，並搭配 Top-2 精簡知識卡。

* **設備 1：RTX 3060 Ti（12GB VRAM / Ollama）**
  * **推薦模型**：`gemma2:9b-instruct-q4_K_M` 或 `qwen2.5:7b-instruct-q8_0` / `qwen2.5:14b-instruct-q4_K_M`
  * **配置考量**：12GB 顯存扣除 RAG 的 embedding 模型（`nomic-embed-text` 約佔數百 MB）與 4K~8K context window 後，9B（Q4/Q5）或 14B（Q4_K_M）為極限甜蜜點。若選 14B Q4 顯存剛好滿載，推論速度約在 25–40 tokens/s。

* **設備 2：Mac mini Pro（24GB 統一記憶體 / vLLM 或 MLX/Ollama）**
  * **推薦模型**：`qwen2.5:14b-instruct-q8_0` 或 `qwen2.5:32b-instruct-q4_K_M` / `gemma3:12b`
  * **注意事項**：vLLM 在 macOS (Apple Silicon Metal) 上的支援度與最佳化相對受限，若遇到環境相容問題，建議改用 **Ollama** 或 **MLX (vLLM-Metal 替代方案)**。
  * **配置考量**：24GB 統一記憶體扣除系統保留約 4–6GB，可使用約 18–19GB，能流暢載入 14B 高量化版本（Q8/FP16）或 32B 的 Q4 量化版。

* **設備 3：RTX 5080（16GB VRAM / Ollama 遠端）**
  * **推薦模型**：`gemma3:12b`（即專案預設）、`qwen2.5:14b-instruct-q8_0` 或 `deepseek-r1:14b`
  * **配置考量**：具備高頻寬記憶體與強大算力，16GB VRAM 裝載 12B–14B 規模模型時，可開滿 8K–16K 長上下文與較高批次，兼顧極佳的推論速度（>60 tokens/s）與台灣教育用語遵循度。

---

### 設備與模型輸出品質差異

| 比較項目 | 最低門檻（GTX 1650 / 2B–4B） | 設備 1（3060 Ti / 7B–9B） | 設備 2（Mac mini Pro / 14B–32B） | 設備 3（5080 / 12B–14B） |
| --- | --- | --- | --- | --- |
| **繁體中文與台灣在地用語** | 需仰賴 `taiwan_vocab.md` 與 Prompt 範例引導校正 | 容易出現中國用語（需仰賴 `taiwan_vocab.md` 強制校正） | 14B/32B 對台灣語境掌握佳，詞彙自然 | 語感精準自然，能穩定消化在地教育術語 |
| **NVC / 冰山理論推理深度** | 能生成基本架構，同理心較導向模板化 | 形式上符合格式，但同理心較為模板化、生硬 | 深度解碼家長情緒與潛在焦慮，洞察力高 | 邏輯推論流暢，層次感與同理轉折自然 |
| **RAG 檢索與法規遵循準確率** | 建議限制 Top-2 檢索，上下文需控制在 2K~4K | 上下文過長時偶爾忽略細節或產生幻覺 | 檢索整合度好，能精確對齊兒少法與霸凌防制細則 | 檢索精準度高，能嚴格依據 Top-3 知識卡輸出 |
| **生成速度與穩定度** | 8–15 t/s (需 CPU RAM 協助卸載)，單機離線可用 | 中等（約 25–40 t/s），顯存餘裕較吃緊 | 穩定流暢（約 20–35 t/s），記憶體餘裕大 | 極快（>60 t/s），多輪修訂或長文本即時反饋佳 |

---

### 綜合落地建議

* **首選部署**：若追求穩定與速度，以 **設備 3 (RTX 5080)** 作為集中式遠端 API 服務端，搭配 `qwen2.5:14b-instruct` 或預設 `gemma3:12b`，在回覆品質（同理心維度、法規正確性）與速度上表現最均衡。
* **單機/個人使用**：若為單機離線環境，**設備 2 (Mac mini)** 載入 `qwen2.5:14b` 效果最佳；**設備 1 (3060 Ti)** 建議精簡知識庫注入長度（Top-2）；若為**入門設備 (GTX 1650)**，請確保將 Embedding 模型切換為 CPU 執行，並使用 4B Q4_K_M 以下模型搭配 2K~4K Context Window。
