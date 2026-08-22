import ingest_pipeline


def test_normalize_text_for_llm_unifies_newlines_and_unicode():
    text = "A\r\nB\r\n\u0065\u0301"

    assert ingest_pipeline.normalize_text_for_llm(text) == "A\nB\né"


def test_stage1_output_budget_and_reasoning_are_configured_for_json():
    assert ingest_pipeline.MAX_STAGE1_OUTPUT_TOKENS == 2000
    assert "不要輸出推理過程" in ingest_pipeline.STAGE1_SYSTEM_PROMPT


def test_extract_stage1_json_skips_reasoning_json_fragments():
    raw = (
        "<|channel>thought\n"
        '{"term":"概念","definition":"說明"}\n'
        '<|channel>final\n'
        '{"main_topics":["主題"],"key_concepts":[],'
        '"legal_references":[],"parent_teacher_relevance":"關聯",'
        '"document_type":"法令條文"}'
    )

    result = ingest_pipeline.extract_stage1_json(raw)

    assert result["main_topics"] == ["主題"]


def test_truncate_for_ingest_prefers_sentence_boundary():
    text = "甲" * 3200 + "。" + "乙" * 1200

    result = ingest_pipeline.truncate_for_ingest(text, 4000)

    assert result.endswith("\n\n（文件內容已截斷）")
    assert result.startswith("甲" * 3200 + "。")


def test_truncate_for_ingest_keeps_short_text_unchanged():
    text = "短文件"

    assert ingest_pipeline.truncate_for_ingest(text, 4000) == text


def test_analyze_document_accepts_json_with_explanatory_text(monkeypatch):
    response = '以下是分析結果：\n{"main_topics": ["校園安全"]}\n以上。'
    monkeypatch.setattr(ingest_pipeline, "_call_ollama", lambda *args, **kwargs: response)

    result = ingest_pipeline.analyze_document("文件內容", "test.md", "http://localhost:11434", "test-model")

    assert result == {"main_topics": ["校園安全"]}


def test_analyze_document_limits_input_and_reserves_output(monkeypatch):
    captured = {}

    def fake_call(*args, **kwargs):
        captured["user_message"] = args[3]
        captured["kwargs"] = kwargs
        return '{"ok": true}'

    monkeypatch.setattr(ingest_pipeline, "_call_ollama", fake_call)
    result = ingest_pipeline.analyze_document("甲" * 10000, "test.md", "http://localhost:11434", "test-model")

    assert result == {"ok": True}
    assert len(captured["user_message"]) < 7000
    assert captured["kwargs"]["temperature"] == 0.2
