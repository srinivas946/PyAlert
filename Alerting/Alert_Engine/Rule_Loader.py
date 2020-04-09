# COMMON IMPORTS
from queue import Queue

# IMPORT RELATED TO CURRENT PROJECT PACKAGES
from Alerting.Alert_Engine.Configs_Parsers import Parsers, datetime, timedelta

# ===============================================================================
#   RULE TRIGGER TO TRIGGER THE RULE WHEN CONDITION MATCHES AND PARSER THE DATA
# ===============================================================================
class RuleTrigger(Parsers):

    def __init__(self, elastic_hostname, elastic_port, index, query, bucket_size, timeframe, alert_name):
        Parsers.__init__(self, elastic_hostname=elastic_hostname, elastic_port=elastic_port)
        self._index = index
        self._query = query
        self._bucket = Queue(maxsize=bucket_size)
        self._timeframe = timeframe
        self._alert_name = alert_name

    # -------------------------------------------------------------------------
    #   GENERATE LIST OF TIMEFRAMES BASED ON THE GIVEN INITIAL TIME AND FRAME
    # -------------------------------------------------------------------------
    def _gen_times(self, initial_time, frame):
        times_frame = [initial_time]
        for i in range(1, frame + 1):
            added_time = (datetime.strptime(initial_time, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=i)).strftime('%Y-%m-%dT%H:%M:%S')
            times_frame.append(added_time)
        return times_frame

    # ----------------------------------------------------
    #   GENERATE ALERT ID'S WHICH ARE EPOCH TIME STAMPS
    # ----------------------------------------------------
    def generate_alert_id(self):
        epoch_time = int(datetime.now().timestamp())
        return epoch_time

    # ------------------------------------------------------------------------------------
    #   APPLY RULE TO ALL THE EVENTS AND STORE THEM IN A QUEUE IF RULE CONDITION MATCHES
    # ------------------------------------------------------------------------------------
    def apply_rule(self, parser_dict, event_id):
        alert_id = self.generate_alert_id()
        timestamps = self.get_data(index=self._index, query=self._query, parser_dict=parser_dict, event_id=event_id)
        alerts_dict = {}
        if len(timestamps) != 0:
            for stamp, my_data in timestamps.items():
                time_frame_list = self._gen_times(initial_time=stamp, frame=self._timeframe)
                for time in time_frame_list:
                    if time in timestamps.keys():
                        data = timestamps[time]
                        data.update({'alert_name': self._alert_name})
                        self._bucket.put(data)
                    if self._bucket.full() is True:
                        alerts_dict[(alert_id, self._alert_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))] = list(self._bucket.queue)
                        with self._bucket.mutex:
                            self._bucket.queue.clear()
                            alert_id += 1
                alert_last_time, event_id = my_data['time'], my_data['event_id']
                with self._bucket.mutex:
                    self._bucket.queue.clear()
            return alerts_dict, alert_last_time, alert_id, event_id
        else: return alerts_dict, 0, alert_id, event_id