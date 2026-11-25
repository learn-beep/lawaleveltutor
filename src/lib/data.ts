import questions from '../data/questions.json';
import papers from '../data/papers.json';
import topics from '../data/topics.json';

export type Q = (typeof questions)[number];
export type Paper = (typeof papers)[number];
export type Topic = (typeof topics)[number];

/** Every question as printed, including the Paper 4 copies of the nature-of-law essays that Paper 3 also prints. */
export const everyQuestion: Q[] = questions as Q[];
/** Questions for topic pages, practice and counts: each question once (Paper 4's copies of Paper 3's Section A are left out). */
export const allQuestions: Q[] = everyQuestion.filter((q) => !q.dupOf);
export const allPapers: Paper[] = papers as Paper[];
export const allTopics: Topic[] = topics as Topic[];

export const byId = new Map(everyQuestion.map((q) => [q.id, q]));
export const topicByslug = new Map(allTopics.map((t) => [t.slug, t]));

export function questionsForTopic(slug: string): Q[] {
  return allQuestions.filter((q) => q.topics.includes(slug)).sort((a, b) => b.year - a.year || a.level.localeCompare(b.level) || a.paper.localeCompare(b.paper) || a.number - b.number);
}

export const OCR_MATERIALS = 'https://www.ocr.org.uk/qualifications/as-and-a-level/law-h018-h418-from-2020/assessment/';
export const FIRST_SERIES = 'June 2022';

/** Where a topic sits: badge label, badge colour, motif and where it is examined. */
export const GROUPS: [string, string, number, string, string][] = [
  ['The legal system', 'Legal system', 1, 'scales', 'A-level Paper 1 Section A (one 8-mark and one 12-mark question); AS Paper 1 Section A'],
  ['Criminal law', 'Crime', 4, 'scales', 'A-level Paper 1 Section B (two 20-mark scenarios and a 20-mark essay); AS Paper 1 Section B'],
  ['Law making', 'Law making', 3, 'book', 'A-level Paper 2 Section A (one 8-mark and one 12-mark question); AS Paper 2 Section A'],
  ['The law of tort', 'Tort', 2, 'people', 'A-level Paper 2 Section B (two 20-mark scenarios and a 20-mark essay); AS Paper 2 Section B'],
  ['The nature of law', 'Nature of law', 1, 'book', 'A-level Paper 3 and Paper 4, Section A (one 20-mark essay from a choice of two)'],
  ['Human rights law', 'Human rights', 2, 'globe', 'A-level Paper 3 Section B (two 20-mark scenarios and a 20-mark essay)'],
  ['The law of contract', 'Contract', 3, 'coins', 'A-level Paper 4 Section B (two 20-mark scenarios and a 20-mark essay)'],
];
export function groupInfo(group: string) {
  const g = GROUPS.find((x) => x[0] === group) || GROUPS[0];
  return { group: g[0], short: g[1], badge: g[2], motif: g[3], where: g[4], area: g[0] };
}

/** The question sentence of a question (the scenario, where there is one, is left out). */
export function essayTitle(q: { title?: string; text?: string }): string {
  return (q.title || q.text || '').replace(/\s+/g, ' ').trim();
}
/** "A-level Paper 1" / "AS Paper 2". */
export function paperLabel(q: { level: string; paper: string }): string {
  return `${q.level === 'AS' ? 'AS' : 'A-level'} ${q.paper}`;
}
