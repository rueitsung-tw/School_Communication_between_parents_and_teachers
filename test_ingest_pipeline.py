import ingest_pipeline


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
