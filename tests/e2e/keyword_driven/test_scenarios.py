# ============================================================
# TEST: KỊCH BẢN KEYWORD-DRIVEN + DATA-DRIVEN (HYBRID)
# Mục tiêu: mỗi dòng TestData trong data/scenarios/*.xlsx là một pytest item độc lập
# Kịch bản: TestSteps (template) + TestData (meta + giá trị placeholder)
# API cần quan sát: read_hybrid_cases, case_params, execute_steps
# WHY: thêm kịch bản = thêm dòng Excel, không sửa code. Danh sách keyword: KEYWORDS.md
# Debug: lỗi đọc/binding Excel xảy ra lúc collection, khác lỗi timeout/AssertionError lúc chạy
# ============================================================
import allure
import pytest

from config import SCENARIO_DIR
from drivers.driver_script import execute_steps
from utils.cases import case_params
from utils.hybrid_reader import read_hybrid_cases

# Nạp/kiểm tra/gắn dữ liệu khi collection: chưa có browser nào được mở.
CASES = [
    {**case, "workbook": path.name}
    for path in sorted(SCENARIO_DIR.glob("*.xlsx"))
    if not path.name.startswith("~$")
    for case in read_hybrid_cases(path)
]


@pytest.mark.parametrize("case", case_params(CASES))
def test_scenario(k, ctx, case):
    allure.dynamic.story(case["workbook"])
    allure.dynamic.parameter("template_id", case["template_id"])
    try:
        execute_steps(k, case["steps"], ctx)
    except Exception as error:
        error.add_note(f"Workbook {case['workbook']}, template {case['template_id']}, case {case['id']}")
        raise
