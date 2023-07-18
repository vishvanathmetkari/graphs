import json
import os
import pprint
import csv
import re
from datetime import datetime

DEFAULT_FOLDER = './files/'
file_path = {}
prefixes = ['cpu', 'disk', 'network', 'memory']
def get_inside_files(folder_name):
    file_path.clear()
    folder_path = DEFAULT_FOLDER+folder_name
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    for file_name in json_files:
        file = file_name.split("-", maxsplit=1)
        pre = next((pre for pre in prefixes if pre in file[-1]), None)
        if pre:
            if file[0] in file_path and file[-1] in file_path[file[0]]:
                file_path[file[0]][file[-1]] = {'path': os.path.join(folder_path, file_name), 'name': file[-1]}
            else:
                file_path.setdefault(file[0], {}).setdefault(file[-1], {'path': os.path.join(folder_path, file_name), 'name': file[-1]})

data_list = []
with open("metric.csv", 'r') as file:
    data_list.clear()
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        data_list.append(row[0])
from collections import OrderedDict

def get_score(foldername):
    file = open(os.path.join(DEFAULT_FOLDER+foldername+'/', "perfkitbenchmarker_results.json"), "r")
    for rows in file:
        parse_json = json.loads(rows)
        if parse_json['metric']=='Aggregate TPM':
            score = parse_json['value']
            pattern = r"server_cpu_arch:([\w]+)"
            match = re.search(pattern,  parse_json['labels'])
            if match:
                server_cpu_arch = match.group(1)
            else:
                server_cpu_arch =''
            break
        else:
            server_cpu_arch=''
            score=''
    return [score,server_cpu_arch]


def get_results(foldername):
    jsonData = []
    jsonData.clear()
    file = open(os.path.join(DEFAULT_FOLDER+foldername+'/', "perfkitbenchmarker_results.json"), "r")
    counts = {}
    for rows in file:
        parse_json = json.loads(rows)
        for key in parse_json.keys():
            try:
                if parse_json[key] in data_list:
                    if parse_json[key] not in counts:
                        counts[parse_json[key]] = 0
                    else:
                        counts[parse_json[key]] += 1
                    suffix = ' - ' + str(counts[parse_json[key]])

                    if parse_json[key] != 'benchmark_spec':
                        parse_json[key] += suffix

        # for key in parse_json.keys():
        #     try:
        #         if parse_json[key] in data_list:
                    newdic = parse_json.copy()
        #             if newdic['metric'] != 'benchmark_spec':
        #                 newdic['metric']=newdic['metric']+' - 0'
                    objectdate = datetime.fromtimestamp (newdic['timestamp'])
                    newdic['date']=str(objectdate.strftime("%Y-%m-%d %H:%M:%S"))
                    # print(parse_json['timestamp'])
                    del newdic['timestamp']
                    parse_json = {"value": newdic.pop("value"),'date':newdic.pop("date"),  **newdic}
                    try:
                        parse_json['official']=str(parse_json['official'])
                    except:
                        pass
                    jsonData.append(parse_json)
            except:
                pass
    return jsonData

def get_cpu_load(file_key):
    with open(file_path[file_key]['cpu-load.json']['path'], 'r') as file:
        file_contents = file.read()
    cpu_data = json.loads(file_contents)
    cpu_load = cpu_data['sysstat']['hosts'][0]['statistics']
    return cpu_load

def get_network_data(file_key):
    with open(file_path[file_key]['network.json']['path'], 'r') as file:
        file_contents = file.read()
    network_json = json.loads(file_contents)
    network_load = network_json['sysstat']['hosts'][0]['statistics']
    return network_load

def get_disk_data(file_key):
    with open(file_path[file_key]['disk.json']['path'], 'r') as file:
        file_contents = file.read()
    disk_json = json.loads(file_contents)
    disk_load = disk_json['sysstat']['hosts'][0]['statistics']
    return disk_load

def get_memory_data(file_key):
    with open(file_path[file_key]['memory.json']['path'], 'r') as file:
        file_contents = file.read()
    memory_json = json.loads(file_contents)
    memory_load = memory_json['sysstat']['hosts'][0]['statistics']
    return memory_load

