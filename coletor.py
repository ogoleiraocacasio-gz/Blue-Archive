import time
import random
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as c_requests

# ==========================================
# 1. COLETOR DE FOTOS (Pornpics com Cache)
# ==========================================
class ColetorDeImagens:
    def __init__(self, url_base="https://www.pornpics.com/"):
        self.url_base = url_base
        self.sessao = requests.Session()
        self.sessao.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            "Referer": self.url_base
        })
        self.cache_galerias = []
        self.modo_cache = None

    def buscar_dados(self, quantidade_fotos=15, modo="normal"):
        try:
            dominio = ".pornpics.com"
            
            if self.modo_cache != modo:
                self.cache_galerias.clear()
                self.modo_cache = modo

            if modo == "trans":
                self.sessao.cookies.set("ppso", "2", domain=dominio)
            else:
                self.sessao.cookies.set("ppso", "3", domain=dominio)

            if not self.cache_galerias:
                res_home = self.sessao.get(self.url_base, timeout=10)
                sopa_home = BeautifulSoup(res_home.text, 'html.parser')
                
                links_home = [urljoin(self.url_base, a.get('href')) for a in sopa_home.find_all('a', class_='rel-link') if a.get('href')]
                if not links_home: return []
                
                res_cat = self.sessao.get(random.choice(links_home), timeout=10)
                sopa_cat = BeautifulSoup(res_cat.text, 'html.parser')
                
                novos_links = [urljoin(self.url_base, item.find('a').get('href')) for item in sopa_cat.find_all('li', class_='thumbwook') if item.find('a')]
                
                if novos_links:
                    self.cache_galerias.extend(novos_links)

            if not self.cache_galerias:
                return []

            url_final = self.cache_galerias.pop(random.randint(0, len(self.cache_galerias) - 1))

            res_final = self.sessao.get(url_final, timeout=10)
            sopa_final = BeautifulSoup(res_final.text, 'html.parser')
            
            tags_finais = []
            for bloco in sopa_final.find_all('div', class_='gallery-info__item'):
                titulo = bloco.find('span', class_='gallery-info__title')
                if titulo and ("Tags List" in titulo.text or "Models" in titulo.text):
                    prefixo = "model_" if "Models" in titulo.text else ""
                    for a in bloco.find_all('a'):
                        t = a.get('title', '')
                        if t:
                            limpo = t.lower().replace(" pics", "").strip().replace(" ", "_")
                            tags_finais.append(f"{prefixo}{limpo}")

            imagens = []
            container = sopa_final.find('ul', id='tiles')
            if container:
                for i, f in enumerate(container.find_all('li', class_='thumbwook')):
                    img = f.find('img')
                    if img:
                        url_img = img.get('data-src') or img.get('src')
                        imagens.append({
                            "nome": f"pornpics_{random.randint(100,999)}_{i}.jpg",
                            "url": urljoin(url_final, url_img),
                            "tags": tags_finais if tags_finais else ["sem_tag"],
                            "url_origem": url_final
                        })
            
            random.shuffle(imagens)
            return imagens[:quantidade_fotos]
            
        except Exception as e:
            print(f"[ COLETOR FOTOS ] Erro: {e}")
            return []

# ==========================================
# 2. COLETOR DE GIFS (XGroovy Blindado)
# ==========================================
class ColetorXGroovyGifs:
    def __init__(self):
        self.url_base = "https://pt.xgroovy.com/gifs/"
        self.sessao = c_requests.Session(impersonate="chrome120")
        self.sessao.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://pt.xgroovy.com/"
        })

    def buscar_dados(self, quantidade_fotos=15, modo="normal"):
        try:
            dominio = ".xgroovy.com"
            if modo == "trans":
                self.sessao.cookies.set("orientation", "2", domain=dominio)
                self.sessao.cookies.set("site_orientation", "2", domain=dominio)
            else:
                self.sessao.cookies.set("orientation", "3", domain=dominio)
                self.sessao.cookies.set("site_orientation", "3", domain=dominio)

            pagina = random.randint(1, 9400)
            url_busca = f"{self.url_base}{pagina}/"

            res = self.sessao.get(url_busca, timeout=15)
            if res.status_code != 200:
                return []

            sopa = BeautifulSoup(res.text, 'html.parser')
            
            container = sopa.find('div', id='list_videos_custom_gifs_list_items')
            if not container:
                container = sopa 

            imagens = []
            
            for i, img in enumerate(container.find_all('img')):
                src = img.get("data-original") or img.get("data-src") or img.get("src")
                if not src: continue
                    
                url_img = urljoin(url_busca, src)
                
                if url_img.lower().split('?')[0].endswith(".gif"):
                    alt_text = img.get("alt", "xgroovy_gif")
                    tag_limpa = alt_text.lower().replace(" ", "_").replace("-", "_")[:30] 
                    
                    link_pai = img.find_parent('a')
                    url_origem = urljoin(url_busca, link_pai.get("href")) if link_pai and link_pai.get("href") else url_busca
                    
                    imagens.append({
                        "nome": f"xgroovy_gif_{random.randint(10000, 99999)}_{i}.gif",
                        "url": url_img,
                        "tags": [tag_limpa, "xgroovy_gif"],
                        "url_origem": url_origem
                    })

            random.shuffle(imagens)
            return imagens[:quantidade_fotos]

        except Exception as e:
            print(f"[ COLETOR GIFS ] Erro: {e}")
            return []
