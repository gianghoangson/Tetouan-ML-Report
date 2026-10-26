"""Read-only repository inspection; all generated files stay under report/."""
from pathlib import Path
import csv
import hashlib
import json
import fitz
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report' / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)
manifest = []
for folder in ['src', 'notebooks', 'docs', 'results', 'data']:
    for p in sorted((ROOT / folder).rglob('*')):
        if p.is_file():
            manifest.append({'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
for name in ['README.md', 'requirements.txt', 'run_all.py']:
    p = ROOT / name
    manifest.append({'path': name, 'bytes': p.stat().st_size,
                     'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT / 'source_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
for p in sorted((ROOT / 'docs').glob('*.pdf')):
    with fitz.open(p) as doc:
        text = '\n\n'.join(f'--- PDF PAGE {i+1} ---\n{page.get_text()}' for i, page in enumerate(doc))
        (OUT / (p.stem + '.txt')).write_text(text, encoding='utf-8')
        print(f'PDF {p.name}: {len(doc)} pages, {len(text)} characters extracted')
for p in sorted((ROOT / 'notebooks').glob('*.ipynb')):
    nb = json.loads(p.read_text(encoding='utf-8'))
    parts = []
    for i, cell in enumerate(nb['cells']):
        parts.append(f"\n--- CELL {i} ({cell['cell_type']}; execution={cell.get('execution_count')}) ---\n" + ''.join(cell['source']))
        for output in cell.get('outputs', []):
            if 'text' in output:
                parts.append('OUTPUT: ' + ''.join(output['text']))
            elif 'text/plain' in output.get('data', {}):
                parts.append('OUTPUT: ' + ''.join(output['data']['text/plain']))
            if output.get('output_type') == 'error':
                parts.append('ERROR: ' + str(output))
    (OUT / (p.stem + '.txt')).write_text('\n'.join(parts), encoding='utf-8')
    print(f'Notebook {p.name}: {len(nb["cells"])} cells')
tables = []
for p in sorted((ROOT / 'results' / 'tables').glob('*.csv')):
    with p.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    tables.append({'file': p.name, 'rows': len(rows), 'columns': list(rows[0]) if rows else []})
    if p.name.startswith('search_'):
        best = min(rows, key=lambda r: float(r['rank_test_RMSE']))
        tables[-1]['best'] = {k: v for k, v in best.items() if k in ['params', 'mean_test_RMSE', 'std_test_RMSE', 'rank_test_RMSE'] or k.startswith('split') and k.endswith('test_RMSE')}
(OUT / 'table_inventory.json').write_text(json.dumps(tables, indent=2), encoding='utf-8')
figures = list(sorted((ROOT / 'results' / 'figures').glob('*.png')))
for batch in range(0, len(figures), 6):
    canvas = Image.new('RGB', (1600, 1500), 'white')
    draw = ImageDraw.Draw(canvas)
    for j, p in enumerate(figures[batch:batch+6]):
        with Image.open(p) as im:
            thumb = ImageOps.contain(im.convert('RGB'), (780, 455))
            x, y = (j % 2) * 800, (j // 2) * 500
            canvas.paste(thumb, (x, y + 30))
            draw.text((x+5, y+5), p.name, fill='black')
    canvas.save(OUT / f'figure_contact_{batch//6+1}.jpg')
print(f'Inventoried {len(tables)} CSV tables and {len(figures)} figures; no experiments executed.')
