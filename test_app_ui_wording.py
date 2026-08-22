import os
import pytest

def test_app_ui_wording_has_no_obsolete_nvc_three_stage_text():
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    assert os.path.exists(app_path), "app.py 檔案不存在"

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 介面文案不得再出現舊版「三段式」或「同理 -> 事實 -> 解方」字樣
    assert "三段式" not in content, "app.py 仍包含舊版『三段式』文案"
    assert "同理 -> 事實 -> 解方" not in content, "app.py 仍包含舊版『同理 -> 事實 -> 解方』文案"

    # 2. 介面文案必須包含 NVC 四步驟內部思維與自然段落之語意
    assert "觀察、感受、需要、請求" in content, "app.py 缺少 NVC 四步驟『觀察、感受、需要、請求』文案"
    assert "自然段落" in content, "app.py 缺少『自然段落』文案"

def test_app_ui_admin_panel_has_source_trust_registration():
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    assert os.path.exists(app_path), "app.py 檔案不存在"

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "with tab_file:" in content and "with tab_url:" in content
    tab_url_idx = content.index("with tab_url:")
    file_tab = content[content.index("with tab_file:"):tab_url_idx]
    url_tab = content[tab_url_idx:content.index("st.markdown(\"---\")", tab_url_idx)]

    assert 'key="rag_upload_trust_level"' in file_tab
    assert '"official"' in file_tab
    assert '"teacher_case"' in file_tab
    assert '"external_unverified"' in file_tab
    assert "rag.register_source_metadata(" in file_tab
    assert "all_sources_registered" in file_tab
    assert "if saved_count > 0 and all_sources_registered:" in file_tab
    assert file_tab.index("rag.register_source_metadata(") < file_tab.index("rag._sync_index()")
    assert "rag.register_source_metadata(" in url_tab
    assert 'trust_level="external_unverified"' in url_tab
    assert 'author_type="web_crawl"' in url_tab
    assert 'verified_status="unverified"' in url_tab
    assert "source_url=input_url.strip()" in url_tab
    assert url_tab.index("rag.register_source_metadata(") < url_tab.index("rag._sync_index()")
