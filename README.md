# Data and scripts

Supplementary material for the article *Domain shapes strategy: culture-specific items in Colville's English translation of al-Jāḥiẓ's al-Bukhalāʾ*.

## Files

| File | Contents |
|---|---|
| `classification_data.xlsx` | One row per candidate occurrence (747 rows; 583 valid; 566 analysed). Columns: case number, pair and page references, domain, term, Arabic word form, validity, English rendering, technique, and notes. Further sheets: **README** (column meanings), **Codebook** (techniques and groups, after Marco 2019), and **Terms** (the 58 terms, with meanings and counts). |
| `term_list.xlsx` | The 58 terms in the order searched, with domain, transliteration, the Arabic forms searched (regular-expression alternatives), and meaning (Methods: Selection of items). |
| `results_tables.xlsx` | The results tables reported in the Results, including the chi-square test, the adjusted standardised residuals (sheet T4b), and the term-level checks (sheet T4c). |
| `alignment_check_50.xlsx` | The random sample of 50 aligned pairs checked by hand (Methods: Corpus): 49 correctly aligned, 1 misaligned (pair 222, excluded from the corpus). |
| `scripts/build_corpus.py` | Cleans the aligned corpus pages, restores book order, locates each pair in the scanned PDF of Colville's book, and excludes three faulty pairs (Methods: Corpus). |
| `scripts/build_alignment_check.py` | Draws the random alignment sample (seed 2027; Methods: Corpus). |
| `scripts/build_coding_sheet.py` | Finds every occurrence of the 58 terms in `term_list.xlsx`, with Arabic prefixes and suffixes, and builds the empty classification sheet (Methods: Selection of items). |
| `scripts/analyse.py` | Produces the results tables, the consistency measures, and the chi-square test (Methods: Analysis; Results). |

## How to rerun

- **The statistics** need only this folder: `python3 scripts/analyse.py` reads `classification_data.xlsx` and writes `results/results_tables.xlsx`.
- **The cases** can be rebuilt from the corpus: `build_corpus.py` produces `corpus_aligned.csv`; with that file and `term_list.xlsx` in the same folder, `build_coding_sheet.py` yields the same 747 cases with the same case numbers.

## Corpus

- **Source.** Al-Jāḥiẓ, *Kitāb al-Bukhalāʾ*, sentence-aligned Arabic–English pairs from Raṣāʾif (Al-Ghamdi 2026), retrieved January 2026 (25 results pages, 1,651 pairs).
- **One translator only.** The English side of Raṣāʾif combines two translations. The 140 pairs from Serjeant's translation (al-Jāḥiẓ 1997) were removed: page 1, segments 65–70; all of page 2; page 3, segments 1–64. All remaining pairs are Colville's (al-Jāḥiẓ 1999).
- **Cleaning.** The Raṣāʾif page header was removed from the first Arabic segment of each page, and book order was restored (Raṣāʾif stores the pairs in reverse order).
- **Exclusions.** Pairs 222, 683, and 927 were dropped because of platform faults; none contains a classified item. Pair numbers were not renumbered. Final corpus: 1,508 pairs.
- **Page references.** Each case gives two printed page numbers, so it can be found in the books without Raṣāʾif: `colville_page` (Colville 1999) and `arabic_page` (al-Ḥājirī's edition of *al-Bukhalāʾ*, Cairo, 1948). Both were found by matching each sentence against OCR text of the two books (runs of consecutive words); pairs that could not be matched took the page of their neighbours when both neighbours were on the same page. `pdf_page` is the page of the scanned PDF of Colville (printed page + 24).
- **Edition.** Colville translated from the second edition of al-Ḥājirī (1954). Page numbers here refer to the first edition (1948); the second may be paginated differently.
- **Order.** Pairs 1443–1444 belong at the end of the text (Arabic p. 194; Colville p. 202) but Raṣāʾif places them earlier. They contain no classified item, and they were left where they are so that pair and case numbers stay the same as in Raṣāʾif.

## Building your own corpus

The study can also be replicated without Raṣāʾif, from the two books: the Arabic text (al-Ḥājirī's edition) and Colville's translation.

- Align the two texts sentence by sentence and save them as plain-text pairs (`page_N_arabic.txt`, `page_N_english.txt`, each segment starting with its number in square brackets, e.g. `[12]`), then build `corpus_aligned.csv` (columns: pair_id, rasaif_page, segment, pdf_page, ar_words, en_words, arabic, english). `build_corpus.py` shows how; its Raṣāʾif-specific steps (header removal, reversed order) can be skipped.
- Run `build_coding_sheet.py` with `term_list.xlsx` to find the candidate occurrences, classify them with the Codebook, and run `analyse.py`.
- Pair and case numbers will differ from ours, because sentence division will differ, and counts may differ slightly with a different edition. Our cases can still be found in the books through `term`, `ar_form`, `arabic_page`, and `colville_page`.

## Notes

- **Full sentences are not included.** The aligned Arabic and English texts come from Raṣāʾif (Al-Ghamdi 2026), an online Arabic–English parallel corpus of classical texts, and the English is Colville's translation (al-Jāḥiẓ 1999). Both remain the property of their owners. The scripts show how the data were processed but need those corpus files to run.
- **Classification was done by hand.** `build_coding_sheet.py` only finds the occurrences; validity, rendering, and technique were then entered manually. Running that script again creates an empty sheet and does not reproduce the classification, which is in `classification_data.xlsx`.
- **Alignment sample.** The sample was drawn before the three faulty pairs (222, 683, 927) were excluded. Drawing it again from the final corpus gives a different sample.
- **Term-level tests.** These use 57 of the 58 terms: *sufra* had two candidates, both not valid, so it has no analysed case.
- **Analysed cases.** Cases classified as *Reference (pronoun)* (15) or *Excluded (Qur'anic quotation)* (2) are valid but left out of the percentages.
- **Software.** Python 3.14 with SciPy 1.17 and openpyxl. Chi-square test of independence with Cramér's V (α = .05); adjusted standardised residuals with a Bonferroni-adjusted threshold of ±3.2 (15 cells). Term-level checks: Kruskal–Wallis test on each term's share of foreignising renderings, and a permutation test reassigning domains to whole terms (10,000 permutations, seed 2027).
