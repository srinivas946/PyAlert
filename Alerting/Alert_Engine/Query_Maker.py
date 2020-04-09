
# ====================================================
#   CREATE QUERY BASED ON RULE PROVIDED IN YAML FILE
# ====================================================
class QueryMaker:

    # ----------------------------------------------------------------
    #   CREATE A QUERY FOR ELASTIC SEARCH BY READING THE RULES FILE
    # ----------------------------------------------------------------
    def get_query(self, rule_file, condition_time, read_yml):
        equal_list, not_equal_list, should_list, notshould_list = [], [], [], []
        for k, v in read_yml.get_rule_info('Rule', rule_file)['Equal'].items():
            if k == 'AND' and v is not None:
                for key, val in v.items():
                    equal_list.append({"match": {key: val}})
            elif k == 'OR' and v is not None:
                for key, val in v.items():
                    should_list.append({"match": {key: val}})
                # equal_list.append({"bool":{"should": should_list}})
        if read_yml.get_rule_info('Rule', rule_file)['Contains'] is not None:
            for kk, vv in read_yml.get_rule_info('Rule', rule_file)['Contains'].items():
                if kk == 'AND' and vv is not None:
                    for key, val in vv.items():
                        equal_list.append({"query_string": {"default_field": key, "query": val}})
                elif kk == 'OR' and vv is not None:
                    for key, val in vv.items():
                        should_list.append({"query_string": {"default_field": key, "query": val}})
                    equal_list.append({"bool": {"should": should_list}})

        for k, v in read_yml.get_rule_info('Rule', rule_file)['NotEqual'].items():
            if k == 'AND' and v is not None:
                for key, val in v.items():
                    not_equal_list.append({"match": {key: val}})
            elif k == 'OR' and v is not None:
                for key, val in v.items():
                    notshould_list.append({"match": {key: val}})
                # not_equal_list.append({"bool":{"should": notshould_list}})
        if read_yml.get_rule_info('Rule', rule_file)['NotContains'] is not None:
            for kk, vv in read_yml.get_rule_info('Rule', rule_file)['NotContains'].items():
                if kk == 'AND' and vv is not None:
                    for key, val in vv.items():
                        not_equal_list.append({"query_string": {"default_field": key, "query": val}})
                elif kk == 'OR' and vv is not None:
                    for key, val in vv.items():
                        notshould_list.append({"query_string": {"default_field": key, "query": val}})
                    not_equal_list.append({"bool": {"should": notshould_list}})

        if len(equal_list) != 0 and len(not_equal_list) != 0:
            final_query = {"size": 10000, "query": {"bool": {"must": equal_list, 'must_not': not_equal_list, "filter": {
                "range": {"@timestamp": {"gt": condition_time}}}}}, "sort": [{"@timestamp": {"order": "asc"}}]}
            return final_query
        elif len(equal_list) != 0 and len(not_equal_list) == 0:
            final_query = {"size": 10000, "query": {
                "bool": {"must": equal_list, "filter": {"range": {"@timestamp": {"gt": condition_time}}}}},
                           "sort": [{"@timestamp": {"order": "asc"}}]}
            return final_query
        elif len(equal_list) == 0 and len(not_equal_list) != 0:
            final_query = {"size": 10000, "query": {
                "bool": {"must_not": not_equal_list, "filter": {"range": {"@timestamp": {"gt": condition_time}}}}},
                           "sort": [{"@timestamp": {"order": "asc"}}]}
            return final_query