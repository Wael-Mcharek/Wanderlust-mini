
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote

class Data():
    
    def scraper(self, searchedword):
        # This is an example of the result of the scraper method !
        test = ('sprechen',[
                {'keyword': 'sprechen', 'blocknum': '1', 'wordname': 'sprechen', 'carac': 'verb', 'phrase': ['none', 'etw. spricht für sich selbst'], 'gerdef': ['● german definition here', '● second german definition here'], 'engdef': ['english definition here', 'second english definition here'], 'exampger': ['german example here', 'second german example here'], 'exampeng': ['english example here', 'second english example here']},
                {'keyword': 'sprechen', 'blocknum': '2', 'wordname': 'Sprechen', 'carac': 'noun', 'phrase': [searchedword + ' : This is the searched word !'], 'gerdef': ['● german definition here'], 'engdef': ['english definition here'], 'exampger': ['german example here'], 'exampeng': ['english example here']}
                ])
        
        return test