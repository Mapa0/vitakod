import requests
from bs4 import BeautifulSoup

class WebScrapper:
    def web_scrap_sesau(self):
        url = "https://www.campogrande.ms.gov.br/sesau/unidades-basicas-de-saude/"
        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser')
        tables = soup.find('table')
        table = tables.find_all('tbody')[3]
        ubs = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if(cols !=  []):
                unidade = None
                regiao = None

                for index, col in enumerate(cols):
                    if(col.h4 != None):
                        if(index % 2 == 0):
                            regiao = col.h4.text.lower()
                        else:
                            unidade = col.h4.text
                ubs.append({
                    "unidade_de_saude": unidade,
                    "regiao": regiao
                })
        return ubs
