from Alerting.Alert_Engine.Alert_Engine import AlertEngine, Fore
from Reporting.Report_Engine.Report_Engine import Report_Engine
from Health_Check.Logstash import Logstash_HC
from configparser import RawConfigParser
import os, yaml

# ============================================
#   READ CONFIGURATION FILES - PARENT CLASS
# ============================================
class Read_Config:

    # --------------------------------------------
    #   CONSTRUCTOR TO LOAD CONFIGURATION FILE
    # --------------------------------------------
    def __init__(self, config_file_path, report_parser_path, alert_parser_path):
        self._config = RawConfigParser()
        self._config_file_path = config_file_path
        self._report_parser_path = report_parser_path
        self._alert_parser_path = alert_parser_path

    # --------------------------------------------------------------
    #   READ CONFIGURATION FILE WITH PROVIDED SECTION AND PROPERTY
    # --------------------------------------------------------------
    def get_config(self, mode, section=None, property=None):
        self._config.read(self._config_file_path)
        if mode == 'keys':
            data_sources = set()
            for k, v in self._config['Indices'].items():
                if k is not None: data_sources.add(v)
            return data_sources
        elif mode == 'values': return self._config.get(section, property)
        elif mode == 'pair': return self._config['Indices']

    # --------------------------------------------------------
    #   READ ELASTIC SEARCH DETAILS FROM CONFIGURATION FILE
    # --------------------------------------------------------
    def elasticsearch_details(self, property):
        self._config.read(self._config_file_path)
        return self._config.get(section="elastic_search", option=property)

    # -------------------------------------------------
    #   MAPPING FOR PARSERS FROM CONFIGURATION FILE
    # -------------------------------------------------
    def get_parsers(self, mode):
        parser_dict = {}
        if mode == 'report':
            for file in os.listdir(self._report_parser_path):
                self._config.read(f'{self._report_parser_path}/{file}')
                parser_dict[file] = self._config['parser']
            return parser_dict
        elif mode == 'alert':
            for file in os.listdir(self._alert_parser_path):
                self._config.read(f'{self._alert_parser_path}/{file}')
                parser_dict[file] = self._config['parser']
            return parser_dict

    # -------------------------------
    #   GET LOGSTASH INFORMATION
    # -------------------------------
    def get_logstash_details(self, section_name):
        logstash_dict = {}
        self._config.read(self._config_file_path)
        for key, val in self._config[section_name].items():
            logstash_dict[key] = val
        return logstash_dict


# ==================================
#   READ YAML CONFIGURATION FILES
# ==================================
class Read_Yaml:

    # ---------------------------------------------------------
    #   GET RULES INFORMATION FROM YAML FILE BY PROVIDING KEY
    # ---------------------------------------------------------
    def get_rule_info(self, key, file):
        with open(file) as ym_file:
            rule_info = yaml.load(ym_file, Loader=yaml.FullLoader)
        return rule_info[key]

    # --------------------------------------------------------------------------------
    #   GET AGGREGATION INFORMATION (ALERT NAME, MATCHES, TIME FRAME) FROM YAML FILE
    # --------------------------------------------------------------------------------
    def get_aggregation_info(self, file):
        agg_dict = {'matches': self.get_rule_info('Aggregation', file)['matches'],
                    'timeframe': self.get_rule_info('Aggregation', file)['timeframe'],
                    'alertname': self.get_rule_info('Alert_Name', file)}
        return agg_dict

    # ----------------------------------------------------------------------
    #   GET REPORT DETAILS FROM THE YAML FILE - REPORT NAME & OUTPUT TYPE
    # ----------------------------------------------------------------------
    def get_report_info(self, file):
        report_dict = {}
        report_dict['report_name'] = self.get_rule_info('Report_Name', file)
        report_dict['output_type'] = self.get_rule_info('Output', file)
        report_dict['time_frame'] = self.get_rule_info('TimeFrame', file)
        report_dict['template_name'] = self.get_rule_info('Template_Name', file)
        return report_dict

    # ----------------------------------
    #   GET WORD TEMPLATE INFORMATION
    # ----------------------------------
    def get_word(self, type, file_path):
        if type == 'details':
            return {'type': self.get_rule_info(key='template', file=file_path)['type'], 'author': self.get_rule_info(key='template', file=file_path)['author']}
        elif type == 'cover_page':
            heading = self.get_rule_info(key='cover_page', file=file_path)['heading']
            subheading = self.get_rule_info(key='cover_page', file=file_path)['subheading']
            paragraph = self.get_rule_info(key='cover_page', file=file_path)['paragraph']
            if self.get_rule_info(key='cover_page', file=file_path)['required'] is True:
                return {'heading': heading, 'subheading': subheading, 'paragraph': paragraph}
            elif self.get_rule_info(key='cover_page', file=file_path)['required'] is False: return None
            else: return None
        elif type == 'table':
            heading = self.get_rule_info(key='table', file=file_path)['heading']
            paragraph = self.get_rule_info(key='table', file=file_path)['paragraph']
            fields = self.get_rule_info(key='table', file=file_path)['fields']
            if self.get_rule_info(key='table', file=file_path)['required'] is True:
                return {'heading': heading, 'paragraph': paragraph, 'fields': fields}
            elif self.get_rule_info(key='table', file=file_path)['required'] is False: return None
            else: return None
        elif type == 'charts':
            heading = self.get_rule_info(key='chart', file=file_path)['heading']
            fields = self.get_rule_info(key='chart', file=file_path)['field']
            chart_type = self.get_rule_info(key='chart', file=file_path)['type']
            width = self.get_rule_info(key='chart', file=file_path)['width']
            height = self.get_rule_info(key='chart', file=file_path)['height']
            if self.get_rule_info(key='chart', file=file_path)['required'] is True:
                return {'heading': heading, 'field': fields, 'type': chart_type, 'width': width, 'height': height}
            elif self.get_rule_info(key='chart', file=file_path)['required'] is False: return None
            else: return None

    # ------------------------------------------
    #   GET POWER POINT TEMPLATE INFORMATION
    # ------------------------------------------
    def get_ppt(self, type, file_path):
        if type == 'details':
            return {'type': self.get_rule_info(key='template', file=file_path)['type'], 'author': self.get_rule_info(key='template', file=file_path)['author']}
        elif type == 'cover_page':
            heading = self.get_rule_info(key='cover_page', file=file_path)['heading']
            subheading = self.get_rule_info(key='cover_page', file=file_path)['subheading']
            return {'heading': heading, 'subheading': subheading}
        elif type == 'table':
            heading = self.get_rule_info(key='table', file=file_path)['heading']
            paragraph = self.get_rule_info(key='table', file=file_path)['paragraph']
            fields = self.get_rule_info(key='table', file=file_path)['fields']
            if self.get_rule_info(key='table', file=file_path)['required'] is True:
                return {'heading': heading, 'paragraph': paragraph, 'fields': fields}
            elif self.get_rule_info(key='table', file=file_path)['required'] is False: return None
            else: return None
        elif type == 'charts':
            heading = self.get_rule_info(key='chart', file=file_path)['heading']
            fields = self.get_rule_info(key='chart', file=file_path)['field']
            chart_type = self.get_rule_info(key='chart', file=file_path)['type']
            width = self.get_rule_info(key='chart', file=file_path)['width']
            height = self.get_rule_info(key='chart', file=file_path)['height']
            if self.get_rule_info(key='chart', file=file_path)['required'] is True:
                return {'heading': heading, 'field': fields, 'type': chart_type, 'width': width, 'height': height}
            elif self.get_rule_info(key='chart', file=file_path)['required'] is False: return None
            else: return None

# ================================
#   ENGINE FOR SIEM TOOL
# ================================
class Engine(Read_Config):

    def __init__(self):
        self._cwd = os.getcwd().replace('\\', '/')
        Read_Config.__init__(self, config_file_path=self._cwd+'/Settings/Map_Indices',
                             report_parser_path=self._cwd+'/Settings/Report_Parsers',
                             alert_parser_path=self._cwd+'/Settings/JSON_Parsers')
        self._yml = Read_Yaml()

    # ----------------------
    #   INITIATE ALERTING
    # ----------------------
    def alerting(self):
        ae = AlertEngine(elastic_hostname=self.elasticsearch_details('hostname'), elastic_port=self.elasticsearch_details('port'),
                         rules_folder=self._cwd+'/Alerting/Alert_Rules',
                         indices_list=self.get_config(mode='pair'), read_yml=self._yml,
                         parser_dict = self.get_parsers(mode='alert'), elastic_query_time=self.elasticsearch_details('search_query_time_interval'))
        ae.main()

    # -----------------------
    #   INITIATE REPORTING
    # -----------------------
    def reporting(self, timeframe):
        re = Report_Engine(elastic_hostname=self.elasticsearch_details('hostname'), elastic_port=self.elasticsearch_details('port'),
                           rules_folder=self._cwd+'/Reporting/Report_Rules', time_format=timeframe,
                           indices_list=self.get_config(mode='pair'),
                           yaml_ref=self._yml, parsers_dict=self.get_parsers(mode='report'),
                           report_gen_path=self._cwd+'/Reporting/Generated_Reports',
                           report_template_path = self._cwd+'/Reporting/Report_Templates',
                           default=self._cwd+'/Settings/default')
        re.run_reports()

    # ---------------------------
    #   INITIATE HEALTH CHECK
    # ---------------------------
    def health_check(self):
        lg = Logstash_HC(logstash_dict=self.get_logstash_details('Logstash'))
        lg.main()

    # -------------------------
    #   INITIATE LOGSEARCH
    # -------------------------
    def logsearch(self): print(f'{Fore.RED}[-] Not Yet Implemented...!')

    # ----------------------------------
    #   USER CHOICE TO SELECT THE TASK
    # ----------------------------------
    def user_choice(self):
        print(f'{Fore.LIGHTYELLOW_EX}[+] Select the Choice\n\t[1] Alerting\n\t[2] Reporting\n\t[3] HealthCheck\n\t[4] LogSearch')
        choice_dict = {'1': 'Alerting', '2': 'Reporting', '3': 'Health Check', '4': 'LogSearch'}
        while True:
            choice = input(f'{Fore.LIGHTMAGENTA_EX}[*] Enter Your Choice : ')
            if choice in ['1', '2', '3', '4']: break
            else: print(f'{Fore.LIGHTRED_EX}[-] Invalid Selection. Please Select Again')
        print(f'{Fore.LIGHTCYAN_EX}[+] You Selected {choice_dict[choice]}')
        if choice == '1': self.alerting()
        elif choice == '2':
            print(f'{Fore.LIGHTYELLOW_EX}\t[+] Select Report Type\n\t\t[1] Daily\n\t\t[2] Weekly\n\t\t[3] Monthly')
            while True:
                rep_choice = input(f'\t{Fore.LIGHTCYAN_EX}[*] Enter Your Choice : ')
                if rep_choice in ['1', '2', '3']: break
                else: print(f'{Fore.LIGHTRED_EX}[-] Invalid Selection. Please Select Again')
            rep_choice_dict = {'1': 'Daily', '2': 'Weekly', '3': 'Monthly'}
            self.reporting(timeframe=rep_choice_dict[rep_choice])
        elif choice == '3': self.health_check()
        elif choice == '4': self.logsearch()

if __name__ == '__main__':
    se = Engine()
    se.user_choice()