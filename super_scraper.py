import traceback
import os

from fp.fp import FreeProxy
from scholarly import scholarly
import name_tools as nt
import json

# if Google Scholar rejects query, try with three proxies before giving up
# sometimes the only option is to wait an hour for the rate-limiting to ease up
def new_proxy():
    print('Trying new proxy... ', end='')
    proxy = FreeProxy().get()
    scholarly.use_proxy(http=proxy, https=proxy)
    print('Secured...')

def proxy_try(func, parameter):
    try:
        result = func(parameter)
        print('Success!')
        return result
    except KeyboardInterrupt:
        raise
    except:
        # if unsuccessful, stop but get a new proxy for next time
        print('Unsuccessful... ', end='')
        new_proxy()
        traceback.print_exc()
        return False

def get_scholars(query):
    return [a for a in scholarly.search_author(query)]
def get_publications(author):
    return author.fill(sections=['publications']).publications
def fill_publication(publication):
    return publication.fill()
# Uncomment to enable manual HTML entering
# scholarly.manual = True
def search_publications(query):
    unrelated = 0
    publications = []
    last_name = nt.split(query)[2].lower()
    # To enable manual HTML entering, set scholarly.manual = True.
    pubs = scholarly.search_pubs(query, False, False)
    for pub in pubs:
        for author in pub.bib['author']:
            if last_name in format_name(author).lower():
                unrelated = 0
                pub.bib['author'] = ' and '.join(pub.bib['author'])
                publications.append(pub)
                break
        else:
            unrelated += 1
            if unrelated > 5:
                break
    return publications

def refill_authors(publication):
    # returns authors of a publication
    # use as a last resort because it requires another call to Google Scholar
    print('Refilling publication: "' + str(publication.bib['title']) + '" --/-- ', end='')
    filled = proxy_try(fill_publication, publication)
    if filled == False or 'author' not in filled.bib:
        return []
    return filled.bib['author'].split(' and ')

def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

def get_authors(publication):
    if 'author' in publication.bib and '...' not in publication.bib['author']:
        authors = publication.bib['author'].split(' and ')
    else:
        # if '...' was in authors list, then there were too many to display at first
        authors = refill_authors(publication)
    year = publication.bib['year'] if 'year' in publication.bib else 'NO_YEAR'
    if not is_int(year):
        year = 'NO_YEAR'
    authors.insert(0, year)
    return authors

def simplify_name(name):
    # Goal: convert 'Laker J. Newhouse, Jr.' to 'Laker Newhouse',
    # but keep 'L. Joseph Newhouse' the same.
    split_name = nt.split(name)
    split_first = split_name[1].split(' ')
    if len(split_first[-1]) <= 2: # i.e. the 'J.' (or just 'J')
        return ' '.join(split_first[:-1]) + ' ' + split_name[2]
    else:
        return split_name[1] + ' ' + split_name[2]

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
    for r in replacements:
        name = name.replace(r, replacements[r])
    name = name.strip()
    # capitalize properly
    parts = name.split(' ')
    name = ' '.join(i.capitalize() for i in parts)
    if len(parts) == 2 and len(parts[0]) == 2:
        # ex. Dj Rapa --> DJ Rapa
        name = ' '.join([parts[0].upper(), parts[1]])
    name = name.strip()
    return name

# ---------------------------------------
# for each name:
# 1. find all publications
# 2. find all authors of each publication
# 3. compile author data
# ---------------------------------------
with open('names.txt', encoding='utf-8-sig') as f:
    names = json.load(f)

def open_from_path(p, default):
    if os.path.isfile(p) and os.access(p, os.R_OK):
        with open(p, encoding='utf-8-sig') as f:
            return json.load(f)
    return default

blacklist = open_from_path('blacklist.txt', [])
def add_to_blacklist(name):
    print('-- BLACKLISTED -- ' + str(name))
    blacklist.append(name)
    with open('blacklist.txt', 'w', encoding='utf-8') as f:
        json.dump(blacklist, f, ensure_ascii=False, indent=4)

dead_queries = open_from_path('dead_queries.txt', {})
def add_to_dead_queries(query):
    print('-- DEAD QUERY -- ' + str(query))
    dead_queries[query] = True
    with open('dead_queries.txt', 'w', encoding='utf-8') as f:
        json.dump(dead_queries, f, ensure_ascii=False, indent=4)

papers = open_from_path('papers.txt', {})
all_papers = open_from_path('../all_papers.txt', {})

def scrape():
    # return whether we still need more info; if not, we are done
    incomplete = False

    counter = 0
    for n in names:
        name = n['name']
        institution = n['institution']
        counter += 1
        print(str(counter) + ' / ' + str(len(names)))
        print('#' * 30)

        # skip names in the blacklist, because they are ambiguous
        if name in blacklist:
            continue

        # check whether we have the author's publications already
        if name in papers:
            for p, authors in papers[name].items():
                if authors is None or len(authors) == 0 or not (authors[0] == 'NO_YEAR' or is_int(authors[0])):
                    break
            else:
                continue
        elif format_name(name) in all_papers:
            papers[name] = all_papers[format_name(name)]
            with open('papers.txt', 'w', encoding='utf-8') as f:
                json.dump(papers, f, ensure_ascii=False, indent=4)
            continue

        # Search strategy:
        # 1. Try "[author name]" + [university], ex. "David Simchi-Levi" Massachusetts Institute of Technology
        # 2. If one author found, done. If zero found, remove quotes and retry step 1. If still none, remove university information. If more than one found, go to step 3. If still none, go to step 4.
        # 3. List all authors. If only only one has the correct affiliation or email, pick them. Else, go to step 4.
        # 4. Search publications with the query "Author Name". Take all publications with an author as "Author Name". If none, terminate and add to author blacklist.
        print(f'Finding {name}...')
        queries = [f'"{name}" {institution}', f'{name} {institution.split(",")[0]}', name, simplify_name(name)]
        authors = []
        for query in queries:
            if query in dead_queries:
                continue
            authors = proxy_try(get_scholars, query)
            if authors == False: # proxy error
                continue
            elif len(authors) == 0:
                add_to_dead_queries(query)
            elif len(authors) > 0:
                break
        if authors == False:
            # We don't want to move forward (searching publications directly) just because our proxies failed.
            incomplete = True
            continue

        if len(authors) > 1: # multiple authors, so check affiliations and email
            possible_authors = []
            # find keywords, i.e. "Massachusettes Institute of Technology" --> ["Massachusettes", "Technology"]
            # ignore locations after commas, i.e. "University of Minnesota, Minneapolis" --> ["Minnesota"]
            # find possible institution acronym, i.e. "MIT" or "UCLA"
            ignore = ['university', 'college', 'institute', 'of', 'at', 'and', 'the']
            institution_keywords = [w.lower() for w in institution.split(' ') if w.lower() not in ignore]
            institution_acronym = ''.join(w[0].lower() for w in institution.split(' ') if w.lower() not in ['of', 'at', 'and', 'the'])
            institution_keywords.append(institution_acronym)
            for author in authors:
                try:
                    affiliation = author.affiliation.lower()
                    email = author.email.lower()
                except:
                    continue
                possible = False
                for i in institution_keywords:
                    if i in affiliation or i in email: # Ex. "chicago" in "@chicagobooth.edu"
                        possible = True
                        break
                if possible and nt.match(author.name, name) >= 0.8:
                    possible_authors.append(author)
            if len(possible_authors) > 0:
                # It's more accurate to take the most relevant author than to direct search publications.
                # That's why we don't direct search if possible authors has no elements.
                authors = possible_authors

        if len(authors) == 0:
            print("Searching publications directly...")
            pubs = []#proxy_try(search_publications, queries[-1])
        elif len(authors) > 0:
            # get publications (if multiple authors, assume first is most relevant)
            print("Getting author's publications...")
            pubs = proxy_try(get_publications, authors[0])

        if pubs == False:
            incomplete = True
            continue
        elif len(pubs) == 0:
            add_to_blacklist(name)
            continue

        if name not in papers:
            papers[name] = {}
        existing_pubs = papers[name]
        for i, pub in enumerate(pubs):
            print(str(i + 1) + ' -/- ' + str(len(pubs)))
            if pub.bib['title'] in existing_pubs:
                continue
            papers[name][pub.bib['title']] = get_authors(pub)
        with open('papers.txt', 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=4)

    return incomplete

while scrape():
    print("\n\n\n\nGOING AGAIN\n\n\n\n")
