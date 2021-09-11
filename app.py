import os
from datetime import datetime

from flask import Flask, abort, request

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
    reply = TextSendMessage(text=f"{get_message}")+" ，貓貓!"
    line_bot_api.reply_message(event.reply_token, reply)
<<<<<<< HEAD
if get_message == "大貓貓":
    line_bot_api.reply_message(event.reply_token, "你才大貓貓！")

=======
<<<<<<< HEAD
    if get_message == "大貓貓":
<<<<<<< HEAD
        line_bot_api.reply_message(event.reply_token, "你才大貓貓！")
=======
        line_bot_api.reply_message(event.reply_token, "你才大貓貓")
>>>>>>> c46c4244b8c9823ae1114f47af6a9629b24d0ec3
=======
>>>>>>> 504bf3c5c68c2c411e2747183be10dbeba14c249
>>>>>>> b5a24e9ca05d9b3aef07fac96e11e6cc8444eeda
