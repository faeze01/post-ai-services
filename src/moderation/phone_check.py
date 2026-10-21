"""تشخیص ساختار شمارهٔ تلفن ایران. فعال بودن شماره را بررسی نمی‌کند.

report_phone یکی از این دو را برمی‌گرداند:
{"found": False}
{"found": True, "kind": "mobile" یا "landline", "strength": "strong" یا "weak"}

strong یعنی شروع با 0 یا +98 یا 0098. weak یعنی موبایل ده‌رقمی بدون پیش‌شماره،
یا هر عدد ۱۲ رقمی که با 98 شروع شود. check_phone فقط found را برمی‌گرداند.
اگر هر دو گذر چیزی پیدا کنند، strong بر weak مقدم است.

عدد حروفی و رقم‌های شبیه حرف بررسی نمی‌شوند.
پوشش داده نمی‌شود: رقم چسبیده بدون فاصله، ثابت بدون صفر،
و پیش‌شمارهٔ موبایل خارج از فهرست مانند 094.
"""
import re
import unicodedata

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
INVISIBLES = re.compile(
    r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff\u00ad\u061c\ufe0f\u20e3\u064b-\u0652]"
)

# strong: 0 یا +98 یا 0098. weak: 98 بدون + و 00.
_STRONG = r"(?:\+98|0098|0)"
MOBILE = re.compile(rf"(?<!\d){_STRONG}9\d{{9}}(?!\d)")
MOBILE_NSN = re.compile(r"(?<!\d)9(?:0[1-5]|1\d|2[0-2]|3\d|9\d)\d{7}(?!\d)")
LANDLINE = re.compile(rf"(?<!\d){_STRONG}[1-8]\d{{9}}(?!\d)")
WEAK_98 = re.compile(r"(?<!\d)98\d{10}(?!\d)")


def base_normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = INVISIBLES.sub("", text)
    text = text.replace("ـ", "")
    text = text.translate(DIGITS)
    return text.lower()


def remove_separators(text: str) -> str:
    return re.sub(r"(?<=\d)[\s\-_.()/\\–—،؛]+(?=\d)", "", text)


def phone_kind(text: str):
    if MOBILE.search(text):
        return ("mobile", "strong")
    if LANDLINE.search(text):
        return ("landline", "strong")
    if MOBILE_NSN.search(text):
        return ("mobile", "weak")
    bare = WEAK_98.search(text)
    if bare:
        kind = "mobile" if bare.group()[2] == "9" else "landline"
        return (kind, "weak")
    return (None, None)


def report_phone(text: str) -> dict:
    normalized = base_normalize(text)
    kind, strength = phone_kind(normalized)
    kind2, strength2 = phone_kind(remove_separators(normalized))
    if strength2 == "strong" or strength is None:
        kind, strength = kind2, strength2
    if kind is None:
        return {"found": False}
    return {"found": True, "kind": kind, "strength": strength}


def check_phone(text: str) -> bool:
    return report_phone(text)["found"]
