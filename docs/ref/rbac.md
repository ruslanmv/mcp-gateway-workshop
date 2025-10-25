
# RBAC & Auth — Cheatsheet

## Roles

```yaml
rbac:
  roles:
    - name: admin
      allow_all: true
    - name: analyst
      allow_tools: ["lf.summarize"]
    - name: viewer
      allow_tools: []
```

## JWT Tips

* Include a `role` claim in tokens  
* Send as `Authorization: Bearer <token>`  
* Use short-lived tokens for agents; rotate regularly
