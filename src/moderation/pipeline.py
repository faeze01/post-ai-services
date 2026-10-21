from moderation.link_check import check_links
from moderation.phone_check import report_phone


def check_post(text: str) -> dict:
    phone = report_phone(text)
    if phone["found"] and phone["strength"] == "strong":
        return {"status": "block", "reason": "phone"}
    if check_links(text) == "block":
        return {"status": "block", "reason": "link"}
    if phone["found"] and phone["strength"] == "weak":
        return {"status": "suspicious", "reason": "phone"}
    return {"status": "ok", "reason": ""}
