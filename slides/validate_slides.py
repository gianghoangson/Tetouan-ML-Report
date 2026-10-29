"""Static integrity and original-file checks; does not claim to validate TeX layout."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
WORKSPACE = REPORT.parent
tex = (HERE / 'main.tex').read_text(encoding='utf-8')
notes = (HERE / 'presenter_notes.md').read_text(encoding='utf-8')
checks = []

def check(label, condition):
    checks.append({'check': label, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(label)

check('16:9 Beamer declaration', r'\documentclass[aspectratio=169]{beamer}' in tex)
main, backup = tex.split(r'\appendix', 1)
check('16 main frames', len(re.findall(r'\\begin\{frame\}', main)) == 16)
check('3 backup frames', len(re.findall(r'\\begin\{frame\}', backup)) == 3)
check('Backups do not increment frame number', backup.count('[noframenumbering]') == 3)
check('No submission date', 'submission date' not in tex.lower() and r'\date{}' in tex)
for value in ['NATIONAL ECONOMICS UNIVERSITY', 'Faculty of Data Science and Artificial Intelligence',
              'MACHINE LEARNING', 'Dang Nhat Minh', '11247196', 'Giang Hoang Son',
              '11247222', 'DS66A', 'Ph.D. Luong Van Thien',
              'A chronological evaluation of conventional regression models']:
    check('Identity: '+value, value in tex)
check('Exact title metadata', r'\title{Machine Learning-Based Electricity Consumption Forecasting in Tetouan City}' in tex)
check('No cross-repository TeX paths', 'Prj Tetouan ML' not in tex and '../' not in tex)
check('Notes total 900 seconds', sum(map(int,re.findall(r'\*\*Speaking time:\*\* (\d+) seconds',notes))) == 900)
check('16 scripts', notes.count('**Script:**') == 16)
check('16 key takeaways', notes.count('**Key takeaway:**') == 16)
check('12 Q&A questions', len(re.findall(r'^## \d+\.', (HERE/'qa_preparation.md').read_text(encoding='utf-8'), re.M)) == 12)

clean = re.sub(r'(?<!\\)%[^\n]*', '', tex)
depth = 0
minimum = 0
for i, ch in enumerate(clean):
    preceding = len(clean[:i])-len(clean[:i].rstrip('\\'))
    if ch in '{}' and preceding % 2 == 0:
        depth += 1 if ch == '{' else -1
        minimum = min(minimum,depth)
check('Balanced braces without negative depth', depth == 0 and minimum == 0)
stack = []
for action, environment in re.findall(r'\\(begin|end)\{([^}]+)\}', clean):
    if action == 'begin':
        stack.append(environment)
    else:
        check('Environment closes '+environment, bool(stack) and stack.pop() == environment)
check('All environments closed', not stack)
for i, frame in enumerate(re.split(r'\\begin\{frame\}',clean)[1:],1):
    dollars = []
    for j,ch in enumerate(frame):
        if ch == '$':
            n = len(frame[:j])-len(frame[:j].rstrip('\\'))
            if n % 2 == 0:
                dollars.append(j)
    check(f'Frame {i}: paired inline math delimiters',len(dollars)%2 == 0)
paths = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',tex)
paths += re.findall(r'\\fig\{([^}]+)\}',tex)
paths += re.findall(r'\\input\{([^}]+)\}',tex)
for relative in paths:
    if '#' not in relative:
        check('Asset exists: '+relative,(REPORT/relative).is_file())
check('Seven data visuals plus logo',len([p for p in paths if p.endswith(('.pdf','.png')) and '#' not in p]) == 8)

manifest = json.loads((HERE/'original_files_manifest.json').read_text())
for relative,digest in manifest.items():
    p = WORKSPACE/relative
    check('Original unchanged: '+relative,p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
outside_new=[]
for relative in ['Prj Tetouan ML/Machine-Learning','Tetouan-ML-Report']:
    root=WORKSPACE/relative
    for p in root.rglob('*'):
        if not p.is_file() or '.git' in p.relative_to(root).parts or HERE in p.parents:
            continue
        if p.relative_to(WORKSPACE).as_posix() not in manifest:
            outside_new.append(str(p))
check('No new files outside slides',not outside_new)
log=(HERE/'main.log').read_text(errors='replace') if (HERE/'main.log').exists() else ''
result={
    'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
    'main_slides':16,'backup_slides':3,'speaking_seconds':900,
    'original_files_checked':len(manifest),'new_files_outside_slides':outside_new,
    'compilation':'Blocked: beamer.cls not found' if 'beamer.cls' in log and 'not found' in log else 'Inspect compilation log',
    'rendered_slide_layout_verified':False,
    'scope':'Static checks are not a substitute for successful compilation and PDF inspection.',
    'checks':checks,
}
(HERE/'quality_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
