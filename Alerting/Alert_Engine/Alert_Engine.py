# IMPORTS RELATED TO CURRENT PROJECT PACKAGES
from Alerting.Alert_Engine.Query_Maker import QueryMaker
from Alerting.Alert_Engine.Rule_Loader import RuleTrigger, datetime

# COMMON IMPORTS
import os, time, threading
from colorama import Fore, init
init(convert=True)

# ======================================================
#   CHILD CLASS EXTENDS FROM QUERY-MAKER FOR ALERTING
# ======================================================
class AlertEngine(QueryMaker):

    def __init__(self, elastic_hostname, elastic_port, rules_folder, indices_list, read_yml, parser_dict, elastic_query_time):
        self._elastic_hostname = elastic_hostname
        self._elastic_port = elastic_port
        self._rules_folders = rules_folder
        self._get_indices_list = indices_list
        self._read_yml = read_yml
        self._parser_dict = parser_dict
        self._elastic_query_time = elastic_query_time

    # --------------------------------------------
    #   PUSH TRIGGERED ALERTS TO OUTPUT CONSOLE
    # --------------------------------------------
    def push_output(self, index_key, alert_dict):
        print(f'{Fore.MAGENTA}[+] {index_key} => Total Alerts Triggered : {len(alert_dict)}')
        for key, val in alert_dict.items():
            print(f'{Fore.LIGHTYELLOW_EX}ID : {key[0]} | Alert Name : {key[1]} | Reported Time : {key[2]} | Triggered Time in Portal : {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}\n\t|')
            for v in val:
                print(f'{Fore.LIGHTYELLOW_EX}\t|-> {Fore.LIGHTBLUE_EX}Event ID : {v["event_id"]}  Name: {v["alert_name"]}')

    # ----------------------------------------------------
    #   GET ALERT RULES FOLDER AND RESPECTIVE MAPPINGS
    # ----------------------------------------------------
    def _get_rule_folders_name(self):
        folder_map = {}
        for folder in os.listdir(self._rules_folders):
            folder_map[folder] = f'{self._rules_folders}/{folder}'
        return folder_map

    # ---------------------------------------------------------------------------------------
    #   COMMON METHOD FOR ALL THE DATA SOURCES TO TRIGGER THE ALERT BASED ON RULE MATCHINGS
    # ---------------------------------------------------------------------------------------
    def specific(self, index_key, index):
        initial_time, alert_id, event_id = 0, 1, 0
        while True:
            for folder, rules_path in self._get_rule_folders_name().items():
                if index.__contains__(folder) or index.__contains__(folder.capitalize()) or index.__contains__(folder.upper()) or index.__contains__(folder.lower()):
                    for rule in os.listdir(rules_path):
                        agg_info = self._read_yml.get_aggregation_info(file=f'{rules_path}/{rule}')
                        query = self.get_query(rule_file=f'{rules_path}/{rule}', condition_time=initial_time, read_yml=self._read_yml)
                        rc = RuleTrigger(elastic_hostname=self._elastic_hostname, elastic_port=self._elastic_port, index=index, query=query, bucket_size=agg_info['matches'], timeframe=agg_info['timeframe'], alert_name=agg_info['alertname'])
                        alert_dict, initial_time_check, alert_id, event_id = rc.apply_rule(parser_dict=self._parser_dict[index_key], event_id=event_id)
                        if initial_time_check != 0: initial_time = initial_time_check
                        self.push_output(index_key, alert_dict)
            print(f'{Fore.LIGHTGREEN_EX}[*] Task Completed | Waiting For {self._elastic_query_time} Seconds to request Elastic search')
            time.sleep(float(self._elastic_query_time))

    # --------------------------------------
    #   MAIN METHOD TO INITIATE ALERTING
    # --------------------------------------
    # CONDITION: Rule Folder name must be in the name of index created in elastic search
    def main(self):
        threads_list = []
        try:
            for index_key, index in self._get_indices_list.items():
                thread = threading.Thread(target=self.specific, kwargs={'index_key':index_key, 'index':index})
                thread.start()
                threads_list.append(thread)
        except KeyboardInterrupt:
            print('Observed Keyboard Interruption. Shutting down....!')
            for thread in threads_list: thread.join()
            del threads_list
