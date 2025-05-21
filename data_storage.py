import json

def save_data(data, filename='data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_data(filename='data.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}