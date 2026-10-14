"""تشخیص ساختار شمارهٔ تلفن ایران. فعال بودن شماره را بررسی نمی‌کند.

report_phone یکی از این دو را برمی‌گرداند:
{"found": False}
{"found": True, "kind": "mobile" یا "landline", "strength": "strong" یا "weak"}

strong یعنی شروع با 0 یا +98 یا 0098. weak یعنی موبایل ده‌رقمی بدون پیش‌شماره،
یا هر عدد ۱۲ رقمی که با 98 شروع شود. check_phone فقط found را برمی‌گرداند.
اگر هر دو گذر چیزی پیدا کنند، strong بر weak مقدم است.

پوشش داده نمی‌شود: رقم چسبیده بدون فاصله («صفرنهیک»)، نیم‌فاصله داخل کلمه،
ثابت بدون صفر، و پیش‌شمارهٔ موبایل خارج از فهرست مانند 094.
«ه» و حروف مشابه فقط وقتی کنار رقم باشند رقم می‌شوند.
"""
import re
import unicodedata

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
LETTERS = str.maketrans("يك", "یک")
INVISIBLES = re.compile(
    r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff\u00ad\u061c\ufe0f\u20e3\u064b-\u0652]"
)
_WORD_PUNCT = ".,،؛:!؟?()[]«»\"'"

NUMBERS = {
    "صفر": 0, "زیرو": 0, "سیفر": 0, "zero": 0,
    "یک": 1, "یه": 1, "وان": 1, "one": 1,
    "دو": 2, "two": 2,
    "سه": 3, "تری": 3, "three": 3,
    "چهار": 4, "چار": 4, "فور": 4, "four": 4,
    "پنج": 5, "فایو": 5, "five": 5,
    "شش": 6, "شیش": 6, "سیکس": 6, "six": 6,
    "هفت": 7, "سون": 7, "seven": 7,
    "هشت": 8, "ایت": 8, "eight": 8,
    "نه": 9, "نُه": 9, "ناین": 9, "nine": 9,
    "ده": 10, "یازده": 11, "دوازده": 12, "سیزده": 13, "چهارده": 14,
    "پانزده": 15, "شانزده": 16, "هفده": 17, "هجده": 18, "نوزده": 19,
    "بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50,
    "شصت": 60, "هفتاد": 70, "هشتاد": 80, "نود": 90,
    "صد": 100, "یکصد": 100, "دویست": 200, "سیصد": 300, "چهارصد": 400,
    "پانصد": 500, "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900,
}

LOOKALIKE = {"o": "0", "ه": "0", "l": "1", "i": "1", "|": "1", "s": "5", "b": "6", "g": "9"}

# strong: 0 یا +98 یا 0098. weak: 98 بدون + و 00.
_STRONG = r"(?:\+98|0098|0)"
MOBILE = re.compile(rf"(?<![\d_]){_STRONG}9\d{{9}}(?![\d_])")
MOBILE_NSN = re.compile(r"(?<![\d_])9(?:0[1-5]|1\d|2[0-2]|3\d|9\d)\d{7}(?![\d_])")
LANDLINE = re.compile(rf"(?<![\d_]){_STRONG}[1-8]\d{{9}}(?![\d_])")
WEAK_98 = re.compile(r"(?<![\d_])98\d{10}(?![\d_])")


def base_normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = INVISIBLES.sub("", text)
    text = text.replace("ـ", "")
    text = text.translate(DIGITS).translate(LETTERS)
    return text.lower()


def words_to_digits(text: str) -> str:
    tokens = re.split(r"(\s+)", text)
    out = []
    prev_number = False
    i = 0
    while i < len(tokens):
        word = tokens[i]
        key = word.strip(_WORD_PUNCT)
        if key not in NUMBERS:
            out.append(word)
            if word.strip():
                prev_number = False
            i += 1
            continue
        value = last = NUMBERS[key]
        i += 1
        while i + 3 < len(tokens) and tokens[i + 1].strip(_WORD_PUNCT) == "و":
            limit = 100 if last >= 100 else 10 if last >= 20 else 0
            nxt = NUMBERS.get(tokens[i + 3].strip(_WORD_PUNCT), 0)
            if not 0 < nxt < limit:
                break
            value += nxt
            last = nxt
            i += 4
        if prev_number and not out[-1].strip():
            out.pop()
        out.append(str(value))
        prev_number = True
    return "".join(out)


def lookalike_to_digits(text: str) -> str:
    chars = list(text)
    n = len(chars)
    for i, ch in enumerate(chars):
        if ch in LOOKALIKE:
            left = chars[i - 1].isdigit() if i > 0 else False
            right = chars[i + 1].isdigit() if i < n - 1 else False
            if left or right:
                chars[i] = LOOKALIKE[ch]
    return "".join(chars)


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
    kind, strength = phone_kind(base_normalize(text))
    normalized = remove_separators(lookalike_to_digits(words_to_digits(base_normalize(text))))
    kind2, strength2 = phone_kind(normalized)
    if strength2 == "strong" or strength is None:
        kind, strength = kind2, strength2
    if kind is None:
        return {"found": False}
    return {"found": True, "kind": kind, "strength": strength}


def check_phone(text: str) -> bool:
    return report_phone(text)["found"]
