import json
import os

names = []
sofar = set()
journals = os.listdir()
for j in journals:
    if os.path.isfile(j + '/names.txt') and os.access(j + '/names.txt', os.R_OK):
        with open(j + '/names.txt', encoding='utf-8-sig') as f:
            current = json.load(f)
            for author in current:
                if author['name'] not in sofar:
                    sofar.add(author['name'])
                    names.append(author)

with open('all/names.txt', 'w', encoding='utf-8') as f:
    json.dump(names, f, ensure_ascii=False, indent=4)
