import json

import json

# Opening JSON file
f = open('GeneralContractors.json', )

# returns JSON object as
# a dictionary
data = json.load(f)
TennesseeData = {}
# Iterating through the json
# list
j=0
for i in range(len(data)):
    if 'TN' in data[i]['address'] or 'Tennessee' in data[i]['address'] or 'Tennessee' in data[i]['plus-code'] or 'TN' in data[i]['plus-code']:
        if '.gov' not in data[i]['website']:
            TennesseeData[j] = data[i]
            print(data[i])
            j = j+1

# Closing file
f.close()

print(TennesseeData)

with open('data.json', 'w') as outfile:
    json.dump(TennesseeData, outfile)

'''
jsonFile = open("GeneralContractorsCleaned.json", "w")
jsonFile.write(jsonString)
jsonFile.close()
'''