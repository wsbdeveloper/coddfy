"""
Módulo central de logging para o backend.
Fornece configuração inicial e helpers para debugs, ferramentas e tratamento de exceções.
"""
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE_PATH = Path("logs/ccm.log")
MAX_LOG_BYTES = 10 * 1024 * 1024  # 10MB por arquivo
BACKUP_COUNT = 5
FORMAT_STRING = "%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s] %(message)s"


def _ensure_log_dir():
    """Garante que o diretório de log exista."""
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def bootstrap_logging():
    """
    Configura o handler rotativo adicional para o logger root.

    Deve ser chamado depois de `pyramid.paster.setup_logging`.
    """
    _ensure_log_dir()
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, RotatingFileHandler) and handler.baseFilename == str(LOG_FILE_PATH):
            return

    handler = RotatingFileHandler(
        filename=str(LOG_FILE_PATH),
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(FORMAT_STRING))
    root_logger.addHandler(handler)


def _format_payload(message: str, context: dict | None) -> str:
    if not context:
        return message
    try:
        payload = json.dumps(context, default=str, ensure_ascii=False)
    except Exception:
        payload = str(context)
    return f"{message} | context={payload}"


def get_logger(name: str | None = None) -> logging.Logger:
    """Retorna o logger configurado para o backend."""
    return logging.getLogger(name or "backend")


def log_debug(message: str, *, context: dict | None = None):
    """Helper para logs de debug."""
    get_logger().debug(_format_payload(message, context))


def log_info(message: str, *, context: dict | None = None):
    """Helper para logs informativos."""
    get_logger().info(_format_payload(message, context))


def log_error(message: str, *, context: dict | None = None):
    """Helper para logs de erro simples."""
    get_logger().error(_format_payload(message, context))


def log_exception(message: str, *, exc: Exception | None = None, context: dict | None = None):
    """
    Loga uma exceção com stack trace completo.

    Usar nos handlers de except para garantir que o traceback vá para os logs rotativos.
    """
    if exc:
        context = {**(context or {}), "exception": str(exc)}
        get_logger().exception(
            _format_payload(message, context),
            exc_info=(type(exc), exc, exc.__traceback__)
        )
        return
    get_logger().exception(_format_payload(message, context))


def log_tool_event(tool_name: str, action: str, *, status: str = "info", details: dict | None = None):
    """
    Log estruturado para integrações com ferramentas externas.
    """
    context = {"tool": tool_name, "action": action, "status": status}
    if details:
        context["details"] = details
    get_logger("backend.tools").info(_format_payload(f"[tool:{tool_name}] {action}", context))

