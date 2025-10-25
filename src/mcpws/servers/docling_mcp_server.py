# File: src/mcpws/servers/docling_mcp_server.py
from __future__ import annotations

import base64
import io
import json
import os
import time
import uuid
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union, cast

import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

# ---------- Logging ----------
import logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format="%(message)s")
log = logging.getLogger("docling_mcp")


def jlog(event: str, **fields: Any) -> None:
    log.info(json.dumps({"event": event, **fields}, ensure_ascii=False))


# ---------- Settings ----------
CHROMA_DIR = os.getenv("CHROMA_DIR", "").strip()
COLLECTION_NAME = os.getenv("DOC_COLLECTION", "docling_rag")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "50"))
PORT = int(os.getenv("PORT", "9200"))
USE_LOCAL_EMBEDDINGS = bool(int(os.getenv("USE_LOCAL_EMBEDDINGS", "0")))

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_EMBED_MODEL = os.getenv("WATSONX_EMBED_MODEL", "sentence-transformers/all-minilm-l6-v2")
WATSONX_LLM_MODEL = os.getenv("WATSONX_LLM_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

# ---------- Docling ----------
try:
    from docling.document_converter import DocumentConverter

    HAVE_DOCLING = True
except Exception as e:  # pragma: no cover - best-effort import
    HAVE_DOCLING = False
    jlog("warn", msg=f"Docling not available: {e}")

# ---------- IBM watsonx.ai SDK (genai) ----------
HAVE_WX = False
wx_client: Any = None
if not USE_LOCAL_EMBEDDINGS:
    try:
        from genai import Client
        from genai.credentials import Credentials

        if WATSONX_API_KEY:
            creds = Credentials(api_key=WATSONX_API_KEY, api_endpoint=WATSONX_URL)
            wx_client = Client(credentials=creds)
            HAVE_WX = True
        else:
            jlog(
                "warn",
                msg="WATSONX_API_KEY not set; embeddings/LLM will use local fallback or be disabled",
            )
    except Exception as e:  # pragma: no cover - optional dependency
        jlog("warn", msg=f"IBM genai SDK not available or failed to init: {e}")

# ---------- Vector store ----------
if CHROMA_DIR:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
else:
    client = chromadb.Client()
collection = client.get_or_create_collection(name=COLLECTION_NAME)

# Local embedding fallback (only used when watsonx embeddings are unavailable)
local_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ---------- Helpers ----------
def _chunk(text: str, size: int, overlap: int) -> Iterable[str]:
    if size <= 0:
        yield text
        return
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + size)
        yield text[start:end]
        start = end - overlap if (end - overlap) > start else end


def _file_too_large(content: bytes) -> bool:
    return (len(content) / (1024 * 1024)) > MAX_FILE_MB


def _ensure_docling() -> None:
    if not HAVE_DOCLING:
        raise RuntimeError("Docling is not installed. `pip install docling`")


def _to_float_vectors(vectors_any: Sequence[Sequence[float | int]]) -> List[List[float]]:
    return [[float(x) for x in row] for row in vectors_any]


def _embed_texts(texts: List[str]) -> List[List[float]]:
    """Embeddings via watsonx (preferred) or local sentence-transformers fallback."""
    if HAVE_WX and not USE_LOCAL_EMBEDDINGS:
        try:
            # Lazy imports for type-check friendliness
            from genai.schema import TextEmbeddingParameters  # type: ignore

            assert wx_client is not None
            params = TextEmbeddingParameters()  # type: ignore[call-arg]
            out = wx_client.embeddings.create(  # type: ignore[attr-defined]
                model_id=WATSONX_EMBED_MODEL,
                input=texts,
                parameters=params,
                project_id=WATSONX_PROJECT_ID or None,
            )
            results = getattr(out, "results", [])
            raw_vecs: List[Sequence[float | int]] = [
                getattr(item, "embedding", []) for item in results
            ]
            return _to_float_vectors(raw_vecs)
        except Exception as e:
            jlog("warn", msg=f"watsonx embeddings failed; falling back to local: {e}")
    # Fallback
    local_vecs_any = local_embedder(texts)
    # Cast to assure mypy that list[ndarray] is compatible with Sequence[Sequence[...]]
    return _to_float_vectors(cast(Sequence[Sequence[float | int]], local_vecs_any))


def _generate_answer(prompt: str, *, max_new_tokens: int = 512, temperature: float = 0.2) -> str:
    if HAVE_WX:
        try:
            from genai.schema import TextGenerationParameters  # type: ignore

            assert wx_client is not None
            params = TextGenerationParameters(  # type: ignore[call-arg]
                decoding_method=cast(Any, "greedy"),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
            )
            resp = wx_client.text.generation.create(  # type: ignore[attr-defined]
                model_id=WATSONX_LLM_MODEL,
                input=prompt,
                parameters=params,
                project_id=WATSONX_PROJECT_ID or None,
            )
            return getattr(resp.results[0], "generated_text", "")  # type: ignore[index]
        except Exception as e:
            return f"[LLM error] {e}"
    return "[LLM not configured] Set WATSONX_* env or run with USE_LOCAL_EMBEDDINGS=1 (no gen)."


# ---------- Schemas ----------
class QueryPayload(BaseModel):
    query: str = Field(..., description="User question")
    k: int = Field(4, description="Top K passages to retrieve")


# ---------- App ----------
app = FastAPI(title="Docling MCP Server", version="1.0.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/tools")
def tools() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "docling.parse",
                "description": "Parse a single PDF/image and return extracted text (and base64 images).",
                "schema": {
                    "type": "object",
                    "properties": {"return_images": {"type": "boolean", "default": False}},
                    "required": [],
                },
            },
            {
                "name": "docling.ingest",
                "description": "Parse & ingest PDFs/images into the vector index.",
                "schema": {
                    "type": "object",
                    "properties": {"metas": {"type": "object"}},
                    "required": [],
                },
            },
            {
                "name": "docling.query",
                "description": "RAG query over ingested documents.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "k": {"type": "integer", "default": 4},
                    },
                    "required": ["query"],
                },
            },
        ]
    }


@app.post("/call/docling.parse")
async def call_parse(
    request: Request,
    return_images: bool = Form(False),
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    started = time.time()
    corr = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    try:
        _ensure_docling()
        content = await file.read()
        if _file_too_large(content):
            raise ValueError(f"File exceeds {MAX_FILE_MB} MB limit")

        converter = DocumentConverter()
        # Use Any for the conversion result to keep mypy happy across docling versions
        result: Any = converter.convert(cast(Any, io.BytesIO(content)), cast(Any, file.filename))

        text = result.document.export_to_markdown()
        images_b64: List[str] = []
        if return_images and getattr(result, "images", None):
            for img in result.images:  # type: ignore[attr-defined]
                buf = io.BytesIO()
                img.pil_image.save(buf, format="PNG")
                images_b64.append(base64.b64encode(buf.getvalue()).decode("utf-8"))

        payload = {
            "filename": file.filename,
            "text": text,
            "images": images_b64,
            "latency_ms": int((time.time() - started) * 1000),
            "correlation_id": corr,
        }
        jlog("docling.parse", corr=corr, file=file.filename, latency_ms=payload["latency_ms"])
        return payload
    except Exception as e:
        jlog("error", tool="docling.parse", corr=corr, error=str(e))
        raise HTTPException(status_code=400, detail=f"{corr}: {e}") from e


@app.post("/call/docling.ingest")
async def call_ingest(
    request: Request,
    metas: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
) -> Dict[str, Any]:
    started = time.time()
    corr = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    try:
        _ensure_docling()
        meta_common = json.loads(metas) if metas else {}
        converter = DocumentConverter()

        texts: List[str] = []
        ids: List[str] = []
        metadatas_raw: List[Dict[str, Any]] = []

        for f in files:
            content = await f.read()
            if _file_too_large(content):
                raise ValueError(f"{f.filename} exceeds {MAX_FILE_MB} MB limit")

            result: Any = converter.convert(cast(Any, io.BytesIO(content)), cast(Any, f.filename))
            md_text = result.document.export_to_markdown()

            for idx, chunk in enumerate(_chunk(md_text, CHUNK_SIZE, CHUNK_OVERLAP)):
                texts.append(chunk)
                ids.append(f"{f.filename}:{idx}")
                metadatas_raw.append({"source": f.filename, **meta_common})

        if not texts:
            raise ValueError("No text extracted from provided files")

        vecs = _embed_texts(texts)

        # Coerce metadata values to supported scalar types for Chroma
        MetaVal = Union[str, int, float, bool, None]
        metadatas: List[Mapping[str, MetaVal]] = []
        for m in metadatas_raw:
            clean: Dict[str, MetaVal] = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)) or v is None:
                    clean[k] = v
                else:
                    clean[k] = str(v)
            metadatas.append(clean)

        collection.upsert(
            documents=texts,
            embeddings=cast(List[Sequence[float]], vecs),
            ids=ids,
            metadatas=cast(Any, metadatas),
        )

        payload = {
            "ingested_docs": len(set(cast(str, m.get("source", "")) for m in metadatas_raw)),
            "chunks": len(texts),
            "latency_ms": int((time.time() - started) * 1000),
            "correlation_id": corr,
        }
        jlog(
            "docling.ingest",
            corr=corr,
            docs=payload["ingested_docs"],
            chunks=payload["chunks"],
            latency_ms=payload["latency_ms"],
        )
        return payload
    except Exception as e:
        jlog("error", tool="docling.ingest", corr=corr, error=str(e))
        raise HTTPException(status_code=400, detail=f"{corr}: {e}") from e


class _QueryOut(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    latency_ms: int
    correlation_id: str


@app.post("/call/docling.query", response_model=_QueryOut)
async def call_query(payload: QueryPayload, request: Request) -> _QueryOut:
    started = time.time()
    corr = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    try:
        qvec = _embed_texts([payload.query])[0]
        res = collection.query(
            query_embeddings=cast(List[Sequence[float]], [qvec]), n_results=payload.k
        )

        docs_any = res.get("documents") or [[]]
        metas_any = res.get("metadatas") or [[]]
        docs = cast(List[List[str]], docs_any)
        metas = cast(List[List[Mapping[str, Union[str, int, float, bool, None]]]], metas_any)

        docs0 = docs[0] if docs else []
        metas0 = metas[0] if metas else []

        context = "\n\n".join(docs0[: payload.k])
        prompt = (
            "You are a helpful assistant. Use the context to answer the question.\n"
            "Cite relevant sources by filename when possible. If unsure, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {payload.query}\n"
            "Answer:"
        )
        answer = _generate_answer(prompt)

        sources: List[Dict[str, Any]] = [dict(m) for m in metas0][: payload.k]
        out = _QueryOut(
            answer=answer,
            sources=sources,
            latency_ms=int((time.time() - started) * 1000),
            correlation_id=corr,
        )
        jlog("docling.query", corr=corr, k=payload.k, latency_ms=out.latency_ms)
        return out
    except Exception as e:
        jlog("error", tool="docling.query", corr=corr, error=str(e))
        raise HTTPException(status_code=400, detail=f"{corr}: {e}") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
