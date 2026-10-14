import pytest

from moderation.phone_check import check_phone, report_phone

STRONG = [
    ("تماس: 09123456789", "mobile"),
    ("تماس: ۰۹۱۲۳۴۵۶۷۸۹", "mobile"),
    ("+98 912 345 6789", "mobile"),
    ("0912-345-6789", "mobile"),
    ("۰۹۱۲ ۳۴۵ ۶۷۸۹", "mobile"),
    ("٠٩١٢٣٤٥٦٧٨٩", "mobile"),
    ("0912\u200c345\u200c6789", "mobile"),
    ("09l2345678g", "mobile"),
    ("0 9 1 2 3 4 5 6 7 8 9", "mobile"),
    ("021-12345678", "landline"),
    ("تماس09123456789", "mobile"),
    ("صفر نه یک دو سه چهار پنج شش هفت هشت نه", "mobile"),
    ("صفر نه یک دو سیصد و چهل و پنج شصت و هفت هشتاد و نه", "mobile"),
    ("0️⃣9️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣", "mobile"),
    ("۰۹۱۲۱۲۳۴۵۶۷ - ۰۹۳۵۱۲۳۴۵۶۷", "mobile"),
    ("تلفن ۰۹۱۲۳۴۵۶۷۸۹ / ۰۲۱۱۲۳۴۵۶۷۸", "mobile"),
    ("تماس ۰۹۱۲۳۴۵۶۷۸۹ ۱۴۰۳", "mobile"),
]

WEAK = [
    ("9123456789", "mobile"),
    ("کد پستی مشهد 9177983412", "mobile"),
    ("کد ملی من 9123456789 است", "mobile"),
    ("قیمت 9.123.456.789 تومان", "mobile"),
    ("جدول: 9 123 456 789 ریال", "mobile"),
    ("98 12 3456 7890", "landline"),
]

NOT_FOUND = [
    "تاریخ 1403/09/12",
    "ساعت 09:30 و 12:45",
    "شماره کارت 6037991234567890",
    "0912345678",
    "در سال 1399 1400 1401 1402",
    "نه نه نه نه نه نه نه نه نه نه نه",
    "<img src='/uploads/photo_9123456789.jpg'>",
    "ISBN 978-964-12345-6-7",
    "یک دو سه چهار پنج شش هفت هشت نه ده",
]


@pytest.mark.parametrize("text,kind", STRONG)
def test_strong(text, kind):
    assert report_phone(text) == {"found": True, "kind": kind, "strength": "strong"}
    assert check_phone(text) is True


@pytest.mark.parametrize("text,kind", WEAK)
def test_weak(text, kind):
    assert report_phone(text) == {"found": True, "kind": kind, "strength": "weak"}
    assert check_phone(text) is True


@pytest.mark.parametrize("text", NOT_FOUND)
def test_not_found(text):
    assert report_phone(text) == {"found": False}
    assert check_phone(text) is False
