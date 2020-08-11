import os
import json

def open_from_path(p, default):
    if os.path.isfile(p) and os.access(p, os.R_OK):
        with open(p, encoding='utf-8-sig') as f:
            return json.load(f)
    return default

def combine(combo):
    names = []
    papers = {}
    sofar = set()
    for j in combo:
        current = open_from_path(j + '/names.txt', {})
        for author in current:
            name = author['name']
            if name not in sofar:
                sofar.add(name)
                author['journal'] = j
                names.append(author)
                papers[name] = all_papers[name]

    combo_name = 'COMBO ' + ' + '.join([''.join(n[0] for n in j.split(' ')) for j in combo])
    os.mkdir(combo_name)
    with open(combo_name + '/names.txt', 'w', encoding='utf-8') as f:
        json.dump(names, f, ensure_ascii=False, indent=4)
    with open(combo_name + '/papers.txt', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=4)

def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

def input_from_list(l, prompt):
    for i in range(len(l)):
        print('  ' + str(i + 1) + ': ' + str(l[i]))
    while True:
        choice = input(prompt + '>')
        if not is_int(choice) or int(choice) < 1 or int(choice) > len(l):
            print('Please enter an integer between 1 and ' + str(len(l)) + '.')
        else:
            return l[int(choice) - 1]

combo = []
all_papers = open_from_path('all_papers.txt', {})
journals = [i for i in os.listdir() if os.path.isdir(i)]
while True:
    print('Pick journals to combine!')
    choice = input_from_list(['quit', 'combine'] + journals, 'journal')
    if choice == 'quit':
        break
    elif choice == 'combine' and len(combo) > 1:
        combine(combo)
        combo = []
        print('\nCombined!\n')
        continue
    else:
        combo.append(choice)
        print('\nSo far, you are combining ' + str(combo) + '.\n')
