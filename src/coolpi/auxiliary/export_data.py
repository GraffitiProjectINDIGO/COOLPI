import json
import os

def export_dict_as_json(data_as_dict, path_json):
    '''
    Function to export data as `dict` to a JSON file

    Parameters:
        data_as_dict    dict    Data to export
        path_json       os      Output JSON file
        
    '''

    with open(path_json, 'w') as fp:
        json.dump(data_as_dict, fp)
