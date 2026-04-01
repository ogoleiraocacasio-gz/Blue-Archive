import customtkinter as ctk
from PIL import Image
import os
import json

ctk.set_appearance_mode("dark")

class TelaMobile(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blue Archive - Mobile")
        
        # Resolução de celular (Em pé)
        self.geometry("450x800")
        self.configure(fg_color="#0F111A")

        self.pacote_atual = []
        self.indice_imagem_atual = 0
        self.loop_ativo = False
        self.id_timer = None 
        self.url_atual = ""
        self.tags_do_pacote = []

        # Variáveis para calcular o "Arrastar" (Swipe)
        self.start_x = 0
        self.start_y = 0

        self.criar_elementos()
        self.configurar_gestos()

    def criar_elementos(self):
        # A tela inteira será ocupada por essa label de imagem
        self.lbl_imagem = ctk.CTkLabel(self, text="[ Carregando... ]", font=("Arial", 20), fg_color="#181B28")
        self.lbl_imagem.pack(fill="both", expand=True, padx=10, pady=10)

        # Barra inferior flutuante para mostrar as tags e a fonte
        self.frame_info = ctk.CTkFrame(self, fg_color="#21263A", corner_radius=15)
        self.frame_info.place(relx=0.5, rely=0.95, anchor="s", relwidth=0.9)

        self.lbl_tags = ctk.CTkLabel(self.frame_info, text="Tags aparecerão aqui...", font=("Arial", 12, "bold"), text_color="#AAB7B8", wraplength=350)
        self.lbl_tags.pack(pady=10, padx=10)

    def configurar_gestos(self):
        # Captura onde o dedo/mouse clicou e onde soltou
        self.lbl_imagem.bind("<Button-1>", self.ao_pressionar)
        self.lbl_imagem.bind("<ButtonRelease-1>", self.ao_soltar)
        
        # Captura o toque duplo rápido (Fav)
        self.lbl_imagem.bind("<Double-Button-1>", lambda event: self.processar_avaliacao(5))

    def ao_pressionar(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def ao_soltar(self, event):
        # Calcula a distância que o dedo percorreu
        distancia_x = event.x - self.start_x
        distancia_y = event.y - self.start_y
        
        limite = 60 # Quantidade mínima de pixels que precisa arrastar para contar como swipe

        # Verifica se arrastou mais na horizontal ou na vertical
        if abs(distancia_x) > abs(distancia_y):
            if distancia_x > limite:
                print("Swipe Direita -> Gostei (+2)")
                self.processar_avaliacao(2)
            elif distancia_x < -limite:
                print("Swipe Esquerda <- Reprovado (-1)")
                self.processar_avaliacao(-1)
        else:
            if distancia_y < -limite:
                print("Swipe Cima ^ Skip")
                self.processar_avaliacao(None)
            elif distancia_y > limite:
                print("Swipe Baixo v Neutro (0)")
                self.processar_avaliacao(0)

    # --- MOTOR DE RENDERIZAÇÃO E ANIMAÇÃO ---
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
                if w < 10: w, h = 400, 700
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
            if w < 10: w, h = 400, 700
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
            self.limpar_label_seguro(label, f"[ Erro GIF: {e} ]")

    def limpar_label_seguro(self, label, texto_aviso="[ Trocando... ]"):
        try:
            img_vazia = ctk.CTkImage(Image.new("RGBA", (1, 1), (0,0,0,0)), size=(1, 1))
            label.configure(image=img_vazia, text=texto_aviso)
            label._image = img_vazia
        except: pass

    def iniciar_loop_imagens(self):
        if not self.pacote_atual: return
        self.loop_ativo = True
        self.trocar_imagem_carrossel()

    def trocar_imagem_carrossel(self):
        if not self.loop_ativo or len(self.pacote_atual) < 1: return
        
        # Como no celular só tem 1 tela, ele mostra só a imagem 1
        img1 = self.pacote_atual[self.indice_imagem_atual]
        self.renderizar_foto_no_label(self.lbl_imagem, img1)
        
        self.indice_imagem_atual = (self.indice_imagem_atual + 1) % len(self.pacote_atual)
        self.id_timer = self.after(1300, self.trocar_imagem_carrossel)

    def processar_avaliacao(self, pontuacao):
        # O main.py vai sobrescrever isso aqui, igual faz na versão de PC
        pass
