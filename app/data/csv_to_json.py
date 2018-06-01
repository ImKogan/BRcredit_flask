import json
import csv
from collections import defaultdict
from pprint import pprint

with open('STI-20180601162514566.csv') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['Date', 'Credit_Card_Revolving_Credit_APR'])
    dict_list = []
    for line in reader:
        dict_list.append(line)

dict_list = dict_list[1:]
pprint(dict_list)

data = defaultdict(list)
keys = list(dict_list[0].keys())

for d in dict_list:
    data[keys[0]].append(d[keys[0]])
    data[keys[1]].append(d[keys[1]])
pprint(data)

with open('cc_apr.json', 'w') as f:
    json.dump(data, f)
