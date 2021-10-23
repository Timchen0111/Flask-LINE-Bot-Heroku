import os
from datetime import datetime
from typing import Text
import psycopg2
from flask import Flask, abort, request

#連接資料庫
DATABASE_URL = 'postgres://xseaswlvhvhgnm:a6383e19f7ab5a17b0b89671e2d8c363ce18a229550faaac57d61058e8269929@ec2-34-233-64-238.compute-1.amazonaws.com:5432/de3mlq5i95dhst'
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

#把使用者上架傳送資料製造成Dictionary
def updateDictionary(text):
    lst = text.split("\n")
    myDict = {}
    myDict["memberName"] = lst[0]
    myDict["phone"] = lst[1]
    myDict["name"] = lst[3] 
    myDict["description"] = lst[4]
    myDict["link"] = lst[5]
    myDict["price"] = int(lst[6])
    myDict["quantity"] = int(lst[7])
    myDict["place"] = lst[8]
    return myDict

#使用者登入函式
def updateMember(id,j):
    cursor.execute('SELECT "lineID" FROM member WHERE "lineID" = \'%s\''%str(id))
    query = cursor.fetchall()
    if query != []:
        print("使用者已登入")
        pass
    else:
        cursor.execute('SELECT MAX("memberNumber") FROM member')
        query = cursor.fetchall()
        maxnum = query[0][0]
        if maxnum == None:
            maxnum = 0
        memberNum = maxnum+1 
        print(type(j))
        name = j["memberName"]
        phone = j["phone"]   
        cursor.execute("INSERT INTO member VALUES(%s,%s,%s,%s);",(memberNum,name,phone,id))
        conn.commit()

#上架函式
def updateProduct(id,j):
    cursor.execute("SELECT \"memberNumber\" From member WHERE \"lineID\" = '%s'"%str(id))
    query = cursor.fetchall()
    print(query)
    memberNum = query[0][0]
    cursor.execute('SELECT MAX("productNumber") FROM product')
    query = cursor.fetchall()
    maxnum = query[0][0]
    print(maxnum)
    if maxnum == None:
        maxnum = 0
    proNum = maxnum+1
    print(proNum)
    cursor.execute('INSERT INTO product("productNumber","memberNumber","productName","productDescription","productPicturelink","productPrice","productQuantity","deliveryPlace") VALUES(%s,%s,%s,%s,%s,%s,%s,%s);',(proNum,memberNum,j["name"],j["description"],j["link"],j["price"],j["quantity"],j["place"]))
    conn.commit()


#處理訊息
def text_reply(content, event):
    reply = TextSendMessage(text=content)
    line_bot_api.reply_message(event.reply_token, reply)



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    id = event.source.user_id  # 獲取使用者ID
    #print(id)
    get_message = event.message.text.rstrip().strip()
    if get_message == "下單":
        errortext = "這邊還沒開發好qq"
        text_reply(errortext,event)
    elif get_message[:2] == "上架":
        d = updateDictionary(get_message)
        work = "努力中"
        text_reply(work,event)
        #print(type(d))
        updateMember(id,d)
        text_reply(work,event)
        updateProduct(id,d)
        finish = "上架完成！"
        text_reply(finish,event)        
    else:
        confuse = "我聽不懂你在說什麼"
        text_reply(confuse,event)

conn.commit()
cursor.close()
conn.close()

        
        

#環境變數DJANGO_SETTINGS_MODULE
