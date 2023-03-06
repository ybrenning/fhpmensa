#!/usr/bin/env python3

"""Basic script to fetch today's menu from the FHP homepage
and send a reformatted version of it to a group chat using the Telegram API.
"""

__author__ = "Yannick Brenning"

import os
import traceback
from datetime import datetime

import bs4
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

API_URL = "https://api.telegram.org/bot"
MENU_URL = "https://www.mensaplan.de/potsdam/mensa-kiepenheuerallee/index.html"

days = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
}

emojis = ["😷", "🤢", "💩", "🤮", "☣️"]


def get_offer_type(offer_num: int) -> str:
    """Get the string corresponding to an offer number

    Args:
        offer_num (int): current offer index

    Returns:
        str: display title for offer
    """
    if offer_num == 5:
        return f"\n{emojis[offer_num-1]} *Tagesangebot* {emojis[offer_num-1]}\n"
    else:
        return f"\n{emojis[offer_num-1]} *Angebot {offer_num}* {emojis[offer_num-1]}\n"


def get_offer_details(content: bs4.element.Tag) -> str:
    """Get the offer details from an offer category

    Args:
        content (bs4.element.Tag): HTML content of offers

    Returns:
        str: names and prices of offers
    """
    descriptions = content.find_all(class_="description")
    prices = content.find_all(class_="price")

    if not descriptions and not prices:
        return "Nicht verfügbar\n"

    detail_text = ""
    for detail in zip(descriptions, prices):
        description, price = detail
        detail_text += description.text.replace("-", "\-") + "\n" + price.text + "\n"

    return detail_text


def scrape_webpage(url: str) -> bs4.element.ResultSet:
    """Get table content of the menu webpage

    Args:
        url (str): URL of the page

    Raises:
        AttributeError: if any element is missing

    Returns:
        bs4.element.ResultSet: HTML rows of menu table
    """
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, features="html.parser")

    table = soup.find("table")
    if not table:
        raise AttributeError("Menu table not found")

    table_body = table.find("tbody")
    if not table_body:
        raise AttributeError("Table body of menu not found")

    table_rows = table_body.find_all("tr")  # type: ignore
    if not table_rows:
        raise AttributeError("Table rows of menu not found")

    return table_rows


def get_todays_menu_body(day: int) -> str:
    """Get the content of today's menu

    Args:
        day (int): given day from 0-6

    Returns:
        str: formatted menu body
    """
    table_rows = scrape_webpage(MENU_URL)

    menu, i = "", 1
    for tr in table_rows:
        cols = tr.find_all("td")

        if not cols:
            menu += get_offer_type(i)
            i += 1
        else:
            menu += get_offer_details(cols[day])

    return menu


def get_todays_menu(day: int) -> str | None:
    """Fetches menu of the current weekday

    Args:
        day (int): day of week from 0-6

    Returns:
        str | None: today's menu if weekday, None otherwise
    """
    if day > 4:
        return None

    try:
        menu = f"📆*Mensaplan für {days[day]}*📆\n" + get_todays_menu_body(day)
        return menu
    except Exception:
        traceback.print_exc()
        return None


def send_menu() -> None:
    """Makes the call to the Telegram API to send a menu message

    Raises:
        KeyError: if the bot API token and chat ID are not configured
        HTTPError: if the call makes a bad request
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
    else:
        print("No menu for today")


def main() -> None:
    send_menu()


if __name__ == "__main__":
    main()
