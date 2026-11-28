"""Exports the AQA A-level Law (7162) question bank to the site's data format.

Usage: python3 boards/aqa/export_aqa.py --bank "<Law/AQA/Question Bank>" [--images]
Writes boards/aqa/data/{questions,papers,topics,spec,weighting}.json and, with --images,
public/img/aqa/<paper>/<name>.webp (lossless WebP from the bank's PNG crops).
"""
import argparse, base64, io, json, re, subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / 'data'
IMG = REPO / 'public' / 'img' / 'aqa'

# site topic: slug, name, the specification topics (3.x.y) or single statements (3.x.y(a)) it covers
TOPIC_LIST = [
    ('nature-of-law', 'Nature of law: legal rules, civil and criminal law, sources of law', ['3.1.1']),
    ('law-and-society', 'Law and society: balancing interests and the role of fault', ['3.1.2']),
    ('law-and-morality', 'Law and morality', ['3.1.3']),
    ('law-and-justice', 'Law and justice', ['3.1.4']),
    ('rule-of-law', 'The rule of law', ['3.1.5']),
    ('parliamentary-law-making', 'Parliamentary law making', ['3.1.6']),
    ('delegated-legislation', 'Delegated legislation', ['3.1.7']),
    ('statutory-interpretation', 'Statutory interpretation', ['3.1.8']),
    ('judicial-precedent', 'Judicial precedent', ['3.1.9']),
    ('law-reform', 'Law reform and the Law Commission', ['3.1.10']),
    ('european-union-law', 'The European Union', ['3.1.11']),
    ('civil-courts-and-adr', 'Civil courts and other forms of dispute resolution', ['3.1.12']),
    ('criminal-courts-and-lay-people', 'Criminal courts and lay people: magistrates, juries and sentencing', ['3.1.13']),
    ('legal-personnel-and-the-judiciary', 'Legal personnel and the judiciary', ['3.1.14']),
    ('access-to-justice-and-funding', 'Access to justice and funding', ['3.1.15']),
    ('theory-in-criminal-law', 'Theory in criminal law: harm, fault and the principles', ['3.2.1']),
    ('actus-reus-and-mens-rea', 'General elements of liability: actus reus, mens rea and causation', ['3.2.2']),
    ('murder-and-voluntary-manslaughter', 'Murder and voluntary manslaughter: loss of control and diminished responsibility', ['3.2.3(a)', '3.2.3(b)', '3.2.3(c)']),
    ('involuntary-manslaughter', 'Involuntary manslaughter: unlawful act and gross negligence', ['3.2.3(d)', '3.2.3(e)']),
    ('non-fatal-offences', 'Non-fatal offences against the person', ['3.2.4']),
    ('theft-and-robbery', 'Property offences: theft and robbery', ['3.2.5']),
    ('attempts', 'Attempt', ['3.2.6']),
    ('insanity-automatism-and-intoxication', 'Capacity defences: insanity, automatism and intoxication', ['3.2.7(a)', '3.2.7(b)', '3.2.7(c)']),
    ('self-defence-and-duress', 'Necessity defences: self-defence, duress and duress of circumstances', ['3.2.7(d)', '3.2.7(e)', '3.2.7(f)']),
    ('theory-of-tort-law', 'Theory of tort law', ['3.3.1']),
    ('negligence', 'Negligence: duty of care, breach and damage', ['3.3.2']),
    ('economic-loss-and-psychiatric-injury', 'Economic loss and psychiatric injury', ['3.3.3']),
    ('occupiers-liability', "Occupiers' liability", ['3.3.4']),
    ('nuisance-and-rylands-v-fletcher', 'Private nuisance and Rylands v Fletcher', ['3.3.5']),
    ('vicarious-liability', 'Vicarious liability', ['3.3.6']),
    ('tort-defences', 'Defences in tort: contributory negligence and consent', ['3.3.7']),
    ('tort-remedies', 'Remedies in tort: damages and injunctions', ['3.3.8']),
    ('theory-of-contract-law', 'Theory of contract law', ['3.4.1']),
    ('formation-of-contract', 'Formation of contract: offer and acceptance, consideration, privity and intention', ['3.4.2']),
    ('contract-terms', 'Contract terms: express and implied terms, conditions and warranties', ['3.4.3']),
    ('consumer-rights-act-2015', 'Consumer Rights Act 2015: implied terms and remedies', ['3.4.4']),
    ('exclusion-clauses', 'Exclusion clauses', ['3.4.5']),
    ('misrepresentation-and-economic-duress', 'Vitiating factors: misrepresentation and economic duress', ['3.4.6']),
    ('discharge-of-contract', 'Discharge of a contract: performance, breach and frustration', ['3.4.7']),
    ('contract-remedies', 'Remedies in contract: damages, equitable remedies and termination', ['3.4.8']),
    ('theory-in-human-rights', 'Theory in human rights', ['3.5.1']),
    ('human-rights-before-the-hra', 'Human rights in international law and in the UK before the Human Rights Act 1998', ['3.5.2', '3.5.3']),
    ('human-rights-act-1998', 'The Human Rights Act 1998 and reform', ['3.5.4', '3.5.13']),
    ('article-2-right-to-life', 'Article 2: the right to life', ['3.5.5']),
    ('article-5-right-to-liberty', 'Article 5: the right to liberty and security', ['3.5.6']),
    ('article-8-private-and-family-life', 'Article 8: respect for private and family life', ['3.5.7']),
    ('articles-10-and-11', 'Articles 10 and 11: freedom of expression, assembly and association', ['3.5.8', '3.5.9']),
    ('restrictions-on-rights', 'Restrictions on the rights (Articles 8.2, 10.2 and 11.2)', ['3.5.10']),
    ('enforcement-of-human-rights', 'Enforcement of human rights and judicial review', ['3.5.11']),
    ('human-rights-and-english-law', 'Human rights and English law: police powers, privacy and protest', ['3.5.12']),
]
GROUP_OF = {'3.1.1': 'Nature of law', '3.1.2': 'Nature of law', '3.1.3': 'Nature of law', '3.1.4': 'Nature of law', '3.1.5': 'Nature of law',
            '3.1.6': 'Law making', '3.1.7': 'Law making', '3.1.8': 'Law making', '3.1.9': 'Law making', '3.1.10': 'Law making', '3.1.11': 'Law making',
            '3.1.12': 'The legal system', '3.1.13': 'The legal system', '3.1.14': 'The legal system', '3.1.15': 'The legal system',
            '3.2': 'Criminal law', '3.3': 'Tort', '3.4': 'Law of contract', '3.5': 'Human rights'}
PAPER_NAMES = {'1': 'Criminal law', '2': 'Tort', '3A': 'Law of contract', '3B': 'Human rights'}
FMT = {'Multiple choice': 'Multiple choice', 'Short answer (5 marks)': 'Explain', 'Application (5 marks)': 'Application',
       'Problem: advise (10 marks)': 'Scenario', 'Extended essay (15 marks)': 'Essay', 'Extended problem (30 marks)': 'Scenario'}


def topic_of(st):  # '3.2.3(d)' -> slug
    sec = st.split('(')[0]
    for slug, name, codes in TOPIC_LIST:
        if st in codes or sec in codes: return slug
    return None


def group_of(code):
    sec = code.split('(')[0]
    return GROUP_OF.get(sec) or GROUP_OF['.'.join(sec.split('.')[:2])]


def load_bank(bank):
    js = Path(bank, 'data', 'index.js').read_text(encoding='utf-8')
    out = subprocess.run(['node', '-e', 'global.window={};eval(require("fs").readFileSync(0,"utf8"));process.stdout.write(JSON.stringify(window.QB))'],
                         input=js, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


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
        if not out.exists():
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
    seen = {}   # (series, question text) -> id of the first copy: Papers 3A and 3B print the same questions 3 to 6
    order = {'1': 1, '2': 2, '3A': 3, '3B': 4}
    for p in sorted(D['papers'], key=lambda p: (p['src'] != 'exam', -p['year'], p['series'], order[str(p['paper'])])):
        n = str(p['paper'])
        specimen = p['src'] != 'exam'
        series = 'Specimen' if specimen else p['series']
        tag = p['id'].split('_')[0]
        pid = f'7162-{n}-{tag}'
        qs = [q for q in D['q'] if q['p'] == p['id']]
        want, rec_ids = [], []
        for q in qs:
            ao = dict(re.findall(r'(AO\d) (\d+)', next((x for x in q['mc'] if x.startswith('Marks: ')), '')))
            aot = ','.join(f'{k}={v}' for k, v in ao.items())
            A = [s_ for s_, k in q['st'] if k == 'A']
            C = [s_ for s_, k in q['st'] if k == 'C']
            topics = list(dict.fromkeys(t for t in map(topic_of, A) if t))
            ans = next((x[8:].strip() for x in q['mc'] if x.startswith('Answer: ')), None)
            notes = [x for x in q['mc'] if not re.match(r'(Marks:|Answer:)', x)]
            focus = notes[0] if notes else ''
            cropname = lambda f: f'/img/aqa/{p["id"]}/{f[:-4]}.webp' if f and f in have.get(p['id'], ()) else None
            et = re.sub(r'\s+', ' ', q.get('et') or '').strip()
            for f in (q['qi'], q['mi'], q['ei'] if et else None):
                if f and f in have.get(p['id'], ()): want.append(f)
            num = int(q['l'])
            qid = f'{pid}-{num}'
            rec_ids.append(qid)
            fmt = FMT[q['fmt']]
            if num in (3, 6): q['qt'] = re.sub(r'(?<=\S)[ \n]box(?=[ \n]|$)', '', q['qt'] or '', count=1)   # the margin's "Do not write outside the box" runs into these two questions in the bank's text
            lines = [l for l in (q['qt'] or '').split('\n') if l.strip()]
            text = re.sub(r'\s+', ' ', q['qt'] or '').strip()
            if fmt == 'Multiple choice':
                title = re.split(r'\s+A\s+(?=[A-Z‘\'"])', text)[0]
            else:  # the instruction: from the last line that opens a new sentence with a command
                k = max((i for i, l in enumerate(lines) if re.match(r'(Advise|Assess|Consider|Discuss|Examine|Explain|Suggest|Outline|Briefly|Describe|Taking|Referring|In relation|Identify|Analyse|Evaluate|Compare|Using)', l)), default=None)
                first = min((i for i, l in enumerate(lines) if re.match(r'(Advise|Assess|Consider|Discuss|Examine|Explain|Suggest|Outline|Briefly|Describe|Taking|Referring|Identify|Analyse|Evaluate|Compare|Using|Having regard|With regard|With reference|Assuming)', l)), default=k)
                title = ' '.join(lines[first if first is not None else 0:]) if fmt != 'Essay' else text
                if fmt != 'Essay' and len(title) > 420:
                    cut = [m.start() for m in re.finditer(r'(?<=[.?!] )(Advise|Assess|Consider|Suggest|Taking|Referring|Having regard|With regard|With reference|Assuming|In relation)', text)]
                    if cut: title = text[min(c for c in cut if len(text) - c < 700) if any(len(text) - c < 700 for c in cut) else cut[-1]:]
            if fmt == 'Application' and len(title) > 300: title = re.split(r'(?<=[.?!]) (?=[A-Z])', text)[-1]
            key = (series, text)
            dup = seen.get(key) if n == '3B' else None
            if n == '3A': seen[key] = qid
            # the bank's tagging notes are not shown on the site; only the figures taken from AQA's report and mark scheme are kept in 'mistakes'
            questions.append({
                'id': qid, 'paperId': pid, 'bundle': p['id'], 'spec': '7162', 'comp': None,
                'paper': f'Paper {n}', 'level': 'A level', 'series': series, 'year': p['year'],
                'question': str(num), 'number': num, 'part': 0, 'marks': q['m'], 'ao': q['ao'], 'aoText': aot,
                'format': fmt, 'commands': q['cmd'], 'scenario': fmt in ('Scenario', 'Application'),
                'section': '', 'sectionLetter': '',
                'crop': cropname(q['qi']), 'msCrop': cropname(q['mi']), 'erCrop': cropname(q['ei']) if et else None,
                'text': text, 'title': title, 'focus': focus, 'msText': re.sub(r'\s+', ' ', q['mt'] or '')[:600], 'erText': '', 'erBrief': et[:400],
                'statements': A, 'context': C, 'topics': topics, 'area': group_of(A[0]) if A else '',
                'skills': [], 'mistakes': [x for x in notes if re.match(r'(About \d+% chose|Substantive \d+)', x)], 'choice': None, 'dupOf': dup,
                'difficulty': q['d'] if q['d'] in ('Easy', 'Medium', 'Hard') else None, 'facility': None, 'notCurrentSpec': False,
                'features': (['extended'] if 'level_of_response' in q['fl'] else []), 'item': False, 'lds': False,
                'mcqAnswers': [ans] if ans else None, 'msBands': [], 'paperName': PAPER_NAMES[n], 'specNote': '',
                'stemCrop': None, 'stemId': None, 'stemText': '', 'sourceLines': '',
            })
        papers.append({
            'id': pid, 'bundle': p['id'], 'kind': 'specimen' if specimen else 'exam', 'series': series, 'year': p['year'], 'spec': '7162',
            'qual': 'A level', 'paper': f'Paper {n}', 'paperNo': n, 'comp': n, 'name': PAPER_NAMES[n], 'total': p['total'], 'questions': rec_ids, 'reprints': [],
            'slug': ('specimen' if specimen else series.lower().replace(' ', '-')) + f'-7162-{n.lower()}',
            'hasReport': bool(p['er']), 'source': 'AQA', 'files': {'qp': p['qp'], 'ms': p['ms'], 'er': p['er']},
        })
        jobs.append((p['id'], str(img_dir / f"{p['id']}.js"), str(IMG / p['id']), want))
    live = [q for q in questions if not q['dupOf']]
    # a topic no question assesses takes the questions that draw on it as context
    assessed = {t for q in live for t in q['topics']}
    for q in questions:
        for s_ in q['context']:
            t = topic_of(s_)
            if t and t not in assessed and t not in q['topics']: q['topics'].append(t)
    topics = []
    for slug, name, codes in TOPIC_LIST:
        sts = []
        for c in codes:
            sec = spec_sections[c.split('(')[0]]
            sts += [st for st in sec['st'] if '(' not in c or st['id'] == c]
        secs = list(dict.fromkeys(c.split('(')[0] for c in codes))
        tq = [q for q in live if slug in q['topics']]
        g = group_of(codes[0])
        topics.append({
            'slug': slug, 'name': name, 'code': ', '.join(secs), 'codes': secs, 'group': g, 'strand': g, 'paper': g,
            'papers': sorted({q['paper'] for q in tq}), 'option': None, 'aLevelOnly': False, 'asOrA': 'A level',
            'statements': [st['id'] for st in sts], 'statementText': {st['id']: st['t'] for st in sts}, 'statementShort': {st['id']: '' for st in sts},
            'asStatements': [], 'levels': {st['id']: None for st in sts},
            'parts': len(tq), 'marks': sum(q['marks'] for q in tq), 'essays': sum(1 for q in tq if q['format'] == 'Essay'),
            'mcq': sum(1 for q in tq if q['format'] == 'Multiple choice'),
            'sectionTitle': ' / '.join(f"{s_} {spec_sections[s_]['title']}" for s_ in secs),
        })
    print('topics with no questions:', [t['slug'] for t in topics if not t['parts']])
    spec = []
    for s_ in D['spec']:
        lvl = len(s_['code'].split('.')) - 1   # 3.1 -> 1 (section), 3.1.6 -> 2 (topic)
        spec.append({'code': s_['code'], 'title': s_['title'], 'level': lvl, 'group': group_of(s_['code']) if lvl == 2 else None,
                     'statements': [{'id': st['id'], 'text': st['t'], 'topic': topic_of(st['id'])} for st in s_['st']]})
    areas = {}
    for slug, name, codes in TOPIC_LIST: areas.setdefault(group_of(codes[0]), group_of(codes[0]))
    byPaper = {}
    for q in questions:   # marks by the first statement assessed; every question printed is counted on its own paper
        if q['statements']:
            g = group_of(q['statements'][0])
            byPaper.setdefault(q['paperId'], {}).setdefault(g, 0); byPaper[q['paperId']][g] += q['marks']
    OUT.mkdir(parents=True, exist_ok=True)
    for name, obj in [('questions', questions), ('papers', papers), ('topics', topics), ('spec', spec), ('weighting', {'areas': areas, 'byPaper': byPaper})]:
        (OUT / f'{name}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=0))
    print(f'{len(papers)} papers, {len(questions)} questions ({len(live)} after folding the Paper 3B copies), {len(topics)} topics; untopiced: {[q["id"] for q in questions if not q["topics"]][:5]}')
    print('no question crop:', sum(1 for q in questions if not q['crop']), ' no MS crop:', sum(1 for q in questions if not q['msCrop']), ' ER crops:', sum(1 for q in questions if q['erCrop']),
          ' MCQ without answer:', sum(1 for q in questions if q['format'] == 'Multiple choice' and not q['mcqAnswers']))
    if a.images:
        with ProcessPoolExecutor() as ex:
            list(ex.map(convert, jobs))
        print('images:', sum(1 for _ in IMG.rglob('*.webp')))


if __name__ == '__main__':
    main()
