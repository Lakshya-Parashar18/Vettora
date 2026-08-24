import re
from typing import List

from app.schemas.job import JobDescription
from app.schemas.requirement import StructuredRequirement
from app.services.ontology_service import ontology_engine


CRITICAL_KEYWORDS = {"must have", "required", "essential", "mandatory", "minimum", "strong knowledge"}
NICE_TO_HAVE_KEYWORDS = {"preferred", "nice to have", "plus", "bonus", "optional", "good to have"}


def detect_importance(phrase: str, is_explicitly_required: bool) -> str:
    """
    Classifies requirement importance: critical | core | supporting | nice_to_have | contextual.
    """
    p_lower = phrase.lower()

    if any(kw in p_lower for kw in NICE_TO_HAVE_KEYWORDS) or not is_explicitly_required:
        return "nice_to_have"
    elif any(kw in p_lower for kw in CRITICAL_KEYWORDS):
        return "critical"
    elif is_explicitly_required:
        return "core"
    return "supporting"


def decompose_compound_requirement(raw_text: str, is_required: bool = True) -> List[StructuredRequirement]:
    """
    Decomposes compound strings (e.g. 'Strong Python and machine learning skills')
    into individual StructuredRequirement items.
    """
    clean_text = raw_text.strip()
    if not clean_text:
        return []

    # Check for compound conjunctions: "X and Y", "X, Y, or Z"
    # But preserve multi-word concepts like "Data Structures & Algorithms" or "AI & ML"
    phrases = [clean_text]
    if " and " in clean_text.lower() and "data structures" not in clean_text.lower() and "ai &" not in clean_text.lower():
        phrases = [p.strip() for p in re.split(r'\band\b|,', clean_text, flags=re.IGNORECASE) if p.strip()]

    results: List[StructuredRequirement] = []

    for phrase in phrases:
        importance = detect_importance(phrase, is_required)
        weight = 2.0 if importance in {"critical", "core"} else 1.0

        concept_info = ontology_engine.get_concept(phrase)
        category = "technical"
        concepts: List[str] = [phrase]
        aliases: List[str] = [phrase]

        if concept_info:
            category = concept_info.get("category", "technical")
            child_concepts = ontology_engine.get_child_concepts(phrase)
            if child_concepts:
                concepts = child_concepts
            aliases.extend(concept_info.get("synonyms", []))

        results.append(
            StructuredRequirement(
                requirement=phrase,
                category=category,
                importance=importance,
                weight=weight,
                concepts=concepts,
                aliases=list(set(aliases)),
                confidence=1.0,
            )
        )

    return results


def decompose_job_description(job: JobDescription) -> List[StructuredRequirement]:
    """
    Decomposes an entire JobDescription object into structured requirements.
    """
    structured_reqs: List[StructuredRequirement] = []

    for req in job.required_skills:
        structured_reqs.extend(decompose_compound_requirement(req, is_required=True))

    for pref in job.preferred_skills:
        structured_reqs.extend(decompose_compound_requirement(pref, is_required=False))

    return structured_reqs
