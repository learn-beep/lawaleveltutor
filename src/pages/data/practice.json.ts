import { allQuestions, allTopics } from '../../lib/data';
export function GET() {
  const q = allQuestions.map((x) => ({
    id: x.id, t: x.topics, s: x.series, y: x.year, p: x.paper, l: x.level, q: x.question, m: x.marks, f: x.format, ao: x.aoText && x.aoText.replace(/=/g, ' ').replace(/,/g, ', '),
    d: x.difficulty, c: x.crop, ms: x.msCrop, st: null, old: x.notCurrentSpec ? 1 : 0, ans: null,
    pid: x.paperId, sc: x.sectionLetter, pt: x.part, n: x.number, ti: x.title,
    e: ((t) => t && t.length > 280 ? t.slice(0, 277).replace(/\s+\S*$/, '') + '…' : t)(x.erText || x.erBrief || ''), cp: x.comp || null,
  }));
  const topics = allTopics.map((t) => ({ slug: t.slug, name: t.name, paper: t.group, parts: t.parts }));
  return new Response(JSON.stringify({ q, topics }), { headers: { 'Content-Type': 'application/json' } });
}
