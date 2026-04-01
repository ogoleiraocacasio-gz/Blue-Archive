import json
import os

class GerenciadorDados:
    def __init__(self):
        self.arquivo_normal = "db_normal.json"
        self.arquivo_trans = "db_trans.json"
        self.modo_atual = "normal"
        self.arquivo_atual = self.arquivo_normal
        self.dados = self.carregar_dados()

    def mudar_modo(self, novo_modo):
        self.modo_atual = novo_modo
        self.arquivo_atual = self.arquivo_trans if novo_modo == "trans" else self.arquivo_normal
        self.dados = self.carregar_dados()

    def carregar_dados(self):
        if os.path.exists(self.arquivo_atual):
            try:
                with open(self.arquivo_atual, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def salvar_dados(self):
        with open(self.arquivo_atual, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

    def atualizar_pontuacao(self, tags, valor, url_origem=""):
        if not tags: return
        
        for tag in tags:
            if tag not in self.dados:
                self.dados[tag] = {"pontos": 0, "ocorrencias": 0, "urls_exemplo": []}
            
            self.dados[tag]["pontos"] += valor
            self.dados[tag]["ocorrencias"] += 1
            
            # Guarda até 5 URLs de exemplo para você poder revisitar
            if url_origem and url_origem not in self.dados[tag]["urls_exemplo"]:
                self.dados[tag]["urls_exemplo"].append(url_origem)
                if len(self.dados[tag]["urls_exemplo"]) > 5:
                    self.dados[tag]["urls_exemplo"].pop(0)
                    
        self.salvar_dados()

    def banir_tag(self, tag):
        if tag not in self.dados:
            self.dados[tag] = {"pontos": 0, "ocorrencias": 0, "urls_exemplo": []}
            
        # Aplica uma nota absurdamente negativa para banimento
        self.dados[tag]["pontos"] = -9999
        self.salvar_dados()
        print(f"[ BANIMENTO ] Tag/Modelo '{tag}' foi banida do modo {self.modo_atual.upper()}!")

    def resetar_dados(self):
        self.dados = {}
        self.salvar_dados()
        print(f"[ SISTEMA ] Banco de dados {self.modo_atual.upper()} resetado com sucesso!")
