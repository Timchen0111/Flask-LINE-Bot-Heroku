import os
from datetime import datetime
from typing import Text
import psycopg2
from flask import Flask, abort, request

#連接資料庫
#conn = psycopg2.connect(database = 'dc12u005giu04i',host = 'ec2-44-195-240-222.compute-1.amazonaws.com',port = '5432',user = 'ktptiqlmwmjwha',password = '35704ce12d9c08c10280138457c662c741af5dc5391f0a505a61ea41ec7bd0a0')
#print('Connectecd')
DATABASE_URL = os.environ['postgres://xseaswlvhvhgnm:a6383e19f7ab5a17b0b89671e2d8c363ce18a229550faaac57d61058e8269929@ec2-34-233-64-238.compute-1.amazonaws.com:5432/de3mlq5i95dhst']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

#連linebot
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


def text_reply(content, event):
    reply = TextSendMessage(text=content)
    line_bot_api.reply_message(event.reply_token, reply)

#資料庫函數
#def writeInfo(thing,price):    
 #   cursor.execute("INSERT INTO table1(thing,price)VALUES(%s,%s);",(thing,price))
  #  return True
    



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    id = event.source.user_id  # 獲取使用者ID
    #print(id)
    get_message = event.message.text.rstrip().strip()
    if get_message == "壞貓貓":
        badcat = "你才壞貓貓"
        text_reply(badcat,event)
    else:
        confuse = "我聽不懂你在說什麼"
        text_reply(confuse,event)

conn.commit()
cursor.close()
conn.close()

        
        

#環境變數DJANGO_SETTINGS_MODULE
