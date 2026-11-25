"""Exports the Cambridge International AS & A Level Law (9084) question bank to the site's data format.

Usage: python3 boards/cambridge/export_cie.py --bank "<Law/CIE/Question Bank>" [--images]
Writes boards/cambridge/data/{questions,papers,topics,spec,weighting}.json and, with --images,
public/img/cie/<paper>/<name>.webp (lossless WebP from the bank's PNG crops).
"""
import argparse, base64, hashlib, io, json, os, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / 'data'
IMG = REPO / 'public' / 'img' / 'cie'

# site topic: slug, name, syllabus sub-sections (x.y.z) it covers
TOPIC_LIST = [
    ('english-legal-system-in-context', 'The English legal system in context: legal systems and the rule of law', ['1.1.1']),
    ('parliamentary-law-making', 'Parliamentary law making', ['1.1.2']),
    ('delegated-legislation', 'Delegated legislation', ['1.1.3']),
    ('statutory-interpretation', 'Statutory interpretation', ['1.1.4']),
    ('judicial-precedent', 'Judicial precedent', ['1.1.5']),
    ('civil-courts', 'Civil courts and civil process', ['1.2.1']),
    ('alternative-dispute-resolution', 'Alternative methods of dispute resolution', ['1.2.2']),
    ('criminal-courts', 'Criminal courts and criminal process', ['1.2.3']),
    ('police-powers', 'Police powers', ['1.2.4']),
    ('the-judiciary', 'The judiciary: superior and inferior judges', ['1.3.1']),
    ('legal-professionals', 'Legal professionals: barristers and solicitors', ['1.3.2']),
    ('lay-personnel', 'Lay personnel: magistrates and juries', ['1.3.3']),
    ('actus-reus-and-mens-rea', 'Actus reus and mens rea', ['2.1.1', '2.1.2']),
    ('theft', 'Theft (s1 Theft Act 1968)', ['2.2.1']),
    ('robbery', 'Robbery (s8 Theft Act 1968)', ['2.2.2']),
    ('burglary', 'Burglary (s9 Theft Act 1968)', ['2.2.3']),
    ('blackmail', 'Blackmail (s21 Theft Act 1968)', ['2.2.4']),
    ('handling-stolen-goods', 'Handling stolen goods (s22 Theft Act 1968)', ['2.2.5']),
    ('making-off-without-payment', 'Making off without payment (s3 Theft Act 1978)', ['2.2.6']),
    ('criminal-damage', 'Criminal damage (Criminal Damage Act 1971)', ['2.2.7']),
    ('fraud', 'Fraud (Fraud Act 2006)', ['2.2.8']),
    ('sentencing-adult-offenders', 'Sentencing adult offenders', ['2.3.1']),
    ('sentencing-young-offenders', 'Sentencing young offenders', ['2.3.2']),
    ('aims-of-sentencing', 'Aims of sentencing', ['2.3.3']),
    ('formation-of-contract', 'Formation of contract: offer, acceptance, intention, consideration and capacity', ['3.1.1', '3.1.2', '3.1.3', '3.1.4', '3.1.5']),
    ('contract-terms', 'Contract terms: express, implied and the status of terms', ['3.2.1', '3.2.2', '3.2.3']),
    ('exemption-clauses', 'Exemption clauses', ['3.2.4']),
    ('performance-and-breach', 'Discharge by performance and breach', ['3.3.1', '3.3.2']),
    ('frustration', 'Discharge by frustration', ['3.3.3']),
    ('contract-remedies', 'Remedies for breach of contract: damages and equitable remedies', ['3.4.1', '3.4.2']),
    ('negligence', 'Negligence: duty of care, breach, causation and remoteness', ['4.1.1', '4.1.2', '4.1.3', '4.1.4']),
    ('novel-duty-situations', 'Novel duty situations: psychiatric injury and economic loss', ['4.1.5']),
    ('occupiers-liability', "Occupiers' liability", ['4.2.1']),
    ('private-nuisance', 'Private nuisance', ['4.2.2']),
    ('rylands-v-fletcher', 'Rylands v Fletcher', ['4.2.3']),
    ('trespass-to-land', 'Trespass to land', ['4.2.4']),
    ('trespass-to-the-person', 'Trespass to the person: assault, battery and false imprisonment', ['4.3.1', '4.3.2', '4.3.3']),
    ('tort-defences', 'General defences in tort', ['4.4.1']),
    ('tort-remedies', 'Remedies in tort', ['4.4.2']),
]
TOPICS = {code: (slug, name) for slug, name, codes in TOPIC_LIST for code in codes}
GROUP_OF = {'1.1': 'Paper 1: Sources of law and law making', '1.2': 'Paper 1: Machinery of justice', '1.3': 'Paper 1: Legal personnel',
            '2.1': 'Paper 2: Criminal law', '2.2': 'Paper 2: Criminal law', '2.3': 'Paper 2: Sentencing',
            '3.1': 'Paper 3: Law of contract', '3.2': 'Paper 3: Law of contract', '3.3': 'Paper 3: Law of contract', '3.4': 'Paper 3: Law of contract',
            '4.1': 'Paper 4: Law of tort', '4.2': 'Paper 4: Law of tort', '4.3': 'Paper 4: Law of tort', '4.4': 'Paper 4: Law of tort'}
PAPER_NAMES = {1: 'English Legal System', 2: 'Criminal Law', 3: 'Law of Contract', 4: 'Law of Tort'}
FMT = {'Short answer': 'Short answer', 'Explain / describe (AO1)': 'Explain or describe', 'Source-based application': 'Source-based application',
       'Problem scenario': 'Scenario', 'Discussion / essay': 'Essay'}
SER = {'March': 'm', 'June': 's', 'November': 'w'}


def load_bank(bank):
    js = Path(bank, 'data', 'index.js').read_text(encoding='utf-8')
    out = subprocess.run(['node', '-e', 'global.window={};eval(require("fs").readFileSync(0,"utf8"));process.stdout.write(JSON.stringify(window.QB))'],
                         input=js, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def sub(code):  # '2.2.7(a)' -> '2.2.7'
    return code.split('(')[0]


def lab(l):  # '3(a)' -> '3a'
    return re.sub(r'[()]', '', l)


def series_slug(p):
    return 'specimen' if p['src'] == 'specimen' else p['series'].lower().replace(' ', '-')


def ao_of(q):
    m = [x for x in q['mc'] if x.startswith('Marks: ')]
    if m:
        d = dict(re.findall(r'(AO\d) (\d+)', m[0]))
        ao = [int(d.get(f'AO{i}', 0)) for i in (1, 2, 3)]
        return ao, ','.join(f'AO{i}={ao[i-1]}' for i in (1, 2, 3) if ao[i - 1])
    return [0, 0, 0], ' + '.join(q['ao'].split(','))


def convert(job):
    bundle, src, dest, want = job
    from PIL import Image
    s = Path(src).read_text()
    items = dict(re.findall(r'"([^"]+\.png)":\s*"data:image/png;base64,([^"]+)"', s))
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for name in want:
        if name not in items: continue
        out = dest / (name[:-4] + '.webp')
        if out.exists(): n += 1; continue
        im = Image.open(io.BytesIO(base64.b64decode(items[name])))
        if im.mode not in ('RGB', 'L'): im = im.convert('RGB')
        im.save(out, 'WEBP', lossless=True, method=4)
        n += 1
    return bundle, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bank', required=True)
    ap.add_argument('--images', action='store_true')
    a = ap.parse_args()
    D = load_bank(a.bank)
    img_dir = Path(a.bank, 'data', 'img')
    have = {f.stem: set(re.findall(r'"([^"]+\.png)":', f.read_text())) for f in img_dir.glob('*.js')}
    spec_sections = {s['code']: s for s in D['spec']}
    papers, questions, jobs = [], [], []
    for p in D['papers']:
        n = p['paper']
        qual = 'AS' if n <= 2 else 'A level'
        sl = series_slug(p)
        comp = p['comp'] if p['src'] == 'exam' else str(n)
        pid = f"9084-{comp}-{p['id'].split('_')[0].upper()}"
        qs = [q for q in D['q'] if q['p'] == p['id']]
        want, rec_ids = [], []
        for q in qs:
            ao, aot = ao_of(q)
            A = [s_ for s_, k in q['st'] if k == 'A']
            subs = list(dict.fromkeys(sub(s_) for s_ in A)) or list(dict.fromkeys(sub(s_) for s_, k in q['st']))
            topics = list(dict.fromkeys(TOPICS[s_][0] for s_ in subs if s_ in TOPICS))
            sec = next((x for x in q['mc'] if x.startswith('Section')), '')
            notes = [x for x in q['mc'] if not re.match(r'(Section|Marks:|Cambridge publishes no AO)', x)]
            cropname = lambda f: f'/img/cie/{p["id"]}/{f[:-4]}.webp' if f and f in have.get(p['id'], ()) else None
            et = re.sub(r'\s+', ' ', q.get('et') or '').strip()
            for f in (q['qi'], q['mi'], q['ei'] if et else None):
                if f and f in have.get(p['id'], ()): want.append(f)
            qid = f'{pid}-{lab(q["l"])}'
            rec_ids.append(qid)
            num = int(re.match(r'\d+', q['l']).group())
            questions.append({
                'id': qid, 'paperId': pid, 'bundle': p['id'], 'spec': '9084', 'comp': comp if p['src'] == 'exam' else None,
                'paper': f'Paper {n}', 'level': qual, 'series': 'Specimen' if p['src'] == 'specimen' else p['series'],
                'year': p['year'], 'question': q['l'], 'number': num, 'part': 0, 'marks': q['m'], 'ao': ','.join(f'AO{i}' for i in (1, 2, 3) if ao[i - 1]) or q['ao'], 'aoText': aot,
                'format': FMT.get(q['fmt'], q['fmt']), 'commands': q['cmd'], 'scenario': q['fmt'] in ('Problem scenario', 'Source-based application'),
                'section': sec, 'sectionLetter': sec[8:9] if sec else '',
                'crop': cropname(q['qi']), 'msCrop': cropname(q['mi']), 'erCrop': cropname(q['ei']) if et else None,
                'text': q['qt'], 'title': q['qt'].split('\n')[-1] if q['qt'] else '', 'msText': q['mt'], 'erText': '', 'erBrief': et[:400],
                'statements': A or [s_ for s_, k in q['st']], 'context': [s_ for s_, k in q['st'] if k == 'C'], 'topics': topics, 'area': GROUP_OF.get('.'.join(subs[0].split('.')[:2]), '').split(': ')[-1] if subs else '',
                'skills': q['sk'], 'mistakes': notes, 'choice': None, 'dupOf': None,
                'difficulty': None, 'facility': None, 'notCurrentSpec': False, 'features': ['has_scenario'] if q['fmt'] == 'Problem scenario' else [],
                'item': False, 'lds': False, 'mcqAnswers': None, 'msBands': [], 'paperName': PAPER_NAMES[n], 'specNote': '',
                'stemCrop': None, 'stemId': None, 'stemText': '', 'sourceLines': '',
            })
        papers.append({
            'id': pid, 'bundle': p['id'], 'kind': 'specimen' if p['src'] == 'specimen' else 'exam', 'series': 'Specimen' if p['src'] == 'specimen' else p['series'],
            'year': p['year'], 'spec': '9084', 'qual': qual, 'paper': f'Paper {n}', 'paperNo': str(n), 'comp': comp,
            'name': PAPER_NAMES[n], 'total': p['total'], 'questions': rec_ids, 'reprints': p.get('twins') or [],
            'slug': f'{sl}-9084-{comp}' if p['src'] == 'exam' else f'specimen-9084-{n}',
            'source': 'Cambridge', 'files': {'qp': p['qp'], 'ms': p['ms'], 'er': p['er']},
        })
        jobs.append((p['id'], str(img_dir / f"{p['id']}.js"), str(IMG / p['id']), want))
    # a topic no question assesses takes the questions that use it as context
    assessed = {t for q in questions for t in q['topics']}
    for q in questions:
        for s_ in q['context']:
            t = TOPICS.get(sub(s_), (None,))[0]
            if t and t not in assessed and t not in q['topics']: q['topics'].append(t)
    topics = []
    for slug, name, codes in TOPIC_LIST:
        secs = [spec_sections[c] for c in codes]
        tq = [q for q in questions if slug in q['topics']]
        g = GROUP_OF['.'.join(codes[0].split('.')[:2])]
        sts = [st for s_ in secs for st in s_['st']]
        tn = int(codes[0].split('.')[0])
        topics.append({
            'slug': slug, 'name': name, 'code': ', '.join(codes), 'codes': codes, 'group': g, 'strand': g, 'paper': g,
            'papers': sorted({q['paper'] for q in tq}), 'option': None, 'aLevelOnly': tn > 2,
            'asOrA': 'AS and A Level' if tn <= 2 else 'A Level only',
            'statements': [st['id'] for st in sts], 'statementText': {st['id']: st['t'] for st in sts}, 'statementShort': {st['id']: '' for st in sts},
            'asStatements': [], 'levels': {st['id']: None for st in sts},
            'parts': len(tq), 'marks': sum(q['marks'] for q in tq), 'essays': sum(1 for q in tq if q['format'] == 'Essay'), 'mcq': 0,
            'sectionTitle': ' / '.join(f"{s_['code']} {s_['title']}" for s_ in secs),
            'syllabusTopic': spec_sections['.'.join(codes[0].split('.')[:2])]['title'],
        })
    print('topics with no questions:', [t['slug'] for t in topics if not t['parts']])
    spec = []
    for s_ in D['spec']:
        lvl = len(s_['code'].split('.'))
        tn = int(s_['code'].split('.')[0])
        spec.append({'code': s_['code'], 'title': s_['title'], 'level': lvl, 'paper': tn, 'aLevelOnly': tn > 2, 'topic': TOPICS.get(s_['code'], (None,))[0],
                     'statements': [{'id': st['id'], 'text': st['t'], 'guidance': st.get('g', ''), 'as': tn <= 2,
                                     'topics': [TOPICS[s_['code']][0]] if s_['code'] in TOPICS else []} for st in s_['st']]})
    areas = {s_['code']: s_['title'] for s_ in D['spec'] if len(s_['code'].split('.')) == 2}
    byPaper = {}
    for q in questions:
        if q['statements']:
            ar = '.'.join(q['statements'][0].split('.')[:2])
            byPaper.setdefault(q['paperId'], {}).setdefault(ar, 0); byPaper[q['paperId']][ar] += q['marks']
    OUT.mkdir(parents=True, exist_ok=True)
    order = {'March': 0, 'June': 1, 'November': 2}
    papers.sort(key=lambda p: (p['kind'] != 'exam', -p['year'], -order.get(p['series'].split(' ')[0], 0), p['comp']))
    for name, obj in [('questions', questions), ('papers', papers), ('topics', topics), ('spec', spec), ('weighting', {'areas': areas, 'byPaper': byPaper})]:
        (OUT / f'{name}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=0))
    print(f'{len(papers)} papers, {len(questions)} parts, {len(topics)} topics, untopiced: {[q["id"] for q in questions if not q["topics"]][:5]}')
    print('no question crop:', sum(1 for q in questions if not q['crop']), ' no MS crop:', sum(1 for q in questions if not q['msCrop']), ' ER crops:', sum(1 for q in questions if q['erCrop']))
    if a.images:
        with ProcessPoolExecutor() as ex:
            list(ex.map(convert, jobs))
        print('images done:', sum(1 for _ in IMG.rglob('*.webp')))


if __name__ == '__main__':
    main()
