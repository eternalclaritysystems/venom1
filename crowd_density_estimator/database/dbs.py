import os
import psycopg2
from pymongo import MongoClient

pg_conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASS"],
    dbname=os.environ["PG_NAME"],
    port=os.environ["PG_PORT"]
)

mongo_conn = MongoClient(os.environ["MONGO_URI"])
