# ============================================================
# prompts/scoring_prompt.py
# Produces a final fit score (0-100) with a detailed explanation.
# Uses few-shot prompting and requests JSON output.
# ============================================================

from langchain_core.prompts import PromptTemplate


FEW_SHOT_EXAMPLE = """
EXAMPLE INPUT (match analysis):
{
  "matched_required_skills": ["Python", "SQL"],
  "missing_required_skills": ["Machine Learning"],
  "matched_preferred_skills": ["Docker"],
  "experience_match": true,
  "experience_detail": "3 years",
  "education_match": true,
  "overall_match_pct": 65,
  "match_summary": "Strong backend skills but missing ML."
}

EXAMPLE OUTPUT:
```json
{
  "fit_score": 58,
  "recommendation": "MAYBE",
  "strengths": [
    "Solid Python and SQL skills",
    "Meets experience requirement",
    "Has Docker containerization knowledge"
  ],
  "weaknesses": [
    "No Machine Learning experience listed",
    "No deep learning or NLP background"
  ],
  "interview_recommendation": "Conditional — interview only if ML training can be provided on the job.",
  "explanation": "The candidate has a good engineering foundation with Python, SQL, and Docker, and meets the experience threshold. However, the core requirement of Machine Learning expertise is absent, which significantly limits their fit for a Data Scientist role. Score reflects strong fundamentals but a critical gap in the primary skill area."
}
```
"""


def get_scoring_prompt() -> PromptTemplate:
    """Return a PromptTemplate that scores a candidate based on match analysis."""

    template = """You are a senior hiring manager making a final decision.
Based on the match analysis below, produce a fit score and detailed explanation.

SCORING RUBRIC (weights):
- Required skills match:  50%
- Experience match:       25%
- Education match:        15%
- Preferred skills match: 10%

RECOMMENDATION BANDS:
- STRONG HIRE:  80-100
- CONSIDER:     60-79
- MAYBE:        40-59
- REJECT:        0-39

RULES:
- Be fair and objective.
- Base the score ONLY on the match analysis provided.
- Give specific, actionable reasons.
- Return ONLY valid JSON — no extra text before or after the JSON block.

{few_shot}

MATCH ANALYSIS:
\"\"\"
{match_analysis}
\"\"\"

Return a JSON object with these exact keys:
- "fit_score" (integer 0-100)
- "recommendation" (string — one of STRONG HIRE / CONSIDER / MAYBE / REJECT)
- "strengths" (list of strings)
- "weaknesses" (list of strings)
- "interview_recommendation" (string — Yes/No with brief reason)
- "explanation" (string — 3-5 sentence evaluation summary)

Respond with ONLY the JSON object:"""

    return PromptTemplate(
        input_variables=["match_analysis"],
        partial_variables={"few_shot": FEW_SHOT_EXAMPLE},
        template=template,
    )