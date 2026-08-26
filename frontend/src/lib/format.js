export const pct = (value) => `${Math.round((value ?? 0) * 100)}%`

export const hours = (value) =>
  value >= 40 ? `${Math.round(value / 8) / 1} d` : `${value} h`

export function humanDate(iso) {
  if (!iso) return ''
  const date = new Date(`${iso}T00:00:00`)
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

export const KIND_STYLE = {
  course: { label: 'Course', className: 'border-accent/40 text-accent bg-accent/10' },
  project: { label: 'Project', className: 'border-mint/40 text-mint bg-mint/10' },
  assessment: { label: 'Assessment', className: 'border-amber/40 text-amber bg-amber/10' },
}

export const LEVEL_LABEL = { 1: 'Beginner', 2: 'Intermediate', 3: 'Advanced' }

/** Component names as the ranker reports them, in learner-facing words. */
export const COMPONENT_LABEL = {
  coverage: 'Closes your gaps',
  semantic: 'Matches your goal',
  collab: 'Similar learners',
  level_fit: 'Right difficulty',
  quality: 'Highly rated',
  modality: 'Your format',
}
