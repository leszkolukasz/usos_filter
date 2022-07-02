""" This file defines easy to use class that filter USOS database to your own liking """

import re
import requests
import datetime
from datetime import time
import logging

from bs4 import BeautifulSoup
from rich import print

logging.basicConfig(filename='exceptions.log')

"""
This class filters groups from USOS databse according to custom rules

Parameters
----------
url: str
    url of the list to filter from
expired: bool
    True if you want to show groups with all seats taken, False otherwise (default: False)
verbose: bool
    True if you want to see currently search url, False othrwise (default: False)

Examples
--------
test = USOSFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN')
test.add_condition(lambda x: float(x['ects']) >= 4)
test.show()
"""
class USOSFilter:
    
    def __init__(self, url, expired=False, *, verbose=False):
        self._url = url
        self._expired = expired
        self.conditions = []
        self._verbose = verbose
        self._total = 0

        # Filter groups with no seats left
        self.add_condition(lambda data: (data['seats'][0] == data['seats'][1]) == self._expired)

    # Use this if you want to add custom condition
    def add_condition(self, condition):
        self.conditions.append(condition)

    def _get_html(self, url):
        try:
            html = requests.get(url).text
        except Exception:
            return None
        return html

    # Use this if you want to show filtered groups
    def show(self):
        self._total = 0
        self._filter(self._url)
        print('*'*75)
        print(f'Found total of {self._total} results')
    
    def _filter(self, url=None):
        html = self._get_html(url)
        if(html is None):
            return

        if self._verbose:
            print(f'Searching: {url}')

        parsed = BeautifulSoup(html, 'html.parser')
        if (links := parsed.select('.odd_row a')) is not None:
            self._filter_list(url, links[::2])
        if (links := parsed.select('.even_row a')) is not None:
            self._filter_list(url, links[::2])
        if (links := parsed.find_all('script')) is not None:
            self._filter_groups(url, links)
        
    def _filter_list(self, url, links):
        for link in links:
            self._filter('https://rejestracja.usos.uw.edu.pl/' + link['href'])

    def _filter_groups(self, url, links):
        for link in links:
            for code in re.findall(r'(\d+),\s*\"\",\s*(\d+)', link.text):
                self._filter_group(f'{url}&course_id={code[0]}&gr_no={code[1]}')

    def _filter_group(self, url):
        html = self._get_html(url)
        if(html is None):
            return

        parsed = BeautifulSoup(html, 'html.parser').select('table[class="wrnav stretch"]')[0]
        group_info = dict()
        for table_row in parsed.children:
            try:
                name = table_row.contents[1].text
                data = table_row.contents[3].text
            except Exception:
                pass
            else:
                group_info[name] = data
        group_info['url'] = url

        group_info = self._clean_data(group_info)
        
        for condition in self.conditions:
            try:
                if not condition(group_info):
                    return
            except Exception as e:
                logging.warning(e)
        self._print(group_info)

    def _clean_data(self, group_info):
        if 'Aktualna tura' in group_info:
            del group_info['Aktualna tura']

        move_from = ['Kod przedmiotu', 'Język wykładowy', 'Liczba godzin', 'Nazwa przedmiotu', 'Punkty ECTS', 'Typ zajęć', 'Cykl dydaktyczny']
        move_to = ['id', 'language', 'span', 'name', 'ects', 'type', 'term']
        move_to_type = [str, str, float, str, float, str, str]

        for from_key, to_key, to_type in zip(move_from, move_to, move_to_type):
            try:
                group_info[to_key] = to_type(group_info[from_key])
                if to_key in ['language', 'name', 'type', 'term']:
                    group_info[to_key] = group_info[to_key].lower()
            except Exception as e:
                group_info[to_key] = -1. if to_type is float else 'unknown'
                logging.warning(e)
            finally:
                if from_key in group_info:
                    del group_info[from_key]
        try:
            group_info['seats'] = (float((tp := group_info['Liczba miejsc (zarejestrowani/limit)'].split('/'))[0]), float(tp[1]))
        except Exception as e:
            group_info['seats'] = (-1., -1.)
            logging.warning(e)
        finally:
            if 'Liczba miejsc (zarejestrowani/limit)' in group_info:
                del group_info['Liczba miejsc (zarejestrowani/limit)']
        try:
            group_info['venue'] = ' '.join(word.strip() for word in group_info['Miejsce'].split(' ')[:-1])
        except Exception as e:
            group_info['venue'] = 'unknown'
            logging.warning(e)
        finally:
            if 'Miejsce' in group_info:
                del group_info['Miejsce']
        try:
            group_info['cost'] = float(group_info['Koszt'].split(' ')[0])
        except Exception as e:
            group_info['cost'] = 0.
            logging.warning(e)
        finally:
            if 'Koszt' in group_info:
                del group_info['Koszt']
        try:
            group_info['time'] = []
            times = group_info['Termin'].split(', ')
            for t in times:
                day, _, hour = t.split(' ')
                group_info['time'].append((day.lower(), time.fromisoformat((h := hour.split('-'))[0].ljust(2, '0')), time.fromisoformat(h[1].ljust(2, '0'))))
        except Exception as e:
           logging.warning(e)
        finally:
            if 'Termin' in group_info:
                del group_info['Termin']
        try:
            group_info['lecturer'] = group_info['Prowadzący'].split(', ')
        except Exception as e:
            group_info['lecturer'] = []
            logging.warning(e)
        finally:
            if 'Prowadzący' in group_info:
                del group_info['Prowadzący']

        return group_info

    def _print(self, group_info):
        self._total += 1
        print(group_info)
        print('-'*75)