class Producao:
    
    def __init__(self, titulo, doi, autores, local, tipo, ano, escopo, issn = None):
        self.titulo = titulo      # from orcid
        self.doi = doi            # from orcid
        self.autores = autores    # from crossref
        self.local = local        # from orcid (or from from crossref if not present in orcid)
        self.tipo = tipo          # from orcid
        self.ano = ano            # from orcid (or from from crossref if not present in orcid)
        self.escopo = escopo      # from portal issn if journal with issn, otherwise from lang detection algorithm
        self.issn = issn          # from crossref