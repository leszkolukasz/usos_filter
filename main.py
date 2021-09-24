from bs4 import BeautifulSoup
import pprint
from collections import defaultdict
import requests
import re

class UsosFilter:
    
    def __init__(self, url, expired=False, *, verbose=False):
        self._url = url
        self._expired = expired
        self.conditions = []
        self._verbose = verbose

        self.add_condition(lambda data: ((fs := data['Liczba miejsc (zarejestrowani/limit)'].split('/'))[0] == fs[1]) == self._expired)

    def add_condition(self, condition):
        self.conditions.append(condition)

    def _get_html(self, url):
        try:
            html = requests.get(url).text
        except Exception:
            return None
        return html

    def filter(self, url=None):
        if url is None:
            url = self._url
        html = self._get_html(url)
        if(url is None):
            return

        if self._verbose:
            print(f'Searching: {url}')

        parsed = BeautifulSoup(html, 'html.parser')
        if (links := parsed.select('.odd_row a')) is not None:
            self._filter_list(url, links)
        if (links := parsed.select('.even_row a')) is not None:
            self._filter_list(url, links)
        if (links := parsed.find_all('script')) is not None:
            self._filter_groups(url, links)
        

    def _filter_list(self, url, links):
        for link in links:
            self.filter('https://rejestracja.usos.uw.edu.pl/' + link['href'])

    def _filter_groups(self, url, links):
        for link in links:
            for code in re.findall(r'(\d+),\s*\"\",\s*(\d+)', link.text):
                self._filter_group(f'{url}&course_id={code[0]}&gr_no={code[1]}')

    def _filter_group(self, url):
        html = self._get_html(url)
        if(url is None):
            return

        parsed = BeautifulSoup(html, 'html.parser').select('table[class="wrnav stretch"]')[0]
        subject_data = defaultdict(str)
        for table_row in parsed.children:
            try:
                name = table_row.contents[1].text
                data = table_row.contents[3].text
            except Exception:
                pass
            else:
                subject_data[name] = data
        subject_data['url'] = url
        
        for condition in self.conditions:
            try:
                if not condition(subject_data):
                    return
            except Exception:
                pass
        self._print(subject_data)

    def _print(self, group_info):
        if 'Aktualna tura' in group_info:
            del group_info['Aktualna tura']
        print('-'*75)
        pprint.pprint(dict(group_info))
        print('-'*75)


test = UsosFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN')
test.add_condition(lambda x: int(x['Punkty ECTS']) >= 4)
test.filter()