import json

# Open the JSON file
with open('data/multiarith/test.json', 'r') as file:
    data = json.load(file)

# Now 'data' is a Python dictionary (or list, depending on the JSON structure)
print(data[:5])
print(json.dumps(data[:5], indent=4))