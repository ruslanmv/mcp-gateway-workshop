
# Troubleshooting & FAQ

**502 from gateway** → adapter URL/port mismatch; fix, restart adapter, retry.

**Tool missing in catalog** → adapter `/tools` returns wrong schema or empty; fix JSON; check gateway logs.

**CORS in UI** → set allowed origins; use CLI while fixing UI.

**Rate limiter not firing** → lower thresholds/window; confirm plugin is enabled.

**RBAC not applying** → confirm JWT contains role claims; reload config; verify header `Authorization: Bearer`.

**Langflow flow errors** → validate `flow_id`, inspect Langflow server logs.
