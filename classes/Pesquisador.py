import requests
from .Producao import Producao
import classes.Util as util

from simplejson import JSONDecodeError
from ipywidgets import IntProgress
from IPython.display import display

class Pesquisador:
    
    def __init__(self, orcid_id, verbose = False):
        self.verbose = verbose
        self.data = self.g_data_from_orcid(orcid_id, verbose)
        
        self.id = orcid_id
        self.nome = self.g_nome(self.data)
        self.pais = self.g_pais(self.data)
        self.palavras_chave = self.g_palavras_chave(self.data)
        # self.links_externos = self.g_links_externos(self.data)
        
        self.producoes = self.g_producoes(self.data, verbose)
        # self.revisoes = self.g_revisoes(self.data)
        
    def g_data_from_orcid(self, orcid_id, verbose = False):
        if verbose: print(f'Download do ORCID ID: {orcid_id}', end = " ")
        
        url = f"https://pub.orcid.org/v3.0/{orcid_id}"

        headers = {
            "Accept": "application/json"
        }

        response = requests.get(url, headers = headers)

        if verbose: print(f'(Concluído)')
        return response.json() if response.status_code == 200 else response.status_code
    
    def g_nome(self, data):
        return data['person']['name']['given-names']['value'] + " " + data['person']['name']['family-name']['value']
    
    def g_pais(self, data):
        if len(data['person']['addresses']['address']) != 0:
            return data['person']['addresses']['address'][0]['country']['value']
        else:
            return ''
    
    def g_palavras_chave(self, data):
        kws = []
        for keyword in data['person']['keywords']['keyword']:
            kws.append(keyword['content'])
        return kws
    
    def g_producoes(self, data, verbose = False):
        prods = data['activities-summary']['works']['group']
        
        producoes = []
        n_prods = len(prods)
        
        if verbose:
            f = IntProgress(min = 0, max = len(prods), description = 'Progresso:')
            display(f)

        for p in prods:
            titulo = p['work-summary'][0]['title']['title']['value']

            if len(p['work-summary'][0]['external-ids']['external-id']) != 0:
                doi = p['work-summary'][0]['external-ids']['external-id'][0]['external-id-normalized']['value']
            else:
                doi = ''

            local = '' if p['work-summary'][0]['journal-title'] == None else p['work-summary'][0]['journal-title']['value']
            tipo = p['work-summary'][0]['type']
            
            pd_dict = p['work-summary'][0]['publication-date']
            if pd_dict:
                ano = p['work-summary'][0]['publication-date']['year']['value']
            else:
                ano = ''

            url = f"https://api.crossref.org/works/{doi}"

            try:
                cdata = requests.get(url).json()
                authors = cdata['message'].get('author', [])
                autores = []
                for author in authors:
                    autores.append(f"{author.get('given', '')} {author.get('family', '')}")

                issn = cdata['message'].get('ISSN', '')
                issn = '' if len(issn) == 0 else issn[0]

                if str(local) == '':
                    event_dict = cdata['message'].get('event', '')
                    if event_dict:
                        local = event_dict['name']
                        
                if str(ano) in ['0', '']:
                    ano = str(cdata['message']['published']['date-parts'][0][0])
                    
            except JSONDecodeError:
                autores = []
                issn = ''
            
            if str(local) != '':
                escopo = util.nat_or_inter(util.issn2country(issn)) if issn != '' else util.detect_scope(local)
            else:
                escopo = ''
            
            producoes.append(Producao(titulo, doi, autores, local, tipo, ano, escopo, issn))
            
            if verbose: f.value += 1
            
        return producoes
    