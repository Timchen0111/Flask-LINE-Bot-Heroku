import os
import psycopg2
from typing import Text
from flask import Flask, abort, request

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

DATABASE_URL = "postgres://xseaswlvhvhgnm:a6383e19f7ab5a17b0b89671e2d8c363ce18a229550faaac57d61058e8269929@ec2-34-233-64-238.compute-1.amazonaws.com:5432/de3mlq5i95dhst"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()


id = "U4341691df852cdb7883463fe87c0d944"
#postgres_select_query = f'SELECT "buyerName" FROM "orderInfo" WHERE "buyerNumber" = {buyerNumber}'
# Uf8c57619b4682e8562b146d3ab032f09

postgres_select_query = 'SELECT "memberNumber" FROM member WHERE "lineID" = \'%s\''%id
cursor.execute(postgres_select_query)
memberNum = cursor.fetchall()
#print(memberNum[0][0])
postgres_select_query2 = 'SELECT "productNumber","productName" FROM "orderInfo" WHERE "buyerNumber" = %d'%memberNum[0][0]
cursor.execute(postgres_select_query2)
query = cursor.fetchall()
s = ''
for i in query:
    for j in i:
        s += str(j)
        s += ","
    s += "\n"
print(s)

def text_reply(content, event):
    reply = TextSendMessage(text=content)
    line_bot_api.reply_message(event.reply_token, reply)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    id = event.source.user_id # 獲取使用者ID 
    get_message = event.message.text.rstrip().strip()
    if get_message == "我買的東西":
        text_reply(s,event)
