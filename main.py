import os
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from interface import TelaAvaliador
from interface_mobile import TelaMobile
from armazenamento import GerenciadorDados
from coletor import ColetorDeImagens, ColetorXGroovyGifs

# Configurações Globais
LINK_DO_SEU_SITE = "https://www.pornpics.com/" 
QTD_FOTOS_CICLO = 15 # Reduzido para encher a manga mais rápido
PASTA_TEMP = "temp_imagens"

# Variáveis de Estado
buffer_rodadas = []
MODO_ATUAL = "normal" 
TIPO_MIDIA = "fotos"

def preparar():
    if not os.path.exists(PASTA_TEMP): 
        os.makedirs(PASTA_TEMP)

def tarefa_baixar(item):
    path = os.path.join(PASTA_TEMP, item['nome'])
    try:
        res = requests.get(item['url'], timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        if res.status_code == 200:
            with open(path, 'wb') as f: f.write(res.content)
            item['caminho_local'] = path
            return item
    except: 
        return None

def worker():
    global buffer_rodadas, MODO_ATUAL, TIPO_MIDIA
    
    # Criamos os dois coletores aqui
    coletor_fotos = ColetorDeImagens(LINK_DO_SEU_SITE)
    coletor_gifs = ColetorXGroovyGifs()
    
    while True:
        try:
            if len(buffer_rodadas) < 30:
                # Escolhe o coletor baseado na chave da interface
                coletor = coletor_gifs if TIPO_MIDIA == "gifs" else coletor_fotos
                
                print(f"[ BUFFER ] Abastecendo {TIPO_MIDIA}: ({len(buffer_rodadas)}/30 prontas) - Modo: {MODO_ATUAL.upper()}")
                print("[ SCRAPER ] Buscando no site...")
                
                imgs = coletor.buscar_dados(QTD_FOTOS_CICLO, MODO_ATUAL)

                if imgs:
                    with ThreadPoolExecutor(max_workers=20) as exe:
                        res = list(exe.map(tarefa_baixar, imgs))
                        pacote = [r for r in res if r is not None]
                    
                    if len(pacote) >= 2 or (TIPO_MIDIA == "gifs" and len(pacote) >= 1): 
                        buffer_rodadas.append(pacote)
                else:
                    print("[ SCRAPER ] Nenhuma mídia encontrada ou site bloqueado. Tentando novamente...")
                    time.sleep(2)
            else:
                time.sleep(1) # Dorme se o buffer estiver cheio
                
        except Exception as e: 
            print(f"[ WORKER ERRO ] {e}")
            time.sleep(5)

def iniciar():
    global MODO_ATUAL, buffer_rodadas, TIPO_MIDIA
    
    preparar()
    banco = GerenciadorDados()
    threading.Thread(target=worker, daemon=True).start()

    # --- PERGUNTA QUAL INTERFACE ABRIR ---
    print("\n" + "="*40)
    print("📱 ESCOLHA A INTERFACE DE EXIBIÇÃO 💻")
    print("="*40)
    print("[ 1 ] Computador (Teclado e Mouse)")
    print("[ 2 ] Celular (Modo Swipe/Tinder)")
    escolha = input("\n-> Digite 1 ou 2 e aperte Enter: ").strip()
    
    if escolha == "2":
        app = TelaMobile()
    else:
        app = TelaAvaliador()

    # --- CONEXÃO COM O BOTÃO DE NORMAL/TRANS ---
    def mudar_modo_global(novo_modo):
        global MODO_ATUAL, buffer_rodadas
        MODO_ATUAL = novo_modo
        buffer_rodadas.clear() 
        banco.mudar_modo(novo_modo) 
        
        # Limpa a tela atual para você não banir uma modelo errada
        app.pacote_atual = []
        app.tags_do_pacote = []
        
        # Adaptação para limpar a tela certa (Celular ou PC)
        if hasattr(app, 'lbl_imagem_1'):
            app.limpar_label_seguro(app.lbl_imagem_1, f"Buscando {novo_modo}...")
            app.limpar_label_seguro(app.lbl_imagem_2, "Aguarde...")
        elif hasattr(app, 'lbl_imagem'):
            app.limpar_label_seguro(app.lbl_imagem, f"Buscando {novo_modo}...")

        print(f"\n[ SISTEMA ] Chave virada! Buscando conteúdo: {novo_modo.upper()}\n")
        
    if hasattr(app, 'callback_mudar_modo'):
        app.callback_mudar_modo = mudar_modo_global
    
    # --- CONEXÃO COM O BOTÃO DE FOTO/GIF ---
    def mudar_tipo_global(novo_tipo):
        global TIPO_MIDIA, buffer_rodadas
        TIPO_MIDIA = novo_tipo
        buffer_rodadas.clear()
        
        app.pacote_atual = []
        if hasattr(app, 'lbl_imagem_1'):
            app.limpar_label_seguro(app.lbl_imagem_1, f"Trocando para {novo_tipo}...")
            app.limpar_label_seguro(app.lbl_imagem_2, "Aguarde...")
        elif hasattr(app, 'lbl_imagem'):
            app.limpar_label_seguro(app.lbl_imagem, f"Trocando para {novo_tipo}...")
            
        print(f"[ SISTEMA ] Tipo de mídia alterado para: {novo_tipo.upper()}")

    if hasattr(app, 'callback_mudar_tipo'):
        app.callback_mudar_tipo = mudar_tipo_global
    
    # Banimento seguro (Cria do zero se precisar)
    if hasattr(app, 'callback_banir_modelo'):
        app.callback_banir_modelo = lambda tag: banco.banir_tag(tag)

    def carregar():
        if buffer_rodadas:
            pacote = buffer_rodadas.pop(0)
            app.pacote_atual = pacote
            app.indice_imagem_atual = 0
            
            # Atualiza labels de fonte/tags baseando se é Mobile ou PC
            if hasattr(app, 'lbl_fonte'):
                app.lbl_fonte.configure(text=f"Fonte: {pacote[0]['url_origem']}")
            
            tags = pacote[0].get('tags', [])
            if hasattr(app, 'lbl_tags'):
                app.lbl_tags.configure(text="Tags/Models: " + ", ".join(tags))
                
            app.tags_do_pacote = tags
            app.url_atual = pacote[0]['url_origem']
            
            app.iniciar_loop_imagens()
        else:
            if hasattr(app, 'lbl_imagem_1'):
                app.limpar_label_seguro(app.lbl_imagem_1, "Baixando mídias...")
                app.limpar_label_seguro(app.lbl_imagem_2, "Aguarde o Buffer...")
            elif hasattr(app, 'lbl_imagem'):
                app.limpar_label_seguro(app.lbl_imagem, "Baixando mídias...")
                
            app.update()
            app.after(1000, carregar)

    def limpar_seguro():
        em_uso = {os.path.basename(img['caminho_local']) for p in buffer_rodadas for img in p if 'caminho_local' in img}
        if app.pacote_atual: 
            for img in app.pacote_atual: 
                if 'caminho_local' in img: 
                    em_uso.add(os.path.basename(img['caminho_local']))
        cont = 0
        for f in os.listdir(PASTA_TEMP):
            if f not in em_uso:
                try: 
                    os.remove(os.path.join(PASTA_TEMP, f))
                    cont += 1
                except: pass
        print(f"[ SISTEMA ] Limpeza concluída: {cont} removidos.")

    if hasattr(app, 'callback_limpar_temp'):
        app.callback_limpar_temp = limpar_seguro
    if hasattr(app, 'callback_resetar_historico'):
        app.callback_resetar_historico = lambda: banco.resetar_dados()
    if hasattr(app, 'callback_reload'):
        app.callback_reload = lambda: [buffer_rodadas.clear(), carregar()]

    def apagar_pacote_fisico(pacote):
        time.sleep(0.5) 
        for img in pacote:
            caminho = img.get('caminho_local')
            if caminho and os.path.exists(caminho):
                try: os.remove(caminho)
                except: pass
        print("[ SISTEMA ] Mídias da última avaliação apagadas do disco.")

    def salvar_e_proxima(v):
        pacote_avaliado = app.pacote_atual.copy() 
        
        if v is not None and app.pacote_atual:
            threading.Thread(
                target=banco.atualizar_pontuacao, 
                args=(app.tags_do_pacote, v, app.url_atual), 
                daemon=True
            ).start()
        
        app.loop_ativo = False
        if app.id_timer: 
            app.after_cancel(app.id_timer)
            app.id_timer = None
        
        app.pacote_atual = []
        
        # Limpa as imagens na tela de forma segura (PC ou Mobile)
        if hasattr(app, 'lbl_imagem_1'):
            app.limpar_label_seguro(app.lbl_imagem_1)
            app.limpar_label_seguro(app.lbl_imagem_2)
        elif hasattr(app, 'lbl_imagem'):
            app.limpar_label_seguro(app.lbl_imagem)
            
        app.update() 
        
        threading.Thread(target=apagar_pacote_fisico, args=(pacote_avaliado,), daemon=True).start()
        carregar()

    app.processar_avaliacao = salvar_e_proxima

    # Aguarda a primeira galeria baixar antes de mostrar a interface
    while not buffer_rodadas: 
        time.sleep(0.1)
    
    carregar()
    app.mainloop()

if __name__ == "__main__":
    iniciar()
