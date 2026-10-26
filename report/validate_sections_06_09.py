"""Validate the resumed report increment without fitting models or compiling LaTeX."""
from pathlib import Path
import hashlib
import json
import re
import shutil

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'report'
TABLES = ROOT / 'results/tables'
NEW = sorted((REPORT / 'sections').glob('0[6-9]_*.tex'))
checks = []


def check(description, condition):
    checks.append({'check': description, 'passed': bool(condition)})


def read(name):
    return pd.read_csv(TABLES / name)


def without_comments(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def references(text):
    return {key.strip() for group in re.findall(
        r'\\(?:[cC]ref|[cC]refrange|[eE]qref|ref)\*?\{([^}]+)\}', text
    ) for key in group.split(',')}


check('Exactly four resumed section files exist', len(NEW) == 4)
all_tex = list(REPORT.rglob('*.tex'))
all_text = '\n'.join(p.read_text(encoding='utf-8') for p in all_tex)
labels = re.findall(r'\\label\{([^}]+)\}', all_text)
check('All existing report labels are unique', len(labels) == len(set(labels)))
bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,]+),',
                         (REPORT / 'references.bib').read_text(encoding='utf-8')))
used_tables, figures = [], []
for path in NEW:
    text = without_comments(path.read_text(encoding='utf-8'))
    check(f'{path.name}: balanced braces', len(re.findall(r'(?<!\\)\{', text)) ==
          len(re.findall(r'(?<!\\)\}', text)))
    stack = []
    matched = True
    for kind, environment in re.findall(r'\\(begin|end)\{([^}]+)\}', text):
        if kind == 'begin':
            stack.append(environment)
        elif not stack or stack.pop() != environment:
            matched = False
    check(f'{path.name}: matched environments', matched and not stack)
    check(f'{path.name}: reference labels exist', references(text) <= set(labels))
    citations = {key.strip() for group in re.findall(r'\\cite\{([^}]+)\}', text)
                 for key in group.split(',')}
    check(f'{path.name}: citation keys exist', citations <= bibkeys)
    check(f'{path.name}: no unexpected control characters',
          not any(ord(c) < 32 and c not in '\n\r\t' for c in text))
    for relative in re.findall(r'\\input\{([^}]+)\}', text):
        table_path = ROOT / relative
        used_tables.append(relative)
        check(f'{path.name}: input exists: {relative}', table_path.is_file())
        table_text = table_path.read_text(encoding='utf-8') if table_path.is_file() else ''
        table_labels = set(re.findall(r'\\label\{([^}]+)\}', table_text))
        check(f'{relative}: numbered, captioned and referenced',
              bool(table_labels) and bool(re.search(r'\\caption\{', table_text))
              and bool(table_labels & references(text)))
    for block in re.findall(r'\\begin\{figure\}.*?\\end\{figure\}', text, re.S):
        paths = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', block)
        figlabels = set(re.findall(r'\\label\{([^}]+)\}', block))
        check(f'{path.name}: figure caption, label and in-text reference',
              bool(paths) and bool(figlabels & references(text)) and '\\caption{' in block)
        for relative in paths:
            figures.append(relative)
            check(f'Figure exists: {relative}', (ROOT / 'results/figures' / relative).is_file())

# Numerical comparisons are read-only checks of the evidence reused in Sections 06--09.
l1 = read('T04_level0_level1_wide.csv').set_index('model')
l2 = read('T05_level2_summary.csv').set_index('model')
l3 = read('T07_default_vs_tuned.csv').set_index('model')
abl = read('T09_ablation_summary.csv').set_index(['feature_set', 'model'])
hor = read('T10_horizon.csv').set_index('model')
check('November lowest RMSE/MAE/MAPE is XGB', all(
    l1[c].idxmin() == 'XGB' for c in ['val_RMSE', 'val_MAE', 'val_MAPE']))
check('DT improves November RMSE but worsens MAE and MAPE',
      l1.loc['DT', 'val_RMSE'] < l1.loc['Naive-24h', 'val_RMSE'] and all(
          l1.loc['DT', c] > l1.loc['Naive-24h', c] for c in ['val_MAE', 'val_MAPE']))
check('November XGB skill rounds to 29.74 percent',
      round(100 * l1.loc['XGB', 'skill_vs_naive24'], 2) == 29.74)
check('Default CV RMSE winner is LR, MAPE winner is RF',
      l2.RMSE_mean.idxmin() == 'LR' and l2.MAPE_mean.idxmin() == 'RF')
folds = read('T05_level2_cv.csv')
means = folds.groupby('model').RMSE.mean().reindex(l2.index)
sds = folds.groupby('model').RMSE.std().reindex(l2.index)
check('Default CV means and sample SDs match saved summary',
      np.allclose(means, l2.RMSE_mean) and np.allclose(sds, l2.RMSE_std))
check('L2 last fold reproduces L1 for all eight shared models', all(
    np.isclose(row.RMSE, l1.loc[row.model, 'val_RMSE'], rtol=1e-6)
    for row in folds[folds.split == 'fold4'].itertuples()))
check('h24 tuned RMSE selects absolute SVR', l3.tuned_RMSE_mean.idxmin() == 'SVR')
check('Residual target lowers tuned h24 RMSE in four of five families', sum(
    l3.loc[m + '_delta', 'tuned_RMSE_mean'] < l3.loc[m, 'tuned_RMSE_mean']
    for m in ['LR', 'DT', 'RF', 'SVR', 'XGB']) == 4)
check('Absolute DT tuned still exceeds CV naive baseline',
      l3.loc['DT', 'tuned_RMSE_mean'] > l2.loc['Naive-24h', 'RMSE_mean'])
top = l3.tuned_RMSE_mean.nsmallest(4)
check('Four leading h24 CV means span 30.4 kW and 1.26 percent',
      round(top.max() - top.min(), 1) == 30.4 and
      round(100 * (top.max() / top.min() - 1), 2) == 1.26)
check('RF residual has lowest tuned h24 MAPE', l3.tuned_MAPE.idxmin() == 'RF_delta')
for m, rounded_drop in [('RF', 67.16), ('XGB', 65.56)]:
    reduction = 100 * (1 - abl.loc[('D', m), 'RMSE_mean'] / abl.loc[('C', m), 'RMSE_mean'])
    check(f'{m} C-to-D relative reduction', round(reduction, 2) == rounded_drop)
for m, expected in [('RF', 22.92), ('XGB', 63.51), ('RF_delta', 12.86), ('XGB_delta', 62.40)]:
    change = 100 * (abl.loc[('E', m), 'RMSE_mean'] / abl.loc[('D', m), 'RMSE_mean'] - 1)
    check(f'{m} D-to-E relative increase', round(change, 2) == expected)
for m, expected in [('RF', 1.59), ('XGB', 1.95), ('RF_delta', 5.31), ('XGB_delta', -0.90)]:
    change = 100 * (abl.loc[('F', m), 'RMSE_mean'] / abl.loc[('E', m), 'RMSE_mean'] - 1)
    check(f'{m} E-to-F relative change', round(change, 2) == expected)
check('Selected SVR h1 CV RMSE reduction rounds to 22.57 percent',
      round(100 * (1 - hor.loc['SVR', 'h1_RMSE'] / hor.loc['SVR', 'h24_RMSE']), 2) == 22.57)
check('h1 persistence worse than daily naive',
      hor.loc['Persistence', 'h1_RMSE'] > hor.loc['Naive-24h', 'h1_RMSE'])
check('All five reported h1 family representatives improve RMSE', all(
    hor.loc[m, 'h1_RMSE'] < hor.loc[m, 'h24_RMSE'] for m in ['LR', 'DT', 'RF', 'SVR', 'XGB']))
params = json.loads((TABLES / 'best_params.json').read_text())
params1 = json.loads((TABLES / 'best_params_h1.json').read_text())
check('Separate horizons select identical absolute SVR parameters', params['SVR'] == params1['SVR'])
check('All 20 saved searches remain present', len(list(TABLES.glob('search_*.csv'))) == 20)

manifest = json.loads((REPORT / 'evidence/source_manifest.json').read_text())
changed = [entry['path'] for entry in manifest if not (ROOT / entry['path']).is_file()
           or hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() != entry['sha256']]
check('Original audited source/data/notebook/result artifacts match SHA-256 manifest', not changed)
missing_main = [p for p in re.findall(r'\\input\{([^}]+)\}',
                (REPORT / 'main.tex').read_text(encoding='utf-8')) if not (ROOT / p).is_file()]
result = {
    'scope': 'Sections 06--09 only; static and saved-evidence validation',
    'checks': checks, 'passed': sum(c['passed'] for c in checks),
    'failed': sum(not c['passed'] for c in checks),
    'section_files': [p.relative_to(ROOT).as_posix() for p in NEW],
    'referenced_tables': used_tables, 'referenced_figures': figures,
    'pending_main_inputs': missing_main,
    'unresolved_references_in_existing_partial_report': sorted(references(all_text) - set(labels)),
    'changed_original_artifacts': changed,
    'tool_paths': {tool: shutil.which(tool) for tool in ['latexmk', 'pdflatex', 'biber']},
    'compilation': 'Not performed. Full main.tex still has pending sections/appendix. '
                   'MiKTeX executables were found, but version probes could not initialize '
                   'the user profile under the current sandbox. No PDF/layout validation claimed.',
}
out = REPORT / 'evidence/sections_06_09_validation.json'
out.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(f"Sections 06--09: {result['passed']} checks passed; {result['failed']} failed; "
      f"{len(figures)} figures and {len(used_tables)} tables referenced.")
if result['failed']:
    raise SystemExit('\n'.join(c['check'] for c in checks if not c['passed']))
