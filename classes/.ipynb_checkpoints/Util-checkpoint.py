import requests
import json
from bs4 import BeautifulSoup
from enum import Enum
from langdetect import detect, DetectorFactory

from .Escopo import Escopo

# Função que detecta o país de origem da revista (periódico) a partir...
# do ISSN. A Funciona com traço (-) e sem traço.
#
# Exemplo de uso: 
#    chamada: get_country_by_issn(1984-2902) ou 
#             get_country_by_issn(19842902)
# 
#    retorno Brazil
#

def issn2country(issn: str) -> str:
    issn_portal_url = "https://portal.issn.org/resource/ISSN/"
    url = issn_portal_url + issn
    res = requests.post(url)
    
    soup = BeautifulSoup(res.content, "html.parser")
    tag = soup.find("script", type="application/ld+json")
    data = json.loads(tag.string)
    
    return str(data['publication']['location']['name'])

    
def nat_or_inter(country: str) -> Escopo:
    return Escopo.NACIONAL if country.lower() in ["brazil", "brasil"] else Escopo.INTERNACIONAL

# ========================
def detect_scope(title):
    l_title = title.lower()
    
    nat_hints = ["nacional", "brasileiro", "brasileira", "brasil", "brazil", "brazilian", "brazilians"]
    inter_hints = ["international", "internacional", "european"]
    
    for h in nat_hints:
        if h in l_title:
            return Escopo.NACIONAL
    
    for h in inter_hints:
        if h in l_title:
            return Escopo.INTERNACIONAL
    # af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
    # hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
    # pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
    DetectorFactory.seed = 0
    lang = detect(l_title)
    return Escopo.NACIONAL if lang == 'pt' else Escopo.INTERNACIONAL