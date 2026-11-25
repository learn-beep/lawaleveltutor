import questions from '../data/questions.json';
import papers from '../data/papers.json';
import topics from '../data/topics.json';

export type Q = (typeof questions)[number];
export type Paper = (typeof papers)[number];
export type Topic = (typeof topics)[number];

export const everyQuestion: Q[] = questions as Q[];
export const allQuestions: Q[] = everyQuestion;
export const allPapers: Paper[] = papers as Paper[];
export const allTopics: Topic[] = topics as Topic[];

export const byId = new Map(everyQuestion.map((q) => [q.id, q]));
export const topicByslug = new Map(allTopics.map((t) => [t.slug, t]));

const SERIES_ORDER: Record<string, number> = { March: 1, June: 2, November: 3 };
/** Newest first: year, then November > June, specimens last. */
export const seriesRank = (s: string) => (s === 'Specimen' ? 0 : Number(s.split(' ')[1]) * 10 + (SERIES_ORDER[s.split(' ')[0]] || 0));

export function questionsForTopic(slug: string): Q[] {
  return allQuestions.filter((q) => q.topics.includes(slug)).sort((a, b) => seriesRank(b.series) - seriesRank(a.series) || a.paper.localeCompare(b.paper) || String(a.comp).localeCompare(String(b.comp)) || a.question.localeCompare(b.question, undefined, { numeric: true }));
}

export const OCR_MATERIALS = 'https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-law-9084/';
export const Cambridge_MATERIALS = OCR_MATERIALS;
export const FIRST_SERIES = 'June 2023';

export const GROUPS: [string, string, number, string, string][] = [
  ['Paper 1: Sources of law and law making', 'P1', 1, 'book', 'Paper 1 (English Legal System), AS Level: Section A short questions and the Section B two-part essays'],
  ['Paper 1: Machinery of justice', 'P1', 1, 'scales', 'Paper 1 (English Legal System), AS Level: Section A short questions and the Section B two-part essays'],
  ['Paper 1: Legal personnel', 'P1', 1, 'people', 'Paper 1 (English Legal System), AS Level: Section A short questions and the Section B two-part essays'],
  ['Paper 2: Criminal law', 'P2', 4, 'scales', 'Paper 2 (Criminal Law), AS Level: Section B (a 5-mark question and a 25-mark essay); the offences also appear in the Section A source-based scenario'],
  ['Paper 2: Sentencing', 'P2', 4, 'scales', 'Paper 2 (Criminal Law), AS Level: the Section A source-based question applies a sentencing guideline to three offenders'],
  ['Paper 3: Law of contract', 'P3', 3, 'coins', 'Paper 3 (Law of Contract), A Level: a 25-mark problem scenario (one from two) and 25-mark essays (two from three)'],
  ['Paper 4: Law of tort', 'P4', 2, 'people', 'Paper 4 (Law of Tort), A Level: a 25-mark problem scenario (one from two) and 25-mark essays (two from three)'],
];
export function groupInfo(group: string) {
  const g = GROUPS.find((x) => x[0] === group) || GROUPS[0];
  return { group: g[0], short: g[1], badge: g[2], motif: g[3], where: g[4], area: g[0].replace(/^Paper \d: /, '') };
}
export function essayTitle(q: { title?: string; text?: string }): string {
  return (q.title || q.text || '').replace(/\s+/g, ' ').trim();
}
export function paperLabel(q: { level?: string; paper: string; comp?: string | null; spec?: string }): string {
  return `${q.paper}${q.comp ? ` (${q.spec}/${q.comp})` : ''}`;
}
