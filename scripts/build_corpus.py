import bisect
import csv
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / 'Colville_corpus' / 'pages'
OCR = ROOT / 'Colville_corpus' / 'Colville_1999_OCR.txt'
OUT = ROOT / 'analysis' / 'corpus_aligned.csv'
HEADER = re.compile('^\\s*نسخة تجريبية.*?النتائج من\\s*\\d+\\s*-\\s*إلى\\s*\\d+\\s*')

def parse(path):
    raw = path.read_text(encoding='utf-8-sig')
    parts = re.split('(?:^|\\n)\\[(\\d+)\\]\\n', raw)
    return [(int(parts[k]), parts[k + 1].strip()) for k in range(1, len(parts), 2)]

def norm(x):
    x = re.sub('-\\s*\\n\\s*', '', x.lower())
    x = re.sub('[^a-z ]+', ' ', x)
    return re.sub('\\s+', ' ', x)
chunks = re.split('=====PAGE p-(\\d+)\\.png', OCR.read_text(errors='ignore'))
book, starts, pdfpage = ('', [], [])
for k in range(1, len(chunks), 2):
    starts.append(len(book))
    pdfpage.append(int(chunks[k]))
    book += norm(chunks[k + 1]) + ' '

def locate(english):
    w = norm(english).split()
    for i in range(0, max(1, len(w) - 5), 2):
        shingle = ' '.join(w[i:i + 6])
        if len(shingle.split()) < 6:
            break
        j = book.find(shingle)
        if j >= 0:
            return pdfpage[bisect.bisect_right(starts, j) - 1]
    return None
pages = sorted((int(re.search('page_(\\d+)_', p.name).group(1)) for p in PAGES.glob('page_*_english.txt')))
seq = [p for p in pages if p != 1] + [1]
rows, headers_removed = ([], 0)
for p in seq:
    ar, en = (parse(PAGES / f'page_{p}_arabic.txt'), parse(PAGES / f'page_{p}_english.txt'))
    assert [n for n, _ in ar] == [n for n, _ in en], p
    for (n, a), (_, e) in zip(ar, en):
        a2 = HEADER.sub('', a)
        headers_removed += a2 != a
        rows.append({'rasaif_page': p, 'segment': n, 'arabic': a2, 'english': e})
rows.reverse()
for i, r in enumerate(rows, 1):
    r['pair_id'] = i
    r['pdf_page'] = locate(r['english'])
    r['ar_words'], r['en_words'] = (len(r['arabic'].split()), len(r['english'].split()))
EXCLUDE = {222, 683, 927}
rows = [r for r in rows if r['pair_id'] not in EXCLUDE]
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, ['pair_id', 'rasaif_page', 'segment', 'pdf_page', 'ar_words', 'en_words', 'arabic', 'english'])
    w.writeheader()
    w.writerows(rows)
print(f"pairs={len(rows)}  headers removed={headers_removed}  located={sum((r['pdf_page'] is not None for r in rows))}")
