# IMPORTS RELATE TO CURRENT PROJECT PACKAGES
from Reporting.Report_Engine.Query_Maker import QueryMaker
from Reporting.Report_Engine.Configs_Parsers import Parsers
from Reporting.Report_Engine.Output_Formatting import JSON, CSV, Word, PPT, Fore, os
import sys

# ===============================================================================
#   CHILD CLASS TO EXTEND THE PROPERTIES OF QUERY-MAKER CLASS AND PARSERS CLASS
# ===============================================================================
class Report_Engine(QueryMaker, Parsers):

    def __init__(self, elastic_hostname, elastic_port, indices_list, rules_folder, time_format, yaml_ref, parsers_dict, report_gen_path, report_template_path, default):
        Parsers.__init__(self, elastic_hostname, elastic_port)
        self._rules_folder = rules_folder + '/' + time_format
        QueryMaker.__init__(self, self._rules_folder)
        self._get_indices_list = indices_list
        self._yaml_ref = yaml_ref
        self.parsers_dict = parsers_dict
        self.report_gen_path = report_gen_path+'/'+time_format
        self._default = default
        self._report_template_path = report_template_path

    # ------------------------------
    #   GET REPORT RULES FOLDERS
    # ------------------------------
    def _get_rule_folders_name(self):
        folder_map = {}
        for folder in os.listdir(self._rules_folder):
            folder_map[folder] = f'{self._rules_folder}/{folder}'
        return folder_map

    # ----------------------------------
    #   VERIFY REPORT RULES TEMPLATE
    # ----------------------------------
    def _verify_report_template(self, template):
        if os.path.exists(f'{self._report_template_path}/{template}.yml'):
            return f'{self._report_template_path}/{template}.yml'
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Template {template} does not exist...!')
            sys.exit()

    # -----------------------------------------
    #   CONSOLE PRINTING RELATED OPERATIONS
    # -----------------------------------------
    def report_decision(self, confirm, report_name, report_gen_path):
        if confirm is True: print(f'\r{Fore.LIGHTGREEN_EX}[+] Report => {report_name} Generated Successfully\n\t|\n\t|-> Generated Reports Path => {report_gen_path}')
        elif confirm is False: print(f'\r{Fore.LIGHTYELLOW_EX}[-] No Data Found to generate report => {report_name}')
        else: print(f'\r{Fore.LIGHTRED_EX}[-] Not able to generated report => {report_name} | Reason : {confirm}')

    # -------------------------------------------------------------
    #   MAIN METHOD TO INITIATE THE PROCESS OF GENERATING REPORTS
    # -------------------------------------------------------------
    def run_reports(self):
        for index_key, index in self._get_indices_list.items():
            for folder, rules_path in self._get_rule_folders_name().items():
                if index.__contains__(folder) or index.__contains__(folder.capitalize()) or index.__contains__(folder.upper()):
                    print(f'Index : {index} | Folder {folder}')
                    for rule in os.listdir(rules_path):
                        query = self.query_maker(f'{rules_path}/{rule}', self._yaml_ref)
                        events_dict = self.get_data(index=index, query=query, parser_dict=self.parsers_dict[index_key])
                        output_format = self._yaml_ref.get_report_info(file=f'{rules_path}/{rule}')['output_type']
                        report_name = self._yaml_ref.get_report_info(file=f'{rules_path}/{rule}')['report_name']
                        print(f"{Fore.LIGHTMAGENTA_EX}[*] Running Report => Name : {self._yaml_ref.get_report_info(file=f'{rules_path}/{rule}')['report_name']} | Output Format : {output_format}")
                        print(f'{Fore.LIGHTCYAN_EX}[+] Report File path..... => {rules_path}/{rule}')
                        template_name = self._yaml_ref.get_report_info(file=f'{rules_path}/{rule}')['template_name']
                        if output_format.lower() == 'json':
                            jsn = JSON(report_path=self.report_gen_path, report_name=report_name)
                            confirm = jsn.create_json(json_obj=events_dict)
                            self.report_decision(confirm, report_name, self.report_gen_path)
                        elif output_format.lower() == 'csv':
                            cs = CSV(report_path=self.report_gen_path, report_name=report_name)
                            confirm = cs.create_csv(json_data=events_dict)
                            self.report_decision(confirm, report_name, self.report_gen_path)
                        elif output_format.lower() == 'word':
                            if template_name is not None:
                                wd = Word(report_path=self.report_gen_path, report_name=report_name, template_name=self._verify_report_template(template=template_name), json_data=events_dict, folder_path = self._default, yaml_ref=self._yaml_ref)
                                confirm = wd.create_word()
                                self.report_decision(confirm, report_name, self.report_gen_path)
                            else: print(f'{Fore.LIGHTRED_EX}[-] Provide the Template Name in the Report Rules => {f"{rules_path}/{rule}"}.yml')
                        elif output_format.lower() == 'ppt':
                            if template_name is not None:
                                pp = PPT(report_path=self.report_gen_path, report_name=report_name, template_name=self._verify_report_template(template=template_name), json_data=events_dict, folder_path= self._default, yaml_ref=self._yaml_ref)
                                confirm = pp.create_ppt()
                                self.report_decision(confirm, report_name, self.report_gen_path)
                            else: print(f'{Fore.LIGHTRED_EX}[-] Provide the Template Name in the Report Rules => {f"{rules_path}/{rule}"}.yml')
