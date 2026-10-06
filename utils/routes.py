# Đường dẫn các trang của app (tương đối với BASE_URL).
from urllib.parse import quote

ROUTES = {
    "home": "/",
    "men": "/nam",
    "women": "/nu",
    "kids": "/tre-em",
    "sale": "/giam-gia",
    "blog": "/blog",
    "about": "/about",
    "shipping": "/shipping",
    "returns": "/returns",
    "privacy": "/privacy",
    "login": "/login",
    "checkout": "/checkout",
    "orderSuccess": "/order-success",
    "profile": "/profile",
    "orders": "/orders",
    "favorites": "/favorites",
    "addresses": "/addresses",
    "adminLogin": "/admin/login",
    "adminDashboard": "/admin",
}


def search_route(query):
    # Giống encodeURIComponent của JS.
    return "/search?q=" + quote(query, safe="!~*'()")


def product_route(slug):
    return f"/product/{slug}"
