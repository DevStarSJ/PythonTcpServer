import json
from pprint import pprint

def get_appsettings():
    with open('appsettings.json') as data_file:
        return json.load(data_file)

if __name__ == "__main__":
    pprint(get_appsettings())
