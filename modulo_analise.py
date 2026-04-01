import customtkinter as ctk
import json
import os
import sys
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

ctk.set_appearance_mode("dark")

class TelaAnalise(ctk.CTk):
    def __init__(self, modo):
        super().__init__()
        self.title(f"📊 Dashboard de Inteligência - Modo: {modo.upper()}")
        self.geometry("1000x700")
        self.configure(fg_color="#0F111A")
        
        self.modo = modo
        # Define qual banco de dados ler com base no argumento recebido
        self.arquivo_db = "db_trans.json" if modo == "trans" else "db_normal.json"
        
        self.gerar_dashboard()

    def gerar_dashboard(self):
        # 1. Tenta carregar os dados
        dados = {}
        if os.path.exists(self.arquivo_db):
            with open(self.arquivo_db, 'r', encoding='utf-8') as f:
                try:
                    dados = json.load(f)
                except:
                    pass
        
        if not dados:
            ctk.CTkLabel(self, text="Nenhum dado encontrado para gerar o gráfico.", font=("Arial", 20)).pack(expand=True)
            return

        # 2. Filtra tags positivas e ordena para pegar o Top 10
        lista_tags = [{"tag": k, "pontos": v["pontos"]} for k, v in dados.items() if v["pontos"] > 0]
        lista_tags = sorted(lista_tags, key=lambda x: x["pontos"], reverse=True)[:10]

        if not lista_tags:
            ctk.CTkLabel(self, text="Nenhuma tag com pontuação positiva encontrada ainda. Comece a avaliar!", font=("Arial", 20)).pack(expand=True)
            return

        # Limpa os nomes para o gráfico ficar bonito
        tags = [item["tag"].replace("model_", "").replace("_", " ").title() for item in lista_tags]
        pontos = [item["pontos"] for item in lista_tags]

        # 3. Estilo do gráfico (Dark Mode Premium)
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#0F111A')
        ax.set_facecolor('#181B28')

        # Desenha as barras horizontais usando Seaborn
        sns.barplot(x=pontos, y=tags, palette="mako", ax=ax)
        
        ax.set_title(f"TOP 10 Preferências ({self.modo.upper()})", fontsize=18, color='white', pad=20)
        ax.set_xlabel("Pontuação Acumulada", fontsize=12, color='gray')
        ax.set_ylabel("", fontsize=12)
        
        # Remove bordas feias do gráfico
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#34495E')
        ax.spines['left'].set_color('#34495E')
        
        plt.tight_layout()
        
        # 4. Salva o gráfico como imagem temporária e exibe
        caminho_grafico = "temp_grafico.png"
        plt.savefig(caminho_grafico, dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()

        try:
            img = Image.open(caminho_grafico)
            img_ctk = ctk.CTkImage(light_image=img, size=(img.width, img.height))
            lbl_img = ctk.CTkLabel(self, image=img_ctk, text="")
            lbl_img.pack(expand=True, padx=20, pady=20)
        except Exception as e:
            ctk.CTkLabel(self, text=f"Erro ao carregar imagem do gráfico: {e}").pack(expand=True)

if __name__ == "__main__":
    # O main.py envia "normal" ou "trans" de forma invisível quando clica no botão
    modo_selecionado = sys.argv[1] if len(sys.argv) > 1 else "normal"
    app = TelaAnalise(modo_selecionado)
    app.mainloop()
