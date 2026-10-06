# FACTORY: sinh dữ liệu test ngẫu nhiên, không trùng giữa các lần chạy.
from utils.data_loader import uid


def build_customer(**overrides):
    id_ = uid()
    return {
        "name": f"E2E Tester {id_[-4:]}",
        "email": f"e2e.{id_}@example.com",
        "phone": f"09{id_[-8:]}",
        "password": "E2e@123456",
        **overrides,
    }


def build_shipping_info(**overrides):
    """city/district/ward là value của <option>, vd: 'hcm', 'quan-1', 'phuong-1'."""
    return {
        "firstName": "Nguyễn",
        "lastName": "Kiểm Thử",
        "phone": "0912345678",
        "city": "hcm",
        "district": "quan-1",
        "ward": "phuong-1",
        "address": "123 Lê Lợi",
        **overrides,
    }


def build_cart_item(**overrides):
    """Item đúng định dạng CartContext lưu trong localStorage `clothing_store_cart`."""
    product_id = overrides.get("product_id", 1)
    return {
        "id": f"{product_id}-M-default-{uid()}",
        "product_id": product_id,
        "variant_id": None,
        "name": "Áo thun E2E",
        "slug": "ao-thun-e2e",
        "price": 199000,
        "compare_price": None,
        "image": None,
        "quantity": 1,
        "size": "M",
        "color": None,
        **overrides,
    }
