"""گزارش لینک در متن. خودش بلاک نمی‌کند.

report_links یکی از این سه را برمی‌گرداند:
{"found": False}
{"found": True, "kind": "blocked", "strength": "strong", "hosts": [...]}
{"found": True, "kind": "unknown", "strength": "weak", "hosts": [...]}

فهرست‌ها از allowed_domains.txt و blocked_domains.txt و messenger_domains.txt
خوانده می‌شوند. مورد بدون نقطه با نام دامنهٔ ثبت‌شده برابر است.
مورد با نقطه با میزبان برابر است یا میزبان به نقطه و آن مورد ختم می‌شود.
"""
import html
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlparse

from tldextract import TLDExtract

STATICS = Path("common-statics")
_extract = TLDExtract(suffix_list_urls=(), cache_dir=None)  # فهرست داخلی کتابخانه، بدون شبکه

_TLDS = "com|net|org|ir|io|me|co|info|app|xyz|top|shop|site|online|click|link|biz|cc|tv|ly"
_LINKS = re.compile(
    rf"https?://[^\s<>\"']+|www\.[^\s<>\"']+"
    rf"|(?<![\w.-])(?:[a-z0-9-]+\.)+(?:{_TLDS})(?![\w-])(?:/[^\s<>\"']*)?",
    re.I,
)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I)
_INVISIBLES = re.compile("[\u00ad\u200b-\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff]")
_TRAIL = ".,)»«،؟؛!]}\"'"


def _load(name: str):
    lines = (STATICS / name).read_text(encoding="utf-8").splitlines()
    items = {l.strip().lower() for l in lines if l.strip() and not l.lstrip().startswith("#")}
    return {i for i in items if "." not in i}, {i for i in items if "." in i}


ALLOWED = _load("allowed_domains.txt")
BLOCKED = _load("blocked_domains.txt")
MESSENGER = _load("messenger_domains.txt")


def _match(host: str, name: str, lists) -> bool:
    labels, hosts = lists
    return name in labels or any(host == h or host.endswith("." + h) for h in hosts)


def normalize_for_links(text: str) -> str:
    out = unicodedata.normalize("NFKC", html.unescape(text))
    out = _INVISIBLES.sub("", out)
    for token in ("[.]", "(.)", "{.}"):
        out = out.replace(token, ".")
    return re.sub(r"hxxp(s?)://", r"http\1://", out, flags=re.I)


def report_links(text: str) -> dict:
    text = normalize_for_links(text)
    blocked, unknown = [], []

    for m in _EMAIL.finditer(text):
        blocked.append(m.group().split("@", 1)[1].lower())
    text = _EMAIL.sub(" ", text)  # تا دامنه‌ی ایمیل دوباره به‌عنوان لینک شمرده نشود

    for m in _LINKS.finditer(text):
        raw = unquote(m.group().rstrip(_TRAIL))
        if not raw.lower().startswith(("http://", "https://")):
            raw = "http://" + raw
        try:
            host = (urlparse(raw).hostname or "").lower()
        except ValueError:
            host = ""
        if not host:
            continue
        name = _extract(host).domain
        if _match(host, name, BLOCKED) or _match(host, name, MESSENGER):
            blocked.append(host)
        elif not _match(host, name, ALLOWED):
            unknown.append(host)

    if blocked:
        return {"found": True, "kind": "blocked", "strength": "strong",
                "hosts": list(dict.fromkeys(blocked))}
    if unknown:
        return {"found": True, "kind": "unknown", "strength": "weak",
                "hosts": list(dict.fromkeys(unknown))}
    return {"found": False}
