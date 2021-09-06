import os
import logging
import cbpro
import re
import sys
import base64
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

dotenv_path = join(dirname(__file__), './.env')
load_dotenv(dotenv_path)

logging.basicConfig(level=logging.DEBUG)

COINBASE_API_KEY = os.environ.get('COINBASE_API_KEY')
COINBASE_API_PASSPHARSE = os.environ.get('COINBASE_API_PASSPHARSE')
COINBASE_API_SECRET = os.environ.get('COINBASE_API_SECRET')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')

app = App(token=SLACK_BOT_TOKEN)
auth_client = cbpro.AuthenticatedClient(COINBASE_API_KEY, COINBASE_API_SECRET, COINBASE_API_PASSPHARSE, api_url="https://api.pro.coinbase.com")

@app.command('/help')
def help(ack, command):
    ack(f"Hello <@{command['user_id']}>")

@app.command('/balance')
def help(ack, command, logger):
    logger.info(auth_client.get_accounts())
    ack(f"Hello <@{command['user_id']}>")

if __name__ == '__main__':
    SocketModeHandler(app, SLACK_APP_TOKEN).start()