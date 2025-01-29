import os
import json

def create_structure(config_file):
    with open(config_file) as f:
        structure = json.load(f)
    
    for file_info in structure['data']:
        path = file_info['filepath']
        content = file_info['content']
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

if __name__ == '__main__':
    create_structure('structure.json')
