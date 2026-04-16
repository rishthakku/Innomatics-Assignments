# ============================================================
# chains/screening_chain.py
# Production-style LangChain LCEL pipeline.
# Flow: Resume → Extract → Match → Score → Explain
# Each step is a proper LCEL chain using the | pipe operator.
# ============================================================

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from prompts.extraction_prompt import get_extraction_prompt
from prompts.matching_prompt import get_matching_prompt
from prompts.scoring_prompt import get_scoring_prompt


class ResumeScreeningChain:
    """
    Three-step LCEL resume screening pipeline.

    Step 1 — Extraction:  Resume text → structured candidate info (JSON)
    Step 2 — Matching:    Extracted info + Job description → match analysis (JSON)
    Step 3 — Scoring:     Match analysis → fit score + explanation (JSON)
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1):
        """
        Initialise the LLM and build three LCEL chains.

        Args:
            model_name:   OpenAI model identifier.
            temperature:  Lower → more deterministic output.
        """
        print(f"\n🤖 Initialising AI model: {model_name}  (temp={temperature})")

        # --- LLM instance (shared across all chains) ---
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        # --- Output parser (converts AIMessage → plain string) ---
        parser = StrOutputParser()

        # --- LCEL chains built with the | pipe operator ---
        # Each chain: PromptTemplate | ChatOpenAI | StrOutputParser
        self.extraction_chain = get_extraction_prompt() | self.llm | parser
        self.matching_chain   = get_matching_prompt()   | self.llm | parser
        self.scoring_chain    = get_scoring_prompt()    | self.llm | parser

        print("✅ LCEL pipeline built  (extraction → matching → scoring)")

    # ------------------------------------------------------------------
    # Individual step methods (useful for debugging a single step)
    # ------------------------------------------------------------------

    def extract_skills(self, resume_text: str, *, tags: list | None = None) -> str:
        """Step 1 — Extract skills and background from a resume."""
        print("  📄 Step 1: Extracting skills …")
        config = {"tags": tags} if tags else {}
        result = self.extraction_chain.invoke(
            {"resume_text": resume_text},
            config=config,
        )
        print("  ✅ Extraction complete")
        return result

    def match_skills(
        self,
        extracted_info: str,
        job_description: str,
        *,
        tags: list | None = None,
    ) -> str:
        """Step 2 — Compare extracted info with job requirements."""
        print("  🔍 Step 2: Matching skills …")
        config = {"tags": tags} if tags else {}
        result = self.matching_chain.invoke(
            {"extracted_info": extracted_info, "job_description": job_description},
            config=config,
        )
        print("  ✅ Matching complete")
        return result

    def score_and_explain(self, match_analysis: str, *, tags: list | None = None) -> str:
        """Step 3 — Score the candidate and generate an explanation."""
        print("  📊 Step 3: Scoring & explaining …")
        config = {"tags": tags} if tags else {}
        result = self.scoring_chain.invoke(
            {"match_analysis": match_analysis},
            config=config,
        )
        print("  ✅ Scoring complete")
        return result

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run_pipeline(
        self,
        resume_text: str,
        job_description: str,
        candidate_name: str = "Unknown",
        candidate_type: str = "unknown",
    ) -> dict:
        """
        Execute the full three-step pipeline.

        Args:
            resume_text:     Raw resume content.
            job_description: Raw job description content.
            candidate_name:  Name shown in logs and output files.
            candidate_type:  Tag for LangSmith (e.g. "strong", "average", "weak").

        Returns:
            dict with keys: candidate_name, candidate_type, status,
                            extracted_info, match_analysis, score_explanation
        """
        print(f"\n{'='*60}")
        print(f"🚀 Pipeline start — {candidate_name} [{candidate_type}]")
        print(f"{'='*60}")

        # LangSmith tags for filtering in the dashboard
        tags = [candidate_type, "resume-screening"]

        try:
            # Step 1 → Step 2 → Step 3  (chained outputs)
            extracted_info  = self.extract_skills(resume_text, tags=tags)
            match_analysis  = self.match_skills(extracted_info, job_description, tags=tags)
            score_explanation = self.score_and_explain(match_analysis, tags=tags)

            print(f"✅ Pipeline complete — {candidate_name}")
            return {
                "candidate_name": candidate_name,
                "candidate_type": candidate_type,
                "status": "SUCCESS",
                "extracted_info": extracted_info,
                "match_analysis": match_analysis,
                "score_explanation": score_explanation,
            }

        except Exception as exc:
            print(f"❌ Pipeline failed — {candidate_name}: {exc}")
            return {
                "candidate_name": candidate_name,
                "candidate_type": candidate_type,
                "status": "FAILED",
                "error": str(exc),
                "extracted_info": None,
                "match_analysis": None,
                "score_explanation": None,
            }