import os
import requests
import json

import nekoweb_api
from nekoweb_secrets import *
from localconfig import configs



if __name__ == '__main__':
    limits = nekoweb_api.get_limits()
    print(limits.text)

    response = nekoweb_api.get_folder(BASE_PATH)

    directory_data = json.loads(response.text)

    for config in configs:
        country = config['country']
        path_name = config['path_name']
        folders = [token['name'] for token in directory_data if token['dir']]
        if country not in folders:
            response = nekoweb_api.create_folder(country)
            
            if response.ok:
                directory_data.append({'name': country, 'dir': True})
            else:
                print('Error when creating folder')
                print(response.text)
                raise Exception()
        file_path = os.path.join(country, f'{path_name}.html')
        files = {'files': open(os.path.join('output', file_path), 'rb')}
        print(f'Uploading {country}/{file_path}')
        response = nekoweb_api.upload_file(country, files)
        if response.ok:
            print("Succesfully uploaded")
        else:
            print("mi bombo")
            print(response.text)

        
        