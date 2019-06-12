from flask import Flask, request, json
from flask import render_template, jsonify, Response
import pymysql
import sys

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def route_index():
    return render_template('index.html')

@app.route("/login", methods=['POST'])
def login():
    status = ""

    # connect databese
    conn = create_db_connection()

    # parse json request
    userid = request.json['id']
    passwd = request.json['pw']

    # select user info
    try:
        with conn.cursor() as cursor:
            sql = "SELECT name, pwd FROM user WHERE id = %s"
            cursor.execute(sql, (userid,))
            record = cursor.fetchone()

            # authenticate user/passwd
            if (record != None) and (passwd == record['pwd']) :
                status = "Welcome - {}".format(record['name'])
            else:
                status = "Invalid user name or password."

    except Exception as e:
        tb = sys.exc_info()[2]
        status = "system error. ({})".format(e.with_traceback(tb))

    finally:
        conn.close()

    return jsonify(ResultSet=json.dumps({"result": status}))

def create_db_connection():
    return pymysql.connect(host='127.0.0.1',
                           port=4000,
                           user='root',
                           password='mdbuser',
                           db='flask_app',
                           cursorclass=pymysql.cursors.DictCursor)

if __name__ == '__main__':
    # start up test server
    app.run('127.0.0.1', port=8888, debug=True)