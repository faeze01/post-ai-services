import pytest

from moderation.phone_check import LANDLINE, MOBILE, MOBILE_NSN, check_phone, report_phone


@pytest.mark.parametrize("text", [
    "شماره من ۰۹۱۲۳۴۵۶۷۸۹",
    "0912 - 345 6789",
    "0912.345.6789",
    "+989123456789",
    "00989123456789",
    "0912\u200b3456789",
])
def test_block(text):
    assert check_phone(text) is True


@pytest.mark.parametrize("text", [
    "کد پیگیری 1234567",
    "کارت 6037991234567890",
    "تماس 123456",
    "واتساپ 12-34-56",
])
def test_not_a_phone(text):
    assert check_phone(text) is False


@pytest.mark.parametrize("text", [
    "سال ۱۴۰۳ قیمت ۱۲۳۴۵ تومان",
    "من سیصد و پنجاه کتاب خواندم",
    "نهصد و سیزده نفر شرکت کردند",
    "۱۲ فروردین ۱۴۰۳ ساعت ۹",
    "امروز هوا خوب بود و با دوستانم به پارک رفتیم. بعد از ظهر چای نوشیدیم و درباره‌ی کتاب‌ها حرف زدیم.",
    "سفارش شماره 12 تحویل شد",
    "صفر نهصد و سیزده سیصد و چهل و پنج شصت و هفت هشتاد و نه",
    "صفر نه یک سه سه چهار پنج شش هفت هشت نه",
    "صفر نه \u064a\u0643 سه سه چهار پنج شش هفت هشت نه",
    "تو را دیدم ساعت ۹",
])
def test_ok(text):
    assert check_phone(text) is False


@pytest.mark.parametrize("text,label,reason", [
    ("شماره من ۰۹۱۲۳۴۵۶۷۸۹", "block", "iran_mobile"),
    ("0912 - 345 6789", "block", "manipulated_mobile"),
    ("کد پیگیری 1234567", "ok", None),
    ("نهصد و سیزده نفر شرکت کردند", "ok", None),
])
def test_report(text, label, reason):
    assert report_phone(text)["found"] is (label == "block")
    assert check_phone(text) is (label == "block")


@pytest.mark.parametrize("text,label,reason", [
    ("09123456789", "block", "iran_mobile"),
    ("شماره من ۰۹۱۲۳۴۵۶۷۸۹", "block", "iran_mobile"),
    ("٠٩١٢٣٤٥٦٧٨٩", "block", "iran_mobile"),
    ("+989123456789", "block", "iran_mobile"),
    ("00989123456789", "block", "iran_mobile"),
    ("02188776655", "block", "iran_landline"),
    ("۰۲۱۸۸۷۷۶۶۵۵", "block", "iran_landline"),
    ("٠٢١٨٨٧٧٦٦٥٥", "block", "iran_landline"),
    ("+982188776655", "block", "iran_landline"),
    ("00982188776655", "block", "iran_landline"),
    ("+98 21 8877 6655", "block", "manipulated_landline"),
    ("0098 912 345 6789", "block", "manipulated_mobile"),
    ("0912 - 345 6789", "block", "manipulated_mobile"),
    ("0912.345.6789", "block", "manipulated_mobile"),
    ("(0912) 345-6789", "block", "manipulated_mobile"),
    ("021 8877 6655", "block", "manipulated_landline"),
    ("(021) 8877-6655", "block", "manipulated_landline"),
    ("021.8877.6655", "block", "manipulated_landline"),
    ("۰۲۱ ۸۸۷۷ ۶۶۵۵", "block", "manipulated_landline"),
    ("٠٢١.٨٨٧٧.٦٦٥٥", "block", "manipulated_landline"),
    ("۰۹۱۲-۳۴۵-۶۷۸۹", "block", "manipulated_mobile"),
    ("٠٩١٢ ٣٤٥ ٦٧٨٩", "block", "manipulated_mobile"),
    ("صفر نه یک دو سه چهار پنج شش هفت هشت نه", "ok", None),
    ("zero nine one two three four five six seven eight nine", "ok", None),
    ("o9123456789", "block", "iran_mobile"),
    ("صفر نه یک دو - سه چهار پنج شش هفت هشت نه", "ok", None),
    ("تماس 123456", "ok", None),
    ("واتساپ 12-34-56", "ok", None),
    ("کد پیگیری 1234567", "ok", None),
    ("کارت 6037991234567890", "ok", None),
    ("سفارش 1234567890123", "ok", None),
    ("1a2b3c4d5e6f7", "ok", None),
    ("123456abcd7", "ok", None),
    ("12309123456789", "ok", None),
    ("09123456789123", "ok", None),
    ("09123456789 123", "block", "iran_mobile"),
    ("12 309 123 456 789", "ok", None),
    ("09123-456789-99", "ok", None),
    ("9123456789", "block", "iran_mobile"),
    ("912 345 6789", "block", "manipulated_mobile"),
    ("9501234567", "ok", None),
    ("سال ۱۴۰۳ قیمت ۱۲۳۴۵ تومان", "ok", None),
    ("۱۲ فروردین ۱۴۰۳ ساعت ۹", "ok", None),
    ("نهصد و سیزده نفر شرکت کردند", "ok", None),
    ("بیست و سه نفر آمدند", "ok", None),
    ("سفارش شماره 12 تحویل شد", "ok", None),
    ("تو را دیدم ساعت ۹", "ok", None),
    ("hotel room 123456", "ok", None),
    ("امروز هوا خوب بود و با دوستانم به پارک رفتیم.", "ok", None),
    ("", "ok", None),
    ("   ", "ok", None),
])
def test_phone_cases(text, label, reason):
    assert report_phone(text)["found"] is (label == "block")
    assert check_phone(text) is (label == "block")


def test_phone_patterns_match_whole_number():
    assert MOBILE.fullmatch("09123456789")
    assert MOBILE.fullmatch("+989123456789")
    assert MOBILE.fullmatch("00989123456789")
    assert LANDLINE.fullmatch("02188776655")
    assert LANDLINE.fullmatch("+982188776655")
    assert MOBILE.search("091234567891") is None
    assert LANDLINE.search("021887766551") is None
    assert MOBILE.search("9123456789") is None
    assert MOBILE_NSN.fullmatch("9123456789")
    assert MOBILE_NSN.search("9501234567") is None
    assert LANDLINE.search("09123456789") is None


@pytest.mark.parametrize("text,label,reason", [
    ("واتس\u200cاپ 123456", "ok", None),
    ("پی\u200cوی 123456", "ok", None),
    ("t.me/name 123456", "ok", None),
    ("wa.me/123456", "ok", None),
    ("best.me room 123456", "ok", None),
    ("0912،345،6789", "block", "manipulated_mobile"),
    ("صفر، نه، یک، دو، سه، چهار، پنج، شش، هفت، هشت، نه", "ok", None),
    ("zero, nine, one, two, three, four, five, six, seven, eight, nine", "ok", None),
    ("صفر نهصد و سیزده، سیصد و چهل و پنج، شصت و هفت، هشتاد و نه", "ok", None),
    ("بیست و سه، نفر آمدند", "ok", None),
    ("صد و بیست و سه.", "ok", None),
])
def test_punctuation_words_and_contact_links(text, label, reason):
    assert report_phone(text)["found"] is (label == "block")
    assert check_phone(text) is (label == "block")
