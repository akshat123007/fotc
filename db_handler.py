from psycopg2 import connect
import psycopg2.extras
import logging
from datetime import datetime
import os

LOG_FILENAME = os.path.join("logs/", datetime.now().strftime('logfile_%H_%M_%S_%d_%m_%Y.log'))
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=LOG_FILENAME, filemode='w', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

DATABASE = "fotcdb"
USER = "postgres"
PASSWORD = "postgres"
HOST = "127.0.0.1"
PORT = "5432"

def fypDB_Connect():
    try:
        conn = connect(
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        logging.info("Opened database successfully")
        return conn
    except Exception as e:
        logging.error(e)


def cursor(conn):
    try:
        cur = conn.cursor()
        logging.info("Cursor generated")
        return cur
    except Exception as e:
        logging.error(e)


def commit(conn):
    try:
        conn.commit()
        logging.info('query commited')
    except Exception as e:
        logging.error(e)


def execute(conn, query):
    try:
        cur = cursor(conn)
        cur.execute(query)
        logging.info("Query Executed.")
        commit(conn)
    except Exception as e:
        logging.error(e)


def fetch(conn, query):
    try:

        cur = cursor(conn)
        cur.execute(query)
        rows = cur.fetchall()
        logging.info('query fetched')
        return rows

    except Exception as e:
        logging.error(e)

def executeDictCursor(conn, query):
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        logging.info("Query executed.")
        commit(conn)
    except Exception as e:
        logging.error(e)

def close(conn):
    try:
        conn.close()
        logging.info('connection closed')
    except Exception as e:
        logging.error(e)
