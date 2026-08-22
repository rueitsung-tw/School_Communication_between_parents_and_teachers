"""
rag_engine.py — 親師溝通知識庫 RAG 引擎（方案 B：語意搜尋版）

功能：
  1. PDF / TXT / MD 文件自動切段（chunking）
  2. 呼叫遠端 Ollama nomic-embed-text 做 embedding
  3. 使用 ChromaDB 本地向量資料庫做儲存與相似度搜尋
  4. 監控 docs/ 目錄，偵測新增或修改的檔案並自動更新索引（排除 summaries/）
  5. 提供 retrieve(query, top_k) 介面，供 app.py 呼叫
  6. 兩階段 Ingest：優先索引 LLM 生成的摘要 .md，fallback 直接切段
"""

import os
import sys
import re
import json
import hashlib
import datetime
import threading
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── 第三方函式庫（懶載入） ───────────────────────────────────────────────────

def _import_fitz():
    try:
        import pymupdf as fitz
        return fitz
    except ImportError:
        try:
            import fitz
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
SUMMARIES_DIR_NAME = "summaries"   # docs/ 下的摘要子目錄，由 ingest_pipeline 生成

SOURCE_TRUST_DEFAULT = {
    "trust_level": "external_unverified",
    "author_type": "web_crawl",
    "verified_status": "unverified",
    "source_url": "",
}
SOURCE_TRUST_LEVELS = {"official", "teacher_case", "external_unverified"}
SOURCE_AUTHOR_TYPES = {"moe_official", "school_admin", "teacher", "web_crawl"}
SOURCE_VERIFIED_STATUSES = {"verified", "unverified"}

_SCRIPT_DIR = Path(__file__).parent
DB_PATH = str(_SCRIPT_DIR / ".chromadb")
DOCS_DIR = str(_SCRIPT_DIR / "docs")


# ── 文字提取 ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    fitz = _import_fitz()
    if fitz is None:
        print("[RAG] ⚠️ PyMuPDF 未安裝，請執行: pip install pymupdf")
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
            print(f"[RAG] ⚠️ 無法讀取 {filepath}: {e}")
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


# ── Embedding（支援 Ollama 與 llama-server / OpenAI 相容介面） ───────────────

def get_embedding(text: str, base_url: str, model: str = EMBED_MODEL, api_key: str = "ollama") -> Optional[List[float]]:
    clean_url = base_url.strip().rstrip("/")
    if clean_url.endswith("/v1"):
        base_v1 = clean_url
        base_root = clean_url[:-3].rstrip("/")
    else:
        base_v1 = f"{clean_url}/v1"
        base_root = clean_url

    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "ollama":
        headers["Authorization"] = f"Bearer {api_key}"

    # 1. 嘗試 OpenAI 相容 /v1/embeddings (llama-server --embedding 預設介面)
    try:
        url = f"{base_v1}/embeddings"
        payload = json.dumps({"model": model, "input": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if "data" in data and len(data["data"]) > 0:
                    emb = data["data"][0].get("embedding")
                    if emb:
                        return emb
    except Exception:
        pass

    # 2. 嘗試 llama.cpp 原生 /embeddings
    try:
        url = f"{base_root}/embeddings"
        payload = json.dumps({"content": text, "input": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict) and "embedding" in data:
                    return data["embedding"]
                elif isinstance(data, list) and len(data) > 0 and "embedding" in data[0]:
                    return data[0]["embedding"]
    except Exception:
        pass

    # 3. 嘗試 Ollama /api/embed
    try:
        url = f"{base_root}/api/embed"
        payload = json.dumps({"model": model, "input": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                embeddings = data.get("embeddings", [])
                if embeddings:
                    return embeddings[0]
    except Exception:
        pass

    # 4. 嘗試 Ollama 舊版 /api/embeddings
    try:
        url = f"{base_root}/api/embeddings"
        payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                emb = data.get("embedding", [])
                if emb:
                    return emb
    except Exception as e:
        print(f"[RAG] ⚠️ Embedding 呼叫失敗: {e}")

    return None


def batch_get_embeddings(texts: List[str], base_url: str, model: str = EMBED_MODEL, api_key: str = "ollama") -> List[Optional[List[float]]]:
    results = []
    for i, text in enumerate(texts):
        vec = get_embedding(text, base_url, model, api_key)
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


def normalize_path(filepath: str) -> str:
    """統一檔案路徑格式（全絕對路徑、大寫磁碟機代號），防範 Windows 大小寫比對失敗。"""
    if not filepath:
        return ""
    norm = os.path.abspath(os.path.normpath(filepath))
    if len(norm) >= 2 and norm[1] == ":":
        norm = norm[0].upper() + norm[1:]
    return norm


def scan_directory_files(directory: str) -> Dict[str, str]:
    """
    掃描 docs/ 目錄下所有支援格式的原始文件。
    #1 修正：明確排除 summaries/ 子目錄，避免摘要被當原始文件二次處理。
    """
    result = {}
    if not os.path.exists(directory):
        return result
    directory_norm = normalize_path(directory)
    summaries_abs = normalize_path(os.path.join(directory_norm, SUMMARIES_DIR_NAME))

    for root, dirs, files in os.walk(directory_norm):
        root_norm = normalize_path(root)
        if root_norm.startswith(summaries_abs):
            dirs.clear()  # 阻止 os.walk 繼續遞迴進入
            continue
        dirs[:] = [d for d in dirs if normalize_path(os.path.join(root, d)) != summaries_abs]

        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                fpath = normalize_path(os.path.join(root, fname))
                result[fpath] = file_fingerprint(fpath)
    return result


# ── ChromaDB 索引管理 ─────────────────────────────────────────────────────────

class RAGEngine:
    """
    親師溝通 RAG 引擎。

    兩階段 Ingest 流程（需 config.json 中 two_step_ingest: true）：
      原始文件 → ingest_pipeline LLM 分析+生成 → docs/summaries/*.md → 向量索引

    Fallback（two_step_ingest: false 或 LLM 生成失敗）：
      原始文件 → 直接切段 → 向量索引
    """

    def __init__(
        self,
        ollama_base_url: str,
        docs_dir: str = DOCS_DIR,
        db_path: str = DB_PATH,
        two_step_ingest: bool = True,
        ingest_model: str = "",
        api_key: str = "ollama",
        embedding_url: str = "",
        embedding_model: str = ""
    ):
        self.ollama_base_url = ollama_base_url
        self.embedding_url = embedding_url if embedding_url else ollama_base_url
        self.embedding_model = embedding_model if embedding_model else EMBED_MODEL
        self.docs_dir = normalize_path(docs_dir)
        self.db_path = normalize_path(db_path)
        self.two_step_ingest = two_step_ingest
        self.ingest_model = ingest_model   # 空字串時由 _ingest_model property 動態取
        self.api_key = api_key

        self._client = None
        self._collection = None
        # #2 修正：兩組獨立指紋
        #   _source_fingerprints：原始文件 md5，用於判斷是否需要重新摘要
        #   _index_fingerprints：實際被索引材料（摘要或原始）的 md5，用於判斷是否需要重新索引
        self._source_fingerprints: Dict[str, str] = {}
        self._index_fingerprints: Dict[str, str] = {}

        # #3 修正：用 RLock（可重入）避免同執行緒再次取鎖時死鎖
        self._lock = threading.RLock()
        # 防止 watchdog 事件風暴的 in_progress flag
        self._sync_in_progress = False

        self._observer = None
        self._status = "未初始化"
        self._last_updated: Optional[datetime.datetime] = None
        self._indexed_files: List[str] = []

    @property
    def _summaries_dir(self) -> str:
        return normalize_path(os.path.join(self.docs_dir, SUMMARIES_DIR_NAME))

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

    # ── 指紋持久化（兩組） ────────────────────────────────────────────────────

    def _source_fp_path(self) -> str:
        return normalize_path(os.path.join(self.db_path, "source_fingerprints.json"))

    def _index_fp_path(self) -> str:
        return normalize_path(os.path.join(self.db_path, "index_fingerprints.json"))

    def _load_fingerprints(self):
        for path_fn, attr in [
            (self._source_fp_path, "_source_fingerprints"),
            (self._index_fp_path, "_index_fingerprints"),
        ]:
            fp_path = path_fn()
            if os.path.exists(fp_path):
                try:
                    with open(fp_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        setattr(self, attr, {normalize_path(k): v for k, v in data.items()})
                except Exception:
                    setattr(self, attr, {})

    def _save_fingerprints(self):
        os.makedirs(self.db_path, exist_ok=True)
        for path_fn, attr in [
            (self._source_fp_path, "_source_fingerprints"),
            (self._index_fp_path, "_index_fingerprints"),
        ]:
            with open(path_fn(), "w", encoding="utf-8") as f:
                data = {normalize_path(k): v for k, v in getattr(self, attr).items()}
                json.dump(data, f, ensure_ascii=False, indent=2)

    # ── 索引同步 ──────────────────────────────────────────────────────────────

    def _sync_index(self):
        """
        掃描 docs/（排除 summaries/），對新增或修改的檔案做增量更新。
        #2 修正：使用兩組指紋分別判斷「是否需要重新摘要」與「是否需要重新索引」。
        """
        with self._lock:
            if self._sync_in_progress:
                return   # #3 修正：防止重入（watchdog 事件風暴）
            self._sync_in_progress = True
        try:
            self._do_sync()
        finally:
            with self._lock:
                self._sync_in_progress = False

    def _do_sync(self):
        current_files = scan_directory_files(self.docs_dir)
        newly_indexed = []
        any_file_processed = False

        for fpath, source_fp in current_files.items():
            fpath = normalize_path(fpath)
            summary_path = self._get_summary_path(fpath)
            has_valid_summary = os.path.isfile(summary_path) and os.path.getsize(summary_path) > 0

            # 檢查摘要是否存在且完整（> 0 byte）
            if has_valid_summary:
                # 摘要已存在且完整：以此摘要為索引材料，跳過 LLM 重新摘要
                index_material = summary_path
                material_fp = file_fingerprint(index_material)
            else:
                # 無有效摘要：若開啟 two_step_ingest，由 LLM 重新生成
                if self.two_step_ingest:
                    new_summary = self._run_ingest(fpath)
                    if new_summary and os.path.isfile(new_summary) and os.path.getsize(new_summary) > 0:
                        index_material = normalize_path(new_summary)
                        material_fp = file_fingerprint(index_material)
                    else:
                        index_material = fpath
                        material_fp = source_fp
                else:
                    index_material = fpath
                    material_fp = source_fp

            # 更新原始文件指紋
            self._source_fingerprints[fpath] = source_fp

            # 判斷實際索引材料是否需要重新向量化
            index_changed = self._index_fingerprints.get(fpath) != material_fp

            if not index_changed:
                continue   # 向量索引內容無變化，跳過

            print(f"[RAG] 📄 處理：{os.path.basename(fpath)}")
            any_file_processed = True

            # 執行向量索引
            success = self._index_file(source_fpath=fpath, material_path=index_material)
            if success:
                self._index_fingerprints[fpath] = material_fp
                newly_indexed.append(fpath)

        # 清理已刪除的原始文件
        for fpath in list(self._source_fingerprints.keys()):
            if fpath not in current_files:
                self._remove_file_from_index(fpath)
                self._source_fingerprints.pop(fpath, None)
                self._index_fingerprints.pop(fpath, None)
                any_file_processed = True

        if newly_indexed or any_file_processed:
            self._last_updated = datetime.datetime.now()

        self._save_fingerprints()
        self._indexed_files = list(current_files.keys())
        count = self._collection.count() if self._collection else 0
        if not self._indexed_files:
            self._status = "⚠️ docs/ 目錄無可索引文件"
        else:
            self._status = f"✅ 已索引 {len(self._indexed_files)} 個檔案，共 {count} 個段落"

    # ── 兩階段 Ingest 串接 ────────────────────────────────────────────────────

    def _get_summary_path(self, source_filepath: str) -> str:
        """回傳原始文件對應的摘要 .md 路徑。"""
        stem = Path(source_filepath).stem
        return normalize_path(os.path.join(self._summaries_dir, f"{stem}_summary.md"))

    def _run_ingest(self, source_filepath: str) -> Optional[str]:
        """
        呼叫 ingest_pipeline 執行兩階段 Ingest。
        #4 修正：先提取文字再傳入 run_two_step_ingest（避免 pipeline 重複提取）。
        回傳摘要路徑，失敗回傳 None。
        """
        try:
            from ingest_pipeline import run_two_step_ingest
        except ImportError:
            print("[RAG] ⚠️ ingest_pipeline 未找到，跳過兩階段 Ingest")
            return None

        raw_text = extract_text_from_file(source_filepath)
        if not raw_text.strip():
            return None

        model = self.ingest_model or self._guess_model()
        return run_two_step_ingest(
            filepath=source_filepath,
            raw_text=raw_text,
            ollama_url=self.ollama_base_url,
            model_name=model,
            api_key=self.api_key,
            summaries_dir=self._summaries_dir
        )

    def _guess_model(self) -> str:
        """從 config.json 取得模型名稱作為 ingest_model 的預設值。"""
        cfg_path = _SCRIPT_DIR / "config.json"
        try:
            with open(str(cfg_path), "r", encoding="utf-8") as f:
                return json.load(f).get("model_name", "gemma3:12b")
        except Exception:
            return "gemma3:12b"

    def _manifest_path(self) -> str:
        return os.path.join(self.docs_dir, "manifest.json")

    def _get_source_metadata(self, source_fpath: str) -> Dict[str, str]:
        metadata = dict(SOURCE_TRUST_DEFAULT)
        try:
            with open(self._manifest_path(), encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, json.JSONDecodeError):
            return metadata
        if not isinstance(manifest, dict):
            return metadata
        stored = manifest.get(normalize_path(source_fpath), {})
        if not isinstance(stored, dict):
            return metadata
        trust_level = stored.get("trust_level", metadata["trust_level"])
        author_type = stored.get("author_type", metadata["author_type"])
        verified_status = stored.get("verified_status", metadata["verified_status"])
        source_url = stored.get("source_url", metadata["source_url"])
        if trust_level not in SOURCE_TRUST_LEVELS or author_type not in SOURCE_AUTHOR_TYPES:
            return metadata
        if verified_status not in SOURCE_VERIFIED_STATUSES:
            return metadata
        if trust_level != "official" and verified_status != "unverified":
            return metadata
        return {
            "trust_level": trust_level,
            "author_type": author_type,
            "verified_status": verified_status,
            "source_url": source_url if isinstance(source_url, str) else ""
        }

    def register_source_metadata(
        self,
        source_fpath: str,
        trust_level: str = "external_unverified",
        author_type: str = "web_crawl",
        verified_status: str = "unverified",
        source_url: str = "",
    ) -> bool:
        if trust_level not in SOURCE_TRUST_LEVELS:
            return False
        if author_type not in SOURCE_AUTHOR_TYPES:
            return False
        if verified_status not in SOURCE_VERIFIED_STATUSES:
            return False
        if trust_level != "official" and verified_status != "unverified":
            return False

        mpath = self._manifest_path()
        manifest = {}
        if os.path.exists(mpath):
            try:
                with open(mpath, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                print(f"[RAG] ❌ manifest.json 讀取失敗，拒絕覆寫")
                return False
            if not isinstance(manifest, dict):
                print(f"[RAG] ❌ manifest.json 根節點非 dict 物件，拒絕覆寫")
                return False

        manifest[normalize_path(source_fpath)] = {
            "trust_level": trust_level,
            "author_type": author_type,
            "verified_status": verified_status,
            "source_url": source_url if isinstance(source_url, str) else ""
        }

        tmp_path = mpath + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, mpath)
            normalized_path = normalize_path(source_fpath)
            self._index_fingerprints.pop(normalized_path, None)
            return True
        except Exception as e:
            print(f"[RAG] ❌ 寫入 manifest 失敗: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            return False

    # ── 向量索引 ──────────────────────────────────────────────────────────────

    def _index_file(self, source_fpath: str, material_path: str) -> bool:
        """
        對 material_path 做切段+向量化並存入 ChromaDB。
        #8 修正：metadata 同時記錄 source（原始路徑）與 indexed_from（實際索引材料路徑）。
        _remove_file_from_index 以 source 為條件刪除，確保語意一致。
        """
        if self._collection is None:
            return False

        self._remove_file_from_index(source_fpath)   # 以原始路徑為 key 刪除舊索引

        text = extract_text_from_file(material_path)
        if not text.strip():
            return False

        chunks = chunk_text(text)
        if not chunks:
            return False

        embeddings = batch_get_embeddings(chunks, self.embedding_url, self.embedding_model, self.api_key)
        valid = [(c, e) for c, e in zip(chunks, embeddings) if e is not None]
        if not valid:
            print("[RAG] ❌ 無法取得 embedding，請確認 Embedding 伺服器與模型設定正確")
            return False

        is_summary = (material_path != source_fpath)
        prefix = hashlib.md5(source_fpath.encode()).hexdigest()
        ids = [f"{prefix}_{i}" for i in range(len(valid))]
        docs = [c for c, _ in valid]
        vecs = [e for _, e in valid]
        source_meta = self._get_source_metadata(source_fpath)
        metas = [{
            "source": source_fpath,           # 永遠指向原始文件（刪除時用此 key）
            "indexed_from": material_path,    # 實際被向量化的材料（摘要或原始）
            "filename": os.path.basename(source_fpath),
            "is_summary": str(is_summary),
            "chunk_index": i,
            "trust_level": source_meta["trust_level"],
            "author_type": source_meta["author_type"],
            "verified_status": source_meta["verified_status"],
            "source_url": source_meta["source_url"]
        } for i in range(len(valid))]

        try:
            self._collection.add(ids=ids, documents=docs, embeddings=vecs, metadatas=metas)
            label = "（摘要）" if is_summary else "（直接切段）"
            print(f"[RAG] ✅ 已索引 {len(valid)} 段 {label}：{os.path.basename(source_fpath)}")
            return True
        except Exception as e:
            print(f"[RAG] ❌ ChromaDB 寫入失敗：{e}")
            return False

    def _remove_file_from_index(self, source_filepath: str):
        """以 source（原始文件路徑）為條件，刪除 ChromaDB 中所有對應 chunk。"""
        if self._collection is None:
            return
        try:
            self._collection.delete(where={"source": source_filepath})
        except Exception:
            pass

    # ── 語意搜尋 ──────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        語意搜尋，回傳最相關的 top_k 段落。
        回傳格式：[{"text": str, "filename": str, "is_summary": bool, "distance": float, ...}]
        """
        if self._collection is None:
            return []
        query_vec = get_embedding(query, self.embedding_url, self.embedding_model, self.api_key)
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
            print(f"[RAG] ⚠️ 查詢失敗：{e}")
            return []

        output = []
        for doc, meta, dist in zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0]
        ):
            output.append({
                "text": doc,
                "source": meta.get("source", ""),
                "filename": meta.get("filename", ""),
                "is_summary": meta.get("is_summary", "False") == "True",
                "distance": round(dist, 4),
                "trust_level": meta.get("trust_level", SOURCE_TRUST_DEFAULT["trust_level"]),
                "author_type": meta.get("author_type", SOURCE_TRUST_DEFAULT["author_type"]),
                "verified_status": meta.get("verified_status", SOURCE_TRUST_DEFAULT["verified_status"]),
                "source_url": meta.get("source_url", SOURCE_TRUST_DEFAULT["source_url"])
            })
        return output

    # ── watchdog 監控 ─────────────────────────────────────────────────────────

    def start_watching(self):
        """啟動 watchdog，監控 docs/（排除 summaries/ 子目錄）。"""
        if self._observer is not None and self._observer.is_alive():
            return

        Observer, FileSystemEventHandler = _import_watchdog()
        if Observer is None:
            print("[RAG] ⚠️ watchdog 未安裝")
            return

        engine_ref = self
        summaries_abs = normalize_path(
            os.path.join(self.docs_dir, SUMMARIES_DIR_NAME)
        )

        class _Handler(FileSystemEventHandler):
            def __init__(self):
                super().__init__()
                self._timer = None
                self._timer_lock = threading.Lock()

            @staticmethod
            def _is_summaries(path: str) -> bool:
                """正確正規化路徑並雙重檢查 summaries/ 子目錄」"""
                norm_path = normalize_path(path)
                if norm_path.startswith(summaries_abs):
                    return True
                return SUMMARIES_DIR_NAME in Path(norm_path).parts

            def _debounced_sync(self):
                with self._timer_lock:
                    if self._timer is not None:
                        self._timer.cancel()
                    self._timer = threading.Timer(1.5, self._trigger_sync)
                    self._timer.daemon = True
                    self._timer.start()

            def _trigger_sync(self):
                if not engine_ref._sync_in_progress:
                    engine_ref._sync_index()

            def on_created(self, event):
                if (not event.is_directory
                        and not self._is_summaries(event.src_path)
                        and Path(event.src_path).suffix.lower() in SUPPORTED_EXTENSIONS):
                    if engine_ref._sync_in_progress:
                        return
                    print(f"[RAG] 🆕 新檔案：{event.src_path}")
                    self._debounced_sync()

            def on_modified(self, event):
                if (not event.is_directory
                        and not self._is_summaries(event.src_path)
                        and Path(event.src_path).suffix.lower() in SUPPORTED_EXTENSIONS):
                    if engine_ref._sync_in_progress:
                        return
                    print(f"[RAG] 🔄 檔案更新：{event.src_path}")
                    self._debounced_sync()

            def on_deleted(self, event):
                if (not event.is_directory
                        and not self._is_summaries(event.src_path)):
                    if engine_ref._sync_in_progress:
                        return
                    print(f"[RAG] 🗑️ 檔案刪除：{event.src_path}")
                    self._debounced_sync()

        os.makedirs(self.docs_dir, exist_ok=True)
        self._observer = Observer()
        self._observer.schedule(_Handler(), self.docs_dir, recursive=True)
        self._observer.daemon = True
        self._observer.start()
        print(f"[RAG] 👁️ 監控中：{self.docs_dir}（排除 summaries/）")

    def stop_watching(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()

    # ── 狀態與管理 ────────────────────────────────────────────────────────────

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

        # #7 修正：list_summary_status 使用 os.listdir 而非 os.walk，排除 summaries/
        summary_status = self._get_summary_status()
        summarized = sum(1 for v in summary_status.values() if v)
        total_docs = len(summary_status)

        return {
            "status": self._status,
            "indexed_files": [os.path.basename(f) for f in self._indexed_files],
            "total_chunks": count,
            "last_updated": self._last_updated.strftime("%Y-%m-%d %H:%M:%S") if self._last_updated else "尚未更新",
            "summary_status": summary_status,
            "summarized_count": summarized,
            "total_docs": total_docs,
            "two_step_ingest": self.two_step_ingest,
        }

    def _get_summary_status(self) -> Dict[str, bool]:
        """
        #7 修正：以 os.listdir 掃描 docs/ 頂層文件（不遞迴），
        排除 summaries/ 子目錄本身，回傳 {filename: has_summary}。
        確認摘要檔案存在且大小 > 0。
        """
        result = {}
        if not os.path.exists(self.docs_dir):
            return result
        for fname in os.listdir(self.docs_dir):
            fpath = os.path.join(self.docs_dir, fname)
            if os.path.isfile(fpath) and Path(fname).suffix.lower() in SUPPORTED_EXTENSIONS:
                stem = Path(fname).stem
                summary_path = os.path.join(self._summaries_dir, f"{stem}_summary.md")
                result[fname] = os.path.isfile(summary_path) and os.path.getsize(summary_path) > 0
        return result

    def force_reindex(self, clear_summaries: bool = False):
        """
        強制完整重建向量索引。
        #9 推回後的設計：預設只清 ChromaDB（保留摘要，直接重新向量化）。
        clear_summaries=True 時額外清除 docs/summaries/（重新跑 LLM 摘要）。
        """
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

            # 只清向量索引指紋，保留 source_fingerprints（避免重新觸發不必要的 LLM 摘要）
            self._index_fingerprints = {}
            if clear_summaries:
                self._source_fingerprints = {}
                # 刪除 summaries/ 目錄下所有 .md
                import shutil
                if os.path.exists(self._summaries_dir):
                    shutil.rmtree(self._summaries_dir)
                    print(f"[RAG] 🗑️ 已清除摘要目錄：{self._summaries_dir}")
            self._save_fingerprints()
        self._sync_index()
