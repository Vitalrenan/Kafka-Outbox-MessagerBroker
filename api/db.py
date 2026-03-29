import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="events",
    user="user",
    password="password"
)

conn.autocommit = True