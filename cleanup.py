import name_tools as nt
import json

papers = {}
with open('papers.txt', encoding='utf-8-sig') as f:
    papers = json.load(f)

def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

# name_tools.match is slow, so we use a preliminary check to reduce how often we have to call nt.match
def possible_match(name, last_name):
    return last_name in name

# STEP 1: capitalize properly and remove non-alphabetic characters
replacements = {
    '  ': ' ', '-': ' ', '‐': ' ', '[': '', ']': '', '0': '', '1': '', '2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
    'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
    'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    'ç': 'c',
}
def format_name(name):
    # replace non-alphabetic characters
    name = name.lower()
    for r in replacements:
        name = name.replace(r, replacements[r])
    name = name.strip()
    # capitalize properly
    parts = name.split(' ')
    name = ' '.join(i.capitalize() for i in parts)
    if len(parts) == 2 and len(parts[0]) == 2:
        # ex. Dj Rapa --> DJ Rapa
        name = ' '.join([parts[0].upper(), parts[1].capitalize()])
    name = name.strip()
    return name

# format authors and coauthors in papers.txt
formatted_papers = {}
for name in papers:
    formatted = format_name(name)
    formatted_papers[formatted] = {paper: authors for paper, authors in papers[name].items()}
for name, pubs in formatted_papers.items():
    for pub in pubs:
        for i in range(1, len(pubs[pub])):
            pubs[pub][i] = format_name(pubs[pub][i])
papers = formatted_papers
with open('papers.txt', 'w', encoding='utf-8') as f:
    json.dump(papers, f, ensure_ascii=False, indent=4)

# format authors in names.txt
names = []
with open('names.txt', encoding='utf-8-sig') as f:
    names = json.load(f)
formatted_names = []
for name in names:
    formatted_names.append(name)
    formatted_names[-1]['name'] = format_name(name['name'])
names = formatted_names
with open('names.txt', 'w', encoding='utf-8') as f:
    json.dump(names, f, ensure_ascii=False, indent=4)

print('\n\n\nSTEP 1 COMPLETE: FORMATTED NAMES\n\n\n')

# STEP 2: remove the author's name from their own papers
counter = 0
for name, pubs in papers.items():
    counter += 1
    print(f'{counter} / {len(papers.items())}')
    print('-~' * 10)
    # name_tools splits into [prefix, first name plus initial, last name, suffix]
    lowercase_name = format_name(name).lower() # important to format_name so author names have same formatting as coauthors
    last_name = nt.split(name)[2].lower()
    # store a set of ways to refer to the author so we save rechecking each time
    variations = set()
    variations.add(lowercase_name)
    variations.add('')
    for pub in pubs:
        #print(f'{TEMP2} -/- {len(pubs)}')
        authors = pubs[pub]
        if len(authors) == 0 or (not is_int(authors[0]) and authors[0] != 'NO_YEAR'):
            print(f'FLAG: {name} -/- {pub}\n{authors}\n--------')
            continue
        for i in range(1, len(authors)):
            lowercase_author = authors[i].lower()
            if lowercase_author in variations:
                del authors[i]
                break
            if possible_match(lowercase_author, last_name):
                # take advantage of short-circuit evaluation to typically not call nt.match, which is slow
                if lowercase_author == lowercase_name or nt.match(lowercase_author, lowercase_name) >= 0.8:
                    variations.add(lowercase_author)
                    del authors[i]
                    break

with open('papers.txt', 'w', encoding='utf-8') as f:
    json.dump(papers, f, ensure_ascii=False, indent=4)

print('\n\n\nSTEP 2 COMPLETE: REMOVED REDUNDANT AUTHOR NAMES\n\n\n')

# STEP 3: crunch coauthors
coauthors = {}

counter = 0
for name, publications in papers.items():
    counter += 1
    print(f'{counter} / {len(papers.items())} -~ ', end='')
    coauthors[name] = {}
    for title, others in publications.items():
        # Skip empty papers OR the "we-thank-the-editors" type papers.
        t = title.lower()
        if others is None or 'editor' in t or (('thank' in t or 'acknowledg' in t) and ('review' in t or 'referee' in t)) or (is_int(others[0]) and int(others[0]) < 1980):
            continue
        for other in others[1:]: # coauthors start at index 1, after the year
            if other not in coauthors[name]:
                coauthors[name][other] = 1
            else:
                coauthors[name][other] += 1

with open('coauthors.txt', 'w', encoding='utf-8') as f:
    json.dump(coauthors, f, ensure_ascii=False, indent=4)

print('\n\n\nSTEP 3 COMPLETE: CRUNCHED COAUTHORS\n\n\n')

# STEP 4: delete non-department-editor coauthors, plus expand names
dept_editor_last_names = set()
last_name_to_full_name = {}
for name in names:
    last_name = name['name'].split(' ')[-1].lower()
    dept_editor_last_names.add(last_name)
    last_name_to_full_name[last_name] = name['name']

formatted_coauthors = {}
# whitelist stores valid ways to refer to department editors
# (i.e. include "B Bushee" because "Brian Bushee" is an editor)
# blacklist stores invalid ways to refer to department editors
# (i.e. include "R Ranarana" because no one is named that)
whitelist = set()
blacklist = set()
counter = 0
for name, coauths in coauthors.items():
    counter += 1
    print(f'{counter} / {len(coauthors.items())}')
    print('-~' * 10)
    formatted_coauthors[name] = {}
    for coauth, weight in coauths.items():
        last_name = coauth.split(' ')[-1].lower()
        if last_name not in dept_editor_last_names:
            continue
        # full_name is what the name should be, i.e. 'Brian Bushee'
        # coauth might be 'B Bushee' or 'R Bushee'
        full_name = last_name_to_full_name[last_name]
        if coauth not in whitelist:
            if nt.match(coauth, full_name) >= 0.8:
                whitelist.add(coauth)
            else:
                blacklist.add(coauth)
                continue
        if full_name not in formatted_coauthors[name]:
            formatted_coauthors[name][full_name] = weight
        else:
            formatted_coauthors[name][full_name] += weight

coauthors = formatted_coauthors
with open('coauthors.txt', 'w', encoding='utf-8') as f:
    json.dump(coauthors, f, ensure_ascii=False, indent=4)

print('\n\n\nSTEP 4 COMPLETE: FORMATTED COAUTHORS\n\n\n')

def undirect(coauthors):
    # We want an undirected graph, but because Google Scholar is imperfect, we sometimes
    # get data that says John Smith has coauthored 12 papers with Sandy Roland, while
    # Sandy Roland has only coauthored 11 papers with John Smith. This function takes a
    # maximum to fix these anomalies and create an approximate undirected graph.
    for name, coauths in coauthors.items():
        for coauth, weight in coauths.items():
            us = weight
            them = coauthors[coauth][name] if name in coauthors[coauth] else 0
            coauths[coauth] = max(us, them)
            coauthors[coauth][name] = max(us, them)
    return coauthors

coauthors = undirect(coauthors)
with open('coauthors.txt', 'w', encoding='utf-8') as f:
    json.dump(coauthors, f, ensure_ascii=False, indent=4)

print('\n\n\nSTEP 5 COMPLETE: MADE GRAPH UNDIRECTED\n\n\n')
