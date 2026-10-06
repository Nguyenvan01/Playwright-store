# ============================================================
# LOGGING CONFIGURATION
#
# Mục tiêu:
# - Ghi cùng một sự kiện ra console và file log của lần chạy.
# - Cho phép đổi mức log bằng TEST_LOG_LEVEL.
# - Chuẩn hóa ngữ cảnh: TC_ID | Step | Action | Target | Result.
# - TC_ID của test đang chạy được giữ trong contextvar -> keyword không cần truyền tay.
# ============================================================
import logging
import os
from contextvars import ContextVar
from pathlib import Path

LOGGER_NAME = "cloth_store_e2e"
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(tc_id)s | %(step)s | "
    "%(action)s | %(target)s | %(result)s | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
CONTEXT_DEFAULTS = {
    "tc_id": "-",
    "step": "-",
    "action": "-",
    "target": "-",
    "result": "-",
}

# Test case đang chạy; conftest đặt giá trị ở đầu mỗi test.
current_tc_id = ContextVar("current_tc_id", default="-")


class ContextDefaultsFilter(logging.Filter):
    """Bổ sung giá trị mặc định để formatter không lỗi với log hệ thống."""

    def filter(self, record):
        for field, default in CONTEXT_DEFAULTS.items():
            if not hasattr(record, field):
                setattr(record, field, default)
        if record.tc_id == "-":
            record.tc_id = current_tc_id.get()
        return True


def resolve_log_level(value=None):
    """Đọc và kiểm tra mức log; không âm thầm chấp nhận cấu hình sai."""
    name = (value or os.getenv("TEST_LOG_LEVEL", "INFO")).strip().upper()
    if name not in ALLOWED_LEVELS:
        raise ValueError(
            f"TEST_LOG_LEVEL={name!r} không hợp lệ; chọn {sorted(ALLOWED_LEVELS)}"
        )
    return getattr(logging, name)


def configure_logging(log_dir, run_id, logger_name=LOGGER_NAME):
    """Cấu hình logger riêng cho framework và trả về logger cùng đường dẫn file."""
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / f"run_{run_id}.log"
    level = resolve_log_level()

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    context_filter = ContextDefaultsFilter()

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger, log_path


def event_context(tc_id="-", step="-", action="-", target="-", result="-"):
    """Tạo trường ngữ cảnh dùng với tham số extra của logging."""
    return {
        "tc_id": str(tc_id or "-"),
        "step": str(step or "-"),
        "action": str(action or "-"),
        "target": str(target or "-"),
        "result": str(result or "-"),
    }


def get_logger():
    """Lấy logger đã được pytest session cấu hình trong tests/conftest.py."""
    return logging.getLogger(LOGGER_NAME)
