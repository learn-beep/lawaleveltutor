import questions from '../data/questions.json';
import papers from '../data/papers.json';
import topics from '../data/topics.json';

export type Q = (typeof questions)[number];
export type Paper = (typeof papers)[number];
export type Topic = (typeof topics)[number];

/** Every question as printed, including Paper 3B's copies of the Questions 3 to 6 that Paper 3A also prints. */
export const everyQuestion: Q[] = questions as Q[];
/** Questions for topic pages, practice and counts: each question once. */
export const allQuestions: Q[] = everyQuestion.filter((q) => !q.dupOf);
export const allPapers: Paper[] = papers as Paper[];
export const allTopics: Topic[] = topics as Topic[];

export const byId = new Map(everyQuestion.map((q) => [q.id, q]));
export const topicByslug = new Map(allTopics.map((t) => [t.slug, t]));

const SERIES_ORDER: Record<string, number> = { June: 2, November: 3 };
/** Newest first: year, then November > June, specimens last. */
export const seriesRank = (s: string) => (s === 'Specimen' ? 0 : Number(s.split(' ')[1]) * 10 + (SERIES_ORDER[s.split(' ')[0]] || 0));

export function questionsForTopic(slug: string): Q[] {
  return allQuestions.filter((q) => q.topics.includes(slug)).sort((a, b) => seriesRank(b.series) - seriesRank(a.series) || a.paper.localeCompare(b.paper) || a.number - b.number);
}

export const OCR_MATERIALS = 'https://www.aqa.org.uk/subjects/law/a-level/law-7162/assessment-resources';
export const AQA_MATERIALS = OCR_MATERIALS;
export const FIRST_SERIES = 'November 2020';

/** Where a topic sits: group, badge label, badge colour, motif and where it is examined. */
const ELS = 'Every paper (1, 2, 3A and 3B): multiple-choice Questions 3 to 5, the 5-mark Question 6, half of the 15-mark Question 9 essay and often the last part of Question 11';
export const GROUPS: [string, string, number, string, string][] = [
  ['Nature of law', 'Nature of law', 1, 'book', 'Every paper: the 15-mark Question 9 essay sets a nature of law theme (fault, morality, justice, balancing interests) against an area of the paper\'s substantive law; it also appears in the multiple choice and at the end of Question 11'],
  ['Law making', 'Law making', 3, 'book', ELS],
  ['The legal system', 'Legal system', 1, 'scales', ELS],
  ['Criminal law', 'Crime', 4, 'scales', 'Paper 1: multiple-choice Questions 1 and 2, the 5-mark Question 7, the 10-mark Question 8, half of the Question 9 essay and the 30-mark Questions 10 and 11'],
  ['Tort', 'Tort', 2, 'people', 'Paper 2: multiple-choice Questions 1 and 2, the 5-mark Question 7, the 10-mark Question 8, half of the Question 9 essay and the 30-mark Questions 10 and 11'],
  ['Law of contract', 'Contract', 3, 'coins', 'Paper 3A: multiple-choice Questions 1 and 2, the 5-mark Question 7, the 10-mark Question 8, half of the Question 9 essay and the 30-mark Questions 10 and 11'],
  ['Human rights', 'Human rights', 2, 'globe', 'Paper 3B: multiple-choice Questions 1 and 2, the 5-mark Question 7, the 10-mark Question 8, half of the Question 9 essay and the 30-mark Questions 10 and 11'],
];
export function groupInfo(group: string) {
  const g = GROUPS.find((x) => x[0] === group) || GROUPS[0];
  return { group: g[0], short: g[1], badge: g[2], motif: g[3], where: g[4], area: g[0] };
}
/** The instruction of a question (the scenario, where there is one, is left out). */
export function essayTitle(q: { title?: string; text?: string }): string {
  return (q.title || q.text || '').replace(/\s+/g, ' ').trim();
}
export function paperLabel(q: { paper: string }): string {
  return q.paper;
}
