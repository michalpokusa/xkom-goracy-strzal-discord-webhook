from datetime import datetime, timedelta, timezone

import requests
import os
import json

TIMEZONE_OFFSET_HOURS = os.environ.get("TIMEZONE_OFFSET_HOURS", None)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", None)

DISCORD_MESSAGE_ID = os.environ.get("DISCORD_MESSAGE_ID", None)

try:
    assert TIMEZONE_OFFSET_HOURS is not None
    assert TIMEZONE_OFFSET_HOURS.isdigit()
    assert DISCORD_WEBHOOK_URL is not None
except AssertionError:
    print("Error: Please make sure the following environment variables are set to correct values:")
    print("- TIMEZONE_OFFSET_HOURS")
    print("- DISCORD_WEBHOOK_URL")
    exit()


HOT_SHOT_URL = "https://www.x-kom.pl/goracy_strzal"

NOW = datetime.now(tz=timezone(offset=timedelta(hours=int(TIMEZONE_OFFSET_HOURS))))


if 10 < NOW.hour < 22:
    HOT_SHOT_END_TIME = NOW.replace(hour=22, minute=0, second=0, microsecond=0)
else:
    HOT_SHOT_END_TIME = NOW.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)


xkomAPIResponse = requests.get(
    url="https://mobileapi.x-kom.pl/api/v1/xkom/hotShots/current?onlyHeader=true&commentAmount=15",
    headers={
        "accept": "application/json, text/plain, */*",
        "origin": 'https://www.x-kom.pl',
        "pragma": 'no-cache',
        "referer": 'https://www.x-kom.pl/',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "x-api-key": "jfsTOgOL23CN2G8Y",
    }
)

xkomAPIResponseJson = xkomAPIResponse.json()

if xkomAPIResponseJson.get('SaleCount', None) == xkomAPIResponseJson.get('PromotionTotalCount', None):
    footerMessage = "Niestety ta oferta się skończyła, następna będzie dostępna:"
else:
    footerMessage = "Śpiesz się, oferta konczy się:"

payload = {
    "content": None,
    "embeds": [
        {
            "title": "Gorący Strzał",
            "description": xkomAPIResponseJson.get('PromotionName','?'),
            "url": "https://www.x-kom.pl/goracy_strzal",
            "color": 16777214,
            "author": {
                "name": f"Stan na {NOW.strftime('%H:%M')}",
            },
            "fields": [
                {
                    "name": "Cena",
                    "value": f"~~{xkomAPIResponseJson.get('OldPrice','?')}~~ {xkomAPIResponseJson.get('Price','?')}",
                    "inline": True
                },
                {
                    "name": "Sprzedano",
                    "value": f"{xkomAPIResponseJson.get('SaleCount','?')}/{xkomAPIResponseJson.get('PromotionTotalCount','?')}",
                    "inline": True
                }
            ],
            "image": {
                "url": xkomAPIResponseJson.get('PromotionPhoto', {}).get('Url','?')
            },
            "footer": {
                "text": footerMessage
            },
            "timestamp": HOT_SHOT_END_TIME.isoformat(),
        }
    ],
    "username": "x-kom.pl",
    "avatar_url": "https://scontent-waw1-1.xx.fbcdn.net/v/t1.6435-1/46089032_2200961156620801_7958246521684623360_n.png?stp=dst-png_p148x148&_nc_cat=1&ccb=1-5&_nc_sid=1eb0c7&_nc_ohc=KCbbYogWuTwAX-e0W9g&_nc_ht=scontent-waw1-1.xx&oh=00_AT-kmylBL3HlAqASBxsNG2aH19bi2Yv1fiA-f_axyK2etg&oe=627B8C25",
    "attachments": []
}

if DISCORD_MESSAGE_ID:
    discordWebhookResponse = requests.patch(
        url=f"{DISCORD_WEBHOOK_URL}/messages/{DISCORD_MESSAGE_ID}",
        json = payload
    )

else:
    discordWebhookResponse = requests.post(
        url=f"{DISCORD_WEBHOOK_URL}?wait=true",
        json = payload
    )

print(json.dumps(discordWebhookResponse.json(), indent=4))
