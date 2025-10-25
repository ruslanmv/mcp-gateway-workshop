# Appendix A — Building a Multimodal RAG Chatbot with Docling + IBM watsonx.ai via the MCP Gateway

> Optional deep‑dive. Ingest PDFs/images with **Docling**, embed with **IBM watsonx.ai**, index in **ChromaDB**, and expose as an **MCP server** behind your **Gateway**. The client talks only to the Gateway.

## Why Docling for RAG?
Docling converts messy PDFs/Office/scans into structured text (and image snippets). Great for enterprise RAG: less noise, preserved structure, multimodal hooks.

## Prerequisites
Gateway on **:4444** + JWT; Python 3.11+; IBM watsonx.ai API key, project ID, region; `curl` + `jq`.

## 1) Environment
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn pydantic chromadb requests python-multipart
pip install docling
pip install ibm-generative-ai
pip install sentence-transformers  # optional local embeddings
export WATSONX_API_KEY="<key>"; export WATSONX_PROJECT_ID="<project>"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
export WATSONX_EMBED_MODEL="sentence-transformers/all-minilm-l6-v2"
export WATSONX_LLM_MODEL="meta-llama/llama-4-scout-17b-16e-instruct"
# optional local fallback
export USE_LOCAL_EMBEDDINGS=1
```

## 2) Docling MCP Server (full)

```python
# docling_mcp_server.py
# (Complete FastAPI server implementing docling.parse, docling.ingest, docling.query,
# with ChromaDB and watsonx.ai, as in the main manuscript Part IV appendix)
# For brevity in this page, reuse the same code from the book's Appendix A section.
```
See the main book appendix for the complete code block.

## 3) Register with Gateway

```bash
export BASE_URL=http://localhost:4444; export TOKEN=$MCPGATEWAY_BEARER_TOKEN
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{
  "name":"docling","url":"http://localhost:9200","description":"Docling RAG Server","enabled":true,"request_type":"STREAMABLEHTTP"
}' $BASE_URL/gateways | jq '.'
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name, gateway: .gatewaySlug}'
```

## 4) Tiny Chat Client (Gateway-only)

```python
# chat_rag_client.py
import os, requests
BASE_URL=os.getenv("GATEWAY_URL","http://localhost:4444"); TOKEN=os.getenv("GATEWAY_TOKEN","")
headers={"Content-Type":"application/json", **({"Authorization":f"Bearer {TOKEN}"} if TOKEN else {})}
def ask(q:str,k:int=4):
  r=requests.post(f"{BASE_URL}/call/docling.query",json={"query":q,"k":k},headers=headers,timeout=60); r.raise_for_status(); return r.json()
if __name__=="__main__":
  resp=ask("Summarize our SOW termination clause."); print(resp.get("answer")); print(resp.get("sources"))
```

## 5) Guardrails, RBAC, Observability
Reuse the main book’s examples: rate limiter, secrets detection, RBAC, OTEL to Phoenix.
