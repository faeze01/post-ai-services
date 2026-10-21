import pytest

from moderation import link_check
from moderation.link_check import report_links


@pytest.fixture(autouse=True)
def domain_lists(monkeypatch):
    monkeypatch.setattr(link_check, "ALLOWED", ({"github", "python", "virgool"}, set()))
    monkeypatch.setattr(link_check, "BLOCKED", ({"porn"}, {"pussy.org"}))
    monkeypatch.setattr(link_check, "MESSENGER", ({"telegram"}, {"t.me", "wa.me"}))


# (متن, found, kind, hosts) — hosts برابر None یعنی بررسی نمی‌شود.
CASES = [
    ("https://github.com/x", False, None, None),
    ("https://docs.github.com/x", False, None, None),
    ("https://github.evil.com", True, "unknown", ["github.evil.com"]),
    ("https://evil.com", True, "unknown", ["evil.com"]),
    ("https://google.com/search?q=spam", True, "unknown", None),
    ("t.me/abc", True, "blocked", ["t.me"]),
    ("https://telegram.org", True, "blocked", None),
    ("https://porn.com", True, "blocked", None),
    ("https://pornography-research.org", True, "unknown", None),
    ("https://pussy.org/x", True, "blocked", None),
    ("example[.]ir/pay", True, "unknown", ["example.ir"]),
    ("hxxp://evil.com", True, "unknown", None),
    ("EXAMPLE.IR", True, "unknown", ["example.ir"]),
    ("https://evil.com.", True, "unknown", ["evil.com"]),
    ("(evil.com)", True, "unknown", ["evil.com"]),
    ("contact: user@gmail.com", True, "blocked", ["gmail.com"]),
    ("https://evil.com و t.me/abc", True, "blocked", ["t.me"]),
    ("main.py", False, None, None),
    ("style.css", False, None, None),
    ("e.g. this", False, None, None),
    ("hello . me", False, None, None),
    ("نقطه ضعف", False, None, None),
    ("قیمت 1.5 میلیون", False, None, None),
    ("@evil_shop", False, None, None),
    ("", False, None, None),
    ('<a href="https://evil.com/x">خرید</a>', True, "unknown", ["evil.com"]),
    ("<p>سایت ما https://evil.com است</p>", True, "unknown", ["evil.com"]),
    ('<a href="mailto:ali@gmail.com">ایمیل</a>', True, "blocked", ["gmail.com"]),
    ('<img src="https://github.com/a.png">', False, None, None),
]


@pytest.mark.parametrize("text,found,kind,hosts", CASES)
def test_report_links(text, found, kind, hosts):
    result = report_links(text)
    if not found:
        assert result == {"found": False}
        return
    assert result["found"] is True
    assert result["kind"] == kind
    assert result["strength"] == ("strong" if kind == "blocked" else "weak")
    if hosts is not None:
        assert result["hosts"] == hosts
