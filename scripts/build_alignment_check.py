import csv
import random
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
HERE = Path(__file__).resolve().parents[1]
SEED, N = (2027, 50)
pairs = list(csv.DictReader(open(HERE / 'corpus_aligned.csv', encoding='utf-8-sig')))
sample = sorted(random.Random(SEED).sample(pairs, N), key=lambda r: int(r['pair_id']))
wb = Workbook()
ws = wb.active
ws.title = 'Check'
head = ['check_id', 'pair_id', 'rasaif_page', 'segment', 'pdf_page', 'arabic', 'english', 'aligned', 'notes']
ws.append(head)
for i, r in enumerate(sample, 1):
    ws.append([i, int(r['pair_id']), int(r['rasaif_page']), int(r['segment']), int(r['pdf_page']) if r['pdf_page'] else None, r['arabic'], r['english'], '', ''])
for c in ws[1]:
    c.font = Font(bold=True)
for col in 'HI':
    ws[f'{col}1'].fill = PatternFill('solid', fgColor='FFF2CC')
for k, w in zip('ABCDEFGHI', [8, 8, 10, 8, 9, 60, 60, 10, 30]):
    ws.column_dimensions[k].width = w
for row in ws.iter_rows(min_row=2):
    for c in row[5:7]:
        c.alignment = Alignment(wrap_text=True, vertical='top')
    row[5].alignment = Alignment(wrap_text=True, vertical='top', horizontal='right')
ws.freeze_panes = 'B2'
dv = DataValidation(type='list', formula1='"Yes,Partly,No"', allow_blank=True)
ws.add_data_validation(dv)
dv.add(f'H2:H{N + 1}')
g = wb.create_sheet('Guide')
for line in [['aligned', 'meaning'], ['Yes', 'The English segment translates the Arabic segment (allowing for free or idiomatic translation).'], ['Partly', 'Most matches, but part of the Arabic is missing from the English, or the English contains text from a neighbouring segment.'], ['No', 'The English does not translate this Arabic segment (it belongs to a different segment).'], ['Seed', f'Random sample of {N} of {len(pairs)} pairs, seed {SEED}.']]:
    g.append(line)
g['A1'].font = g['B1'].font = Font(bold=True)
g.column_dimensions['A'].width, g.column_dimensions['B'].width = (10, 110)
wb.properties.creator = None
wb.save(HERE / 'alignment_check_50.xlsx')
print('saved', len(sample), 'pairs; pair_ids:', [int(r['pair_id']) for r in sample][:10], '...')
