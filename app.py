import os
from datetime import datetime
from typing import Text
#import psycopg2
from flask import Flask, abort, request
import time

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
    lst = text.split(";")
    myDict = {}
    myDict["memberName"] = lst[1]
    myDict["phone"] = lst[2]
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
        pass
    else:
        cursor.execute('SELECT MAX("memberNumber") FROM member')
        query = cursor.fetchall()
        maxnum = query[0][0]
        if maxnum == None:
            maxnum = 0
        memberNum = maxnum+1 
        name = j["memberName"]
        phone = j["phone"]   
        cursor.execute("INSERT INTO member VALUES(%s,%s,%s,%s);",(memberNum,name,phone,id))
        conn.commit()

#上架函式
def updateProduct(id,j):
    cursor.execute("SELECT \"memberNumber\" From member WHERE \"lineID\" = '%s'"%str(id))
    query = cursor.fetchall()
    memberNum = query[0][0]
    cursor.execute('SELECT MAX("productNumber") FROM product')
    query = cursor.fetchall()
    maxnum = query[0][0]
    if maxnum == None:
        maxnum = 0
    proNum = maxnum+1
    cursor.execute('INSERT INTO product("productNumber","memberNumber","productName","productDescription","productPicturelink","productPrice","productQuantity","deliveryPlace","productState") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);',(proNum,memberNum,j["name"],j["description"],j["link"],j["price"],j["quantity"],j["place"],True))
    conn.commit()

#放入購物車
def orderCart(proNum,id,quantity):
    #從ID找用戶代碼
    proNum = int(proNum)
    cursor.execute("SELECT \"memberNumber\" From member WHERE \"lineID\" = '%s'"%str(id))
    query = cursor.fetchall()
    print(query)
    memberNum = query[0][0]
    #確認商品是否還在
    cursor.execute("SELECT \"productState\" From product WHERE \"productNumber\" = '%s'"%proNum)
    query = cursor.fetchall()
    if query[0][0] == False:
        return False
    #製造流水號
    cursor.execute('SELECT MAX("serialNumber") FROM "orderCart"')
    query = cursor.fetchall()
    maxnum = query[0][0]
    if maxnum == None:
        maxnum = 0
    serialNumber = maxnum+1
    #找商品名稱
    cursor.execute("SELECT \"productName\" From product WHERE \"productNumber\" = '%s'"%proNum)
    query = cursor.fetchall()
    name = query[0][0]

    cursor.execute('INSERT INTO "orderCart" VALUES(%s,%s,%s,%s,%s,%s);',(serialNumber,True,memberNum,proNum,quantity,name))
    cursor.execute('Update product SET "productQuantity" = "productQuantity"-1 WHERE "productNumber" = %d'%proNum)
    cursor.execute("SELECT \"productQuantity\" From product WHERE \"productNumber\" = '%s'"%proNum)
    query = cursor.fetchall()
    if query[0][0] == 0:
        cursor.execute('Update product SET "productState" = false WHERE "productNumber" = %d'%proNum)
    conn.commit()
   

#查看購物車
def checkCart(id):
    #從ID找用戶代碼
    cursor.execute("SELECT \"memberNumber\" From member WHERE \"lineID\" = '%s'"%str(id))
    query = cursor.fetchall()
    memberNum = query[0][0]
    #印出購物車
    cursor.execute('SELECT *From "orderCart" WHERE "memberNumber" = \'%s\''%memberNum)
    query =  cursor.fetchall()
    lst = []
    for i in query:
        if i[1] == True:
            lst.append(i)
    return lst

#下單
def orderCartProduct(id):
    #從ID找用戶代碼
    cursor.execute("SELECT \"memberNumber\" From member WHERE \"lineID\" = '%s'"%str(id))
    query = cursor.fetchall()
    memberNum = query[0][0]
    #找到要調的資料
    lst_cart = checkCart(id)
    #print(lst_cart) 
    lst_productNumber = []
    lst_productName = []
    for i in lst_cart:
        lst_productNumber.append(i[3])
        lst_productName.append(i[5])
    #print(lst_productNumber,lst_productName)
    #print(lst)
    #製造流水號
    cursor.execute('SELECT MAX("orderNumber") FROM "orderInfo"')
    query = cursor.fetchall()
    maxnum = query[0][0]
    if maxnum == None:
        maxnum = 0
    orderNum = maxnum+1
    #print(orderNum)
    #時間
    nowtime = time.ctime()
    orderTime = nowtime.split(' ')[3]
    orderDate = nowtime.split(' ')[1]+'-'+nowtime.split(' ')[2]+'-'+nowtime.split(' ')[4]

    #數量
    productQuantity = 0
    for i in lst_cart:
        productQuantity += i[4]
    #找賣家是誰
    lst = []
    lst2 = []
    for i in lst_cart:
        proNum = i[3]
        cursor.execute('SELECT "memberNumber" FROM "product" WHERE "productNumber" = \'%s\''%proNum)
        query = cursor.fetchall()
        #print(query[0][0])
        lst2.append(query[0][0])
        print(lst2)
    #一一丟資料
    cursor.execute('SELECT "memberNumber" FROM member WHERE "lineID" = \'%s\''%id)
    query = cursor.fetchall()
    lst3 = []
    memberNum = int(query[0][0])
    for i in range(len(lst_cart)):             
        cursor.execute('INSERT INTO "orderInfo" VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',(orderNum,orderTime,productQuantity,None,True,orderDate,lst2[i],lst_productNumber[i],memberNum,lst_productName[i]))
        print('happy')
        orderNum += 1     
    #清空購物車
        lst3.append([orderNum,orderTime,productQuantity,orderDate,lst2[i],lst_productNumber[i],memberNum,lst_productName[i])])
    for i in lst_productNumber:
        cursor.execute('UPDATE "orderCart" SET "productState" = false WHERE "productNumber" = %s'%int(i))
    s = ""
    for i in lst3:
        for j in i:
            s += str(j)
            s += ','
        s += "\n"
    conn.commit()

def get_order_cart_information():
    productNameList = []
    productQuantityList = []
    totalMoneyList = []
    index = []
    
    return productNameList, productQuantityList, totalMoneyList, index






#處理訊息
def text_reply(content, event):
    reply = TextSendMessage(text=content)
    line_bot_api.reply_message(event.reply_token, reply)



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    id = event.source.user_id # 獲取使用者ID 
    get_message = event.message.text.rstrip().strip()
    if get_message[:5] == "放入購物車":
        lst = get_message.split(";") 
        productNumber = lst[1]
        quantity = lst[2]
        if orderCart(productNumber,id,quantity) == False:
            qq = "已售完QQ"
            text_reply(qq,event)
        else:
            finish_ = "已放入購物車！\n若要查看購物車請輸入\"查看購物車\"，若要下訂單請輸入\"下單\""
            text_reply(finish_,event)
    elif get_message == "查看購物車":
        checkCart(id)
        lst = checkCart(id)
        print(lst)
        string = ''
        for i in lst:
            for j in i:
                string += str(j)
                string += ','
            string += "\n"
        text_reply(string,event)
    elif get_message == "下單":
        orderlist = orderCartProduct(id)
        s = ''
        for i in orderlist:
            for j in i:
                s += str(j)
                s += ","
            s += "\n" 
        buy = "已完成下單！您的訂單內容為："+s
        text_reply(buy,event)
    elif get_message[:2] == "上架":
        d = updateDictionary(get_message)
        updateProduct(id,d)
        finish = "上架完成！"
        text_reply(finish,event)
    else:
        confuse = "我聽不懂你在說什麼"
        text_reply(confuse,event)

conn.commit()

