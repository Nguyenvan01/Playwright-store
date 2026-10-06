# ============================================================
# HỖ TRỢ CHUNG cho test tài khoản: mẫu URL API + mock dữ liệu trang hồ sơ.
# ============================================================
from utils.data_loader import load_data

# Mẫu URL (glob Playwright) của các API tài khoản. `*` không vượt qua "/".
API = {
    "profile": "**/api/profile",
    "changePassword": "**/api/profile/change-password",
    # GET danh sách (có query ?page=&limit=) và POST tạo đơn.
    "orders": "**/api/orders*",
    "createOrder": "**/api/orders",
    "orderDetail": "**/api/orders/*",
    "cancelOrder": "**/api/orders/*/cancel",
    "wishlist": "**/api/wishlist",
    "wishlistItem": "**/api/wishlist/*",
    "addresses": "**/api/addresses",
    "address": "**/api/addresses/*",
}

EMPTY = {
    "orders": load_data("account/orders.json#empty"),
    "wishlist": load_data("account/wishlist.json#empty"),
    "addresses": load_data("account/addresses.json#empty"),
}


def mock_account_data(k, profile=None, orders=None, wishlist=None, addresses=None):
    """Mock 4 API mà trang hồ sơ gọi (profile, orders, wishlist, addresses).
    Không truyền profile -> dùng dữ liệu thật của tài khoản test; các API còn lại mặc định rỗng."""
    if profile:
        k.common.mock_get(API["profile"], profile)
    k.common.mock_get(API["orders"], orders if orders is not None else EMPTY["orders"])
    k.common.mock_get(API["wishlist"], wishlist if wishlist is not None else EMPTY["wishlist"])
    k.common.mock_get(API["addresses"], addresses if addresses is not None else EMPTY["addresses"])
