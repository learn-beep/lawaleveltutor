import { allQuestions, allTopics } from '../../lib/data';
export function GET() {
  const q = allQuestions.map((x) => ({
    id: x.id, t: x.topics, s: x.series, y: x.year, p: x.paper, l: x.level, q: x.question, m: x.marks, f: x.format, ao: x.aoText && x.aoText.replace(/=/g, ' ').replace(/,/g, ', '),
    d: x.difficulty, c: x.crop, ms: x.msCrop, st: null, old: 0, ans: x.mcqAnswers || null,
    pid: x.paperId, sc: '', pt: 0, n: x.number, ti: x.title,
    e: ((t) => t && t.length > 280 ? t.slice(0, 277).replace(/\s+\S*$/, '') + '…' : t)(x.erBrief || ''), cp: null,
  }));
  const topics = allTopics.map((t) => ({ slug: t.slug, name: t.name, paper: t.group, parts: t.parts }));
  return new Response(JSON.stringify({ q, topics }), { headers: { 'Content-Type': 'application/json' } });
}
