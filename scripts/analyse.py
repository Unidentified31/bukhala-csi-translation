import re
from collections import Counter, defaultdict
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from scipy.stats import chi2_contingency
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / 'results'
OUT.mkdir(exist_ok=True)
GROUP = {'Pure borrowing': 'Foreignising', 'Naturalised borrowing': 'Foreignising', 'Literal translation': 'Foreignising', 'Description': 'Neutralising', 'Generalisation': 'Neutralising', 'Particularisation': 'Neutralising', 'Amplification': 'Neutralising', 'Compression': 'Neutralising', 'Intracultural adaptation': 'Domesticating', 'Intercultural adaptation': 'Domesticating', 'Omission': 'Domesticating'}
ORDER_T = list(GROUP)
ORDER_G = ['Foreignising', 'Neutralising', 'Domesticating']
CATS = ['Dish', 'Ingredient', 'Vessel/household', 'Money/measure', 'Clothing']
ws = load_workbook(HERE / 'classification_data.xlsx', read_only=True)['Classification']
rows = list(ws.iter_rows(values_only=True))
H = rows[0]
R = [dict(zip(H, r)) for r in rows[1:]]
valid = [r for r in R if str(r['valid']).strip().lower() == 'yes']
ana = [r for r in valid if r['technique'] in GROUP]
excl = Counter((r['technique'] for r in valid if r['technique'] not in GROUP))

def pct(a, b):
    return round(100 * a / b, 1) if b else 0

def norm_r(s):
    s = re.sub("[’']s\\b", '', str(s).lower().strip())
    return re.sub('(?<=[a-z]{3})s\\b', '', s)
wb = Workbook()
first = True

def sheet(name, header, body):
    global first
    w = wb.active if first else wb.create_sheet()
    first = False
    w.title = name
    w.append(header)
    for c in w[1]:
        c.font = Font(bold=True)
    for b in body:
        w.append(b)
sheet('T1 Overview', ['', 'n'], [['Candidates', len(R)], ['Valid', len(valid)]] + [[f'Excluded: {k}', v] for k, v in excl.items()] + [['Analysed', len(ana)]])
tc = Counter((r['technique'] for r in ana))
sheet('T2 Techniques', ['Technique', 'Group', 'n', '%'], [[t, GROUP[t], tc[t], pct(tc[t], len(ana))] for t in ORDER_T])
gc = Counter((GROUP[r['technique']] for r in ana))
sheet('T3 Groups', ['Group', 'n', '%'], [[g, gc[g], pct(gc[g], len(ana))] for g in ORDER_G])
tab = [[sum((1 for r in ana if r['category'] == c and GROUP[r['technique']] == g)) for g in ORDER_G] for c in CATS]
chi2, p, dof, _ = chi2_contingency(tab)
n = sum(map(sum, tab))
V = (chi2 / (n * (min(len(CATS), 3) - 1))) ** 0.5
body = []
for c, row in zip(CATS, tab):
    s = sum(row)
    body.append([c, s] + [f'{x} ({pct(x, s)}%)' for x in row])
body.append([f"Chi-square({dof}) = {chi2:.2f}, p = {p:.2g}, Cramér's V = {V:.2f}"])
sheet('T4 Groups by category', ['Category', 'n'] + ORDER_G, body)
_tot = sum(map(sum, tab))
_rs = [sum(r) for r in tab]
_cs = [sum(c) for c in zip(*tab)]
resid = [[round((tab[i][j] - _rs[i] * _cs[j] / _tot) / (_rs[i] * _cs[j] / _tot * (1 - _rs[i] / _tot) * (1 - _cs[j] / _tot)) ** 0.5, 1) for j in range(len(ORDER_G))] for i in range(len(CATS))]
sheet('T4b Residuals', ['Category'] + ORDER_G, [[c] + r for c, r in zip(CATS, resid)])

import random
from scipy.stats import kruskal
_terms = defaultdict(list); _tcat = {}
for r in ana:
    _terms[r["term"]].append(GROUP[r["technique"]]); _tcat[r["term"]] = r["category"]
_share = {t: v.count("Foreignising") / len(v) for t, v in _terms.items()}
_groups = [[_share[t] for t in _terms if _tcat[t] == c] for c in CATS]
kw_h, kw_p = kruskal(*_groups)
def _chi(lab):
    tb = [[0] * len(ORDER_G) for _ in CATS]
    for t, v in _terms.items():
        for g in v:
            tb[CATS.index(lab[t])][ORDER_G.index(g)] += 1
    return chi2_contingency(tb)[0]
_ts = list(_terms); _labs = [_tcat[t] for t in _ts]; _rng = random.Random(2027); _ge = 0
for _ in range(10000):
    _rng.shuffle(_labs)
    if _chi(dict(zip(_ts, _labs))) >= chi2 - 1e-9:
        _ge += 1
perm_p = (_ge + 1) / 10001
sheet("T4c Term-level", ["Test", "Result"],
      [["Terms", len(_terms)],
       ["Kruskal-Wallis on share of foreignising per term", f"H(4) = {kw_h:.2f}, p = {kw_p:.2g}"],
       ["Median share of foreignising per term (%)", ", ".join(f"{c} {100 * sorted(g)[len(g) // 2] if len(g) % 2 else 100 * (sorted(g)[len(g) // 2 - 1] + sorted(g)[len(g) // 2]) / 2:.0f}" for c, g in zip(CATS, _groups))],
       ["Permutation test (domains reassigned to terms, 10,000 runs, seed 2027)", f"p = {perm_p:.4f}"]])
print(f"term-level: KW H={kw_h:.2f} p={kw_p:.2g}; permutation p={perm_p:.4f}")
ct = defaultdict(Counter)
for r in ana:
    ct[r['category']][r['technique']] += 1
sheet('T5 Techniques by category', ['Technique'] + CATS, [[t] + [ct[c][t] for c in CATS] for t in ORDER_T])
terms = defaultdict(list)
for r in ana:
    terms[r['category'], r['term']].append(r)
body = []
for (c, t), rs in sorted(terms.items(), key=lambda kv: (CATS.index(kv[0][0]), -len(kv[1]))):
    rend = Counter((norm_r(r['en_rendering']) for r in rs if r['en_rendering']))
    top, topn = rend.most_common(1)[0] if rend else ('—', 0)
    tech = Counter((r['technique'] for r in rs)).most_common(1)[0]
    g = Counter((GROUP[r['technique']] for r in rs))
    body.append([c, t, len(rs), len(rend), top, pct(topn, len(rs)), f'{tech[0]} ({tech[1]})', g['Foreignising'], g['Neutralising'], g['Domesticating']])
sheet('T6 Terms', ['Category', 'Term', 'n', 'Distinct renderings', 'Most frequent', 'Its share %', 'Main technique', 'Foreign.', 'Neutral.', 'Domest.'], body)
wb.properties.creator = None
wb.save(OUT / 'results_tables.xlsx')
print(f'candidates={len(R)} valid={len(valid)} excluded={dict(excl)} analysed={len(ana)}')
print('groups:', {g: (gc[g], pct(gc[g], len(ana))) for g in ORDER_G})
for c, row in zip(CATS, tab):
    s = sum(row)
    print(f'  {c:17s} n={s:3d} ' + '  '.join((f'{g[:5]}={pct(x, s)}%' for g, x in zip(ORDER_G, row))))
print(f'chi2({dof})={chi2:.2f} p={p:.4g} V={V:.2f}')
print('techniques:', tc.most_common())
