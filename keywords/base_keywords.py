# ============================================================
# LỚP CHA CỦA MỌI NHÓM KEYWORD
# Quy ước:
# - Mỗi method public có @keyword("tenCamelCase") = 1 keyword, kịch bản Excel gọi bằng
#   "nhóm.tenCamelCase" (vd: "cart.verifyCartBadge"). Registry tường minh, không eval.
# - Docstring dòng đầu = mô tả keyword (dùng để sinh KEYWORDS.md).
# - Thân hàm bọc trong `with self.step(...)`: 1 Allure step + log START/PASS/FAIL.
# - Keyword không quản lý vòng đời browser; Verify giữ assertion nghiệp vụ.
# ============================================================
from contextlib import contextmanager

import allure

from utils.data_loader import mask_secrets
from utils.error_classifier import classify_exception
from utils.logging_config import event_context, get_logger


def keyword(name):
    """Đánh dấu method là keyword công khai với tên dùng trong kịch bản."""

    def decorate(function):
        function.keyword_name = name
        return function

    return decorate


class BaseKeywords:
    # Tên nhóm trong kịch bản, vd: "cart" -> "cart.openCart". Lớp con bắt buộc khai báo.
    group = ""

    def __init__(self, page, po, api, common=None):
        self.page = page
        self.po = po
        self.api = api
        # Nhóm common dùng chung (request đã bắt bởi mockWrite...). None với chính CommonKeywords.
        self.common = common

    @contextmanager
    def step(self, title):
        title = mask_secrets(title)
        logger = get_logger()
        context = event_context(action=self.group, target=title, result="START")
        logger.debug("Bắt đầu keyword", extra=context)
        with allure.step(title):
            try:
                yield
            except Exception as error:
                category = classify_exception(error)
                logger.error(
                    f"Keyword thất bại; category={category}",
                    extra={**context, "result": "FAIL"},
                )
                raise
        logger.info("Hoàn thành keyword", extra={**context, "result": "PASS"})

    @classmethod
    def keywords(cls):
        """{tên keyword: tên method} của nhóm, theo thứ tự khai báo."""
        found = {}
        for klass in reversed(cls.__mro__):
            for attr, value in vars(klass).items():
                name = getattr(value, "keyword_name", None)
                if name:
                    found[name] = attr
        return found
