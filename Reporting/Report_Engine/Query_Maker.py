# COMMON IMPORTS
import calendar

# IMPORTS RELATED TO CURRENT PROJECT PACKAGES
from Reporting.Report_Engine.Configs_Parsers import datetime, timedelta

# ====================================================
#   CREATE QUERY BASED ON RULE PROVIDED IN YAML FILE
# ====================================================
class QueryMaker:

    # ----------------------------------------------------------
    #   CONSTRUCTOR TO LOAD RULES FOLDER WHILE OBJECT CREATION
    # ----------------------------------------------------------
    def __init__(self, rules_folder_path):
        self._rules_folder_path = rules_folder_path
        if self._rules_folder_path.__contains__('Daily'): self._report_type = 'daily'
        elif self._rules_folder_path.__contains__('Weekly'): self._report_type = 'weekly'
        elif self._rules_folder_path.__contains__('Monthly'): self._report_type = 'monthly'
        self._formated_date = '%Y-%m-%d'

    # ----------------------------------------------
    #   GET REPORT TYPE BASED ON FOLDER PATH GIVEN
    # ----------------------------------------------
    def create_timeframe(self):
        if self._report_type.__contains__('daily'):
            dates_dict = {}
            date = (datetime.today() - timedelta(days=1)).strftime(self._formated_date)
            dates_dict['start_time'] = f'{date}T00:00:00'
            dates_dict['end_time'] = f'{date}T23:59:59'
            return dates_dict
        if self._report_type.__contains__('weekly'):
            dates_dict = {}
            initial_date = datetime.today() - timedelta(days=1)
            start = initial_date - timedelta(days=initial_date.weekday())
            end = start + timedelta(6)
            dates_dict['start_time'] = f'{start.strftime(self._formated_date)}T00:00:00'
            dates_dict['end_time'] = f'{end.strftime(self._formated_date)}T23:59:59'
            return dates_dict
        if self._report_type.__contains__('monthly'):
            dates_dict = {}
            today = datetime.today()
            month_last_day = calendar.monthrange(year=today.year, month=today.month)[1]
            time_format = self._formated_date.split('-')
            format_dict = {'%Y': today.year, '%m': str(today.month).zfill(2), '%d': month_last_day}
            dates_dict['start_time'] = f'{format_dict[time_format[0]]}-{str(format_dict[time_format[1]]).zfill(2)}-01T00:00:00'
            dates_dict['end_time'] = f'{format_dict[time_format[0]]}-{str(format_dict[time_format[1]]).zfill(2)}-{format_dict[time_format[2]]}T23:59:00'
            return dates_dict

    # ----------------------------------------------------------------
    #   CREATE A QUERY FOR ELASTIC SEARCH BY READING THE RULES FILE
    # ----------------------------------------------------------------
    def query_maker(self, file, yaml_ref):
        equal_list, not_equal_list, should_list, notshould_list = [], [], [], []
        for k, v in yaml_ref.get_rule_info('Rule', file)['Equal'].items():
            if k == 'AND' and v is not None:
                for key, val in v.items():
                    equal_list.append({"match": {key: val}})
            elif k == 'OR' and v is not None:
                for key, val in v.items():
                    should_list.append({"match": {key: val}})
                # equal_list.append({"bool":{"should": should_list}})
        if yaml_ref.get_rule_info('Rule', file)['Contains'] is not None:
            for kk, vv in yaml_ref.get_rule_info('Rule', file)['Contains'].items():
                if kk == 'AND' and vv is not None:
                    for key, val in vv.items():
                        equal_list.append({"query_string": {"default_field": key, "query": val}})
                elif kk == 'OR' and vv is not None:
                    for key, val in vv.items():
                        should_list.append({"query_string": {"default_field": key, "query": val}})
                    equal_list.append({"bool": {"should": should_list}})

        for k, v in yaml_ref.get_rule_info('Rule', file)['NotEqual'].items():
            if k == 'AND' and v is not None:
                for key, val in v.items():
                    not_equal_list.append({"match": {key: val}})
            elif k == 'OR' and v is not None:
                for key, val in v.items():
                    notshould_list.append({"match": {key: val}})
                # not_equal_list.append({"bool":{"should": notshould_list}})
        if yaml_ref.get_rule_info('Rule', file)['NotContains'] is not None:
            for kk, vv in yaml_ref.get_rule_info('Rule', file)['NotContains'].items():
                if kk == 'AND' and vv is not None:
                    for key, val in vv.items():
                        not_equal_list.append({"query_string": {"default_field": key, "query": val}})
                elif kk == 'OR' and vv is not None:
                    for key, val in vv.items():
                        notshould_list.append({"query_string": {"default_field": key, "query": val}})
                    not_equal_list.append({"bool": {"should": notshould_list}})
        time_dict = self.create_timeframe()
        if len(equal_list) != 0 and len(not_equal_list) != 0:
            final_query = {"size": 10000, "query": {"bool": {"must": equal_list, 'must_not': not_equal_list, "filter": {
                "range": {"@timestamp": {"gte": time_dict['start_time'], "lte": time_dict['end_time']}}}}},
                           "sort": [{"@timestamp": {"order": "asc"}}]}
            return final_query
        elif len(equal_list) != 0 and len(not_equal_list) == 0:
            final_query = {"size": 10000, "query": {"bool": {"must": equal_list, "filter": {
                "range": {"@timestamp": {"gte": time_dict['start_time'], "lte": time_dict['end_time']}}}}},
                           "sort": [{"@timestamp": {"order": "asc"}}]}
            return final_query
        elif len(equal_list) == 0 and len(not_equal_list) != 0:
            final_query = {"size": 10000, "query": {"bool": {"must_not": not_equal_list, "filter": {
                "range": {"@timestamp": {"gte": time_dict['start_time'], "lte": time_dict['end_time']}}}}},
                           "sort": [{"@timestamp": {"order": "asc"}}]}
            return final_query