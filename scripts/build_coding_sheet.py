import csv
import re
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
HERE = Path(__file__).resolve().parents[1]
PRE = '(?:^|[\\s«\\"(])(?:و|ف)?(?:ب|ل|ك)?(?:ال|لل)?'
SUF = '(?:ه|ها|هم|هما|ي|ك|كم|نا|ات|ين|ان|ا)?(?=[\\s،.؟!:»\\")]|$)'
EN = {'tharīd': 'broth|stew|crumb|tharid', 'maraq': 'broth|gravy|sauce|soup|stock', 'shiwāʾ': 'roast|grill|spit|kebab', 'harīsa': 'harisa|harissa|porridge|gruel|stew|pudding', 'ruqāq': 'flatbread|wafer|thin|bread', 'ḥays': 'hays|pudding|dates', 'ʿaṣīda': 'porridge|pudding|gruel', 'fālūdhaj': 'marzipan|sweet|faludh|jelly|nougat', 'khabīṣ': 'pudding|sweet|custard|khabis', 'sikbāj': 'vinegar|pickled|sikbaj|stew', 'ṭabāhaj': 'fried|slices|tabahaj', 'jūdhāb': 'pudding|judhab', 'sawīq': 'meal|porridge|gruel|sawiq', 'jawārishn': 'digestive|tonic|electuary|sweet', 'libaʾ': 'beestings|colostrum|milk', 'raghīf': 'loaf|loaves|bread|roll', 'ḥuwwārā': 'white|fine|bread|flour', 'raʾs': 'head', 'ruṭab': 'dates|fresh|ripe', 'samn': 'ghee|butter|fat', 'udm': 'relish|condiment|dip|sauce', 'nabīdh': 'wine|nabidh|drink|liquor|date', 'khiwān': 'table|tray|board', 'māʾida': 'table|spread|meal|repast', 'qaṣʿa': 'bowl|dish|platter|basin', 'qidr': 'pot|cauldron|pan|kettle', 'ṭabaq': 'dish|platter|plate|tray', 'ṭast': 'basin|bowl|tub', 'mindīl': 'napkin|towel|cloth|handkerchief', 'sufra': 'mat|cloth|table|spread', 'tannūr': 'oven|tannur|kiln', 'miṣbāḥ': 'lamp|light|lantern', 'misraja': 'lamp|lantern', 'sirāj': 'lamp|light', 'fatīla': 'wick', 'ushnān': 'potash|soap|lye|washing|ushnan', 'bakhūr': 'incense|perfume|smoke', 'nūra': 'depilatory|lime|nura', 'dirham': 'dirham', 'dīnār': 'dinar', 'fals': 'fils|fals|copper|penny|coin', 'dāniq': 'daniq|danaq|sixth|farthing|coin', 'qīrāṭ': 'qirat|carat', 'raṭl': 'ratl|pound|rotl', 'makkūk': 'makkuk|measure|bushel', 'mudd': 'mudd|measure|handful', 'qamīṣ': 'shirt|tunic|robe|smock|chemise', 'thawb': 'garment|cloth|clothes|robe|dress|gown|shirt|outfit', 'kisāʾ': 'cloak|wrap|mantle|blanket|garment', 'jubba': 'coat|gown|jubba|robe|cloak', 'ṭaylasān': 'shawl|scarf|taylasan|hood', 'ʿimāma': 'turban', 'ridāʾ': 'cloak|mantle|wrap|robe', 'izār': 'wrap|waist|loincloth|sheet|cloth', 'khuff': 'boot|slipper|sock|shoe', 'naʿl': 'sandal|shoe|sole', 'qalansuwa': 'cap|hat|bonnet', 'sarāwīl': 'trousers|breeches|pants|drawers'}
TECHNIQUES = [('Pure borrowing', 'Foreignising', 'The Arabic word is kept as is (e.g., dirham).'), ('Naturalised borrowing', 'Foreignising', 'The Arabic word is kept but adapted to English spelling or morphology.'), ('Literal translation', 'Foreignising', 'The standard dictionary equivalent (e.g., qamīṣ → shirt).'), ('Description', 'Neutralising', 'The item is replaced by an explanation of what it is (e.g., tharīd → bread broth).'), ('Generalisation', 'Neutralising', 'A more general word (e.g., fālūdhaj → sweetmeats; khiwān → table).'), ('Particularisation', 'Neutralising', 'A more specific word than the Arabic.'), ('Amplification', 'Neutralising', 'Information is added to the rendering (e.g., borrowing + gloss).'), ('Compression', 'Neutralising', "Part of the item's information is left out."), ('Intracultural adaptation', 'Domesticating', 'Replaced by another source-culture item more familiar to English readers.'), ('Intercultural adaptation', 'Domesticating', 'Replaced by an English/Western item (e.g., fālūdhaj → marzipan).'), ('Omission', 'Domesticating', 'The item is not translated.')]

def norm(t):
    t = re.sub('[ً-ْـ]', '', t)
    t = re.sub('[أإآ]', 'ا', t)
    return t.replace('ة', 'ه').replace('ى', 'ي')
pairs = list(csv.DictReader(open(HERE / 'corpus_aligned.csv', encoding='utf-8-sig')))
tl = load_workbook(HERE / 'term_list.xlsx').active
terms = [dict(zip([c.value for c in tl[1]], [c.value for c in row])) for row in tl.iter_rows(min_row=2)]
terms = [t for t in terms if (t['INCLUDE? (Y/N)'] or '').strip().upper() == 'Y']
rows = []
for p in pairs:
    ar = norm(p['arabic'])
    for t in terms:
        forms = t['Arabic forms searched'].replace(' / ', '|')
        for m in re.finditer(PRE + '(?:' + forms + ')' + SUF, ar):
            hits = sorted({h.lower() for h in re.findall('\\b(?:' + EN[t['transliteration']] + ')\\w*', p['english'], re.I)})
            rows.append([p['pair_id'], p['rasaif_page'], p['segment'], p['pdf_page'], t['category'], t['transliteration'], m.group(0).strip(' «"('), p['arabic'], p['english'], ', '.join(hits)])
wb = Workbook()
ws = wb.active
ws.title = 'Coding'
head = ['case_id', 'pair_id', 'rasaif_page', 'segment', 'pdf_page', 'category', 'term', 'ar_form', 'arabic', 'english', 'en_matches', 'valid', 'en_rendering', 'technique', 'notes']
ws.append(head)
for i, r in enumerate(rows, 1):
    ws.append([i] + r + ['', '', '', ''])
fill = PatternFill('solid', fgColor='FFF2CC')
for c in ws[1]:
    c.font = Font(bold=True)
for col in 'LMNO':
    ws[f'{col}1'].fill = fill
widths = dict(zip('ABCDEFGHIJKLMNO', [7, 7, 7, 7, 7, 15, 11, 12, 60, 60, 18, 7, 22, 22, 25]))
for k, v in widths.items():
    ws.column_dimensions[k].width = v
for row in ws.iter_rows(min_row=2):
    for c in row[8:10]:
        c.alignment = Alignment(wrap_text=True, vertical='top')
ws.freeze_panes = 'B2'
dv1 = DataValidation(type='list', formula1='"Yes,No"', allow_blank=True)
dv2 = DataValidation(type='list', formula1='=Codebook!$A$2:$A$' + str(len(TECHNIQUES) + 1), allow_blank=True)
ws.add_data_validation(dv1)
ws.add_data_validation(dv2)
dv1.add(f'L2:L{len(rows) + 1}')
dv2.add(f'N2:N{len(rows) + 1}')
cb = wb.create_sheet('Codebook')
cb.append(['technique', 'group (Marco, 2019)', 'definition'])
for t in TECHNIQUES:
    cb.append(list(t))
cb.append([])
cb.append(['valid = Yes', '', 'The Arabic word refers to the material item (food, vessel, coin/measure, garment).'])
cb.append(['valid = No', '', "Another sense or word (e.g., qadr 'amount', raʾs 'a person's head', madda 'stretch'), or a name."])
cb.append(['en_rendering', '', 'The English word(s) that render the item; blank if omitted.'])
for c in cb[1]:
    c.font = Font(bold=True)
for k, v in zip('ABC', [26, 22, 90]):
    cb.column_dimensions[k].width = v
tw = wb.create_sheet('Terms')
tw.append(['category', 'term', 'meaning', 'occurrences'])
for t in terms:
    tw.append([t['category'], t['transliteration'], t['meaning'], sum((1 for r in rows if r[5] == t['transliteration']))])
for c in tw[1]:
    c.font = Font(bold=True)
wb.properties.creator = None
wb.save(HERE / 'coding_sheet.xlsx')
print(f'cases={len(rows)}  with English keyword hit={sum((1 for r in rows if r[9]))}')
