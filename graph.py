import os
import json
from webweb import Web # interactive graph visualization
import networkx as nx
import matplotlib.pyplot as plt

def get_top_n_institutions(names, n):
    institutions = {}
    for name in names:
        i = name['institution']
        if i in institutions:
            institutions[i] += 1
        else:
            institutions[i] = 1
    ranked = sorted(institutions.items(), key=lambda x: x[1], reverse=True)
    if len(ranked) < n:
        return ranked
    else:
        return [i[0] for i in ranked[0:n]]

def get_shortest_path(G, source, target):
    try:
        return len(nx.shortest_path(G, source=source, target=target)) - 1
    except:
        return 'infinity'

def graph(journal):
    with open(journal + '/names.txt', encoding='utf-8-sig') as f:
        names = json.load(f)
    with open(journal + '/coauthors.txt', encoding='utf-8-sig') as f:
        coauthors = json.load(f)

    G = nx.Graph()
    edges = []
    def get_edge_index(a, b):
        for i, edge in enumerate(edges):
            if (edge[0] == a and edge[1] == b) or (edge[0] == b and edge[1] == a):
                return i
        return -1

    # this is so it's easier to see links
    visibility_constant = 10

    # build edge list
    tags_dict = {}
    max_degree = 0
    editor_in_chief_degree = 0
    editor_in_chief = [a for a in names if a['section'].lower() == 'editor-in-chief'][0]['name']
    for name, coauths in coauthors.items():
        G.add_node(name)
        for coauth, weight in coauths.items():
            index = get_edge_index(name, coauth)
            if index == -1:
                edges.append([name, coauth, weight + visibility_constant])
                G.add_edge(name, coauth)
        if len(coauths.items()) > max_degree:
            max_degree = len(coauths.items())
        if name == editor_in_chief:
            editor_in_chief_degree = len(coauths.items())

    # set node properties
    nodes = {}
    journals = []
    top_institutions = get_top_n_institutions(names, 15)
    for author in names:
        n = author['name']
        nodes[n] = {
            'URM': 0 if author['URM'] == 'false' else 1,
            'female': 1 if author['gender'] == 'female' else 0,
            'section': author['section'],
            'institution': author['institution'] if author['institution'] in top_institutions else 'other',
            #'editor-in-chief': 'editor-in-chief' if author['section'].lower() == 'editor-in-chief' else 'other',
            'editor-in-chief': 1 if author['section'].lower() == 'editor-in-chief' else 0,
            'path to editor-in-chief': get_shortest_path(G, author['name'], editor_in_chief)
        }
        if 'journal' in author:
            j = author['journal']
            if j not in journals:
                journals.append(j)
            nodes[n]['journal'] = 0 if author['section'].lower() == 'editor-in-chief' else 1 + journals.index(j)

    web = Web(adjacency = edges, display = {'nodes': nodes}, title=journal)
    web.display.colorBy = 'editor-in-chief'
    web.display.scaleLinkWidth = True
    web.display.showLegend = True
    web.display.radius = 8
    web.display.charge = 600
    web.display.gravity = 0.5
    #web.display.width = 500
    #web.display.height = 500
    web.show()

    # webweb finished
    # moving on to the bar plot
    plt.style.use('ggplot')

    x = [i for i in range(max_degree + 1)]
    counts = [0 for i in range(max_degree + 1)]
    for name, coauths in coauthors.items():
        counts[len(coauths.items())] += 1
    editor_in_chief_count = counts[editor_in_chief_degree]

    p = editor_in_chief_degree # partition index
    bars = plt.bar(x[0:p], counts[0:p], color='cornflowerblue') + plt.bar(p, counts[p], color='red', hatch='//')
    if p < max_degree:
        bars = bars + plt.bar(x[p+1:max_degree+1], counts[p+1:max_degree+1], color='cornflowerblue')
    plt.xlabel('Degree')
    plt.ylabel('Number of editors with degree')
    #plt.title('Plot of editor degrees')

    plt.xticks(x)

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
coauthors = {}
journals = [i for i in os.listdir() if os.path.isdir(i)]
while True:
    print('Pick a journal to graph!')
    choice = input_from_list(['quit'] + ['graph all'] + journals, 'journal')
    if choice == 'quit':
        break
    elif choice == 'graph all':
        for journal in journals:
            graph(journal)
    else:
        graph(choice)
    print('')
