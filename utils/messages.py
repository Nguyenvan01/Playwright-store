# Các chuỗi hiển thị trên UI / API. Đổi text ở app thì chỉ cần sửa tại đây.
MSG = {
    "login": {
        "requiredIdentifier": "Vui lòng nhập email hoặc số điện thoại",
        "invalidIdentifier": "Email hoặc số điện thoại không hợp lệ",
        "requiredPassword": "Vui lòng nhập mật khẩu",
        "shortPassword": "Mật khẩu phải có ít nhất 6 ký tự",
        "wrongCredentials": "Email hoặc mật khẩu không đúng",
    },
    "register": {
        "requiredName": "Vui lòng nhập họ và tên",
        "requiredPhone": "Vui lòng nhập số điện thoại",
        "passwordMismatch": "Mật khẩu xác nhận không khớp",
        "emailTaken": "Email đã được sử dụng",
    },
    "product": {
        "selectSize": "Vui lòng chọn kích cỡ",
        "notFound": "Không tìm thấy sản phẩm.",
    },
    "cart": {"empty": "Giỏ hàng trống"},
    "checkout": {
        "missingInfo": "Vui lòng điền đầy đủ thông tin bắt buộc.",
        "success": "Đặt hàng thành công",
        "pendingPayment": "Đang chờ thanh toán",
    },
    "search": {"noResult": "Không tìm thấy sản phẩm nào"},
}


def added_to_cart(name):
    return f'Đã thêm "{name}" vào giỏ hàng'
