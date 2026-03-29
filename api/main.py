from fastapi import FastAPI
import psycopg2
import json
from prometheus_client import Counter, start_http_server

api_requests = Counter('api_requests_total', 'Total API requests')
outbox_events_created = Counter('outbox_events_created_total', 'Events written to outbox')

start_http_server(8003, addr="0.0.0.0")

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API running"}

# Rota para ENVIAR mensagens
@app.post("/message")
def create_message(content: str, sender: str = "Desconhecido"):
    api_requests.inc()
    conn = psycopg2.connect(host="localhost", database="events", user="user", password="password")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (content, sender) VALUES (%s, %s) RETURNING id",
            (content, sender)
        )
        message_id = cur.fetchone()[0]

        event = {
            "event": "message_created",
            "id": message_id,
            "content": content,
            "sender": sender
        }

        cur.execute("INSERT INTO outbox (payload) VALUES (%s)", (json.dumps(event),))
        conn.commit()
        outbox_events_created.inc()
        return {"status": "saved", "id": message_id}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Rota para LER o histórico (A que estava dando o erro 405)
@app.get("/history")
def get_history():
    conn = psycopg2.connect(host="localhost", database="events", user="user", password="password")
    try:
        cur = conn.cursor()
        cur.execute("SELECT sender, content FROM messages ORDER BY id ASC")
        rows = cur.fetchall()
        
        history = []
        for row in rows:
            history.append({"sender": row[0], "content": row[1]})
            
        return {"data": history}
    finally:
        cur.close()
        conn.close()

# Rota para APAGAR o histórico
@app.delete("/history")
def delete_history():
    conn = psycopg2.connect(host="localhost", database="events", user="user", password="password")
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM messages")
        conn.commit()
        return {"status": "Histórico apagado com sucesso"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()