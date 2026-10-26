"""Check the integrated report against saved evidence; never fit or execute notebooks."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import shutil

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'report'
T = ROOT / 'results/tables'
checks = []
included = []
missing = []
seen = set()


def check(name, condition):
    checks.append({'check': name, 'passed': bool(condition)})


def clean(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def walk(path):
    if path in seen:
        check(f'Input included once: {path.relative_to(ROOT)}', False)
        return ''
    seen.add(path)
    if not path.is_file():
        missing.append(path.relative_to(ROOT).as_posix())
        return ''
    included.append(path)
    text = clean(path.read_text(encoding='utf-8'))
    for relative in re.findall(r'\\input\{([^}]+)\}', text):
        child = ROOT / relative
        if child.suffix != '.tex':
            child = child.with_suffix('.tex')
        text += '\n' + walk(child)
    return text


text = walk(REPORT / 'main.tex')
check('All transitive LaTeX inputs exist', not missing)
check('Exactly thirteen main section files integrated',
      len([p for p in included if p.parent.name == 'sections']) == 13)
check('Supplementary appendix integrated', REPORT / 'appendices/supplementary.tex' in included)
labels = re.findall(r'\\label\{([^}]+)\}', text)
duplicates = [key for key, count in Counter(labels).items() if count > 1]
check('No duplicate labels in include graph', not duplicates)
refs = {key.strip() for group in re.findall(
    r'\\(?:[cC]ref|ref|[eE]qref)\*?\{([^}]+)\}', text) for key in group.split(',')}
unresolved = sorted(refs - set(labels))
check('Every explicit reference label is defined', not unresolved)
bib = (REPORT / 'references.bib').read_text(encoding='utf-8')
keys = re.findall(r'@\w+\s*\{\s*([^,]+),', bib)
cites = {key.strip() for group in re.findall(
    r'\\(?:cite|parencite|textcite)\*?\{([^}]+)\}', text) for key in group.split(',')}
check('Bibliography has unique keys', len(keys) == len(set(keys)))
check('All citation keys resolve', cites <= set(keys))
check('All bibliography entries are cited', set(keys) <= cites)
check('Bibliography braces balance', len(re.findall(r'(?<!\\)\{', bib)) ==
      len(re.findall(r'(?<!\\)\}', bib)))
check('Declared bibliography resource exists', all((ROOT / p).is_file()
      for p in re.findall(r'\\addbibresource\{([^}]+)\}', text)))

for path in included:
    content = clean(path.read_text(encoding='utf-8'))
    name = path.relative_to(ROOT).as_posix()
    check(f'Balanced unescaped braces: {name}',
          len(re.findall(r'(?<!\\)\{', content)) == len(re.findall(r'(?<!\\)\}', content)))
    stack = []
    valid = True
    for kind, env in re.findall(r'\\(begin|end)\{([^}]+)\}', content):
        if kind == 'begin':
            stack.append(env)
        elif not stack or stack.pop() != env:
            valid = False
    check(f'Matched environments: {name}', valid and not stack)
    check(f'No corrupt control characters: {name}',
          not any(ord(c) < 32 and c not in '\r\n\t' for c in content))

figures = re.findall(r'\\begin\{figure\}.*?\\end\{figure\}', text, re.S)
tables = re.findall(r'\\begin\{(?:table|longtable)\}.*?\\end\{(?:table|longtable)\}', text, re.S)
assets = []
for number, block in enumerate(figures, 1):
    paths = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', block)
    flabels = re.findall(r'\\label\{([^}]+)\}', block)
    check(f'Figure {number}: caption, label, in-text reference',
          bool(paths) and '\\caption{' in block and bool(set(flabels) & refs))
    for relative in paths:
        assets.append(relative)
        check(f'Figure asset exists: {relative}', (ROOT / 'results/figures' / relative).is_file())
for number, block in enumerate(tables, 1):
    tlabels = re.findall(r'\\label\{([^}]+)\}', block)
    check(f'Table {number}: caption, label, in-text reference',
          '\\caption{' in block and bool(set(tlabels) & refs))
check('All 22 generated evidence tables are included',
      len([p for p in included if p.parent.name == 'tables']) == 22)
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.S).group(1)
abstract_words = len(abstract.split())
check('Abstract is approximately 200--250 words', 200 <= abstract_words <= 260)

# The detailed evidence checker independently recomputes prediction metrics.
prior = json.loads((REPORT / 'evidence/numerical_checks.json').read_text())
check('All saved detailed numerical checks passed', all(c['passed'] for c in prior['checks']))
def read(name):
    return pd.read_csv(T / name).set_index('model')
day, hour = read('T08_final_test.csv'), read('T08_final_test_h1.csv')
cv = read('T07_default_vs_tuned.csv')
check('CV-selected h24 variant remains absolute SVR', cv.tuned_RMSE_mean.idxmin() == 'SVR')
check('Observed h24 test-best variant is residual SVR', day.RMSE.idxmin() == 'SVR_delta-tuned')
for setting, frame, expected in [('h24', day, [1624.6, 1094.6, 1.78, .9869]),
                                  ('h1', hour, [1195.8, 861.8, 1.41, .9929])]:
    for metric, value, decimals in zip(['RMSE', 'MAE', 'MAPE', 'R2'], expected, [1, 1, 2, 4]):
        check(f'{setting} selected-SVR narrative {metric}',
              round(float(frame.loc['SVR-tuned', metric]), decimals) == value)
check('Residual SVR test narrative RMSE', round(day.loc['SVR_delta-tuned', 'RMSE'], 1) == 1419.1)
check('h24 selected daily-naive skill is 50.71 percent',
      round(100 * day.loc['SVR-tuned', 'skill_vs_naive24'], 2) == 50.71)
check('h1 selected skills are 63.72 and 78.16 percent',
      round(100 * hour.loc['SVR-tuned', 'skill_vs_naive24'], 2) == 63.72 and
      round(100 * hour.loc['SVR-tuned', 'skill_vs_persistence'], 2) == 78.16)
check('Selected h24 test RMSE is 32.60 percent below development mean',
      round(100 * (1 - day.loc['SVR-tuned', 'RMSE'] / cv.loc['SVR', 'tuned_RMSE_mean']), 2) == 32.60)
check('h1 RMSE and MAE/MAPE winners differ as stated', hour.RMSE.idxmin() == 'SVR-tuned'
      and hour.MAE.idxmin() == hour.MAPE.idxmin() == 'XGB_delta-tuned')
pred = pd.read_csv(T / 'T08_test_predictions.csv')
errors = pred['SVR-tuned'] - pred['actual']
for description, actual, expected in [('bias', errors.mean(), -202.1),
                                     ('minimum error', errors.min(), -9362.1),
                                     ('maximum error', errors.max(), 6514.2),
                                     ('December mean', pred.actual.mean(), 63750.8)]:
    check(f'Selected h24 diagnostic: {description}', round(actual, 1) == expected)
worst = pd.read_csv(T / 'T08_worst_days.csv').iloc[0]
check('Worst day and MAE match narrative', worst.DateTime == '2017-12-01'
      and round(worst.MAE, 1) == 4579.2 and round(worst.bias, 1) == -3616.7)
diagnostic = pd.read_csv(T / 'T12_leakage_settings.csv').set_index('setting')
check('S4 reproduces absolute RF rather than selected SVR',
      np.isclose(diagnostic.loc['S4', 'RMSE'], day.loc['RF-tuned', 'RMSE']))
kfold = pd.read_csv(T / 'T12b_kfold_vs_tscv.csv').set_index('cv_method')
check('KFold and TSCV signed discrepancies match narrative',
      round(kfold.loc['KFold (shuffled)', 'optimism_%'], 2) == 8.27 and
      round(kfold.loc['TimeSeriesSplit', 'optimism_%'], 2) == -32.14)
manifest = json.loads((REPORT / 'evidence/source_manifest.json').read_text())
changed = [e['path'] for e in manifest if not (ROOT / e['path']).is_file() or
           hashlib.sha256((ROOT / e['path']).read_bytes()).hexdigest() != e['sha256']]
check('Original audited artifacts retain their SHA-256 hashes', not changed)

logpath = REPORT / 'main.log'
log = logpath.read_text(encoding='utf-8', errors='replace') if logpath.exists() else ''
missing_packages = re.findall(r"File [`']([^`']+\.sty)' not found", log)
pdf_success = bool(re.search(r'Output written on .*main\.pdf', log)) and (REPORT / 'main.pdf').is_file()
unresolved_log = re.findall(r'LaTeX Warning: (?:Reference|Citation).*', log)
overfull = re.findall(r'Overfull \\[hv]box.*', log)
result = {
    'scope': 'Complete integrated report; no ML experiments executed',
    'passed': sum(c['passed'] for c in checks), 'failed': sum(not c['passed'] for c in checks),
    'checks': checks, 'section_count': 13, 'figure_count': len(figures), 'table_count': len(tables),
    'bibliography_entries': len(keys), 'cited_entries': len(cites), 'abstract_word_count': abstract_words,
    'included_files': [p.relative_to(ROOT).as_posix() for p in included],
    'figure_assets': assets, 'missing_inputs': missing, 'duplicate_labels': duplicates,
    'unresolved_source_references': unresolved, 'missing_citation_keys': sorted(cites - set(keys)),
    'changed_original_artifacts': changed,
    'prior_numerical_checks': len(prior['checks']),
    'tool_paths': {k: shutil.which(k) for k in ['pdflatex', 'biber', 'latexmk']},
    'compilation': {'attempted': bool(log), 'pdf_success': pdf_success,
                    'missing_packages': missing_packages, 'unresolved_log_warnings': unresolved_log,
                    'overfull_box_messages': overfull,
                    'layout_validated': False,
                    'note': 'Compiler was invoked with automatic package installation disabled. '
                            'A failed early build cannot establish layout or bibliography resolution.'},
}
(REPORT / 'evidence/report_validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(f"Report validation: {result['passed']} passed, {result['failed']} failed; "
      f"{len(figures)} figures, {len(tables)} tables, {len(keys)} references; PDF success: {pdf_success}.")
if result['failed']:
    raise SystemExit('\n'.join(c['check'] for c in checks if not c['passed']))
