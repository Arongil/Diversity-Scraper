import os
import json

def analyze(names, coauthors):
    stats = {
        'editors_total': 0,
        'editors_men': 0,
        'editors_women': 0,
        'editors_URM': 0,
        'degree_total': 0,
        'degree_total_men': 0,
        'degree_total_women': 0,
        'degree_max': 0,
        'degree_average': 0,
        'degree_average_men': 0,
        'degree_average_women': 0,
        'degrees_editors_in_chief': [],
        'isolated_nodes': 0,
        'institutions': 0
    }
    stats['editors_total'] = len(coauthors.items())
    institutions = []
    for author in names:
        name = author['name']
        coauths = coauthors[name]
        cur_degree = len(coauths.items())
        stats['degree_total'] += cur_degree
        if author['gender'] == 'male':
            stats['editors_men'] += 1
            stats['degree_total_men'] += cur_degree
        else:
            stats['editors_women'] += 1
            stats['degree_total_women'] += cur_degree
        if author['URM'] == 'true':
            stats['editors_URM'] += 1
        if author['section'].lower() == 'editor-in-chief':
            stats['degrees_editors_in_chief'].append(cur_degree)
        if cur_degree > stats['degree_max']:
            stats['degree_max'] = cur_degree
        if cur_degree == 0:
            stats['isolated_nodes'] += 1
        if author['institution'] not in institutions:
            institutions.append(author['institution'])
    stats['degree_average'] = round(stats['degree_total'] / stats['editors_total'], 1)
    stats['degree_average_men'] = round(stats['degree_total_men'] / stats['editors_men'], 1)
    stats['degree_average_women'] = round(stats['degree_total_women'] / stats['editors_women'], 1)
    stats['normalized_degree_average'] = round(stats['degree_total'] / (stats['editors_total']*(stats['editors_total']-1)), 3)
    stats['institutions'] = len(institutions)
    return stats

statistics = {}
journals = os.listdir()
for j in journals:
    if os.path.isfile(j + '/names.txt') and os.access(j + '/names.txt', os.R_OK) and os.path.isfile(j + '/coauthors.txt') and os.access(j + '/coauthors.txt', os.R_OK):
        with open(j + '/names.txt', encoding='utf-8-sig') as f:
            names = json.load(f)
        with open(j + '/coauthors.txt', encoding='utf-8-sig') as f:
            coauthors = json.load(f)
        journal_stats = analyze(names, coauthors)
        statistics[j] = journal_stats

with open('stats.txt', 'w', encoding='utf-8') as f:
    json.dump(statistics, f, ensure_ascii=False, indent=4)
