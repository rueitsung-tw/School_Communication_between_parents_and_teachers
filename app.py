import os
import re
import json
import importlib
import streamlit as st
import utils
importlib.reload(utils)
from rag_engine import RAGEngine

# 設定頁面配置
st.set_page_config(
    page_title="國小親師溝通小幫手 — AI 隱形、教學顯性",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 設定路徑 ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DOCS_DIR    = os.path.join(BASE_DIR, "docs")
TAXONOMY_PATH = os.path.join(BASE_DIR, "theme_taxonomy.md")
VOCAB_PATH    = os.path.join(BASE_DIR, "taiwan_vocab.md")

# ── 讀取設定 ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    """讀取 config.json，取得固定的模型與 API 設定。"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "provider": "ollama",
        "ollama_url": "http://localhost:11434",
        "api_key": "ollama",
        "model_name": "gemma3:12b",
        "two_step_ingest": True,
        "ingest_model": "",
        "admin_password": "12345678"
    }

cfg         = load_config()
provider    = cfg.get("provider", "ollama")
base_url    = cfg.get("ollama_url", "http://localhost:11434")
current_key = cfg.get("api_key", "ollama")
model_name  = cfg.get("model_name", "gemma3:12b")
two_step_ingest = cfg.get("two_step_ingest", True)
ingest_model    = cfg.get("ingest_model", "")
admin_password  = str(cfg.get("admin_password", "12345678"))
embedding_url   = cfg.get("embedding_url", base_url)
embedding_model = cfg.get("embedding_model", "nomic-embed-text")

# ── RAG 引擎初始化（使用 st.session_state 確保單例） ──────────────────────────
if "rag_engine" not in st.session_state:
    engine = RAGEngine(
        ollama_base_url=base_url,
        docs_dir=DOCS_DIR,
        two_step_ingest=two_step_ingest,
        ingest_model=ingest_model,
        api_key=current_key,
        embedding_url=embedding_url,
        embedding_model=embedding_model
    )
    ok = engine.initialize()
    if ok:
        engine.start_watching()
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

# ── 已索引文件與智慧摘要對話框 ──────────────────────────────────────────────────
@st.dialog("📋 已索引文件與智慧摘要清單")
def show_indexed_files_dialog(rag_summary: dict):
    if rag_summary.get("two_step_ingest"):
        summarized = rag_summary["summarized_count"]
        total_docs = rag_summary["total_docs"]
        st.markdown(f"### 🧠 智慧摘要狀態（共 {summarized}/{total_docs} 份文件）")
        status_dict = rag_summary.get("summary_status", {})
        if status_dict:
            for fname, has_summary in status_dict.items():
                icon = "✅ 已摘要" if has_summary else "⏳ 處理中/等待摘要"
                st.markdown(f"- **{icon}**：`{fname}`")
        else:
            st.info("`docs/` 目錄尚無文件。")
    else:
        st.markdown("### 📄 已索引檔案清單")
        files = rag_summary.get("indexed_files", [])
        if files:
            for fname in files:
                st.markdown(f"- 📄 `{fname}`")
        else:
            st.info("尚無已索引檔案。")

    st.caption(
        f"共 **{rag_summary.get('total_chunks', 0)}** 個段落｜"
        f"最後更新：{rag_summary.get('last_updated', '未知')}"
    )

# ── 側邊欄 ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    # 1. 模型設定資訊
    st.header("⚙️ 目前模型設定")
    st.success("✅ 模型已連接成功")
    st.caption("如需變更，請編輯 `config.json`。")
    st.markdown("---")

    # 2. 知識庫管理面板
    st.header("📂 知識庫管理（RAG）")

    rag_summary = rag.get_summary()
    st.caption(rag_summary["status"])

    # 簡短顯示摘要統計與彈窗連結按鈕
    if rag_summary.get("two_step_ingest"):
        summarized = rag_summary["summarized_count"]
        total_docs = rag_summary["total_docs"]
        st.caption(f"🧠 **智慧摘要**：{summarized}/{total_docs} 份文件已 LLM 摘要")
    else:
        st.caption(f"📄 **已索引文件**：{len(rag_summary.get('indexed_files', []))} 份")

    if rag_summary["total_chunks"] > 0 or rag_summary["indexed_files"]:
        st.caption(
            f"共 **{rag_summary['total_chunks']}** 個段落｜"
            f"最後更新：{rag_summary['last_updated']}"
        )
    else:
        st.warning("⚠️ `docs/` 目錄尚無可索引文件。")

    if st.button("📋 查閱已索引文件清單", use_container_width=True):
        show_indexed_files_dialog(rag_summary)

    st.markdown("---")

    # 3. 管理員功能區塊（密碼解鎖防護）
    if "is_admin_authenticated" not in st.session_state:
        st.session_state["is_admin_authenticated"] = False

    st.subheader("🔐 管理員控制台")

    if not st.session_state["is_admin_authenticated"]:
        with st.form("admin_login_form"):
            input_pwd = st.text_input("🔑 輸入管理者密碼", type="password", placeholder="預設密碼 12345678")
            submit_pwd = st.form_submit_button("🔓 解鎖管理功能", use_container_width=True)
            if submit_pwd:
                if input_pwd == admin_password:
                    st.session_state["is_admin_authenticated"] = True
                    st.success("✅ 驗證成功，管理權限已解鎖！")
                    st.rerun()
                else:
                    st.error("❌ 密碼錯誤，無法存取管理功能。")
        st.caption("🔒 索引重建、新增網址與上傳檔案需要管理者權限。")
    else:
        col_lock1, col_lock2 = st.columns([3, 1])
        with col_lock1:
            st.success("🔓 已取得管理者權限")
        with col_lock2:
            if st.button("🔒 鎖定", use_container_width=True, help="登出管理者權限"):
                st.session_state["is_admin_authenticated"] = False
                st.rerun()

        col_r1, col_r2 = st.columns(2)
        if col_r1.button("🔄 增量更新", use_container_width=True, help="掃描新增或修改的文件並更新索引"):
            with st.spinner("正在掃描並更新索引..."):
                rag._sync_index()
            st.success("✅ 索引已更新！")
            st.rerun()

        if col_r2.button("🔁 重建索引", use_container_width=True,
                         help="清除向量索引並重新向量化（保留 LLM 摘要，速度較快）"):
            with st.spinner("正在重建向量索引..."):
                rag.force_reindex(clear_summaries=False)
            st.success("✅ 索引重建完成！")
            st.rerun()

        if rag_summary.get("two_step_ingest"):
            if st.button("🔁 重建索引＋重新摘要", use_container_width=True,
                         help="清除摘要並重新跑 LLM 兩階段 Ingest（耗時較長）"):
                with st.spinner("正在清除摘要並完整重建，請稍候..."):
                    rag.force_reindex(clear_summaries=True)
                st.success("✅ 完整重建完成！")
                st.rerun()

        # 快速新增內容區塊 (檔案上傳 / 網址匯入)
        with st.expander("➕ 新增文件或網址至知識庫", expanded=False):
            tab_file, tab_url = st.tabs(["📤 上傳檔案", "🌐 輸入網址"])
            
            with tab_file:
                uploaded_files = st.file_uploader(
                    "選擇 `.pdf` / `.txt` / `.md` 檔案",
                    type=["pdf", "txt", "md"],
                    accept_multiple_files=True,
                    key="rag_file_uploader"
                )
                upload_trust_level = st.selectbox(
                    "標記檔案來源信任等級：",
                    options=["official", "teacher_case", "external_unverified"],
                    format_func=lambda x: {
                        "official": "官方規章（已核定）",
                        "teacher_case": "教師個案／經驗（未核定）",
                        "external_unverified": "外部資料（待人工確認）"
                    }[x],
                    key="rag_upload_trust_level"
                )
                st.caption("ℹ️ 個案經驗與外部資料僅供親師溝通對話與同理參考，不可作為現行個案事實或法規依據。")
                if st.button("📥 儲存檔案並更新索引", use_container_width=True, key="btn_save_uploaded"):
                    if uploaded_files:
                        upload_metadata = {
                            "official": ("school_admin", "verified"),
                            "teacher_case": ("teacher", "unverified"),
                            "external_unverified": ("teacher", "unverified"),
                        }
                        author_type, verified_status = upload_metadata[upload_trust_level]
                        saved_count = 0
                        all_sources_registered = True
                        for ufile in uploaded_files:
                            ok, fname, msg = utils.save_uploaded_file(ufile, DOCS_DIR)
                            if ok:
                                saved_path = os.path.join(DOCS_DIR, fname)
                                metadata_ok = rag.register_source_metadata(
                                    source_fpath=saved_path,
                                    trust_level=upload_trust_level,
                                    author_type=author_type,
                                    verified_status=verified_status,
                                    source_url="",
                                )
                                if metadata_ok:
                                    saved_count += 1
                                else:
                                    all_sources_registered = False
                                    st.error(f"❌ {fname}: 來源 metadata 登記失敗！")
                            else:
                                all_sources_registered = False
                                st.error(f"❌ {fname}: {msg}")
                        if saved_count > 0 and all_sources_registered:
                            with st.spinner("正在進行向量化與智慧摘要..."):
                                rag._sync_index()
                            st.success(f"✅ 成功上傳 {saved_count} 個檔案並完成索引！")
                            st.rerun()
                        elif saved_count > 0 and not all_sources_registered:
                            st.warning("⚠️ 部分檔案登記失敗，整批已暫緩手動同步索引。已成功儲存之檔案將於下一次同步時自動更新。")
                    else:
                        st.warning("請先選擇要上傳的檔案。")

            with tab_url:
                input_url = st.text_input("貼上網頁網址 (URL)", placeholder="https://example.com/article", key="rag_url_input")
                if st.button("🌐 抓取網頁並更新索引", use_container_width=True, key="btn_fetch_url"):
                    if input_url.strip():
                        with st.spinner("正在抓取網頁內容..."):
                            ok, filename, content_or_msg = utils.fetch_url_content(input_url.strip())
                        if ok:
                            target_path = os.path.join(DOCS_DIR, filename)
                            try:
                                with open(target_path, "w", encoding="utf-8") as f:
                                    f.write(content_or_msg)
                                metadata_ok = rag.register_source_metadata(
                                    source_fpath=target_path,
                                    trust_level="external_unverified",
                                    author_type="web_crawl",
                                    verified_status="unverified",
                                    source_url=input_url.strip(),
                                )
                                if metadata_ok:
                                    with st.spinner("正在進行向量化與智慧摘要..."):
                                        rag._sync_index()
                                    st.success(f"✅ 成功抓取網頁並儲存為 `{filename}`！")
                                    st.rerun()
                                else:
                                    st.error("❌ 網址來源 metadata 登記失敗！")
                            except Exception as e:
                                st.error(f"❌ 檔案寫入失敗: {e}")
                        else:
                            st.error(f"❌ {content_or_msg}")
                    else:
                        st.warning("請輸入有效的網址。")

    st.markdown("---")

    # 4. 主題知識卡
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

available_themes = [k for k in theme_options.keys() if utils.theme_has_prompts(k, prompts_db)]
if not available_themes:
    available_themes = list(theme_options.keys())

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
        st.sidebar.info("💡 **通用親師溝通**：適合處理非特定爭議（如例行通知、日常關懷）的溝通情境。建議將非暴力溝通（NVC）觀察、感受、需要、請求四步驟內化為自然段落。")
else:
    st.sidebar.info("💡 **通用親師溝通**：適合處理非特定爭議（如例行通知、日常關懷）的溝通情境。建議將非暴力溝通（NVC）觀察、感受、需要、請求四步驟內化為自然段落。")

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
                if "{選填：教師補充背景}" in prompt_run:
                    prompt_run = prompt_run.replace("{選填：教師補充背景}", context)

                full_system_prompt = utils.compose_system_prompt(
                    task_prompt=prompt_run,
                    knowledge_context=knowledge_context,
                    rag_context=rag_context
                )

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
        try:
            # 語意搜尋
            rag_context, rag_results = build_rag_context(parent_message)

            analysis_response = None
            if system_prompt_a:
                with st.spinner("🔍 第一階段：AI 正在深入分析家長訴求與冰山下的情緒 (Type A)..."):
                    prompt_run_a = system_prompt_a
                    if "{在此貼上家長的訊息}" in prompt_run_a:
                        prompt_run_a = prompt_run_a.replace("{在此貼上家長的訊息}", parent_message)
                    if "{選填：教師補充背景}" in prompt_run_a:
                        prompt_run_a = prompt_run_a.replace("{選填：教師補充背景}", context)

                    full_system_prompt_a = utils.compose_system_prompt(
                        task_prompt=prompt_run_a,
                        knowledge_context=knowledge_context,
                        rag_context=rag_context
                    )

                    analysis_response = utils.call_llm_api(
                        provider=provider,
                        api_key=current_key,
                        model_name=model_name,
                        system_prompt=full_system_prompt_a,
                        user_message=user_message,
                        base_url=base_url
                    )

            with st.spinner("✉️ 第二階段：AI 正在融合情境分析，依非暴力溝通架構生成溫暖回覆草稿 (Type B)..."):
                prompt_run_b = system_prompt_b
                if "{在此貼上家長的訊息}" in prompt_run_b:
                    prompt_run_b = prompt_run_b.replace("{在此貼上家長的訊息}", parent_message)
                if "{選填：教師補充背景}" in prompt_run_b:
                    prompt_run_b = prompt_run_b.replace("{選填：教師補充背景}", context)

                full_system_prompt_b = utils.compose_system_prompt(
                    task_prompt=prompt_run_b,
                    knowledge_context=knowledge_context,
                    rag_context=rag_context
                )

                # 組合 User Message，若有第一階段分析則一併注入
                if analysis_response:
                    user_message_b = f"{user_message}\n\n【第一階段 Type A 情境與冰山分析報告參考】：\n{analysis_response}\n\n請依據以上家長訊息、教師背景與第一階段情境分析報告，將非暴力溝通（NVC）觀察、感受、需要、請求內化為自然段落，生成溫暖之回覆草稿。"
                else:
                    user_message_b = user_message

                response = utils.call_llm_api(
                    provider=provider,
                    api_key=current_key,
                    model_name=model_name,
                    system_prompt=full_system_prompt_b,
                    user_message=user_message_b,
                    base_url=base_url
                )

            validation_errors = utils.validate_parent_reply(response)
            if validation_errors:
                st.warning(f"⚠️ 本次 AI 生成之草稿未符合格式品質規範（原因：{'；'.join(validation_errors)}），未予顯示。請點擊按鈕重新生成。")
            else:
                st.success("✅ 兩階段草稿生成完成！")
                st.markdown("### 💬 AI 建議回覆草稿")
                st.info("💡 以下草稿已融合 Type A 冰山診斷與非暴力溝通（NVC）四步驟內部思維生成，以自然段落表達，無條列式與官方用語。您可直接在下方編輯器微調。")

                edited_response = st.text_area(
                    "✏️ 編輯與微調回覆：",
                    value=response,
                    height=200
                )
                st.caption("💡 提示：您可直接點擊編輯框右上角的複製按鈕（滑鼠移過去會顯示），即可貼回 LINE 或聯絡簿。")

            if analysis_response:
                with st.expander("🔍 查看 第一階段 AI 冰山分析報告 (Type A)", expanded=False):
                    st.markdown(analysis_response)

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
