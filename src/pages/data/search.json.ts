import { allTopics, allPapers } from '../../lib/data';
import spec from '../../data/spec.json';
const tools = [{"t": "Practice player", "u": "/practice/", "kind": "Tool"}, {"t": "Mini-mock builder", "u": "/mock/", "kind": "Tool"}, {"t": "Question of the day", "u": "/today/", "kind": "Tool"}, {"t": "Spec checklist", "u": "/specification/", "kind": "Tool"}, {"t": "Grade boundaries and calculator", "u": "/grade-boundaries/", "kind": "Tool"}, {"t": "Exam dates", "u": "/exam-dates/", "kind": "Tool"}, {"t": "Revision planner", "u": "/planner/", "kind": "Tool"}, {"t": "What comes up (analysis)", "u": "/analysis/", "kind": "Tool"}, {"t": "What came up last summer", "u": "/what-came-up/", "kind": "Tool"}, {"t": "Every paper as a timeline", "u": "/timeline/", "kind": "Tool"}, {"t": "Tutor", "u": "/tutors/", "kind": "Tool"}, {"t": "Essays and timed essay", "u": "/essays/", "kind": "Tool"}, {"t": "Scenario (problem) questions", "u": "/questions/type/scenarios/", "kind": "Tool"}, {"t": "Describe and explain questions", "u": "/questions/type/describe-explain/", "kind": "Tool"}, {"t": "Evaluation questions", "u": "/questions/type/evaluation/", "kind": "Tool"}, {"t": "Essay questions", "u": "/questions/type/essays/", "kind": "Tool"}, {"t": "Key terms flashcards", "u": "/flashcards/", "kind": "Tool"}];
export function GET() {
  const items = [
    ...allTopics.map((t) => ({ t: t.name, k: t.group, u: `/questions/${t.slug}/`, kind: 'Topic' })),
    ...allPapers.map((p) => ({ t: `${p.kind === 'exam' ? p.series : 'Sample paper'} ${p.qual === 'AS' ? 'AS' : 'A-level'} ${p.paper}`, k: p.spec, u: `/past-papers/${p.slug}/`, kind: 'Paper' })),
  ...spec.flatMap((s) => s.statements.map((st) => ({ t: `${st.id} ${st.text.slice(0, 80)}`, k: s.title, u: `/questions/${s.topic}/`, kind: 'Spec statement' }))),
    ...tools,
  ];
  return new Response(JSON.stringify(items), { headers: { 'Content-Type': 'application/json' } });
}
