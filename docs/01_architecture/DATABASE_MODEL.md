# Database Model

## Main entities detected

| entity | purpose | state |
| --- | --- | --- |
| `users` | Authentication and role owner | implemented |
| `candidates` | Candidate profile data | implemented |
| `companies` | Company profile data | implemented |
| `company_culture` | Company values and culture profile | implemented |
| `jobs` | Job postings | implemented |
| `team_profiles` | Team-level job context | implemented |
| `team_members` | Individual team member context | implemented |
| `candidate_skills` | Candidate skill inventory | implemented |
| `job_skills` | Job skill requirements | implemented |
| `candidate_interviews` | HR Copilot output / interview summary | implemented but output is dummy |
| `applications` | Candidate applications to jobs | implemented |
| `job_recommendations` | Candidate-job recommendation tracking | implemented |
| `co_teaching_pairs` | Complementary candidate pairs per job | implemented |

## Clear relationships

- A user can have one candidate profile or one company profile.
- A company can have many jobs.
- A job can have many job skills, applications and co-teaching pairs.
- A candidate can have many candidate skills, interviews, applications and recommendations.
- A job can have one team profile and many team members through that profile.

## Inferred relationships

- Candidate skills and job skills are used as inputs for matching.
- Company culture feeds value and team-fit logic.
- Candidate interviews influence value and team-fit scores in heuristic form.

## What still needs confirmation

- Whether every table has a matching migration layer in the repository snapshot.
- Whether all JSON/text columns are used consistently by every route and frontend screen.
- Whether every model field in docs matches the current DB schema one-to-one, especially where scripts and routes add fields opportunistically.

## Warning

The repository shows SQLAlchemy models and seed scripts, but no explicit migration workflow was found in the inspected files.
That means the model layer should be treated as the best available source of truth, but still verified before schema-heavy changes.
