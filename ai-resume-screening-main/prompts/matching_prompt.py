# ============================================================
# prompts/matching_prompt.py
# Compares extracted resume data against a job description.
# Uses few-shot prompting and requests JSON output.
# ============================================================

from langchain_core.prompts import PromptTemplate


FEW_SHOT_EXAMPLE = """
EXAMPLE INPUT:
Extracted Info:
{
  "candidate_name": "Jane Doe",
  "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
  "years_of_experience": 3,
  "tools_and_technologies": ["Docker", "Git"],
  "education": "B.Sc Computer Science",
  "certifications": ["AWS Solutions Architect"],
  "key_projects": ["E-commerce API"]
}

Job requires: Python, Machine Learning, SQL, Docker, 2+ years experience.

EXAMPLE OUTPUT:
```json
{
  "matched_required_skills": ["Python", "SQL (PostgreSQL)"],
  "missing_required_skills": ["Machine Learning"],
  "matched_preferred_skills": ["Docker", "Git"],
  "experience_match": true,
  "experience_detail": "3 years exceeds the 2-year minimum",
  "education_match": true,
  "education_detail": "B.Sc Computer Science meets the requirement",
  "overall_match_pct": 65,
  "match_summary": "Strong backend skills but missing core ML experience."
}
```
"""


def get_matching_prompt() -> PromptTemplate:
    """Return a PromptTemplate that matches resume data to a job description."""

    template = """You are an expert technical recruiter.
Compare the candidate's extracted information with the job description and
identify matches and gaps.

RULES:
- Only match skills that are EXPLICITLY stated in the extracted info.
- Do NOT give benefit of the doubt for missing skills.
- Be objective and precise.
- Return ONLY valid JSON — no extra text before or after the JSON block.

{few_shot}

CANDIDATE EXTRACTED INFORMATION:
\"\"\"
{extracted_info}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

Return a JSON object with these exact keys:
- "matched_required_skills" (list of strings)
- "missing_required_skills" (list of strings)
- "matched_preferred_skills" (list of strings)
- "experience_match" (boolean)
- "experience_detail" (string — brief explanation)
- "education_match" (boolean)
- "education_detail" (string — brief explanation)
- "overall_match_pct" (integer 0-100)
- "match_summary" (string — 2-3 sentence summary)

Respond with ONLY the JSON object:"""

    return PromptTemplate(
        input_variables=["extracted_info", "job_description"],
        partial_variables={"few_shot": FEW_SHOT_EXAMPLE},
        template=template,
    )