import customtkinter as ctk
from PIL import Image
import os
import subprocess
import sys
import webbrowser
import json

# Configurações globais de tema para um visual mais premium
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class TelaAvaliador(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔷 BLUE ARCHIVE - Motor de Curadoria e Inteligência")
        
        # Resolução maior e tela cheia amigável
        self.geometry("1400x900")
        self.minsize(1200, 800)
        self.configure(fg_color="#0F111A")
        
        self.update_idletasks() 

        # Variáveis de Estado do main.py
        self.pacote_atual = []
        self.indice_imagem_atual = 0
        self.loop_ativo = False
        self.id_timer = None 
        self.botoes_objetos = []
        self.url_atual = ""
        self.tags_do_pacote = []

        # Callbacks do main.py
        self.callback_limpar_temp = None
        self.callback_resetar_historico = None
        self.callback_reload = None
        self.callback_mudar_modo = None 
        self.callback_mudar_tipo = None
        self.callback_banir_modelo = None

        self.criar_elementos()
        self.configurar_atalhos()

    def criar_elementos(self):
        # --- ESTRUTURA BASE (GRID) ---
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. SIDEBAR (PAINEL LATERAL ESQUERDO)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, fg_color="#181B28", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Título
        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="BLUE ARCHIVE", font=("Arial Black", 24, "bold"), text_color="#3498DB")
        self.lbl_logo.pack(pady=(30, 5), padx=20, anchor="w")
        ctk.CTkLabel(self.sidebar, text="Curadoria Pessoal v2.0", font=("Arial", 12), text_color="gray50").pack(padx=20, anchor="w", pady=(0, 20))

        # --- CAIXA DE CHAVES (MODOS E MÍDIA) ---
        self.frame_modo = ctk.CTkFrame(self.sidebar, fg_color="#21263A", corner_radius=10)
        self.frame_modo.pack(fill="x", padx=20, pady=10)
        
        # 1. Botão de Normal/Trans
        ctk.CTkLabel(self.frame_modo, text="ALVO DA COLEÇÃO", font=("Arial", 11, "bold"), text_color="gray60").pack(pady=(10, 0), anchor="w", padx=15)
        self.var_modo = ctk.StringVar(value="normal")
        self.switch_modo = ctk.CTkSwitch(
            self.frame_modo, text="Modo: Normal", 
            command=self.alternar_modo, variable=self.var_modo, 
            onvalue="trans", offvalue="normal",
            font=("Arial", 14, "bold"), text_color="white",
            fg_color="#34495E", progress_color="#8E44AD", switch_width=45, switch_height=22
        )
        self.switch_modo.pack(fill="x", pady=(15, 5), padx=15)

        # 2. Botão de Fotos/GIFs
        ctk.CTkLabel(self.frame_modo, text="TIPO DE MÍDIA", font=("Arial", 11, "bold"), text_color="gray60").pack(pady=(10, 0), anchor="w", padx=15)
        self.var_tipo_midia = ctk.StringVar(value="fotos")
        self.switch_midia = ctk.CTkSwitch(
            self.frame_modo, text="Modo: Fotos", 
            command=self.alternar_tipo_midia, variable=self.var_tipo_midia, 
            onvalue="gifs", offvalue="fotos",
            font=("Arial", 14, "bold"), text_color="white",
            fg_color="#34495E", progress_color="#27AE60", switch_width=45, switch_height=22
        )
        self.switch_midia.pack(fill="x", pady=(5, 15), padx=15)

        # --- MENU DE MÓDULOS ---
        ctk.CTkLabel(self.sidebar, text="INTELIGÊNCIA & DADOS", font=("Arial", 12, "bold"), text_color="gray50").pack(pady=(20, 10), anchor="w", padx=20)
        
        self.btn_analise = self._criar_botao_menu(self.sidebar, "📊 Dashboard Top 10", "#2980B9", self.abrir_analise)
        self.btn_favs = self._criar_botao_menu(self.sidebar, "⭐ Coleção de Elite", "#D35400", self.abrir_favoritos)
        self.btn_db = self._criar_botao_menu(self.sidebar, "🗄️ Editar Banco (JSON)", "#16A085", self.abrir_editor_db)

        # Controles de Sistema
        self.frame_sistema = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_sistema.pack(side="bottom", fill="x", pady=20)
        
        self._criar_botao_acao(self.frame_sistema, "🔄 Forçar Recarregamento", "#2C3E50", lambda: self.callback_reload() if self.callback_reload else None)
        self._criar_botao_acao(self.frame_sistema, "🗑️ Limpar Pasta Temp", "#7B241C", lambda: self.callback_limpar_temp() if self.callback_limpar_temp else None)

        # ==========================================
        # 2. CONTEÚDO PRINCIPAL (ÁREA DIREITA)
        # ==========================================
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_view.grid_rowconfigure(1, weight=1) 
        self.main_view.grid_columnconfigure(0, weight=1)

        # --- Top Info Bar ---
        self.top_bar = ctk.CTkFrame(self.main_view, fg_color="#181B28", height=50, corner_radius=10)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.lbl_fonte = ctk.CTkLabel(self.top_bar, text="Fonte: Aguardando conexão...", font=("Arial", 12), text_color="#5DADE2")
        self.lbl_fonte.pack(side="left", padx=20, pady=10)
        
        self.btn_link = ctk.CTkButton(self.top_bar, text="🔗 Abrir no Navegador (L)", width=150, fg_color="#21263A", hover_color="#2C3E50", command=self.abrir_link_atual)
        self.btn_link.pack(side="right", padx=10, pady=10)

        # --- Área de Imagens ---
        self.frame_imagens = ctk.CTkFrame(self.main_view, fg_color="#181B28", corner_radius=15)
        self.frame_imagens.grid(row=1, column=0, sticky="nsew")
        self.frame_imagens.columnconfigure((0, 1), weight=1)
        self.frame_imagens.rowconfigure(0, weight=1)

        self.lbl_imagem_1 = ctk.CTkLabel(self.frame_imagens, text="[ Conectando ao Servidor... ]", font=("Arial", 18), fg_color="#0F111A", corner_radius=10)
        self.lbl_imagem_1.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        self.lbl_imagem_2 = ctk.CTkLabel(self.frame_imagens, text="[ Preparando Buffer... ]", font=("Arial", 18), fg_color="#0F111A", corner_radius=10)
        self.lbl_imagem_2.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        # --- Painel de Tags ---
        self.frame_tags = ctk.CTkFrame(self.main_view, fg_color="#21263A", corner_radius=10)
        self.frame_tags.grid(row=2, column=0, sticky="ew", pady=15)
        
        self.lbl_tags = ctk.CTkLabel(self.frame_tags, text="Tags/Models detectadas aparecerão aqui...", font=("Arial", 14, "italic"), text_color="#AAB7B8", wraplength=1000)
        self.lbl_tags.pack(pady=12, padx=20)

        # --- Barra de Votação Inferior ---
        self.frame_votacao = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.frame_votacao.grid(row=3, column=0, sticky="ew")

        self.btn_pular = ctk.CTkButton(self.frame_votacao, text="⏭️ Skip (Espaço)", width=130, height=50, font=("Arial", 14, "bold"), fg_color="#34495E", command=lambda: self.processar_avaliacao(None))
        self.btn_pular.pack(side="left")

        self.btn_banir = ctk.CTkButton(self.frame_votacao, text="🚫 Banir (B)", width=130, height=50, font=("Arial", 14, "bold"), fg_color="#8E44AD", hover_color="#732D91", command=self.banir_modelo_atual)
        self.btn_banir.pack(side="right")

        self.frame_notas = ctk.CTkFrame(self.frame_votacao, fg_color="transparent")
        self.frame_notas.pack(side="top", anchor="center")

        self.config_botoes = [
            ("1. 🤢 Repugna", -5, "#641E16", "#922B21"),
            ("2. 🤮 M. Ruim", -3, "#922B21", "#C0392B"),
            ("3. 👎 Ruim", -1, "#A04000", "#D35400"),
            ("4. 😐 Normal", 0, "#4D5656", "#7F8C8D"),
            ("5. 🙂 Gostei", 2, "#1A5276", "#2980B9"),
            ("6. 😍 Amei", 4, "#145A32", "#27AE60"),
            ("7. 💦 Fav!", 5, "#B7950B", "#F1C40F")
        ]

        for index, (texto, valor, cor_fundo, cor_hover) in enumerate(self.config_botoes):
            btn = ctk.CTkButton(
                self.frame_notas, text=texto, font=("Arial", 13, "bold"),
                fg_color=cor_fundo, hover_color=cor_hover, 
                width=110, height=50, corner_radius=10,
                command=lambda v=valor: self.processar_avaliacao(v)
            )
            btn.pack(side="left", padx=5)
            self.botoes_objetos.append(btn)

    # --- FUNÇÕES DE INTERFACE AUXILIARES ---
    def _criar_botao_menu(self, parent, texto, cor, comando):
        btn = ctk.CTkButton(parent, text=texto, font=("Arial", 14, "bold"), fg_color="transparent", 
                            text_color="gray80", hover_color="#21263A", anchor="w", height=45, command=comando)
        btn.pack(fill="x", padx=10, pady=2)
        linha = ctk.CTkFrame(btn, width=4, fg_color=cor, corner_radius=2)
        linha.place(relx=0, rely=0.1, relheight=0.8)
        return btn

    def _criar_botao_acao(self, parent, texto, cor, comando):
        ctk.CTkButton(parent, text=texto, font=("Arial", 12, "bold"), fg_color=cor, height=35, command=comando).pack(fill="x", padx=20, pady=5)

    # --- LÓGICAS DA INTERFACE ---
    def alternar_modo(self):
        modo = self.var_modo.get()
        if modo == "trans":
            self.switch_modo.configure(text="Modo: Trans")
            self.lbl_logo.configure(text_color="#8E44AD")
        else:
            self.switch_modo.configure(text="Modo: Normal")
            self.lbl_logo.configure(text_color="#3498DB")
            
        if hasattr(self, 'callback_mudar_modo') and self.callback_mudar_modo:
            self.callback_mudar_modo(modo)

    def abrir_link_atual(self):
        if self.url_atual: webbrowser.open(self.url_atual)

    def banir_modelo_atual(self):
        if not hasattr(self, 'tags_do_pacote') or not self.tags_do_pacote: return
        modelos_na_foto = [t for t in self.tags_do_pacote if t.startswith("model_")]
        
        if not modelos_na_foto: 
            return 

        janela_ban = ctk.CTkToplevel(self)
        janela_ban.title("🚫 Selecionar Alvo")
        janela_ban.geometry("350x400")
        janela_ban.attributes("-topmost", True)
        janela_ban.grab_set() 
        
        ctk.CTkLabel(janela_ban, text="Quais modelos deseja banir?", font=("Arial", 16, "bold")).pack(pady=(20, 10))
        vars_check = {}
        for m in modelos_na_foto:
            nome = m.replace("model_", "").replace("_", " ").title()
            var = ctk.BooleanVar(value=False)
            vars_check[m] = var
            ctk.CTkCheckBox(janela_ban, text=nome, variable=var, font=("Arial", 14)).pack(pady=8, padx=30, anchor="w")

        def confirmar_ban():
            para_banir = [m for m, v in vars_check.items() if v.get()]
            for m in para_banir: 
                self._efetivar_ban(m)
            janela_ban.destroy()
            
            if para_banir: 
                self.processar_avaliacao(None) 

        ctk.CTkButton(janela_ban, text="💀 Confirmar Banimento", fg_color="#8E44AD", hover_color="#732D91", height=40, command=confirmar_ban).pack(pady=20, side="bottom")

    def alternar_tipo_midia(self):
        tipo = self.var_tipo_midia.get()
        if tipo == "gifs":
            self.switch_midia.configure(text="Modo: GIFs")
        else:
            self.switch_midia.configure(text="Modo: Fotos")
            
        if hasattr(self, 'callback_mudar_tipo') and self.callback_mudar_tipo:
            self.callback_mudar_tipo(tipo)

    def _efetivar_ban(self, modelo_tag):
        if hasattr(self, 'callback_banir_modelo') and self.callback_banir_modelo:
            self.callback_banir_modelo(modelo_tag)
        else:
            print("[ ERRO ] Falha na conexão! O main.py não recebeu o comando de banir.")

    def abrir_modulo(self, nome_arquivo):
        diretorio = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(diretorio, nome_arquivo)
        modo_atual = self.var_modo.get()
        if os.path.exists(script): subprocess.Popen([sys.executable, script, modo_atual])

    def abrir_analise(self): self.abrir_modulo("modulo_analise.py")
    def abrir_favoritos(self): self.abrir_modulo("modulo_favoritos.py")
    def abrir_editor_db(self): self.abrir_modulo("modulo_banco.py")

    def configurar_atalhos(self):
        for i in range(7):
            self.bind(str(i + 1), lambda e, v=self.config_botoes[i][1]: self.processar_avaliacao(v))
        self.bind("<space>", lambda e: self.processar_avaliacao(None))
        self.bind("b", lambda e: self.banir_modelo_atual())
        self.bind("l", lambda e: self.abrir_link_atual())

    def iniciar_loop_imagens(self):
        if not self.pacote_atual: return
        self.loop_ativo = True
        self.trocar_imagem_carrossel()

    def renderizar_foto_no_label(self, label, img_data):
        path = img_data.get('caminho_local', '')
        
        label.current_media_path = path 

        if os.path.exists(path):
            try:
                if path.lower().endswith(".gif"):
                    self.reproduzir_gif(label, path)
                    return

                with Image.open(path) as img_temp:
                    img = img_temp.copy()
                self.update_idletasks()
                w, h = label.winfo_width(), label.winfo_height()
                if w < 10: w, h = 480, 500
                ratio = min(w / img.size[0], h / img.size[1])
                new_size = (max(1, int(img.size[0] * ratio)), max(1, int(img.size[1] * ratio)))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=new_size)
                label.configure(image=ctk_img, text="")
                label._image = ctk_img
            except Exception as e:
                self.limpar_label_seguro(label, f"[ Erro: {e} ]")
        else:
            self.limpar_label_seguro(label, "[ Arquivo já apagado ]")

    def reproduzir_gif(self, label, img_path):
        try:
            gif = Image.open(img_path)
            w, h = label.winfo_width(), label.winfo_height()
            if w < 10: w, h = 480, 500
            
            duracao = gif.info.get('duration', 80) or 80
            total_frames = getattr(gif, "n_frames", 1)

            def proximo_quadro(idx):
                if hasattr(label, 'current_media_path') and label.current_media_path == img_path:
                    try:
                        gif.seek(idx)
                        frame_rgba = gif.copy().convert("RGBA")
                        
                        ratio = min(w / frame_rgba.size[0], h / frame_rgba.size[1])
                        new_size = (max(1, int(frame_rgba.size[0] * ratio)), max(1, int(frame_rgba.size[1] * ratio)))
                        
                        img_ctk = ctk.CTkImage(light_image=frame_rgba, size=new_size)
                        label.configure(image=img_ctk, text="")
                        label._image = img_ctk
                        
                        proximo_idx = (idx + 1) % total_frames
                        label.after(duracao, proximo_quadro, proximo_idx)
                    except Exception:
                        pass 

            proximo_quadro(0) 
        except Exception as e:
            self.limpar_label_seguro(label, f"[ Erro ao abrir GIF: {e} ]")

    def limpar_label_seguro(self, label, texto_aviso="[ Trocando... ]"):
        try:
            img_vazia = ctk.CTkImage(Image.new("RGBA", (1, 1), (0,0,0,0)), size=(1, 1))
            label.configure(image=img_vazia, text=texto_aviso)
            label._image = img_vazia
        except: pass

    def trocar_imagem_carrossel(self):
        if not self.loop_ativo or len(self.pacote_atual) < 2: return
        img1 = self.pacote_atual[self.indice_imagem_atual]
        img2 = self.pacote_atual[(self.indice_imagem_atual + 1) % len(self.pacote_atual)]
        self.renderizar_foto_no_label(self.lbl_imagem_1, img1)
        self.renderizar_foto_no_label(self.lbl_imagem_2, img2)
        self.indice_imagem_atual = (self.indice_imagem_atual + 2) % len(self.pacote_atual)
        self.id_timer = self.after(1300, self.trocar_imagem_carrossel)

    def processar_avaliacao(self, pontuacao):
        pass
