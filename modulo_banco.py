import customtkinter as ctk
import json
import os
import sys

ctk.set_appearance_mode("dark")

class TelaBanco(ctk.CTk):
    def __init__(self, modo):
        super().__init__()
        self.title(f"🗄️ Editor do Banco de Dados - Modo: {modo.upper()}")
        self.geometry("900x700")
        self.configure(fg_color="#0F111A")
        
        self.modo = modo
        # Descobre qual arquivo abrir baseado no que o main.py mandou
        self.arquivo_db = "db_trans.json" if modo == "trans" else "db_normal.json"
        
        self.criar_elementos()
        self.carregar_json()

    def criar_elementos(self):
        # Barra Superior
        self.frame_top = ctk.CTkFrame(self, fg_color="#181B28", corner_radius=10)
        self.frame_top.pack(fill="x", padx=20, pady=20)
        
        lbl_titulo = ctk.CTkLabel(self.frame_top, text=f"Editando Diretamente: {self.arquivo_db}", font=("Arial", 16, "bold"), text_color="#3498DB")
        lbl_titulo.pack(side="left", padx=20, pady=15)
        
        btn_salvar = ctk.CTkButton(self.frame_top, text="💾 Salvar Alterações", fg_color="#27AE60", hover_color="#1E8449", font=("Arial", 14, "bold"), command=self.salvar_json)
        btn_salvar.pack(side="right", padx=20, pady=15)

        # Caixa de Texto estilo Código (Onde o JSON vai aparecer)
        self.caixa_texto = ctk.CTkTextbox(self, font=("Courier New", 14), fg_color="#21263A", text_color="#AAB7B8", wrap="none")
        self.caixa_texto.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Avisos do Sistema
        self.lbl_status = ctk.CTkLabel(self, text="⚠️ Cuidado ao editar! Se apagar uma vírgula ou chave '{ }' sem querer, o arquivo pode quebrar.", font=("Arial", 12), text_color="#F1C40F")
        self.lbl_status.pack(pady=(0, 10))

    def carregar_json(self):
        if os.path.exists(self.arquivo_db):
            with open(self.arquivo_db, 'r', encoding='utf-8') as f:
                try:
                    dados = json.load(f)
                    # Converte o dicionário do Python de volta para texto JSON bonitinho
                    texto_json = json.dumps(dados, indent=4, ensure_ascii=False)
                    self.caixa_texto.insert("0.0", texto_json)
                except:
                    self.caixa_texto.insert("0.0", "{\n  // Erro crítico: O arquivo JSON está corrompido.\n}")
        else:
            self.caixa_texto.insert("0.0", "{\n  // O arquivo ainda não existe. Faça uma avaliação primeiro!\n}")

    def salvar_json(self):
        texto_editado = self.caixa_texto.get("0.0", "end").strip()
        try:
            # Tenta ler o texto que você digitou. Se faltar vírgula, ele cai no "except" e não deixa salvar!
            dados = json.loads(texto_editado)
            
            with open(self.arquivo_db, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
                
            self.lbl_status.configure(text="✅ Salvo com sucesso! O Cérebro principal já está usando os novos dados.", text_color="#27AE60")
            
            # Depois de 3 segundos, volta a mensagem de aviso normal
            self.after(3000, lambda: self.lbl_status.configure(text="⚠️ Cuidado ao editar! Se apagar uma vírgula ou chave '{ }' sem querer, o arquivo pode quebrar.", text_color="#F1C40F"))
        except Exception as e:
            # Se você errar a formatação, ele avisa onde está o erro e impede a quebra do sistema
            self.lbl_status.configure(text=f"❌ Erro de Sintaxe: {e}", text_color="#E74C3C")

if __name__ == "__main__":
    modo_selecionado = sys.argv[1] if len(sys.argv) > 1 else "normal"
    app = TelaBanco(modo_selecionado)
    app.mainloop()
