# COMMON IMPORTS
import json, requests
from datetime import datetime, timedelta
from colorama import Fore

# =====================================
#   PARENT CLASS TO LOAD JSON PARSERS
# =====================================
class Parsers:

    def __init__(self, elastic_hostname, elastic_port):
        self._elastic_hostname = elastic_hostname
        self._elastic_port = elastic_port

    # ----------------------------------------------------
    #   DYNAMIC JSON BUILDER FROM PARSER CONFIGURATION
    # ----------------------------------------------------
    def _list_maker(self, each, v):
        result_value = ''
        for i in v.split(','):
            try:
                if result_value != '': result_value = result_value[i.strip()]
                else: result_value = each[i.strip()]
            except (KeyError, TypeError): result_value = 'No Info'
        return result_value

    # ----------------------------------------------------
    #   GET DATA BY REQUESTING ELASTIC SEARCH FREQUENTLY
    # ----------------------------------------------------
    def get_data(self, index, query, parser_dict):
        data = json.dumps(query)
        res = requests.request('GET', f'http://{self._elastic_hostname}:{self._elastic_port}/{index}/_search', headers={'Content-Type': 'application/json'}, data=data)
        if res.status_code == 200:
            try:
                if len(res.json()) != 0:
                    res_data = res.json()['hits']['hits']
                    timestamps = {}
                    if len(res_data) != 0:
                        for each in res_data:
                            event_dict = {}
                            for k, v in parser_dict.items():
                                event_dict[k] = self._list_maker(each['_source'], v)
                            event_dict['time'] = each['_source']['@timestamp']
                            timestamps[datetime.strptime(each['_source']['@timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%dT%H:%M:%S')] = event_dict
                        return timestamps
                    else:
                        print(f'{Fore.LIGHTYELLOW_EX}[+] No hits observed for this request....!\n')
                        return timestamps
                else: return {}
            except KeyError as e:
                print(f'{Fore.LIGHTRED_EX}[-] Met with Error | Reason : {e}')
                return {}
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Status Code : {res.status_code} | Reason : {res.reason}')
            return {}