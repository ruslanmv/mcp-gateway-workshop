# Appendix D — Troubleshooting & FAQ

- **502 from gateway** → Adapter URL/port mismatch; fix and retry.  
- **Tool missing** → Adapter `/tools` must return valid JSON; check gateway logs.  
- **CORS in UI** → Set allowed origins; use CLI while fixing UI.  
- **Rate limiter not firing** → Lower thresholds/window; ensure plugin is enabled.  
- **RBAC not applying** → Confirm JWT contains proper role claims; reload config.
