# FHP Mensa Bot

[![Build](https://github.com/ybrenning/poopy/actions/workflows/python-app.yml/badge.svg)](https://github.com/ybrenning/poopy/actions/workflows/python-app.yml)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://pycqa.github.io/isort/"><img alt="isort" src="https://img.shields.io/badge/%20imports-isort-%231674b1"></a>

Telegram bot that gets today's menu and sends it via a Telegram channel.

[Link to the Telegram channel](https://t.me/fhp_mensa)

## Setup

### Dependencies

Create a virtual environment and install `requirements.txt`.

```bash
$ python -m venv venv
$ . venv/Scripts/activate.bat
(venv)
$ pip install -r requirements.txt
```

Set the corresponding environment variables to your `BOT_TOKEN` and `CHAT_ID`.

### Run

```bash
$ python bot.py
```
