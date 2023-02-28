import logging
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

API_URL = "https://api.telegram.org/bot"
MENU_URL = "https://www.mensaplan.de/potsdam/mensa-kiepenheuerallee/index.html"

days = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
}

emojis = ["😷", "🤢", "💩", "🤮", "☣️"]


def get_todays_menu(day: int) -> str | None:
    if day > 4:
        return None

    menu = f"📆*Menu for {days[day]}*📆\n"

    r = requests.get(MENU_URL)
    soup = BeautifulSoup(r.text, features="html.parser")

    table = soup.find("table")

    assert table is not None
    table_body = table.find("tbody")

    table_rows = table_body.find_all("tr")  # type: ignore

    i = 1
    for tr in table_rows:
        cols = tr.find_all("td")

        if not cols:
            if i == 5:
                menu += f"\n{emojis[i-1]} *Tagesangebot* {emojis[i-1]}\n"
            else:
                menu += f"\n{emojis[i-1]} *Angebot {i}* {emojis[i-1]}\n"
                i += 1
        else:
            if cols[day].find(class_="description"):
                menu += (
                    cols[day].find(class_="description").text.replace("-", "\-") + "\n"
                )
            else:
                menu += "Nothing\n"
            if cols[day].find(class_="price"):
                menu += cols[day].find(class_="price").text + "\n"

    return menu


def main() -> None:
    assert BOT_TOKEN is not None

    menu = get_todays_menu(day=datetime.now().weekday())

    if menu:
        response = requests.get(
            f"{API_URL}{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={menu}&parse_mode=MarkdownV2"
        )
    else:
        response = "No request made"

    logging.debug(response)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
    main()
