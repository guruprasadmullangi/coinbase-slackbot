import os
import logging
import json
import cbpro
from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from timerthread import RepeatedTimer

dotenv_path = join(dirname(__file__), './.env')
load_dotenv(dotenv_path)

logging.basicConfig(level=logging.DEBUG)

INTERVAL=60
pd = os.environ.get('pd')
pd_list = json.loads(pd)

COINBASE_API_KEY = os.environ.get('COINBASE_API_KEY')
COINBASE_API_PASSPHARSE = os.environ.get('COINBASE_API_PASSPHARSE')
COINBASE_API_SECRET = os.environ.get('COINBASE_API_SECRET')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)
auth_client = cbpro.AuthenticatedClient(COINBASE_API_KEY, COINBASE_API_SECRET, COINBASE_API_PASSPHARSE, api_url="https://api.pro.coinbase.com")
public_client = cbpro.PublicClient()

def porl():
    msg = '```'
    accounts = auth_client.get_accounts()
    for account in accounts:
        if float(account['balance']) > 0.0000000000000000:
            currency = account['currency']
            available = account['available']
            total_deposit = float(pd_list[currency]) #add total deposits for this currency by calling coinbase api
            ticker_price = public_client.get_product_ticker(product_id=currency+'-USD')
            current_total = float(available) * float(ticker_price['price'])
            if current_total < total_deposit:
                loss = float(total_deposit) - float(current_total)
                loss_percent = (loss / total_deposit) * 100
                if loss_percent > 10:
                    msg = msg + f"Your {currency} holding is in loss by {loss_percent}%\n"
    msg = msg + '```'
    client.chat_postMessage(channel='U02AGCSP1L3', text=msg)


@app.command('/help')
def help(ack, command):
    ack(f"Hello <@{command['user_id']}>")

@app.command('/accounts')
def help(ack, command):
    accounts = auth_client.get_accounts()
    msg = "{:<15} {:<27} {:<27} {:<27}\n\n```".format('`Currency`', '`Available`', '`Ticker Price`', '`Current Value`')
    for account in accounts:
        if float(account['available']) > 0.0000000000000000:
            currency = account['currency']
            available = account['available']
            ticker_price = public_client.get_product_ticker(product_id=currency+'-USD')
            msg = msg + "{:<10} {:<20} {:<20} {:<20}\n".format(currency, available, ticker_price['price'], float(available) * float(ticker_price['price']))

    msg = msg + '```'
    ack(f"*Your accounts:*\n\n{msg}")

@app.command('/porl')
def help(ack, command):
    accounts = auth_client.get_accounts()
    msg = "{:<15} {:<15}\n\n```".format('`Currency`', '`Profit/Loss`')
    for account in accounts:
        if float(account['balance']) > 0.0000000000000000:
            currency = account['currency']
            available = account['available']
            total_deposit = float(pd_list[currency]) #add total deposits for this currency by calling coinbase api
            ticker_price = public_client.get_product_ticker(product_id=currency+'-USD')
            current_total = float(available) * float(ticker_price['price'])
            porl = current_total - total_deposit
            msg = msg + "{:<10} {:<10}".format(currency, porl) + '\n'
    
    msg = msg + '```'
    ack(f"*Profits and losses:*\n\n{msg}")
          

if __name__ == '__main__':
    rt = RepeatedTimer(INTERVAL, porl)
    try:
        SocketModeHandler(app, SLACK_APP_TOKEN).start()
    finally:
        rt.stop()