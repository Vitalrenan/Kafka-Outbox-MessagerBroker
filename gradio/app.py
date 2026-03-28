import gradio as gr
import requests
import sys

USER = sys.argv[1] if len(sys.argv) > 1 else "Alfa"
PORT = 7860 if USER == "Alfa" else 7861
API_URL = "http://127.0.0.1:8000"

def send_message(content):
    if not content.strip():
        return ""
    try:
        requests.post(f"{API_URL}/message", params={"content": content, "sender": USER})
    except Exception as e:
        print("Erro ao enviar:", e)
    return ""

def get_chat_history():
    try:
        response = requests.get(f"{API_URL}/history")
        data = response.json().get("data", [])
        
        if not data:
            return "📭 *Nenhuma mensagem no histórico.*"

        chat_display = ""
        for msg in data:
            remetente = msg['sender']
            texto = msg['content']
            if remetente == USER:
                chat_display += f"🟢 **Você ({remetente})**: {texto}\n\n"
            else:
                chat_display += f"🔵 **{remetente}**: {texto}\n\n"
        return chat_display
    except:
        return "🚨 Conectando ao servidor..."

# Nova função para limpar o chat
def clear_history():
    try:
        requests.delete(f"{API_URL}/history")
    except Exception as e:
        print("Erro ao limpar:", e)

with gr.Blocks() as interface:
    gr.Markdown(f"# 📱 Chat Kafka - Logado como: **{USER}**")
    
    chat_box = gr.Markdown(value="Carregando...")
    
    with gr.Row():
        msg_input = gr.Textbox(placeholder="Digite sua mensagem...", show_label=False, scale=4)
        send_btn = gr.Button("Enviar 🚀", scale=1)
        clear_btn = gr.Button("🗑️ Limpar Chat", scale=1) # Novo botão!

    # Ações
    send_btn.click(fn=send_message, inputs=msg_input, outputs=msg_input)
    msg_input.submit(fn=send_message, inputs=msg_input, outputs=msg_input)
    
    # Ação do novo botão
    clear_btn.click(fn=clear_history, inputs=None, outputs=None)
    
    # Atualização em tempo real
    timer = gr.Timer(2)
    timer.tick(fn=get_chat_history, inputs=None, outputs=chat_box)
    interface.load(fn=get_chat_history, inputs=None, outputs=chat_box)

if __name__ == "__main__":
    print(f"Iniciando App {USER} na porta {PORT}...")
    interface.launch(server_port=PORT, theme=gr.themes.Soft())