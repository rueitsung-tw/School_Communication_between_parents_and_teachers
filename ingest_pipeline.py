"""
ingest_pipeline.py — 兩階段智慧 Ingest Pipeline

基於 llm_wiki 的 Two-Step Chain-of-Thought Ingest 概念：

  Stage 1（分析）：LLM 閱讀原始文件 → 輸出結構化 JSON 分析
    - 主要主題、重要概念、法令條文引用、與親師溝通的關聯

  Stage 2（生成）：LLM 根據分析 → 輸出 Markdown 摘要 Wiki 頁
    - YAML frontmatter、摘要段落、概念表格、法令列表、應用建議

摘要存放位置：docs/summaries/<原始檔名>_summary.md
向量索引時優先使用摘要，fallback 回原始文字直接切段。
"""

import os
import sys
import re
import json
import hashlib
import datetime
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── 常數 ──────────────────────────────────────────────────────────────────────

SUMMARIES_DIR_NAME = "summaries"   # 在 docs/ 下的子目錄名稱
MAX_TEXT_FOR_INGEST = 6_000        # 為 Stage 1 的 JSON 回覆保留 context window 空間
MAX_STAGE1_OUTPUT_TOKENS = 1_200   # 避免輸入截斷後仍因輸出預留不足而被拒絕

# ── 文字清洗 ──────────────────────────────────────────────────────────────────

def clean_text_for_llm(text: str) -> str:
    """
    清理即將傳給 LLM 的文字：
    1. 移除 ASCII 控制字元 ([\x00-\x08\x0b\x0c\x0e-\x1f\x7f])，特別是 PDF 提取時常產生的 \x00 (Null Byte)
    2. 移除 Unicode 零寬字元 ([\u200b-\u200d\ufeff])
    """
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
    return text

# ── Stage 1：分析提示詞 ────────────────────────────────────────────────────────

STAGE1_SYSTEM_PROMPT = """\
你是國小教育領域的知識整理專家，專精台灣教育法令與親師溝通。
請仔細閱讀以下文件內容，以「純 JSON」格式輸出分析結果，不要有任何前後說明文字。
輸出格式：
{
  "main_topics": ["主題1", "主題2"],
  "key_concepts": [
    {"term": "概念名稱", "definition": "簡短定義（1-2句）"}
  ],
  "legal_references": [
    {"article": "條號或法令名稱", "summary": "條文核心重點（1-2句）"}
  ],
  "parent_teacher_relevance": "此文件與親師溝通的具體關聯（2-3句，說明教師可如何應用）",
  "document_type": "法令條文 | 教育研究 | 實務指引 | 其他"
}
注意：請使用繁體中文，僅輸出 JSON，不要輸出 markdown 或其他格式。
"""

STAGE1_USER_TEMPLATE = """\
文件名稱：{filename}
文件內容：
{text}
"""

# ── Stage 2：生成摘要提示詞 ───────────────────────────────────────────────────

STAGE2_SYSTEM_PROMPT = """\
你是國小親師溝通知識庫的編輯，請根據以下的文件分析結果，
生成一份結構化的繁體中文 Markdown 知識摘要頁。

格式要求（請嚴格遵守）：
1. 開頭必須有 YAML frontmatter（三個 --- 包圍）
2. ## 文件摘要 — 2-3段說明文件核心內容，使用自然段落文字，禁止條列
3. ## 重要概念 — 表格格式（| 概念 | 說明 |）
4. ## 相關法令 — 若有法令引用，列出條號與一句話摘要；若無則省略此節
5. ## 親師溝通應用 — 具體說明教師如何將此文件知識應用於親師溝通情境（1-2段）

語氣規範：
- 使用台灣繁體中文慣用語（說「導師」不說「班主任」）
- 語氣溫暖、半正式，非官腔
- 嚴禁條列式（1. 2. 3. 或 •）出現在「文件摘要」與「親師溝通應用」段落
- 適當使用省略號（……）增加呼吸感
"""

STAGE2_USER_TEMPLATE = """\
原始文件名稱：{filename}
生成時間：{generated_at}

分析結果：
{analysis_json}

請生成符合格式要求的 Markdown 摘要頁。
"""

# ── LLM 呼叫（重用與 utils.py 相同的 Ollama/OpenAI 邏輯） ───────────────────

def _call_ollama(
    base_url: str,
    model_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    api_key: str = "ollama"
) -> Optional[str]:
    """
    呼叫 Ollama（OpenAI 相容介面），回傳回覆字串。
    temperature 預設 0.3（比問答低，確保分析穩定）。
    具備 180 秒超時設定、3 次重試與增強型 HTTP 400 回應解析機制。
    """
    import time
    base = base_url.strip().rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3].rstrip("/")
    endpoint = f"{base}/v1/chat/completions"

    payload = json.dumps({
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": temperature,
        "max_tokens": MAX_STAGE1_OUTPUT_TOKENS,
        "stream": False
    }).encode("utf-8")

    max_retries = 3
    for attempt in range(max_retries):
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            msg = f"HTTP Error {e.code}: {e.reason}"
            if error_body:
                msg += f" | 伺服器回應: {error_body[:300]}"
            if attempt < max_retries - 1:
                print(f"[Ingest] ⚠️ LLM 呼叫失敗（第 {attempt + 1} 次重試）: {msg}")
                time.sleep(3 * (attempt + 1))
            else:
                print(f"[Ingest] ⚠️ LLM 呼叫失敗：{msg}")
                return None
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[Ingest] ⚠️ LLM 呼叫失敗（第 {attempt + 1} 次重試）: {e}")
                time.sleep(3 * (attempt + 1))
            else:
                print(f"[Ingest] ⚠️ LLM 呼叫失敗：{e}")
                return None
    return None


# ── 核心：兩階段 Ingest ────────────────────────────────────────────────────────

def analyze_document(
    text: str,
    filename: str,
    ollama_url: str,
    model_name: str,
    api_key: str = "ollama"
) -> Optional[Dict[str, Any]]:
    """
    Stage 1：呼叫 LLM 分析文件，回傳 JSON 格式的分析結果 dict。
    失敗時回傳 None。
    """
    # 進行文字清洗（移除控制字元與不可列印字元）
    cleaned = clean_text_for_llm(text)

    # 截斷過長的文字（避免超過 context window）
    truncated = cleaned[:MAX_TEXT_FOR_INGEST]
    if len(cleaned) > MAX_TEXT_FOR_INGEST:
        print(f"[Ingest] ⚠️ 文件超過 {MAX_TEXT_FOR_INGEST} 字，已截斷後送入 Stage 1")

    user_msg = STAGE1_USER_TEMPLATE.format(filename=filename, text=truncated)
    raw = _call_ollama(ollama_url, model_name, STAGE1_SYSTEM_PROMPT, user_msg, temperature=0.2, api_key=api_key)

    if not raw:
        return None

    # 嘗試解析 JSON（LLM 有時會夾帶 ```json ... ``` 或前後說明文字）
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # 擷取第一個完整 JSON 物件，避免模型在 JSON 前後加說明導致整體解析失敗。
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start:end + 1]

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[Ingest] ⚠️ Stage 1 JSON 解析失敗：{e}\n原始輸出：{raw[:300]}")
        return None


def generate_summary_md(
    analysis: Dict[str, Any],
    filename: str,
    ollama_url: str,
    model_name: str,
    api_key: str = "ollama"
) -> Optional[str]:
    """
    Stage 2：根據 Stage 1 的分析結果，呼叫 LLM 生成 Markdown 摘要頁。
    回傳 Markdown 字串，失敗時回傳 None。
    """
    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)

    user_msg = STAGE2_USER_TEMPLATE.format(
        filename=filename,
        generated_at=generated_at,
        analysis_json=analysis_json
    )
    md_content = _call_ollama(ollama_url, model_name, STAGE2_SYSTEM_PROMPT, user_msg, temperature=0.4, api_key=api_key)

    if not md_content:
        return None

    # 若 LLM 輸出沒有 YAML frontmatter，補一個
    if not md_content.strip().startswith("---"):
        topics = analysis.get("main_topics", [])
        fallback_front = (
            "---\n"
            f"source: {filename}\n"
            f"topics: {json.dumps(topics, ensure_ascii=False)}\n"
            f"generated_at: {generated_at}\n"
            "---\n\n"
        )
        md_content = fallback_front + md_content

    return md_content


def run_two_step_ingest(
    filepath: str,
    raw_text: str,
    ollama_url: str,
    model_name: str,
    api_key: str = "ollama",
    summaries_dir: Optional[str] = None
) -> Optional[str]:
    """
    對單一文件執行完整的兩階段 Ingest。

    Args:
        filepath: 原始文件路徑（用於生成摘要檔名）
        raw_text: 已提取的原始文字（由 rag_engine 提供，避免重複提取）
        ollama_url: Ollama 伺服器網址
        model_name: 使用的模型名稱
        api_key: API 金鑰
        summaries_dir: 摘要儲存目錄（預設：與 filepath 同層的 summaries/ 子目錄）

    Returns:
        摘要 .md 的檔案路徑（成功）或 None（失敗）
    """
    if not raw_text or not raw_text.strip():
        print(f"[Ingest] ⚠️ 空文件，跳過：{filepath}")
        return None

    filename = os.path.basename(filepath)
    stem = Path(filepath).stem

    # 決定摘要存放目錄
    if summaries_dir is None:
        parent_dir = str(Path(filepath).parent)
        summaries_dir = os.path.join(parent_dir, SUMMARIES_DIR_NAME)
    os.makedirs(summaries_dir, exist_ok=True)

    summary_path = os.path.join(summaries_dir, f"{stem}_summary.md")

    print(f"[Ingest] 🧠 Stage 1：分析文件《{filename}》...")
    analysis = analyze_document(raw_text, filename, ollama_url, model_name, api_key)
    if analysis is None:
        print(f"[Ingest] ❌ Stage 1 失敗，跳過《{filename}》")
        return None

    print(f"[Ingest] ✍️  Stage 2：生成摘要《{filename}》...")
    md_content = generate_summary_md(analysis, filename, ollama_url, model_name, api_key)
    if md_content is None:
        print(f"[Ingest] ❌ Stage 2 失敗，跳過《{filename}》")
        return None

    # 寫入摘要檔
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[Ingest] ✅ 摘要已儲存：{summary_path}")
    return summary_path


# ── 工具函式 ──────────────────────────────────────────────────────────────────

def get_summary_path(source_filepath: str, summaries_dir: str) -> str:
    """給定原始文件路徑，回傳對應摘要 .md 的預期路徑。"""
    stem = Path(source_filepath).stem
    return os.path.join(summaries_dir, f"{stem}_summary.md")


def summary_exists(source_filepath: str, summaries_dir: str) -> bool:
    """檢查某原始文件是否已有對應且完整的摘要（檔案存在且非 0 byte）。"""
    path = get_summary_path(source_filepath, summaries_dir)
    return os.path.isfile(path) and os.path.getsize(path) > 0


def list_summary_status(docs_dir: str) -> Dict[str, bool]:
    """
    掃描 docs/ 目錄，回傳每個原始文件的摘要狀態。
    回傳格式：{filename: has_summary}
    """
    summaries_dir = os.path.join(docs_dir, SUMMARIES_DIR_NAME)
    supported = {".pdf", ".txt", ".md"}
    result = {}

    if not os.path.exists(docs_dir):
        return result

    for fname in os.listdir(docs_dir):
        fpath = os.path.join(docs_dir, fname)
        if os.path.isfile(fpath) and Path(fname).suffix.lower() in supported:
            result[fname] = summary_exists(fpath, summaries_dir)

    return result
