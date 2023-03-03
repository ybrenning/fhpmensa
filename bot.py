#!/usr/bin/env python3

"""Basic script to fetch today's menu from the FHP homepage
and send a reformatted version of it to a group chat using the Telegram API.
"""

__author__ = "Yannick Brenning"

import os
import traceback
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
    """Fetches menu of the current weekday

    Args:
        day (int): day of week from 0-6

    Raises:
        AttributeError: if the page does not contain the menu table

    Returns:
        str | None: today's menu if weekday, None otherwise
    """
    if day > 4:
        return None

    menu = f"📆*Menu for {days[day]}*📆\n"

    try:
        r = requests.get(MENU_URL)
        soup = BeautifulSoup(r.text, features="html.parser")

        table = soup.find("table")

        if not table:
            raise AttributeError("Menu table not found")

        table_body = table.find("tbody")

        if not table_body:
            raise AttributeError("Table body of menu not found")

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
                        cols[day].find(class_="description").text.replace("-", "\-")
                        + "\n"
                    )
                else:
                    menu += "Not Available\n"
                if cols[day].find(class_="price"):
                    menu += cols[day].find(class_="price").text + "\n"
    except Exception:
        traceback.print_exc()
        menu = None

    return menu


def send_menu() -> None:
    """Makes the call to the Telegram API to send a menu message

    Raises:
        KeyError: if the bot API token and chat ID are not configured
    """
    if not BOT_TOKEN or not CHAT_ID:
        raise KeyError("Missing environment variable configuration")

    menu = get_todays_menu(day=datetime.now().weekday())

    if menu:
        try:
            response = requests.get(
                f"{API_URL}{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={menu}&parse_mode=MarkdownV2"
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            traceback.print_exc()


def main() -> None:
    send_menu()


if __name__ == "__main__":
    main()
