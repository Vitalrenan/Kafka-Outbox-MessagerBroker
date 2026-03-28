from confluent_kafka import Consumer, KafkaError
from prometheus_client import start_http_server, Counter
import json

# 1. Definição das Métricas
messages_consumed = Counter('messages_consumed_total', 'Total messages consumed')

# 2. Servidor de métricas (Com addr="0.0.0.0" para o Prometheus/Docker conseguir acessar)
start_http_server(8001, addr="0.0.0.0")

# 3. Configuração do Consumer
consumer = Consumer({
    "bootstrap.servers": "localhost:29092",
    "group.id": "test-consumer-2",
    "auto.offset.reset": "earliest"
})

consumer.subscribe(["messages"])

print("🚀 Consumer + Metrics running na porta 8001...")

while True:
    # Busca mensagens no Kafka (espera até 1 segundo)
    msg = consumer.poll(1.0)

    # Se não tem mensagem, volta para o início do loop em silêncio
    if msg is None:
        continue

    # Tratamento de erros de conexão/leitura do próprio Kafka
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            # Apenas chegou ao fim da fila atual, ignoramos
            continue
        else:
            print(f"🚨 Erro de leitura no Kafka: {msg.error()}")
            continue

    # 4. Tratamento Blindado da Mensagem (Anti Poison-Pill)
    try:
        # Decodifica os bytes para string
        raw_value = msg.value().decode('utf-8')
        
        # Tenta transformar a string em um dicionário Python (JSON)
        event = json.loads(raw_value)

        # ✅ SUCESSO! A mensagem é válida. Agora sim incrementamos a métrica.
        messages_consumed.inc()
        print("✅ Evento processado:", event)

    except json.JSONDecodeError:
        # PÍLULA ENVENENADA: Mensagem corrompida lida do passado. Ignoramos e seguimos.
        print(f"⚠️ Ignorando lixo/mensagem malformada: {msg.value()}")
        continue
        
    except Exception as e:
        # Proteção extra contra qualquer outro erro bizarro que possa derrubar o script
        print(f"❌ Erro inesperado ao processar: {e}")
        continue