from kafka import KafkaProducer
import psycopg2
import json
import time
from prometheus_client import start_http_server, Counter

events_processed = Counter('worker_events_processed_total', 'Total events processed by worker')
start_http_server(8002, addr="0.0.0.0")
print("Outbox worker started...")

conn = psycopg2.connect(
    host="localhost",
    database="events",
    user="user",
    password="password"
)

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

while True:

    cur = conn.cursor()

    cur.execute(
        "SELECT id, payload FROM outbox WHERE processed = FALSE"
    )

    rows = cur.fetchall()

    for row in rows:
        event_id = row[0]
        payload = row[1]   # ✅ AQUI está o payload

        print("Sending event:", payload)

        producer.send("messages", payload)

        # marcar como processado
        cur.execute(
            "UPDATE outbox SET processed = TRUE WHERE id = %s",
            (event_id,)
        )

    conn.commit()

    time.sleep(2)