import json
import os

papers = {}
journals = os.listdir()
for j in journals:
    if os.path.isfile(j + '/papers.txt') and os.access(j + '/papers.txt', os.R_OK):
        with open(j + '/papers.txt', encoding='utf-8-sig') as f:
            current = json.load(f)
            for author, publications in current.items():
                if author not in papers:
                    papers[author] = publications

with open('all_papers.txt', 'w', encoding='utf-8') as f:
    json.dump(papers, f, ensure_ascii=False, indent=4)
