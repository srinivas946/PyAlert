# COMMON IMPORTS
import requests
from configparser import RawConfigParser
from colorama import Fore

# ========================================================
#   HEALTH CHECK FOR LOGSTASH - OS, CPU, PIPELINES, JVM
# ========================================================
class Logstash_HC:

    # ----------------------------------------------------------------------------
    #   CONSTRUCTOR TO LOAD AT THE TIME OF OBJECT CREATION WITH REQUIRED DETAILS
    # ----------------------------------------------------------------------------
    def __init__(self, logstash_dict):
        if logstash_dict['hostname'] in ['localhost', '127.0.0.1']:
            self._hostname = f"http://{logstash_dict['hostname']}"
            self._cert = None
            self._verify = False
        else:
            self._hostname = f"https://{logstash_dict['hostname']}"
            self._cert = logstash_dict['cert_path']
            self._verify = True
        self._port = logstash_dict['port']
        self._jvm_stats = f"{self._hostname}:{self._port}/{logstash_dict['jvm_stats']}"
        self._process_stats = f"{self._hostname}:{self._port}/{logstash_dict['process_stats']}"
        self._event_stats = f"{self._hostname}:{self._port}/{logstash_dict['event_stats']}"
        self._os_stats = f"{self._hostname}:{self._port}/{logstash_dict['os_stats']}"
        self._hot_threads = f"{self._hostname}:{self._port}/{logstash_dict['hot_threads']}"
        self._pipeline_stats = f"{self._hostname}:{self._port}/{logstash_dict['pipeline_stats']}"

    # ----------------------------------------------------------
    #   GET JVM STATISTICS - STATUS, THREADS, HEAP INFORMATION
    # ----------------------------------------------------------
    def get_jvm_stats(self):
        response = requests.get(self._jvm_stats, cert=self._cert, verify=self._verify)
        if response.status_code == 200:
            res = response.json()
            status_dict = {}
            status_dict['STATUS'] = res['status']
            status_dict['THREADS'] = res['jvm']['threads']['count']
            status_dict['HEAD_USED_PERCENT'] = res['jvm']['mem']['heap_used_percent']
            status_dict['MAX HEAP'] = f"{(res['jvm']['mem']['heap_max_in_bytes'] / 1000000000)} GB"
            status_dict['HEAD_USED'] = f"{(res['jvm']['mem']['heap_used_in_bytes'] / 1000000000)} GB"
            status_dict['NON_HEAD_USED'] = f"{(res['jvm']['mem']['non_heap_used_in_bytes'] / 1000000000)} GB"
            return status_dict
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Not able to Connect | Status Code : {response.status_code} | Reason : {response.reason}')
            return None

    # -------------------------------------------------------------------
    #   GET PROCESS STATISTICS - STATUS, PIPELINE, PROCESS, CPU DETAILS
    # -------------------------------------------------------------------
    def get_process_stats(self):
        response = requests.get(self._process_stats, cert=self._cert, verify=self._verify)
        if response.status_code == 200:
            res = response.json()
            process_dict = {}
            process_dict['STATUS'] = res['status']
            process_dict['PIPELINE'] = res['pipeline']
            process_dict['PROCESS'] = f"MAX_FILE_DESCRIPTORS : {res['process']['max_file_descriptors']} | OPEN_FILE_DESCRIPTORS : {res['process']['open_file_descriptors']}"
            process_dict['CPU'] = res['process']['cpu']
            return process_dict
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Not able to Connect | Status Code : {response.status_code} | Reason : {response.reason}')
            return None

    # ---------------------------------------------------------------------------
    #   GET EVENT STATISTICS - STATUS, PIPELINE, EVENTS IN AND OUT INFORMATION
    # ---------------------------------------------------------------------------
    def get_event_stats(self):
        response = requests.get(self._event_stats, cert=self._cert, verify=self._verify)
        if response.status_code == 200:
            res = response.json()
            event_dict = {}
            event_dict['STATUS'] = res['status']
            event_dict['PIPELINE'] = f"WORKERS = {res['pipeline']['workers']} | BATCH_SIZE = {res['pipeline']['batch_size']} | BATCH_DELAY = {res['pipeline']['batch_delay']}"
            event_dict['INFO'] = f"EVENTS_IN = {res['events']['in']} | EVENTS_OUT = {res['events']['out']} | FILTERED = {res['events']['filtered']}"
            return event_dict
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Not able to Connect | Status Code : {response.status_code} | Reason : {response.reason}')
            return None

    # -----------------------------------------------------------------------------------
    #   GET OS STATISTICS - STATUS, PIPELINE, CONTROLLED GROUPS, TROTTLED COUNT DETAILS
    # -----------------------------------------------------------------------------------
    def get_os_stats(self):
        response = requests.get(self._os_stats, cert=self._cert, verify=self._verify)
        if response.status_code == 200:
            res = response.json()
            os_dict = {}
            os_dict['STATUS'] = res['status']
            os_dict['PIPELINE'] = f"WORKERS = {res['pipeline']['workers']} | BATCH_SIZE = {res['pipeline']['batch_size']} | BATCH_DELAY = {res['pipeline']['batch_delay']}"
            if len(res['os']) != 0:
                os_dict['CGROUP_CONTROL'] = res['cgroup']['cpuacct']['control_group']
                os_dict['CGROUP_USAGE_IN_NANOS'] = res['cgroup']['cpuacct']['usage_nanos']
                os_dict['CPU_CONTROL'] = res['cgroup']['cpu']['control_group']
                os_dict['CFS_PERIOD_IN_MACRO'] = res['cgroup']['cpu']['cfs_period_micros']
                os_dict['ELAPSED_PERIOD_COUNT'] = res['cgroup']['cpu']['stat']['number_of_elapsed_periods']
                os_dict['THROTTLED_COUNT'] = res['cgroup']['cpu']['stat']['number_of_times_throttled']
            return os_dict
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Not able to Connect | Status Code : {response.status_code} | Reason : {response.reason}')
            return None

    # -----------------------------------------------------------------------------
    #   GET CPU STATISTICS - STATUS, PIPELINES, BUSY THREADS, THREADS INFORMATION
    # -----------------------------------------------------------------------------
    def get_cpu_stats(self):
        response = requests.get(self._hot_threads, cert=self._cert, verify=self._verify)
        if response.status_code == 200:
            res = response.json()
            cpu_dict = {}
            cpu_dict['STATUS'] = res['status']
            cpu_dict['PIPELINE'] = f"WORKERS = {res['pipeline']['workers']} | BATCH_SIZE = {res['pipeline']['batch_size']} | BATCH_DELAY = {res['pipeline']['batch_delay']}"
            cpu_dict['BUSY_THREADS'] = f" {res['hot_threads']['busiest_threads']}"
            thread_info = {}
            for thread in res['hot_threads']['threads']:
                thread_info[thread['name']] = f"THREAT ID : {thread['thread_id']} | CPU TIME UTILITY : {thread['percent_of_cpu_time']}%"
            cpu_dict['THREAD_INFO'] = thread_info
            return cpu_dict
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Not able to Connect | Status Code : {response.status_code} | Reason : {response.reason}')
            return None

    # --------------------------------------------------------------------------------
    #   GET PIPELINE STATISTICS - STATUS, PIPELINES, EVENTS IN AND OUT COUNT DETAILS
    # --------------------------------------------------------------------------------
    def get_pipeline_stats(self):
        response = requests.get(self._pipeline_stats, cert=self._cert, verify=self._verify)
        if response.status_code == 200:
            res = response.json()
            pipeline_dict = {}
            pipeline_dict['STATUS'] = res['status']
            for key in res['pipelines'].keys():
                pipeline_dict[key] = f"EVENTS_IN = {res['pipelines'][key]['events']['in']} | EVENTS_OUT = {res['pipelines'][key]['events']['out']} | EVENTS_FILTERED = {res['pipelines'][key]['events']['filtered']}"
            return pipeline_dict
        else:
            print(f'{Fore.LIGHTRED_EX}[-] Not able to Connect | Status Code : {response.status_code} | Reason : {response.reason}')
            return None

    # -----------------------------------------------------
    #   MAIN METHOD TO INITIATE HEALTH CHECK FOR LOGSTASH
    # -----------------------------------------------------
    def main(self):
        print(f'{Fore.LIGHTMAGENTA_EX}[+] JVM Statistics')
        color_dict = {'green': Fore.GREEN, 'red': Fore.RED, 'yellow': Fore.YELLOW}
        jvm_info = self.get_jvm_stats()
        if jvm_info is not None:
            for k, v in jvm_info.items():
                if 'STATUS' == k: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {color_dict[v]}{v}')
                else: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {Fore.WHITE}{v}')
        else: print(f'\t{Fore.LIGHTBLUE_EX}[-] No Information Available')
        print(f'{Fore.LIGHTMAGENTA_EX}[+] Process Statistics')
        process_info = self.get_process_stats()
        if process_info is not None:
            for k, v in process_info.items():
                if isinstance(v, str):
                    if 'STATUS' == k: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {color_dict[v]}{v}')
                    else: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {Fore.WHITE}{v}')
                elif isinstance(v, dict):
                    print(f'\t{Fore.LIGHTCYAN_EX}{k} - ')
                    for key, val in v.items(): print(f'\t\t{Fore.LIGHTCYAN_EX}{key} - {Fore.WHITE}{val}')
        else: print(f'\t{Fore.LIGHTBLUE_EX}[-] No Information Available')
        print(f'{Fore.LIGHTMAGENTA_EX}[+] Event Statistics')
        events_info = self.get_event_stats()
        if events_info is not None:
            for k, v in events_info.items():
                if 'STATUS' == k: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {color_dict[v]}{v}')
                else: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {Fore.WHITE}{v}')
        else: print(f'\t{Fore.LIGHTBLUE_EX}[-] No Information Available')
        print(f'{Fore.LIGHTMAGENTA_EX}[+] OS Statistics')
        os_info = self.get_os_stats()
        if os_info is not None:
            for k, v in os_info.items():
                if 'STATUS' == k: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {color_dict[v]}{v}')
                else: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {Fore.WHITE}{v}')
        else: print(f'\t{Fore.LIGHTBLUE_EX}[-] No Information Available')
        print(f'{Fore.LIGHTMAGENTA_EX}[+] CPU Statistics')
        cpu_info = self.get_cpu_stats()
        if cpu_info is not None:
            for k, v in cpu_info.items():
                if isinstance(v, str):
                    if 'STATUS' == k: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {color_dict[v]}{v}')
                    else: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {Fore.WHITE}{v}')
                elif isinstance(v, dict):
                    print(f'\t{Fore.LIGHTCYAN_EX}{k} - ')
                    for key, val in v.items(): print(f'\t\t{Fore.LIGHTCYAN_EX}{key} - {Fore.WHITE}{val}')
        else: print(f'\t{Fore.LIGHTBLUE_EX}[-] No Information Available')
        print(f'{Fore.LIGHTMAGENTA_EX}[+] PipeLine Statistics')
        pipeline_info = self.get_pipeline_stats()
        if pipeline_info is not None:
            for k, v in pipeline_info.items():
                if 'STATUS' == k: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {color_dict[v]}{v}')
                else: print(f'\t{Fore.LIGHTCYAN_EX}{k} - {Fore.WHITE}{v}')
        else: print(f'\t{Fore.LIGHTBLUE_EX}[-] No Information Available')
