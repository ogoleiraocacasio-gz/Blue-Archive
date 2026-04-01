import customtkinter as ctk
import json
import os
import sys
import webbrowser

ctk.set_appearance_mode("dark")

class TelaFavoritos(ctk.CTk):
    def __init__(self, modo):
        super().__init__()
        self.title(f"⭐ Coleção de Elite - Modo: {modo.upper()}")
        self.geometry("900x700")
        self.configure(fg_color="#0F111A")
        
        self.modo = modo
        # Descobre qual arquivo abrir baseado no modo selecionado na interface principal
        self.arquivo_db = "db_trans.json" if modo == "trans" else "db_normal.json"
        
        self.criar_elementos()
        self.carregar_favoritos()

    def criar_elementos(self):
        # Cabeçalho
        self.frame_top = ctk.CTkFrame(self, fg_color="#181B28", corner_radius=10)
        self.frame_top.pack(fill="x", padx=20, pady=20)
        
        lbl_titulo = ctk.CTkLabel(self.frame_top, text="⭐ Galeria VIP (Top Models e Tags)", font=("Arial", 20, "bold"), text_color="#F1C40F")
        lbl_titulo.pack(pady=15)

        # Área rolável para a lista (Scrollbar)
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def carregar_favoritos(self):
        dados = {}
        if os.path.exists(self.arquivo_db):
            with open(self.arquivo_db, 'r', encoding='utf-8') as f:
                try: 
                    dados = json.load(f)
                except: pass
        
        if not dados:
            ctk.CTkLabel(self.scroll_area, text="Nenhum dado encontrado no banco.", font=("Arial", 16)).pack(pady=20)
            return

        # Filtra e ordena as tags com pontuação alta (Acima de 5 pontos)
        elites = [{"tag": k, "dados": v} for k, v in dados.items() if v.get("pontos", 0) >= 5]
        elites = sorted(elites, key=lambda x: x["dados"]["pontos"], reverse=True)

        if not elites:
            ctk.CTkLabel(self.scroll_area, text="Você ainda não tem favoritos. Dê notas altas para popular esta lista!", font=("Arial", 16)).pack(pady=20)
            return

        # Cria os blocos visuais (Cards) para cada tag/modelo VIP
        for item in elites:
            tag_nome = item["tag"].replace("model_", "").replace("_", " ").title()
            pontos = item["dados"]["pontos"]
            urls = item["dados"].get("urls_exemplo", [])

            card = ctk.CTkFrame(self.scroll_area, fg_color="#21263A", corner_radius=10)
            card.pack(fill="x", pady=10)

            # Info da Tag (Lado Esquerdo)
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=20, pady=15, fill="y")
            
            ctk.CTkLabel(info_frame, text=tag_nome, font=("Arial", 18, "bold"), text_color="#3498DB").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Pontuação: {pontos} pts", font=("Arial", 14), text_color="#27AE60").pack(anchor="w")

            # Links de Exemplo (Lado Direito)
            links_frame = ctk.CTkFrame(card, fg_color="transparent")
            links_frame.pack(side="right", padx=20, pady=15)
            
            if urls:
                ctk.CTkLabel(links_frame, text="Links de Origem:", font=("Arial", 12), text_color="gray").pack(anchor="e", pady=(0, 5))
                for i, url in enumerate(urls):
                    # O comando lambda prende a URL no botão para abrir no navegador quando clicado
                    btn = ctk.CTkButton(links_frame, text=f"🔗 Acessar Fonte {i+1}", width=120, height=28, fg_color="#34495E", hover_color="#2C3E50", 
                                        command=lambda u=url: webbrowser.open(u))
                    btn.pack(pady=2, anchor="e")
            else:
                ctk.CTkLabel(links_frame, text="Nenhum link salvo.", font=("Arial", 12, "italic"), text_color="gray").pack(anchor="e")

if __name__ == "__main__":
    modo_selecionado = sys.argv[1] if len(sys.argv) > 1 else "normal"
    app = TelaFavoritos(modo_selecionado)
    app.mainloop()
