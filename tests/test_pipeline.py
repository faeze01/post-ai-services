from moderation.pipeline import check_post


def test_weak_without_link():
    assert check_post("کد پستی 9123456789") == {"status": "suspicious", "reason": "phone"}


def test_strong_and_bad_link():
    assert check_post("09123456789 https://t.me/x") == {"status": "block", "reason": "phone"}


def test_weak_and_bad_link():
    assert check_post("9123456789 https://t.me/x") == {"status": "block", "reason": "link"}


def test_clean():
    assert check_post("امروز هوا خوب بود و با دوستانم به پارک رفتیم.") == {"status": "ok", "reason": ""}
