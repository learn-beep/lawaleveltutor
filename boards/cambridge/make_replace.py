"""Writes boards/cambridge/replace.json: the string replacements the Cambridge build applies to a copy of src/ (specific first, then generic).
Whole pages that differ are in boards/cambridge/overrides/src/ and are copied over afterwards (no replacements are applied to them)."""
import json, pathlib
pairs = [
    ['Past-paper questions, mark schemes and examiner reports are © OCR and are shown free for study.',
     "Past-paper questions, mark schemes and examiners' reports are © Cambridge University Press &amp; Assessment and are shown free for study."],
    ["line = 'Scenario answers stuck in Level 2, or running out of time on the 20-markers? Book a trial lesson with Sue, who has taught A-level Law for 25 years.'",
     "line = 'Problem answers stuck in the middle levels, or running out of time on the 25-markers? Book a trial lesson with Sue, a qualified solicitor who has taught A-level Law for 25 years.'"],
    ['<h2>Work with an OCR A-level Law tutor</h2>', '<h2>Work with an A-level Law tutor</h2>'],
    ["Hi, I'm looking for an OCR Law Tutor.", "Hi, I'm looking for a Cambridge International Law Tutor."],
    ['return `${t} | OCR A-level Law`;', 'return `${t} | Cambridge A Level Law 9084`;'],
    ["description = 'Free OCR A-level Law past-paper questions by topic, with mark schemes, examiner comments, practice and an OCR Law tutor.'",
     "description = 'Free Cambridge International AS and A Level Law (9084) past-paper questions by topic, with mark schemes, examiners\\' report comments, practice and an online Law tutor.'"],
    ["alternateName: ['lawaleveltutor.com', 'OCR A-level Law Tutor']", "alternateName: ['lawaleveltutor.com', 'Cambridge A Level Law Tutor']"],
    ["Open this paper on OCR's site", "See Cambridge's 9084 page"],
    ["<Icon name=\"comment\" />Examiner's comment</button>", "<Icon name=\"comment\" />Examiners' report</button>"],
    ["<h4>Examiner's comment</h4>", "<h4>Examiners' report on this question</h4>"],
    ['{topic.name}: OCR Law past-paper questions pack', '{topic.name}: Cambridge 9084 Law past-paper questions pack'],
    ['OCR AS and A-level Law past-paper questions since 2022 · {qs.length} questions · mark schemes follow the questions · www.lawaleveltutor.com · Questions and mark schemes © OCR',
     'Cambridge International AS and A Level Law (9084) past-paper questions since 2023 · {qs.length} questions · mark schemes follow the questions · www.lawaleveltutor.com · Questions and mark schemes © Cambridge University Press &amp; Assessment'],
    ["const papers = allPapers.filter((p) => p.kind === 'exam').sort((a, b) => b.year - a.year || a.spec.localeCompare(b.spec) || Number(a.paperNo) - Number(b.paperNo));",
     "const rank = (s) => Number(s.split(' ')[1]) * 10 + ({ March: 1, June: 2, November: 3 }[s.split(' ')[0]] || 0);\nconst papers = allPapers.filter((p) => p.kind === 'exam').sort((a, b) => rank(b.series) - rank(a.series) || Number(a.paperNo) - Number(b.paperNo) || a.comp.localeCompare(b.comp));"],
    ["{p.series.replace('June ', 'Jun ').replace('November ', 'Nov ')} {p.qual === 'AS' ? 'AS ' : ''}P{p.paperNo}", "{p.series.replace('June ', 'Jun ').replace('November ', 'Nov ')} {p.comp}"],
    ['Every OCR A-level Law paper as a timeline, 2022–2025', 'Every Cambridge A Level Law 9084 paper as a timeline, 2023–2025'],
    ['Tap a block to open it. Every question printed is shown, though students answer only some: one of each pair in Section A and one of the two parts in Section B. The 20-mark scenarios and essays are the big blocks.',
     'Tap a block to open it. Each row is one paper (9084/12 is Paper 1, variant 2). Every question printed is shown, though students answer only some of them: two of the three Paper 1 essays, one of the two Paper 2 Section B questions, and on Papers 3 and 4 one scenario and two essays. The 25-mark questions are the big blocks.'],
    ["with the mark scheme and the examiner's comment. Same question for everyone", "with the mark scheme and the examiners' report. Same question for everyone"],
    ['OCR AS and A-level Law', 'Cambridge International AS and A Level Law'],
    ['OCR A-level Law', 'Cambridge A Level Law 9084'],
    ['OCR Law', 'Cambridge Law 9084'],
    ["OCR's", "Cambridge's"],
    ['OCR_MATERIALS', 'OCR_MATERIALS'],
    ['OCR', 'Cambridge'],
    ['H418', '9084'], ['H018', '9084'],
    ['2022–2025', '2023–2025'],
    ["'malt-", "'malt-cie-"], ['`malt-', '`malt-cie-'], ['"malt-', '"malt-cie-'],
]
json.dump({'all': pairs, 'delete': ['src/data/decks']}, open(pathlib.Path(__file__).with_name('replace.json'), 'w'), indent=1, ensure_ascii=False)
print(len(pairs))
