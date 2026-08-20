"""
rag_engine.py — 親師溝通知識庫 RAG 引擎（方案 B：語意搜尋版）

功能：
  1. PDF / TXT / MD 文件自動切段（chunking）
  2. 呼叫遠端 Ollama nomic-embed-text 做 embedding
  3. 使用 ChromaDB 本地向量資料庫做儲存與相似度搜尋
  4. 監控 docs/ 目錄，偵測新增或修改的檔案並自動更新索引
  5. 提供 retrieve(query, top_k) 介面，供 app.py 呼叫
"""

import os
import re
import json
import hashlib
import datetime
import threading
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

# ── 第三方函式庫（懶載入，避免 import 錯誤影響主程式） ────────────────────

def _import_fitz():
    try:
        import fitz  # PyMuPDF
        return fitz
    except ImportError:
        return None

def _import_chromadb():
    try:
        import chromadb
        return chromadb
    except ImportError:
        return None

def _import_watchdog():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        return Observer, FileSystemEventHandler
    except ImportError:
        return None, None


# ── 常數 ─────────────────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
EMBED_MODEL = "nomic-embed-text"
COLLECTION_NAME = "parent_teacher_rag"

_SCRIPT_DIR = Path(__file__).parent
DB_PATH = str(_SCRIPT_DIR / ".chromadb")
DOCS_DIR = str(_SCRIPT_DIR / "docs")


# ── 文字提取 ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    fitz = _import_fitz()
    if fitz is None:
        print("[RAG] ⚠️ PyMuPDF 未安裝，無法解析 PDF。請執行: pip install pymupdf")
        return ""
    try:
        doc = fitz.open(pdf_path)
        pages_text = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages_text)
    except Exception as e:
        print(f"[RAG] ⚠️ 無法解析 PDF {pdf_path}: {e}")
        return ""


def extract_text_from_file(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in {".txt", ".md"}:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"[RAG] ⚠️ 無法讀取檔案 {filepath}: {e}")
            return ""
    return ""


# ── 文字切段（Chunking） ───────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text or not text.strip():
        return []
    paragraphs = re.split(r"\n{2,}", text.strip())
    chunks = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    sub = para[i:i + chunk_size]
                    if sub.strip():
                        chunks.append(sub.strip())
                current = ""
            else:
                current = para
    if current:
        chunks.append(current)
    return [c for c in chunks if len(c.strip()) >= 20]


# ── Embedding（呼叫遠端 Ollama） ───────────────────────────────────────────────

def get_embedding(text: str, ollama_base_url: str, model: str = EMBED_MODEL) -> Optional[List[float]]:
    base = ollama_base_url.strip().rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3].rstrip("/")
    url = f"{base}/api/embed"
    payload = json.dumps({"model": model, "input": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            embeddings = data.get("embeddings", [])
            if embeddings:
                return embeddings[0]
    except Exception as e:
        print(f"[RAG] ⚠️ Embedding 呼叫失敗: {e}")
    return None


def batch_get_embeddings(texts: List[str], ollama_base_url: str, model: str = EMBED_MODEL) -> List[Optional[List[float]]]:
    results = []
    for i, text in enumerate(texts):
        vec = get_embedding(text, ollama_base_url, model)
        results.append(vec)
        if (i + 1) % 10 == 0:
            print(f"[RAG] Embedding 進度：{i + 1}/{len(texts)}")
    return results


# ── 檔案指紋 ──────────────────────────────────────────────────────────────────

def file_fingerprint(filepath: str) -> str:
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def scan_directory_files(directory: str) -> Dict[str, str]:
    result = {}
    if not os.path.exists(directory):
        return result
    for root, _, files in os.walk(directory):
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                fpath = os.path.join(root, fname)
                result[fpath] = file_fingerprint(fpath)
    return result


# ── ChromaDB 索引管理 ─────────────────────────────────────────────────────────

class RAGEngine:
    """
    親師溝通 RAG 引擎。

    使用方式：
        engine = RAGEngine(ollama_base_url="http://172.20.10.51:11434")
        engine.initialize()
        results = engine.retrieve("家長質疑座位安排", top_k=3)
    """

    def __init__(self, ollama_base_url: str, docs_dir: str = DOCS_DIR, db_path: str = DB_PATH):
        self.ollama_base_url = ollama_base_url
        self.docs_dir = docs_dir
        self.db_path = db_path
        self._client = None
        self._collection = None
        self._indexed_fingerprints: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._observer = None
        self._status = "未初始化"
        self._last_updated: Optional[datetime.datetime] = None
        self._indexed_files: List[str] = []

    def initialize(self) -> bool:
        chromadb = _import_chromadb()
        if chromadb is None:
            self._status = "❌ chromadb 未安裝，請執行 pip install chromadb"
            return False
        try:
            self._client = chromadb.PersistentClient(path=self.db_path)
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            self._status = "✅ ChromaDB 已連線"
        except Exception as e:
            self._status = f"❌ ChromaDB 初始化失敗: {e}"
            return False
        self._load_fingerprints()
        self._sync_index()
        return True

    def _fingerprint_path(self) -> str:
        return os.path.join(self.db_path, "indexed_fingerprints.json")

    def _load_fingerprints(self):
        fp_path = self._fingerprint_path()
        if os.path.exists(fp_path):
            try:
                with open(fp_path, "r", encoding="utf-8") as f:
                    self._indexed_fingerprints = json.load(f)
            except Exception:
                self._indexed_fingerprints = {}

    def _save_fingerprints(self):
        fp_path = self._fingerprint_path()
        os.makedirs(os.path.dirname(fp_path), exist_ok=True)
        with open(fp_path, "w", encoding="utf-8") as f:
            json.dump(self._indexed_fingerprints, f, ensure_ascii=False, indent=2)

    def _sync_index(self):
        with self._lock:
            current_files = scan_directory_files(self.docs_dir)
            newly_indexed = []

            for fpath, fp in current_files.items():
                if self._indexed_fingerprints.get(fpath) != fp:
                    print(f"[RAG] 📄 索引檔案：{os.path.basename(fpath)}")
                    success = self._index_file(fpath)
                    if success:
                        self._indexed_fingerprints[fpath] = fp
                        newly_indexed.append(fpath)

            for fpath in list(self._indexed_fingerprints.keys()):
                if fpath not in current_files:
                    self._remove_file_from_index(fpath)
                    del self._indexed_fingerprints[fpath]

            if newly_indexed:
                self._save_fingerprints()
                self._last_updated = datetime.datetime.now()

            self._indexed_files = list(current_files.keys())

            if not self._indexed_files:
                self._status = "⚠️ docs/ 目錄無可索引文件"
            else:
                count = self._collection.count() if self._collection else 0
                self._status = f"✅ 已索引 {len(self._indexed_files)} 個檔案，共 {count} 個段落"

    def _index_file(self, filepath: str) -> bool:
        if self._collection is None:
            return False
        self._remove_file_from_index(filepath)
        text = extract_text_from_file(filepath)
        if not text.strip():
            return False
        chunks = chunk_text(text)
        if not chunks:
            return False
        embeddings = batch_get_embeddings(chunks, self.ollama_base_url)
        valid = [(c, e) for c, e in zip(chunks, embeddings) if e is not None]
        if not valid:
            print(f"[RAG] ❌ 無法取得 embedding，請確認 nomic-embed-text 已安裝於遠端 Ollama")
            return False
        fname = os.path.basename(filepath)
        prefix = hashlib.md5(filepath.encode()).hexdigest()
        ids = [f"{prefix}_{i}" for i in range(len(valid))]
        docs = [c for c, _ in valid]
        vecs = [e for _, e in valid]
        metas = [{"source": filepath, "filename": fname, "chunk_index": i} for i in range(len(valid))]
        try:
            self._collection.add(ids=ids, documents=docs, embeddings=vecs, metadatas=metas)
            print(f"[RAG] ✅ 已索引 {len(valid)} 個段落：{fname}")
            return True
        except Exception as e:
            print(f"[RAG] ❌ ChromaDB 寫入失敗：{e}")
            return False

    def _remove_file_from_index(self, filepath: str):
        if self._collection is None:
            return
        try:
            self._collection.delete(where={"source": filepath})
        except Exception:
            pass

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        語意搜尋，回傳最相關的 top_k 段落。
        回傳格式：[{"text": str, "filename": str, "distance": float}]
        """
        if self._collection is None:
            return []
        query_vec = get_embedding(query, self.ollama_base_url)
        if query_vec is None:
            return []
        count = self._collection.count()
        if count == 0:
            return []
        actual_top_k = min(top_k, count)
        try:
            results = self._collection.query(
                query_embeddings=[query_vec],
                n_results=actual_top_k,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"[RAG] ⚠️ ChromaDB 查詢失敗：{e}")
            return []
        output = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        for doc, meta, dist in zip(docs, metas, dists):
            output.append({
                "text": doc,
                "source": meta.get("source", ""),
                "filename": meta.get("filename", ""),
                "distance": round(dist, 4)
            })
        return output

    def start_watching(self):
        """啟動 watchdog 監控 docs/ 目錄。"""
        Observer, FileSystemEventHandler = _import_watchdog()
        if Observer is None:
            print("[RAG] ⚠️ watchdog 未安裝")
            return
        engine_ref = self

        class _Handler(FileSystemEventHandler):
            def on_created(self, event):
                if not event.is_directory and Path(event.src_path).suffix.lower() in SUPPORTED_EXTENSIONS:
                    print(f"[RAG] 🆕 新檔案：{event.src_path}")
                    engine_ref._sync_index()

            def on_modified(self, event):
                if not event.is_directory and Path(event.src_path).suffix.lower() in SUPPORTED_EXTENSIONS:
                    print(f"[RAG] 🔄 檔案更新：{event.src_path}")
                    engine_ref._sync_index()

            def on_deleted(self, event):
                if not event.is_directory:
                    print(f"[RAG] 🗑️ 檔案刪除：{event.src_path}")
                    engine_ref._sync_index()

        os.makedirs(self.docs_dir, exist_ok=True)
        self._observer = Observer()
        self._observer.schedule(_Handler(), self.docs_dir, recursive=True)
        self._observer.daemon = True
        self._observer.start()
        print(f"[RAG] 👁️ 監控中：{self.docs_dir}")

    def stop_watching(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()

    @property
    def status(self) -> str:
        return self._status

    @property
    def last_updated(self) -> Optional[datetime.datetime]:
        return self._last_updated

    @property
    def indexed_files(self) -> List[str]:
        return self._indexed_files

    def get_summary(self) -> Dict:
        count = 0
        if self._collection:
            try:
                count = self._collection.count()
            except Exception:
                pass
        return {
            "status": self._status,
            "indexed_files": [os.path.basename(f) for f in self._indexed_files],
            "total_chunks": count,
            "last_updated": self._last_updated.strftime("%Y-%m-%d %H:%M:%S") if self._last_updated else "尚未更新",
        }

    def force_reindex(self):
        """強制完整重建索引。"""
        with self._lock:
            if self._collection and self._client:
                try:
                    self._client.delete_collection(COLLECTION_NAME)
                    self._collection = self._client.get_or_create_collection(
                        name=COLLECTION_NAME,
                        metadata={"hnsw:space": "cosine"}
                    )
                except Exception as e:
                    print(f"[RAG] ❌ 重建失敗：{e}")
                    return
            self._indexed_fingerprints = {}
            self._save_fingerprints()
        self._sync_index()
