import pytest

from moderation.link_check import check_links


@pytest.mark.parametrize("text", [
    "https://t.me/channel",
    "t.me/abc",
    "HTTPS://T.ME/ABC",
    "سایت ما www.shop-example.com",
    "ببینید example.ir/offer",
    "https://wikipedia.org.evil.com/x",
    "https://evilwikipedia.org",
    "https://wikipedia.org@evil.com",
    "bit.ly/abc",
    "example[.]com",
    "example(dot)com",
    "example دات com",
    "hxxp://evil.com",
    "t . me / abc",
    "t\u200c.me/abc",
    "ｅｘａｍｐｌｅ．ｃｏｍ",
    "https://evil.com%2Fx",
    "exa\u200bmple.com",
    "example&#46;com",
])
def test_block(text):
    assert check_links(text) == "block"


@pytest.mark.parametrize("text", [
    "https://fa.wikipedia.org/wiki/تهران",
    "منبع: https://en.wikipedia.org/wiki/Python.",
    "(https://fa.wikipedia.org/wiki/ایران)",
    "فایل main.py و node.js را باز کن",
    "امروز هوا خوب بود و با دوستانم به پارک رفتیم.",
    "تمام شد. سپس رفتم",
    "آپدات com",
    "تمام شد. me too",
])
def test_ok(text):
    assert check_links(text) == "ok"


@pytest.mark.parametrize("text, expected", [
    pytest.param("https://stackoverflow.com/q/1", "ok", id="allowed-stackoverflow"),
    pytest.param("https://meta.stackoverflow.com", "ok", id="allowed-subdomain-stackoverflow"),
    pytest.param("a.github.com", "ok", id="allowed-subdomain-github"),
    pytest.param("github.com.example.org", "block", id="deceptive-host-contains-github"),
    pytest.param("http://example.dev", "block", id="scheme-suffix-outside-old-list"),
    pytest.param("www.example.uk", "block", id="www-suffix-outside-old-list"),
    pytest.param("example.dev", "block", id="bare-dev"),
    pytest.param("example.uk", "block", id="bare-uk"),
    pytest.param("promo.store/off", "block", id="bare-store-with-path"),
    pytest.param("report.xyz", "block", id="bare-xyz-still-block"),
    pytest.param("hello.world", "ok", id="bare-world-still-ok"),
    pytest.param("example(.)com", "block", id="paren-dot"),
    pytest.param("example{.}com", "block", id="brace-dot"),
    pytest.param("example نقطه com", "block", id="word-noghte"),
    pytest.param("example dot com", "block", id="word-dot"),
    pytest.param("example DOT com", "block", id="word-dot-upper"),
    pytest.param("example(DOT)com", "block", id="paren-dot-word-upper"),
    pytest.param("hXXp://shop.store", "block", id="hxxp-mixed-case"),
    pytest.param("example。com", "block", id="ideographic-dot"),
    pytest.param("example·com", "block", id="middle-dot"),
    pytest.param("https://fa.wikipedia.org؟", "ok", id="allowed-trailing-persian-question"),
    pytest.param("https://fa.wikipedia.org؛", "ok", id="allowed-trailing-persian-semicolon"),
    pytest.param("https://github.com!", "ok", id="allowed-trailing-exclamation"),
    pytest.param("https://evil.com]", "block", id="trailing-bracket"),
    pytest.param("http://[", "block", id="invalid-ipv6-no-crash"),
    pytest.param("readme.md", "ok", id="filename-md"),
    pytest.param("style.css", "ok", id="filename-css"),
    pytest.param("گزارش.pdf", "ok", id="filename-pdf"),
    pytest.param("contact@example.com", "block", id="email-other-domain-current"),
    pytest.param("contact@github.com", "ok", id="email-allowed-domain-current"),
    pytest.param("example%252Ecom", "ok", id="percent-decoded-once"),
    pytest.param("", "ok", id="empty"),
    pytest.param("   ", "ok", id="blank"),
    pytest.param("سلام", "ok", id="plain-persian"),
    pytest.param("http://.", "block", id="dot-only-host"),
])
def test_cases(text, expected):
    assert check_links(text) == expected


def test_input_is_not_modified():
    text = "example[.]com"
    check_links(text)
    assert text == "example[.]com"
