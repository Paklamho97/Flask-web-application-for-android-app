#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask
from flask import request
from flask import jsonify
import mysql.connector
from flask import g
import re
import requests


class MyDatabase:
    conn = None
    cursor = None
    def __init__ (self) :
        self.connect()
        return
    def connect(self):
        self.conn = mysql.connector.connect(
            host = "localhost",
            port = 3306, # default, can be omitted
            user = "dbuser",
            password = "password",
            database = "iems5722",
        )
        self.cursor = self.conn.cursor(dictionary = True)
        return


app = Flask(__name__)


@app.before_request
def before_request():
    g.mydb = MyDatabase()
    return

@app.teardown_request
def teardown_request(exception):
    mydb = getattr(g,"mydb",None)
    if mydb is not None:
        mydb.conn.close( )
    return

@app.route("/api/a3/get_chatrooms")
def get_chatrooms():
    query = "SELECT * FROM chatrooms"
    g.mydb.cursor.execute(query)
    results = g.mydb.cursor.fetchall()
    if results is None:
        return jsonify(status="ERROR")
    else:
        return jsonify(status="OK", data=results)

@app.route("/api/a3/get_messages", methods=['GET'])
def get_messages():
    chatroom_id = request.args.get("chatroom_id")
    page = int(request.args.get("page"))
    cp = (page-1)*5
    query = "SELECT * FROM messages WHERE chatroom_id = %s ORDER BY message_time DESC LIMIT %s, 5"
    params = (chatroom_id, cp,)
    g.mydb.cursor.execute(query, params)
    results = g.mydb.cursor.fetchall()
    if results is None:
        return jsonify(status="ERROR")
    else:
        jsondata = {"current_page": page, "messages": results, "total_pages": total_pages(chatroom_id)}
        return jsonify(status="OK", data=jsondata)

@app.route("/api/a3/send_message", methods=['POST'])
def send_message():
    chatroom_id = request.form.get('chatroom_id')
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    message = request.form.get('message')
    if re.match('^[0-9]*$', chatroom_id) is None:
        return jsonify(message="<error message>", status="ERROR")
    if re.match('^[0-9]*$', user_id) is None:
        return jsonify(message="<error message>", status="ERROR")
    #if re.match('^\w+$', message) is None:
        #return jsonify(message="<error message>", status="ERROR")
    #if re.match('^\w+$', name) is None:
        #return jsonify(message="<error message>", status="ERROR")
    query = "INSERT INTO messages (chatroom_id, user_id, name, message) VALUES (%s, %s, %s, %s)"
    params = (chatroom_id, user_id, name, message, )
    try:
        g.mydb.cursor.execute(query, params)
        g.mydb.conn.commit()
        url = "http://18.222.138.26/api/a4/broadcast_room"
        headers = {
            "Content-Type" : "application/json"
        }
        payload = {
            "chatroom_id" : chatroom_id,
            "message" : message
        }
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            print("Request is sent successfully!")
        return jsonify(status="OK")
    except:
        g.mydb.conn.rollback()
        return jsonify(status="ERROR")

@app.route("/getname", methods=["GET"])
def getname():
    name = request.args.get("name")
    return jsonify(name=name)

def total_pages(i):
    query = "SELECT * FROM messages WHERE chatroom_id = %s"
    params = (i,)
    g.mydb.cursor.execute(query, params)
    results = g.mydb.cursor.fetchall()
    return int(len(results)/5+1)

if __name__ == "__main__" :
    app.debug="true"
    app.run('0.0.0.0')


# In[ ]:




