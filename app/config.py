import sys
import os
import logging
from dotenv import find_dotenv, load_dotenv


def load_configurations(app):
    load_dotenv(find_dotenv())
    app.config["ACCESS_TOKEN"] = os.environ["ACCESS_TOKEN"]
    app.config["APP_ID"] = os.environ["APP_ID"]
    app.config["APP_SECRET"] = os.environ["APP_SECRET"]
    app.config["RECIPIENT_WAID"] = os.environ["RECIPIENT_WAID"]
    app.config["VERSION"] = os.environ["VERSION"]
    app.config["PHONE_NUMBER_ID"] = os.environ["PHONE_NUMBER_ID"]
    app.config["VERIFY_TOKEN"] = os.environ["VERIFY_TOKEN"]


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
