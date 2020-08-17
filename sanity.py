import name_tools as nt
import pyperclip
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

def input_from_list(l, prompt):
    for i in range(len(l)):
        print('  ' + str(i + 1) + ': ' + str(l[i]))
    while True:
        choice = input(prompt + '>')
        if not is_int(choice) or int(choice) < 1 or int(choice) > len(l):
            print('Please enter an integer between 1 and ' + str(len(l)) + '.')
        else:
            return l[int(choice) - 1]
def get_yes_no(prompt):
    while True:
        a = input(prompt).lower()
        if a == 'yes' or a == 'y':
            return True
        elif a == 'no' or a == 'n':
            return False
        else:
            print('Please type yes or no.')

board_full_names = {name.split(' ')[-1]: name for name in papers}
board_last_names = [name.split(' ')[-1] for name in papers]
board_names_found = []

name = input_from_list([i[0] for i in papers.items()], 'Who are we checking on today?')
main_last_name = name.split(' ')[-1]

coauthors = {}
for n, publications in papers.items():
    for title, others in publications.items():
        if n.split(' ')[-1] in board_names_found:
            continue
        t = title.lower()
        if others is None or (('thank' in t or 'acknowledge' in t) and ('review' in t or 'referee' in t)):
            continue
        if n == name:
            # Check whether the author has written papers with others.
            for other in others[1:]: # coauthors start at index 1, after the year
                last_name = other.split(' ')[-1]
                if other not in coauthors and last_name in board_last_names and last_name not in board_names_found and nt.match(board_full_names[last_name].lower(), other.lower()) >= 0.8:
                    pyperclip.copy(title)
                    if get_yes_no('Is this a valid paper for ' + board_full_names[last_name] + '?\n\t' + str(title) + ' --/-- ' + str(others[0]) + '\ny/n>'):
                        coauthors[other] = title + ' ---/--- ' + str(others[0])
                        board_names_found.append(last_name)
        else:
            # Check whether others have written papers with the author.
            for other in others[1:]: # coauthors start at index 1, after the year
                if other.split(' ')[-1].lower() == main_last_name.lower() and nt.match(other.lower(), name.lower()) >= 0.8:
                    pyperclip.copy(title)
                    if get_yes_no('Is this a valid paper for ' + n + '?\n\t' + str(title) + ' --/-- ' + str(others[0]) + '\ny/n>'):
                        coauthors[n] = title + ' ---/--- ' + str(others[0])
                        board_names_found.append(n.split(' ')[-1])
                        break

with open(name + ' SANITY CHECK.txt', 'w', encoding='utf-8') as f:
    json.dump(coauthors, f, ensure_ascii=False, indent=4)
