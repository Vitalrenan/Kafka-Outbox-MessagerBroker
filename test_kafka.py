from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

producer.send("messages", {
    "event": "message_created",
    "content": "hello world"
})

producer.flush()

print("Mensagem enviada com sucesso!")