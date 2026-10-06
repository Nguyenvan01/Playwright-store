# ============================================================
# DEMO: LOGGING CONFIGURATION
# Mục tiêu: kiểm tra mức log cấu hình được và định dạng Hybrid thống nhất.
# Kịch bản: tạo logger DEBUG riêng, ghi một bước và đọc lại file.
# Kết quả: log có TC_ID | Step | Action | Target | Result; TC_ID tự lấy từ test đang chạy.
# ============================================================
import logging

import pytest

from utils.logging_config import (
    configure_logging,
    current_tc_id,
    event_context,
    resolve_log_level,
)

pytestmark = pytest.mark.core


def test_log_level_from_environment(monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "DEBUG")
    assert resolve_log_level() == logging.DEBUG


def test_invalid_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "VERBOSE")
    with pytest.raises(ValueError, match="không hợp lệ"):
        resolve_log_level()


def test_log_file_contains_hybrid_context(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "DEBUG")
    logger, log_path = configure_logging(tmp_path, "contract", "hybrid_contract_test")
    logger.info(
        "Hoàn thành bước",
        extra=event_context("KD-SHOP-02", "6", "cart.increaseQuantity", '"Áo thun E2E", 2', "PASS"),
    )
    for handler in logger.handlers:
        handler.flush()
    content = log_path.read_text(encoding="utf-8")
    assert 'KD-SHOP-02 | 6 | cart.increaseQuantity | "Áo thun E2E", 2 | PASS | Hoàn thành bước' in content


def test_tc_id_taken_from_running_test(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_LOG_LEVEL", "INFO")
    logger, log_path = configure_logging(tmp_path, "tc", "hybrid_tc_test")
    token = current_tc_id.set("CART-01")
    try:
        logger.info("Không truyền tc_id", extra=event_context(action="cart", result="PASS"))
    finally:
        current_tc_id.reset(token)
    for handler in logger.handlers:
        handler.flush()
    assert "| CART-01 | - | cart | - | PASS | Không truyền tc_id" in log_path.read_text(encoding="utf-8")
