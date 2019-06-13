from flask import Flask,redirect, request, session, json, render_template, jsonify, Response, url_for
import pymysql
import sys
import time
import hashlib
import os
from datetime import datetime
from flask_wtf import CSRFProtect

app = Flask(__name__)
csrf_protect = CSRFProtect(app)

'''
top page

'''
@app.route("/", methods=["POST", "GET"])
def index():
    if not session.get('is_logged_in') or session['is_logged_in'] == False:
        return render_template('index.html', )

    return redirect(url_for('mypage'))

'''
user page

'''
@app.route("/mypage")
def mypage():
    if not session.get('is_logged_in'):
        return index()

    name = session['user_name']
    return "Hello {}".format(name)

'''
create user

'''

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_regist", methods=['POST'])
def create_user():
    status = ""
    reason = ""
    foward = ""
    json_obj = ""
    conn = create_db_connection()

    userid   = request.json['id']
    username = request.json['name']
    passwd   = "" #request.json['pw']

    try:
        with conn.cursor() as cursor:
            # check existing user id
            sql = "SELECT COUNT(*) AS cnt FROM user WHERE id = %s"
            cursor.execute(sql, (userid))
            count = cursor.fetchone()

            if count['cnt'] != 0:
                status = "NG"
                reason = "{} is already exist."

            else:
                sql = "INSERT INTO user (id, name, pwd) VALUES (%s, %s, %s)"
                r = cursor.execute(sql, (userid, username, passwd))
                if r == 1:
                    conn.commit()
                    status = "OK"
                    reason = "{} has completed registration."
                    foward = "login"
                else:
                    conn.rollback()

                    status = "NG"
                    reason = "system error."

            json_obj = {"status": status, "reason": reason, "foward": foward}            
         
    except Exception as e:
        tb = sys.exc_info()[2]
        status = "NG"
        reason = "system error.\n {}".format(e.with_traceback(tb))     
    
    finally:
        json_obj = {"status": status, "reason": reason, "foward": foward}
        return jsonify(ResultSet=json.dumps(json_obj))

'''
login page

'''
@app.route("/login", methods=["POST"])
def login():
   
    status = ""
    foward = ""

    # connect databese
    conn = create_db_connection()

    # parse json request
    userid = request.json['id']
    passwd = request.json['pw']

    # select user info
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, pwd FROM user WHERE id = %s"
            cursor.execute(sql, (userid,))
            record = cursor.fetchone()

            # authenticate user/passwd
            if (record != None) and (passwd == record['pwd']) :
                status = "OK"
                foward = "mypage"

                # set session
                session['is_logged_in'] = True
                session['user_name'] = userid

            else:
                status = "Invalid user name or password."
                foward = "/"
                session['is_logged_in'] = False
            
    except Exception as e:
        tb = sys.exc_info()[2]
        status = "system error. ({})".format(e.with_traceback(tb))

    finally:
        conn.close()

    return jsonify(ResultSet=json.dumps({"result": status, "redirect": foward}))
   
'''
logout

'''
@app.route("/logout")
def logout():
    session['is_logged_in'] = False
    session['user_name'] = ""   

    return index()

def create_db_connection():
    return pymysql.connect(host='127.0.0.1',
                           port=4000,
                           user='root',
                           password='mdbuser',
                           db='flask_app',
                           cursorclass=pymysql.cursors.DictCursor)

def create_seed():
    unix_time = datetime.now().strftime("%Y/%m/%d%H:%M:%S")
    rnd       = os.urandom(1000)
    seed_str  = "{}{}".format(unix_time, rnd)

    return hashlib.sha3_512(seed_str.encode()).hexdigest()

if __name__ == '__main__':
    # start up test server
    app.secret_key = create_seed()
    app.run('127.0.0.1', port=8888, debug=True)
