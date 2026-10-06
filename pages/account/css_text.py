# Chuỗi an toàn cho selector / RegExp.
import re


def css_text(text):
    """Chuỗi an toàn để đặt trong selector CSS `:text-is("...")`."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def escape_regex(text):
    """Escape chuỗi để dùng trong RegExp."""
    return re.escape(text)
