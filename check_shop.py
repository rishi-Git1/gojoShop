import logging
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from twilio.rest import Client

SHOP_URL = "https://fortnite-api.com/v2/shop/br"
DEFAULT_SEARCH_TERMS = ["gojo satoru", "gojo"]


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("gojo-shop-checker")


def _normalize(value: str) -> str:
    return value.strip().lower()


def fetch_shop() -> dict:
    response = requests.get(SHOP_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("status") == 200:
        raise RuntimeError(f"Unexpected API response status: {data.get('status')}")
    return data


def _entry_text(entry: dict) -> str:
    fields = []

    display = entry.get("displayName")
    if display:
        fields.append(display)

    for item in entry.get("items", []):
        if item.get("name"):
            fields.append(item["name"])

        for style in item.get("styles", []):
            if style.get("name"):
                fields.append(style["name"])

    return " | ".join(fields).lower()


def find_matching_entries(shop_data: dict, search_terms: list[str]) -> list[dict]:
    normalized_terms = [_normalize(term) for term in search_terms if term and term.strip()]
    if not normalized_terms:
        normalized_terms = DEFAULT_SEARCH_TERMS

    matches = []
    for entry in shop_data.get("data", {}).get("entries", []):
        haystack = _entry_text(entry)
        if any(term in haystack for term in normalized_terms):
            matches.append(entry)

    return matches


def send_sms(message: str) -> None:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_FROM_PHONE")
    to_phone = os.getenv("TARGET_PHONE")

    missing = [
        key
        for key, value in {
            "TWILIO_ACCOUNT_SID": account_sid,
            "TWILIO_AUTH_TOKEN": auth_token,
            "TWILIO_FROM_PHONE": from_phone,
            "TARGET_PHONE": to_phone,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    client = Client(account_sid, auth_token)
    result = client.messages.create(body=message, from_=from_phone, to=to_phone)
    logger.info("SMS sent to target number with SID %s", result.sid)


def build_message(matches: list[dict], shop_data: dict) -> str:
    date_str = shop_data.get("data", {}).get("date")
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(timezone.utc)
            shop_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            shop_date = date_str
    else:
        shop_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        f"Fortnite shop check for {shop_date}: Gojo Satoru is in the shop!",
        "Matching entries:",
    ]
    for entry in matches[:5]:
        title = entry.get("displayName") or "Unnamed entry"
        final_price = entry.get("finalPrice")
        if final_price:
            lines.append(f"- {title} ({final_price} V-Bucks)")
        else:
            lines.append(f"- {title}")

    lines.append("Open Fortnite to buy before the daily reset.")
    return "\n".join(lines)


def main() -> None:
    load_dotenv()

    terms_env = os.getenv("SEARCH_TERMS", "")
    search_terms = [term.strip() for term in terms_env.split(",") if term.strip()] or DEFAULT_SEARCH_TERMS

    logger.info("Fetching Fortnite shop data...")
    shop_data = fetch_shop()
    matches = find_matching_entries(shop_data, search_terms)

    logger.info("Found %s matching entries for terms: %s", len(matches), ", ".join(search_terms))
    if not matches:
        logger.info("No Gojo entries found today; no SMS sent.")
        return

    message = build_message(matches, shop_data)
    send_sms(message)


if __name__ == "__main__":
    main()
