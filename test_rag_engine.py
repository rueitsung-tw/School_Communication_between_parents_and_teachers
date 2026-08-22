import os
import tempfile
from pathlib import Path
from rag_engine import normalize_path, _import_fitz, RAGEngine, SUMMARIES_DIR_NAME

import json
import rag_engine

def test_normalize_path():
    p1 = "c:\\test\\docs\\file.txt"
    p2 = "C:\\test\\docs\\file.txt"
    assert normalize_path(p1) == normalize_path(p2)
    assert normalize_path(p1).startswith("C:\\")

def test_import_fitz():
    fitz = _import_fitz()
    print("fitz module loaded:", fitz is not None)

def test_is_summaries_filtering():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = normalize_path(os.path.join(tmpdir, "docs"))
        summaries_dir = normalize_path(os.path.join(docs_dir, SUMMARIES_DIR_NAME))
        os.makedirs(summaries_dir, exist_ok=True)
        
        drive = summaries_dir[0]  # e.g., 'C'
        lower_drive = drive.lower()
        upper_drive = drive.upper()

        lower_summary_file = f"{lower_drive}:{summaries_dir[2:]}\\test_summary.md"
        upper_summary_file = f"{upper_drive}:{summaries_dir[2:]}\\test_summary.md"

        engine = RAGEngine(ollama_base_url="http://localhost:11434", docs_dir=docs_dir)

        norm_lower = normalize_path(lower_summary_file)
        norm_upper = normalize_path(upper_summary_file)
        norm_docs = normalize_path(summaries_dir)

        assert norm_lower.startswith(norm_docs)
        assert norm_upper.startswith(norm_docs)
        assert SUMMARIES_DIR_NAME in Path(norm_lower).parts

        print("[OK] RAG engine unit tests passed!")

def test_register_source_metadata_normalizes_key_and_persists_contract():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir)
        engine = RAGEngine("http://unused", docs_dir=docs_dir)
        source = os.path.join(docs_dir, "official.md")

        assert engine.register_source_metadata(
            source, "official", "school_admin", "verified", ""
        ) is True

        with open(os.path.join(docs_dir, "manifest.json"), encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest[normalize_path(source)] == {
            "trust_level": "official",
            "author_type": "school_admin",
            "verified_status": "verified",
            "source_url": "",
        }

def test_register_source_metadata_rejects_verified_non_official():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir)
        engine = RAGEngine("http://unused", docs_dir=docs_dir)

        assert engine.register_source_metadata(
            os.path.join(docs_dir, "case.md"), "teacher_case", "teacher", "verified", ""
        ) is False
        assert not os.path.exists(os.path.join(docs_dir, "manifest.json"))

def test_unregistered_source_uses_safe_default_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir)
        engine = RAGEngine("http://unused", docs_dir=docs_dir)

        assert engine._get_source_metadata(os.path.join(docs_dir, "unregistered.md")) == {
            "trust_level": "external_unverified",
            "author_type": "web_crawl",
            "verified_status": "unverified",
            "source_url": "",
        }

def test_indexed_and_retrieved_chunks_preserve_or_default_source_metadata(monkeypatch):
    class FakeCollection:
        def __init__(self):
            self.added = None
            self.query_metadata = {"source": "legacy.md", "filename": "legacy.md"}
        def delete(self, **kwargs):
            return None
        def add(self, **kwargs):
            self.added = kwargs
        def count(self):
            return 1
        def query(self, **kwargs):
            return {"documents": [["舊索引段落"]], "metadatas": [[self.query_metadata]], "distances": [[0.1]]}

    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir)
        source = os.path.join(docs_dir, "official.md")
        with open(source, "w", encoding="utf-8") as f:
            f.write("可供索引的測試文字，長度足以形成一個段落。")
        engine = RAGEngine("http://unused", docs_dir=docs_dir)
        fake_collection = FakeCollection()
        engine._collection = fake_collection
        assert engine.register_source_metadata(source, "official", "school_admin", "verified", "")
        monkeypatch.setattr(rag_engine, "batch_get_embeddings", lambda texts, *args: [[0.1] for _ in texts])
        monkeypatch.setattr(rag_engine, "get_embedding", lambda *args: [0.1])

        assert engine._index_file(source, source) is True
        assert fake_collection.added["metadatas"][0]["trust_level"] == "official"
        assert fake_collection.added["metadatas"][0]["verified_status"] == "verified"

        result = engine.retrieve("測試")
        assert result[0]["trust_level"] == "external_unverified"
        assert result[0]["author_type"] == "web_crawl"
        assert result[0]["verified_status"] == "unverified"
        assert result[0]["source_url"] == ""

def test_manifest_non_dict_root_safely_degrades_and_rejects_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir)
        manifest_file = os.path.join(docs_dir, "manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write("[]")

        engine = RAGEngine("http://unused", docs_dir=docs_dir)
        source = os.path.join(docs_dir, "file.md")

        assert engine._get_source_metadata(source) == {
            "trust_level": "external_unverified",
            "author_type": "web_crawl",
            "verified_status": "unverified",
            "source_url": "",
        }

        assert engine.register_source_metadata(
            source, "official", "school_admin", "verified", ""
        ) is False

        with open(manifest_file, encoding="utf-8") as f:
            content = f.read()
        assert content == "[]"

if __name__ == "__main__":
    test_normalize_path()
    test_import_fitz()
    test_is_summaries_filtering()
    test_register_source_metadata_normalizes_key_and_persists_contract()
    test_register_source_metadata_rejects_verified_non_official()
    test_unregistered_source_uses_safe_default_metadata()
    test_indexed_and_retrieved_chunks_preserve_or_default_source_metadata()
    test_manifest_non_dict_root_safely_degrades_and_rejects_overwrite()
