import psycopg2
from userInfo import *

def connect_database():
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)

    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS scans(
        id SERIAL PRIMARY KEY,
        screenshot_name VARCHAR(255),
        scanned_text VARCHAR(255),
        response VARCHAR(255)
    );
                """)

    return cur, conn

def add_to_database(screenshot_name, scanned_text, response):
    cur, conn = connect_database()

    cur.execute("""INSERT INTO scans (screenshot_name, scanned_text, response) VALUES (%s, %s, %s)""", (screenshot_name, scanned_text, response))

    conn.commit()
    cur.close()
    conn.close()

def read_from_database(screenshot_name):
    cur, conn = connect_database()

    cur.execute("""SELECT * FROM scans WHERE screenshot_name = %s""", (screenshot_name,))
    info = cur.fetchone()

    cur.close()
    conn.close()

    return info