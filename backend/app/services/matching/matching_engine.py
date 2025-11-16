# backend/app/services/matching/matching_engine.py

class MatchingEngine:
    """
    Miguel: combinará skills_match, values_match, team_fit.
    De momento, devolvemos valores dummy.
    """

    def compute_scores(self, job, candidate) -> dict:
        # TODO: lógica real
        return {
            "score_global": 0.85,
            "skills_match": 0.9,
            "values_match": 0.8,
            "team_fit": 0.78
        }
