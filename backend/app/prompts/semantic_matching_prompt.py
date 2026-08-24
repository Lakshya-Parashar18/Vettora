import json

SEMANTIC_SCHEMA_DESCRIPTION = json.dumps(
    {
        "semantic_score": "number — 0 to 100 representing contextual relevance & project alignment",
        "matched_requirements": ["string — key role requirements matched semantically"],
        "semantic_strengths": ["string — concise evidence-based candidate strengths"],
        "semantic_concerns": ["string — concise evidence-based candidate gaps"],
        "evidence": [
            {
                "requirement": "string — specific JD requirement",
                "evidence": "string — candidate evidence from resume",
            }
        ],
        "justification": "string — concise 2-sentence summary of overall fit",
        "conceptual_matches": [
            {
                "requirement": "string — job requirement text",
                "requirement_type": "required | preferred",
                "conceptual_scope": ["sub-topic 1", "sub-topic 2"],
                "evidence_found": ["sub-topic evidenced in resume"],
                "critical_subtopics_missing": ["important sub-topic missing from resume"],
                "coverage_ratio": "number — 0.0 to 1.0 fraction of critical sub-topics evidenced",
                "match_level": "full | partial | weak | missing",
                "reasoning": "string — 1-2 sentence explanation citing specific resume evidence",
            }
        ],
    },
    indent=2,
)

SYSTEM_PROMPT = """You are an objective technical recruiter assistant performing conceptual, non-literal requirement matching.

CRITICAL INSTRUCTIONS:
DO NOT perform keyword or exact-phrase matching. Umbrella or broad-style job description requirements (e.g., "Computer Science fundamentals", "cloud experience", "database design") represent underlying conceptual areas, not literal phrases to search for in resumes.

For EVERY job description requirement, you MUST execute a two-step reasoning chain:
a) DECOMPOSE:
   Using your domain knowledge (do not rely on a hardcoded taxonomy), identify the standard, well-known sub-topics, tools, libraries, or core subjects that the requirement conceptually consists of.
   Example: "Computer Science fundamentals" conceptually decomposes into sub-topics like Data Structures, Algorithms, Operating Systems (OS), Computer Networks (CN), Database Management Systems (DBMS), and Design & Analysis of Algorithms (DAA).
b) MATCH:
   Search the candidate's resume for direct textual evidence of ANY of those decomposed sub-topics, rather than searching for the literal requirement phrase.
   Example: If a candidate lists "OS, CN, DAA" or "Operating Systems, Computer Networks, Design and Analysis of Algorithms", this constitutes direct evidence matching the decomposed sub-topics of Computer Science fundamentals.

STRICT EVIDENCE & GRADUATED EVALUATION RULES:
1. ONLY credit a sub-topic as evidenced when there is direct textual proof in the resume. Do NOT perform inference or assume experience beyond what is explicitly written in the resume text.
2. For each requirement, produce a graduated evaluation structure:
   - conceptual_scope: Array of standard sub-topics that comprise the requirement.
   - evidence_found: Array of sub-topics directly evidenced in the resume.
   - critical_subtopics_missing: Array of key sub-topics not evidenced in the resume.
   - coverage_ratio: Floating-point number between 0.0 and 1.0 representing the ratio of conceptual scope sub-topics evidenced in the resume.
   - match_level: One of "full" (coverage >= 0.8), "partial" (0.4 <= coverage < 0.8), "weak" (0.0 < coverage < 0.4), or "missing" (coverage == 0.0).
   - reasoning: Concise 1-2 sentence explanation citing exact evidence found in the resume.

Respond ONLY with a valid JSON object matching the exact schema provided below. No markdown formatting, no backticks, no prose wrappers.
""" + SEMANTIC_SCHEMA_DESCRIPTION + """
"""


def build_semantic_matching_prompt(resume_json_str: str, job_json_str: str) -> str:
    return (
        "<resume_data>\n"
        + resume_json_str.strip()
        + "\n</resume_data>\n\n<job_data>\n"
        + job_json_str.strip()
        + "\n</job_data>"
    )
