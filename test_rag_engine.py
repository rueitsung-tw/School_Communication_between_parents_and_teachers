import os
import tempfile
from pathlib import Path
from rag_engine import normalize_path, _import_fitz, RAGEngine, SUMMARIES_DIR_NAME

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

if __name__ == "__main__":
    test_normalize_path()
    test_import_fitz()
    test_is_summaries_filtering()
