# ============================================================
# DRIVER SCRIPT: thực thi một kịch bản đã binding và phát log theo từng bước.
# Lỗi được phân loại, bổ sung ngữ cảnh rồi ném lại; không đổi FAIL thành boolean.
#
# Hai tầng thay biến:
#   {cot}        -> gắn lúc collection từ dòng TestData (utils/template_binding.py)
#   ${product.x} -> thay lúc chạy từ context runtime (sản phẩm thật lấy qua API, .env...)
# ============================================================
import json

import allure

from keywords import KEYWORD_MAP
from utils.data_loader import mask_secrets, resolve_data
from utils.error_classifier import classify_exception
from utils.logging_config import event_context, get_logger

FIELDS = {"case_id", "step", "keyword", "args", "note"}


def is_check_step(keyword_name):
    """Bước kiểm tra: verify* hoặc keyword có chờ kết quả (…Expecting…)."""
    method = keyword_name.split(".", 1)[-1]
    return method.startswith("verify") or "Expecting" in method


def validate_steps(steps):
    """Báo lỗi schema trước khi thao tác UI; không bỏ qua keyword không biết."""
    if not isinstance(steps, list) or not steps:
        raise ValueError("Kịch bản không có bước")
    case_id = steps[0].get("case_id") if isinstance(steps[0], dict) else None
    for index, row in enumerate(steps, 1):
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError(f"Bước {index}: sai schema")
        if not case_id or row["case_id"] != case_id or row["step"] != str(index):
            raise ValueError(f"Bước {index}: sai case_id hoặc thứ tự step")
        if row["keyword"] not in KEYWORD_MAP:
            raise ValueError(f"Bước {index}: keyword chưa khai báo: {row['keyword']}")
        if not isinstance(row["args"], list):
            raise ValueError(f"Bước {index}: args phải là mảng JSON")
        if not isinstance(row["note"], str):
            raise ValueError(f"Bước {index}: note phải là chuỗi")
    if not any(is_check_step(row["keyword"]) for row in steps):
        raise ValueError(f"Kịch bản {case_id} cần ít nhất một bước kiểm tra (verify*)")
    return steps


def format_args(args):
    parts = []
    for arg in args:
        text = f'"{arg}"' if isinstance(arg, str) else json.dumps(arg, ensure_ascii=False)
        parts.append(text if len(text) <= 60 else f"{text[:57]}...")
    return ", ".join(parts)


def execute_steps(k, steps, ctx):
    validate_steps(steps)
    logger = get_logger()
    case_id = steps[0]["case_id"]
    allure.dynamic.feature("Keyword-driven")
    logger.info(
        "Bắt đầu kịch bản",
        extra=event_context(tc_id=case_id, action="execute_case", result="START"),
    )
    for row in steps:
        args = resolve_data(row["args"], ctx)
        target = mask_secrets(format_args(args))
        context = event_context(
            tc_id=case_id, step=row["step"], action=row["keyword"], target=target, result="START",
        )
        logger.info("Bắt đầu bước", extra=context)
        title = f"{row['step']}. {row['keyword']}({target})"
        if row["note"]:
            title += f" — {row['note']}"
        with allure.step(mask_secrets(title)):
            try:
                k.resolve(row["keyword"])(*args)
            except Exception as error:
                category = classify_exception(error)
                error.add_note(
                    f"Case {case_id}, step {row['step']}, keyword {row['keyword']}, "
                    f"args {target or '-'}, category {category}"
                )
                logger.exception(
                    f"Bước thất bại; category={category}",
                    extra={**context, "result": "FAIL"},
                )
                allure.attach(category, "error-category", allure.attachment_type.TEXT)
                raise
            else:
                logger.info("Hoàn thành bước", extra={**context, "result": "PASS"})
    logger.info(
        "Hoàn thành kịch bản",
        extra=event_context(tc_id=case_id, action="execute_case", result="PASS"),
    )
