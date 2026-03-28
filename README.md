# 🚀 Kafka Event-Driven Chat: Outbox Pattern & Observability

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000?style=for-the-badge&logo=apachekafka)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-FF7C00?style=for-the-badge&logo=gradio&logoColor=white)

Este projeto é uma simulação de ponta a ponta (End-to-End) de um aplicativo de mensageria em tempo real, construído sobre uma **Arquitetura Orientada a Eventos (EDA)**. 

Ele soluciona o problema clássico de *Dual-Write* (dupla escrita em sistemas distribuídos) através do **Padrão Outbox (Outbox Pattern)**, garantindo consistência entre o banco de dados principal e o broker de mensageria, aliado a um monitoramento completo da saúde do sistema.

## 🎯 O Desafio e a Solução
Em microsserviços, salvar uma mensagem no banco e publicá-la no Kafka não é uma operação atômica. Uma falha de rede entre as duas ações gera inconsistência.
Nossa solução utiliza o **Outbox Pattern**: a mensagem e o evento são gravados na mesma transação no PostgreSQL. Um *Worker* assíncrono lê essa tabela de eventos e garante a entrega ao Kafka (*At-Least-Once Delivery*), desacoplando a interface do usuário do processamento pesado.

## 🏗️ Arquitetura do Sistema

```mermaid
graph TD
    %% Estilização Básica
    classDef frontend fill:#2b313c,stroke:#4a5568,stroke-width:2px,color:#fff;
    classDef api fill:#0f4c75,stroke:#3282b8,stroke-width:2px,color:#fff;
    classDef db fill:#1b262c,stroke:#bbe1fa,stroke-width:2px,color:#fff;
    classDef async fill:#401f3e,stroke:#9a4c95,stroke-width:2px,color:#fff;
    classDef obs fill:#3d2c05,stroke:#fca311,stroke-width:2px,color:#fff;

    %% Componentes Frontend
    subgraph Frontend ["Frontend (Clientes Gradio)"]
        Alfa("📱 Cliente Alfa"):::frontend
        Beta("📱 Cliente Beta"):::frontend
    end

    %% Componentes API
    subgraph API_Layer ["API Layer (FastAPI)"]
        POST["POST /message<br/>(Envia)"]:::api
        GET["GET /history<br/>(Polling a cada 2s)"]:::api
        DEL["DELETE /history<br/>(Limpa Chat)"]:::api
    end

    %% Banco de Dados
    subgraph Database ["Persistência (PostgreSQL)"]
        TB_MSG[("Tabela: messages<br/>(Histórico Real)")]:::db
        TB_OUT[("Tabela: outbox<br/>(Fila de Eventos)")]:::db
    end

    %% Processamento Assíncrono / Mensageria
    subgraph Mensageria ["Pipeline Assíncrono (Event-Driven)"]
        Worker["⚙️ Outbox Worker<br/>(Relay)"]:::async
        Kafka{{"Apache Kafka<br/>(Tópico: messages)"}}:::async
        Consumer["📥 Kafka Consumer<br/>(Processamento)"]:::async
    end

    %% Observabilidade
    subgraph Observabilidade ["Observabilidade"]
        Prometheus["📡 Prometheus"]:::obs
        Grafana["📊 Grafana"]:::obs
    end

    %% --- RELACIONAMENTOS E LÓGICA ---
    Alfa -- "1. Digita e Envia" --> POST
    Beta -- "1. Digita e Envia" --> POST
    
    Alfa -. "Atualiza tela (2s)" .-> GET
    Beta -. "Atualiza tela (2s)" .-> GET
    GET -. "Retorna histórico" .-> TB_MSG

    POST -- "2a. Salva a Mensagem" --> TB_MSG
    POST -- "2b. Cria Evento" --> TB_OUT

    Worker -- "3. Lê eventos" --> TB_OUT
    Worker -- "4. Publica evento" --> Kafka
    Worker -- "5. Processado = True" --> TB_OUT

    Kafka -- "6. Consome evento" --> Consumer

    Prometheus -. "Scrape :8003" .-> POST
    Prometheus -. "Scrape :8002" .-> Worker
    Prometheus -. "Scrape :8001" .-> Consumer
    Grafana -. "PromQL" .-> Prometheus