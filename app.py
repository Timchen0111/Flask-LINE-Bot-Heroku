import os
from datetime import datetime

from flask import Flask, abort, request

import psycopg2
DATABASE_URL = 'postgres://xseaswlvhvhgnm:a6383e19f7ab5a17b0b89671e2d8c363ce18a229550faaac57d61058e8269929@ec2-34-233-64-238.compute-1.amazonaws.com:5432/de3mlq5i95dhst'
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()


# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)


        
        

#環境變數DJANGO_SETTINGS_MODULE
