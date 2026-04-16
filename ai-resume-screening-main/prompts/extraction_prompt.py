# ============================================================
# prompts/extraction_prompt.py
# Extracts structured information from a resume.
# Uses few-shot prompting and requests JSON output.
# ============================================================

from langchain_core.prompts import PromptTemplate


# --------------- Few-shot example (guides the model) ---------------
FEW_SHOT_EXAMPLE = """
EXAMPLE INPUT RESUME:
\"\"\"
NAME: Jane Doe
SUMMARY: 3 years experience in backend engineering.
EXPERIENCE:
  Backend Engineer | Acme Corp | 2021-Present
  - Built REST APIs with Python/FastAPI
  - Managed PostgreSQL databases
SKILLS: Python, FastAPI, PostgreSQL, Docker, Git
EDUCATION: B.Sc Computer Science, MIT, 2020
CERTIFICATIONS: AWS Solutions Architect
PROJECTS: 1. E-commerce API (FastAPI, Docker)
\"\"\"

EXAMPLE OUTPUT:
```json
{
  "candidate_name": "Jane Doe",
  "technical_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
  "years_of_experience": 3,
  "tools_and_technologies": ["PostgreSQL", "Docker", "Git"],
  "education": "B.Sc Computer Science, MIT, 2020",
  "certifications": ["AWS Solutions Architect"],
  "key_projects": ["E-commerce API (FastAPI, Docker)"]
}
```
"""


def get_extraction_prompt() -> PromptTemplate:
    """Return a PromptTemplate that extracts resume information as JSON."""

    template = """You are an expert HR analyst and resume parser.
Read the resume below and extract the requested information.

RULES:
- Only include what is ACTUALLY stated in the resume.
- Do NOT hallucinate or assume skills that are not mentioned.
- If a field is not mentioned, use null or an empty list.
- Return ONLY valid JSON — no extra text before or after the JSON block.

{few_shot}

NOW PROCESS THIS RESUME:
\"\"\"
{resume_text}
\"\"\"

Return a JSON object with these exact keys:
- "candidate_name" (string)
- "technical_skills" (list of strings)
- "years_of_experience" (number — total professional years, 0 if none)
- "tools_and_technologies" (list of strings — platforms, software, services)
- "education" (string — highest degree and institution)
- "certifications" (list of strings, empty list if none)
- "key_projects" (list of strings — short descriptions)

Respond with ONLY the JSON object:"""

    return PromptTemplate(
        input_variables=["resume_text"],
        partial_variables={"few_shot": FEW_SHOT_EXAMPLE},
        template=template,
    )