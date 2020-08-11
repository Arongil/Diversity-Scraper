import json
import pyperclip

with open('silly_splitter.txt', 'w', encoding='utf-8') as f:
    pass

chunk_size = 10000 # in characters
while True:
    print('Paste text into silly_splitter.txt.')
    input('continue>')

    with open('silly_splitter.txt', encoding='utf-8-sig') as f:
        silly = f.read()

    if len(silly) <= chunk_size:
        pyperclip.copy(silly)
        print('Done splitting!\n')
        continue

    i = 0
    chunks = len(silly) // chunk_size + 1
    for i in range(chunks - 1):
        pyperclip.copy(silly[i*chunk_size : (i+1)*chunk_size])
        input('copied ' + str(i + 1) + '/' + str(chunks) + '>')
    pyperclip.copy(silly[(chunks - 1)*chunk_size:len(silly)])
    input('copied ' + str(chunks) + '/' + str(chunks) + '>')
    print('Done splitting!\n')
