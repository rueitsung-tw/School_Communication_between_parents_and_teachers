import os
import re
import json
import streamlit as st
import utils
from rag_engine import RAGEngine

# 設定頁面配置
st.set_page_config(
    page_title="國小親師溝通小幫手 — AI 隱形、教學顯性",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 設定路徑 ───────────────────────────────────────────────────────────────────
BASE_DIR    = r"F:\親師溝通提示詞"
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DOCS_DIR    = os.path.join(BASE_DIR, "docs")
TAXONOMY_PATH = os.path.join(BASE_DIR, "theme_taxonomy.md")
VOCAB_PATH    = os.path.join(BASE_DIR, "taiwan_vocab.md")

# ── 讀取設定 ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    """讀取 config.json，取得固定的模型與 API 設定。"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

cfg         = load_config()
provider    = cfg.get("provider", "ollama")
base_url    = cfg.get("ollama_url", "http://localhost:11434")
current_key = cfg.get("api_key", "ollama")
model_name  = cfg.get("model_name", "gemma3:12b")

# ── RAG 引擎初始化（使用 st.session_state 確保單例） ──────────────────────────
if "rag_engine" not in st.session_state:
    engine = RAGEngine(ollama_base_url=base_url, docs_dir=DOCS_DIR)
    ok = engine.initialize()
    if ok:
        engine.start_watching()   # 啟動背景監控
    st.session_state["rag_engine"] = engine
    st.session_state["rag_initialized"] = ok

rag: RAGEngine = st.session_state["rag_engine"]

# ── 快取資料載入 ────────────────────────────────────────────────────────────────
@st.cache_data
def get_prompts():
    return utils.load_all_prompts(PROMPTS_DIR)

@st.cache_data
def get_taxonomy():
    return utils.load_theme_taxonomy(TAXONOMY_PATH)

prompts_db = get_prompts()
taxonomy_db = get_taxonomy()

# ── 側邊欄 ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    # 1. 模型設定資訊
    st.header("⚙️ 目前模型設定")
    st.info(
        f"**供應商**：{provider.upper()}\n\n"
        f"**API 網址**：{base_url}\n\n"
        f"**模型**：{model_name}\n\n"
        f"*如需變更，請編輯 `config.json`。*"
    )
    st.markdown("---")

    # 2. 知識庫管理面板
    st.header("📂 知識庫管理（RAG）")

    rag_summary = rag.get_summary()
    st.caption(rag_summary["status"])

    if rag_summary["indexed_files"]:
        st.markdown("**已索引文件：**")
        for fname in rag_summary["indexed_files"]:
            st.markdown(f"- 📄 {fname}")
        st.caption(
            f"共 **{rag_summary['total_chunks']}** 個段落｜"
            f"最後更新：{rag_summary['last_updated']}"
        )
    else:
        st.warning("⚠️ docs/ 目錄尚無可索引文件。\n請將 PDF / TXT / MD 放入 docs/ 資料夾。")

    col_r1, col_r2 = st.columns(2)
    if col_r1.button("🔄 增量更新", use_container_width=True, help="掃描新增或修改的文件並更新索引"):
        with st.spinner("正在掃描並更新索引..."):
            rag._sync_index()
        st.success("✅ 索引已更新！")
        st.rerun()

    if col_r2.button("🔁 完整重建", use_container_width=True, help="清除所有索引，從頭重新建立（大型文件建議在離峰時間操作）"):
        with st.spinner("正在完整重建索引，請稍候..."):
            rag.force_reindex()
        st.success("✅ 索引重建完成！")
        st.rerun()

    st.caption(
        "📌 **新增文件方式**：將 `.pdf` / `.txt` / `.md` 放入 `docs/` 資料夾，"
        "按「🔄 增量更新」即可自動索引，無需重啟系統。"
    )

    st.markdown("---")

    # 3. 主題知識卡（動態依選擇主題顯示，後段程式碼填入）
    st.header("📖 心理學與法令知識卡")

# ── 主題選單 ────────────────────────────────────────────────────────────────────
theme_options = {
    "00_通用": "00 通用親師溝通情境",
    "01_座位安排與班級經營": "01 座位安排與班級經營爭議",
    "02_成績評量與學習表現": "02 成績評量與學習表現質疑",
    "03_同儕衝突與霸凌處理": "03 同儕衝突與霸凌處理",
    "04_管教方式與獎懲制度": "04 管教方式與獎懲制度",
    "05_作業量與課業壓力": "05 作業量與課業壓力",
    "06_特殊生權益與融合教育": "06 特殊生權益與融合教育",
    "07_校園安全與意外事故": "07 校園安全與意外事故",
    "08_生活照顧與責任邊界": "08 生活照顧與責任邊界",
    "09_班費使用與行政事務": "09 班費使用與行政事務",
    "10_LINE群組溝通禮儀與界線": "10 LINE 群組溝通禮儀與界線"
}

available_themes = [k for k in theme_options.keys() if any(k in pk for pk in prompts_db.keys())]

selected_theme_key = st.selectbox(
    "🎯 請選擇親師溝通主題：",
    available_themes,
    format_func=lambda x: theme_options[x]
)

# ── 側邊欄：主題知識卡 ─────────────────────────────────────────────────────────
theme_id_match = re.search(r"(\d+)", selected_theme_key)
if theme_id_match:
    theme_id = int(theme_id_match.group(1))
    if theme_id in taxonomy_db:
        theme_info = taxonomy_db[theme_id]
        st.sidebar.subheader(f"📌 {theme_info['name']}")
        data = theme_info["data"]
        if "底層心理需求" in data:
            st.sidebar.info(f"💡 **底層心理需求（薩提爾冰山）**\n\n{data['底層心理需求']}")
        if "常見教師地雷" in data:
            st.sidebar.warning(f"⚠️ **常見教師地雷句**\n\n{data['常見教師地雷']}")
        if "相關法令依據" in data:
            st.sidebar.success(f"⚖️ **相關法令依據**\n\n{data['相關法令依據']}")
        if "建議溝通策略" in data:
            st.sidebar.markdown(f"🤝 **建議溝通策略**\n\n{data['建議溝通策略']}")
    else:
        st.sidebar.info("💡 **通用親師溝通**：適合處理非特定爭議（如例行通知、日常關懷）的溝通情境。建議運用非暴力溝通三段式結構。")
else:
    st.sidebar.info("💡 **通用親師溝通**：適合處理非特定爭議（如例行通知、日常關懷）的溝通情境。建議運用非暴力溝通三段式結構。")

# ── 主標題 ──────────────────────────────────────────────────────────────────────
st.title("🏫 國小親師溝通小幫手")
st.markdown("##### 💡 AI 隱形、教學顯性：為一線教師行政減負與情緒勞動降溫")
st.write("本系統基於非暴力溝通（NVC）、薩提爾冰山理論、心理防衛機制與台灣教育法令，協助教師分析家長訴求，並生成有溫度、有呼吸感的回覆。")

# ── 輸入區 ──────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    parent_message = st.text_area(
        "📥 請貼上家長的原始訊息：",
        height=180,
        placeholder="例如：「老師，為什麼這次換座位把我們家小明換到最後面？他近視你看不到怎麼辦？...」"
    )

with col2:
    context = st.text_area(
        "📝 教師補充背景資訊（選填）：",
        height=180,
        placeholder="例如：「小明有戴眼鏡矯正。座位固定每四週輪換一次。」\n\n提供背景資訊能讓 AI 生成更精確、更符合事實的回覆。"
    )

# ── RAG 語意搜尋：取得相關知識段落 ───────────────────────────────────────────────
def build_rag_context(query: str) -> tuple[str, list]:
    """
    使用語意搜尋從向量資料庫取出最相關段落，
    組合成 RAG context 字串，同時回傳原始結果供 UI 展示。
    """
    results = rag.retrieve(query, top_k=3)
    if not results:
        return "", []

    lines = ["【語意搜尋知識庫參考段落（Top-3 最相關）】"]
    for i, r in enumerate(results, 1):
        lines.append(f"\n--- 段落 {i}（來源：{r['filename']}，相似度：{1 - r['distance']:.2%}）---")
        lines.append(r["text"])
    return "\n".join(lines), results

# 取得本地靜態知識庫脈絡
knowledge_context = utils.build_knowledge_context(selected_theme_key, taxonomy_db, vocab_filepath=VOCAB_PATH)

# ── 執行按鈕 ────────────────────────────────────────────────────────────────────
st.markdown("### 🚀 開始處理")

rag_status_text = (
    f"🔍 **RAG 語意搜尋**：已啟用（{rag_summary['total_chunks']} 個段落可搜尋）"
    if rag_summary["total_chunks"] > 0
    else "⚠️ **RAG 語意搜尋**：docs/ 尚無索引文件，僅使用靜態知識庫"
)
st.caption(f"🛡️ **知識庫狀態**：已啟用本地專案知識庫 + 台灣繁體中文辭彙規範。{rag_status_text}")

btn_col1, btn_col2, _ = st.columns([1, 1, 2])

# 取得對應主題的提示詞
db_keys = list(prompts_db.keys())
matched_keys = [k for k in db_keys if selected_theme_key in k]

system_prompt_a = None
system_prompt_b = None

if selected_theme_key == "00_通用":
    for k in db_keys:
        if "TypeA" in k:
            system_prompt_a = prompts_db[k].get("Type A")
        elif "TypeB" in k:
            system_prompt_b = prompts_db[k].get("Type B")
else:
    if matched_keys:
        system_prompt_a = prompts_db[matched_keys[0]].get("Type A")
        system_prompt_b = prompts_db[matched_keys[0]].get("Type B")

# 組合 User Message
if context.strip():
    user_message = f"家長原始訊息如下：\n「{parent_message}」\n\n教師補充背景如下：\n「{context}」"
else:
    user_message = f"家長原始訊息如下：\n「{parent_message}」"

# ── 執行分析 Type A ─────────────────────────────────────────────────────────────
if btn_col1.button("🔍 分析家長需求 (Type A)", use_container_width=True):
    if not current_key.strip():
        st.error("❌ 請在側邊欄輸入 API 金鑰後再執行！")
    elif not parent_message.strip():
        st.warning("⚠️ 請先貼入家長的原始訊息！")
    elif not system_prompt_a:
        st.error("❌ 找不到此主題的 Type A 分析提示詞！")
    else:
        with st.spinner("🔍 AI 正在深入分析家長訴求與冰山下的情緒..."):
            try:
                # 語意搜尋：以家長訊息為 query
                rag_context, rag_results = build_rag_context(parent_message)

                prompt_run = system_prompt_a
                if "{在此貼上家長的訊息}" in prompt_run:
                    prompt_run = prompt_run.replace("{在此貼上家長的訊息}", parent_message)

                # 組合：靜態知識庫 + 語意搜尋結果
                full_system_prompt = prompt_run + "\n\n" + knowledge_context
                if rag_context:
                    full_system_prompt += "\n\n" + rag_context

                response = utils.call_llm_api(
                    provider=provider,
                    api_key=current_key,
                    model_name=model_name,
                    system_prompt=full_system_prompt,
                    user_message=user_message,
                    base_url=base_url
                )
                st.success("✅ 分析完成！")
                st.markdown("### 📊 家長訴求與底層需求分析報告")
                st.markdown(response)

                with st.expander("📚 查看本次 AI 參考的知識庫依據", expanded=False):
                    st.markdown("**靜態知識庫（主題分類）：**")
                    st.markdown(knowledge_context)
                    if rag_results:
                        st.markdown("---\n**語意搜尋結果（docs/ 文件）：**")
                        for r in rag_results:
                            st.markdown(f"**{r['filename']}**（相似度：{1 - r['distance']:.2%}）")
                            st.text(r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"])

            except Exception as e:
                st.error(f"❌ 呼叫 API 發生錯誤：{str(e)}")

# ── 執行生成 Type B ─────────────────────────────────────────────────────────────
if btn_col2.button("✉️ 生成回覆草稿 (Type B)", use_container_width=True):
    if not current_key.strip():
        st.error("❌ 請在側邊欄輸入 API 金鑰後再執行！")
    elif not parent_message.strip():
        st.warning("⚠️ 請先貼入家長的原始訊息！")
    elif not system_prompt_b:
        st.error("❌ 找不到此主題的 Type B 生成提示詞！")
    else:
        with st.spinner("✉️ AI 正在以非暴力溝通架構生成溫暖、有呼吸感的回覆..."):
            try:
                # 語意搜尋
                rag_context, rag_results = build_rag_context(parent_message)

                prompt_run = system_prompt_b
                if "{在此貼上家長的訊息}" in prompt_run:
                    prompt_run = prompt_run.replace("{在此貼上家長的訊息}", parent_message)
                if "{選填：教師補充背景}" in prompt_run:
                    prompt_run = prompt_run.replace("{選填：教師補充背景}", context)

                full_system_prompt = prompt_run + "\n\n" + knowledge_context
                if rag_context:
                    full_system_prompt += "\n\n" + rag_context

                response = utils.call_llm_api(
                    provider=provider,
                    api_key=current_key,
                    model_name=model_name,
                    system_prompt=full_system_prompt,
                    user_message=user_message,
                    base_url=base_url
                )
                st.success("✅ 草稿生成完成！")
                st.markdown("### 💬 AI 建議回覆草稿")
                st.info("💡 以下草稿已依非暴力溝通三段式結構（同理 -> 事實 -> 解方）生成，無條列式與官方用語。您可直接在下方編輯器微調。")

                edited_response = st.text_area(
                    "✏️ 編輯與微調回覆：",
                    value=response,
                    height=200
                )
                st.caption("💡 提示：您可直接點擊編輯框右上角的複製按鈕（滑鼠移過去會顯示），即可貼回 LINE 或聯絡簿。")

                with st.expander("📚 查看本次 AI 參考的知識庫依據", expanded=False):
                    st.markdown("**靜態知識庫（主題分類）：**")
                    st.markdown(knowledge_context)
                    if rag_results:
                        st.markdown("---\n**語意搜尋結果（docs/ 文件）：**")
                        for r in rag_results:
                            st.markdown(f"**{r['filename']}**（相似度：{1 - r['distance']:.2%}）")
                            st.text(r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"])

            except Exception as e:
                st.error(f"❌ 呼叫 API 發生錯誤：{str(e)}")

# ── 頁尾 ────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
    "親師溝通小幫手 v2.0.0 | 基於「AI 隱形、教學顯性」理念開發 | RAG 語意搜尋版"
    "</div>",
    unsafe_allow_html=True
)
