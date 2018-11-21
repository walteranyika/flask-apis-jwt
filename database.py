import mysql.connector as db
import sys

mydb = db.connect(host="localhost", user="walter", passwd="walter", database="flask_apis")
sys.setrecursionlimit(10000)

import jwt


def insert(public_id, names, password, admin):
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO `users`(`public_id`, `names`, `password`, `admin`) VALUES (%s,%s,%s,%s)",
                   (public_id, names, password, admin))
    mydb.commit()
    return True


def get_all_users():
    cursor = mydb.cursor()
    cursor.execute("select public_id, names, password, admin from users")
    return cursor.fetchall()


def get_one_user(public_id):
    cursor = mydb.cursor()
    cursor.execute("select public_id, names, password, admin from users WHERE  public_id=%s limit 1", (public_id,))
    data = cursor.fetchone()
    return list(data)

    # print(get_one_user('7c3afb0d-01d2-420c-9688-491ec173ca0f'))

tk='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfaWQiOiI3YzNhZmIwZC0wMWQyLTQyMGMtOTY4OC00OTFlYzE3M2NhMGYiLCJleHAiOjE1NDI4MDc1Njd9.9W8IKzZ8kn3I7xY_o_bFdr4g8-0vmdy8PJXLP-P7jOE'
token=jwt.decode(tk, 'super_secret_key')
print(token)