import os
import json
import matplotlib.pyplot as plt

def simplify(university):
    parts = university.split(' ')
    rejoined = ' '.join([(part if part.lower() != 'university' else 'U') for part in parts])
    return rejoined

def get_top_n_institutions(names, n):
    institutions = {}
    for name in names:
        i = name['institution']
        if i in institutions:
            institutions[i] += 1
        else:
            institutions[i] = 1
    ranked = sorted(institutions.items(), key=lambda x: x[1], reverse=True)
    return ranked[0:min(n, len(ranked) - 1)]

def graph(journal):
    with open(journal + '/names.txt', encoding='utf-8-sig') as f:
        names = json.load(f)

    all_institutions = get_top_n_institutions(names, 99999)
    print('Out of ' + str(len(all_institutions)))
    n = 7
    top_institutions = get_top_n_institutions(names, n)
    plt.style.use('ggplot')

    x = range(len(top_institutions))
    counts = [i[1] for i in top_institutions]


    inst_names = [i[0] for i in top_institutions]
    editor_in_chief_institution = [a['institution'] for a in names if a['section'].lower() == 'editor-in-chief'][0]
    if editor_in_chief_institution not in inst_names:
        p = len(top_institutions)
        plt.bar(x, counts, color='cornflowerblue')
    else:
        p = [i for i in range(len(inst_names)) if inst_names[i] == editor_in_chief_institution][0]
        bars = plt.bar(x[0:p], counts[0:p], color='cornflowerblue') + plt.bar(p, counts[p], color='red', hatch='//')
        if p < n:
            bars = bars + plt.bar(x[p+1:n+1], counts[p+1:n+1], color='cornflowerblue')

    #plt.xlabel('Home Institution')
    plt.ylabel('Number of Editors')
    #plt.title('Plot of Home Institutions')

    plt.xticks(x, [simplify(i[0]) for i in top_institutions])
    plt.xticks(rotation=45, fontsize=18, ha='right')

    plt.rc('axes', labelsize=20)

    plt.show()

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

names = {}
journals = [i for i in os.listdir() if os.path.isdir(i)]
while True:
    print('Pick a journal to institutionalize!')
    choice = input_from_list(['quit'] + ['institutionalize all'] + journals, 'journal')
    if choice == 'quit':
        break
    elif choice == 'institutionalize all':
        for journal in journals:
            graph(journal)
    else:
        graph(choice)
    print('')
