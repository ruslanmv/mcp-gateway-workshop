
# Plugins & Guardrails — Cheatsheet

## Rate Limiter

```yaml
- name: rate_limiter
  kind: plugins.rate_limiter.rate_limiter.RateLimiterPlugin
  hooks: ["prompt_pre_fetch", "tool_pre_invoke"]
  mode: enforce
  priority: 50
  config:
    by_user: "60/m"
    by_tenant: "600/m"
    by_tool: "30/m"
    burst: 5
```

## Secrets Detection

```yaml
- name: SecretsDetection
  kind: plugins.secrets_detection.secrets_detection.SecretsDetectionPlugin
  hooks: ["prompt_pre_fetch", "tool_post_invoke", "resource_post_fetch"]
  mode: enforce
  priority: 45
  config:
    detectors:
      patterns:
        openai_key: true
        slack_token: true
        private_key_block: true
        jwt_like: true
    redact: true
    redaction_text: "***REDACTED***"
    block_on_detection: true
    min_findings_to_block: 1
```

## PII Filter (example)

```yaml
- name: pii_filter
  kind: plugins.pii_filter.pii_filter.PIIFilterPlugin
  hooks: ["tool_pre_invoke", "tool_post_invoke"]
  mode: enforce
  priority: 40
  config:
    action: redact
    categories: [email, phone, credit_card]
```
