from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import threading
import time
import os
from armazenamento import GerenciadorDados
from coletor import ColetorDeImagens, ColetorXGroovyGifs

# Inicializa o Servidor Web (Flask)
app = Flask(__name__, template_folder="templates", static_folder="temp_imagens")
CORS(app) # Remove bloqueios de segurança entre celular e PC

# Variáveis Globais iguais as do seu projeto original
banco = GerenciadorDados()
buffer_rodadas = []
MODO_ATUAL = "normal"
TIPO_MIDIA = "fotos"

# ==========================================
# MOTOR DE DOWNLOADS EM SEGUNDO PLANO
# ==========================================
def worker():
    global buffer_rodadas, MODO_ATUAL, TIPO_MIDIA
    coletor_fotos = ColetorDeImagens("https://www.pornpics.com/")
    coletor_gifs = ColetorXGroovyGifs()
    
    while True:
        try:
            if len(buffer_rodadas) < 10:
                coletor = coletor_gifs if TIPO_MIDIA == "gifs" else coletor_fotos
                print(f"[ SERVIDOR ] Buscando {TIPO_MIDIA} - Modo: {MODO_ATUAL.upper()}...")
                
                imgs = coletor.buscar_dados(10, MODO_ATUAL) # Baixa de 10 em 10 para a web
                if imgs:
                    for img in imgs:
                        # Aqui simplificamos o download para focar no servidor
                        import requests
                        path = os.path.join("temp_imagens", img['nome'])
                        try:
                            res = requests.get(img['url'], timeout=10)
                            if res.status_code == 200:
                                with open(path, 'wb') as f: f.write(res.content)
                                img['caminho_local'] = img['nome'] # O HTML só precisa do nome
                                buffer_rodadas.append(img)
                        except: pass
                else:
                    time.sleep(2)
            else:
                time.sleep(1)
        except Exception as e: 
            print(f"[ ERRO WORKER ] {e}")
            time.sleep(5)

# ==========================================
# ROTAS DA API (A PONTE COM O CELULAR)
# ==========================================

# 1. Rota principal: Entrega a página HTML (O visual)
@app.route('/')
def index():
    return render_template('index.html')

# 2. Rota de Dados: O celular pede uma imagem nova
@app.route('/api/proxima_imagem', methods=['GET'])
def proxima_imagem():
    if buffer_rodadas:
        img = buffer_rodadas.pop(0)
        return jsonify({"status": "ok", "imagem": img})
    else:
        return jsonify({"status": "carregando", "mensagem": "Aguarde, baixando..."})

# 3. Rota de Avaliação: O celular avisa que você fez o Swipe
@app.route('/api/avaliar', methods=['POST'])
def avaliar():
    dados = request.json
    tags = dados.get('tags', [])
    nota = dados.get('nota', 0)
    url_origem = dados.get('url_origem', '')
    
    if nota is not None:
        banco.atualizar_pontuacao(tags, nota, url_origem)
        print(f"[ AVALIAÇÃO WEB ] Nota {nota} computada com sucesso!")
        
    return jsonify({"status": "sucesso"})

# ==========================================
# INICIAR O MOTOR EM SEGUNDO PLANO
# ==========================================
# Ao deixar fora do if __name__ == '__main__', o Gunicorn da nuvem vai executar isso!
if not os.path.exists("temp_imagens"): 
    os.makedirs("temp_imagens")

print("Iniciando Motor de Downloads...")
threading.Thread(target=worker, daemon=True).start()

# ==========================================
# INICIAR O SERVIDOR DE TESTE LOCAL
# ==========================================
if __name__ == '__main__':
    print("\n🌐 SERVIDOR LOCAL ATIVO! 🌐")
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
