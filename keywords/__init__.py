# ============================================================
# THƯ VIỆN KEYWORD (tầng nghiệp vụ). Dùng trong test qua fixture `k`:
#     k.catalog.open_product(slug)
#     k.cart.verify_cart_badge(1)
# Kịch bản Excel gọi cùng các keyword này bằng tên "nhóm.tenCamelCase", vd: "cart.verifyCartBadge".
# KEYWORD_MAP là registry tường minh: tên keyword -> (thuộc tính nhóm, tên method).
# ============================================================
from keywords.kw_account import AccountKeywords
from keywords.kw_admin import AdminKeywords
from keywords.kw_admin_catalog import AdminCatalogKeywords
from keywords.kw_admin_marketing import AdminMarketingKeywords
from keywords.kw_admin_ops import AdminOpsKeywords
from keywords.kw_admin_sales import AdminSalesKeywords
from keywords.kw_auth import AuthKeywords
from keywords.kw_cart import CartKeywords
from keywords.kw_catalog import CatalogKeywords
from keywords.kw_checkout import CheckoutKeywords
from keywords.kw_common import CommonKeywords
from keywords.kw_content import ContentKeywords
from keywords.kw_listing import ListingKeywords
from keywords.kw_product import ProductKeywords
from pages.page_objects import PageObjects

# (thuộc tính trên Keywords, lớp keyword). Thứ tự = thứ tự trong KEYWORDS.md.
GROUPS = (
    ("common", CommonKeywords),
    ("auth", AuthKeywords),
    ("catalog", CatalogKeywords),
    ("listing", ListingKeywords),
    ("product", ProductKeywords),
    ("content", ContentKeywords),
    ("cart", CartKeywords),
    ("checkout", CheckoutKeywords),
    ("account", AccountKeywords),
    ("admin", AdminKeywords),
    ("admin_catalog", AdminCatalogKeywords),
    ("admin_sales", AdminSalesKeywords),
    ("admin_marketing", AdminMarketingKeywords),
    ("admin_ops", AdminOpsKeywords),
)


def build_keyword_map():
    keyword_map = {}
    for attr, klass in GROUPS:
        if not klass.group:
            raise ValueError(f"{klass.__name__} chưa khai báo group")
        for name, method in klass.keywords().items():
            full_name = f"{klass.group}.{name}"
            if full_name in keyword_map:
                raise ValueError(f"Keyword trùng tên: {full_name}")
            keyword_map[full_name] = (attr, method)
    return keyword_map


KEYWORD_MAP = build_keyword_map()


class Keywords:
    def __init__(self, page, api):
        self.page = page
        self.po = PageObjects(page)
        self.common = CommonKeywords(page, self.po, api)
        for attr, klass in GROUPS[1:]:
            setattr(self, attr, klass(page, self.po, api, self.common))

    def resolve(self, name):
        """Tìm keyword theo tên "nhóm.tenCamelCase" -> method đã bind sẵn."""
        if name not in KEYWORD_MAP:
            raise ValueError(f'Keyword không tồn tại: "{name}". Xem danh sách trong KEYWORDS.md')
        attr, method = KEYWORD_MAP[name]
        return getattr(getattr(self, attr), method)
