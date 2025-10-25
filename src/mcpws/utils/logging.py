import logging, json, time, os, sys, uuid
from typing import Any, Dict

def _json_formatter(record: logging.LogRecord) -> str:
    base = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
        "level": record.levelname,
        "name": record.name,
        "msg": record.getMessage(),
    }
    if record.exc_info:
        base["exc_info"] = True
    if hasattr(record, "extra") and isinstance(record.extra, dict):
        base.update(record.extra)  # type: ignore
    return json.dumps(base, ensure_ascii=False)

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        return _json_formatter(record)

def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger

def correlation_id() -> str:
    return uuid.uuid4().hex
