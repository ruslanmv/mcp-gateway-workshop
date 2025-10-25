
# Observability — Logs & Traces

## Phoenix (OTEL)

```bash
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
export OTEL_ENABLE_OBSERVABILITY=true
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
mcpgateway
```

## Log Checklist

* correlation/request IDs  
* latency (ms)  
* policy decisions (rate-limit, redaction)  
* tool names & payload shape (avoid sensitive data)
