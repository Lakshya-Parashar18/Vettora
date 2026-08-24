# Vettora Matching & Scoring Engine Pipeline Audit Report

## 1. Executive Summary

This document provides a comprehensive architectural audit of Vettora's resume-JD evaluation pipeline prior to the Phase 1 refactoring.

The audit identifies the root cause of false-negative evaluation failures (such as the **Presidio Associate Engineer** candidate test case, where a candidate with core subjects *Data Structures & Algorithms, Object-Oriented Programming, DBMS, Operating Systems, Computer Networks* received a 0% CS Fundamentals score and a 4.7/10 overall rating).

---

## 2. Component Inventory & Responsibilities

The current evaluation pipeline is governed by six primary backend components in `backend/app/`:

| Component | File Path | Primary Responsibility |
| :--- | :--- | :--- |
| **Job Extractor** | [`prompts/job_extraction_prompt.py`](file:///d:/Official/Vettora/backend/app/prompts/job_extraction_prompt.py) & [`services/llm_service.py`](file:///d:/Official/Vettora/backend/app/services/llm_service.py#L204-L230) | Parses raw JD text into `JobDescription` model containing `required_skills` (flat string array) and `preferred_skills`. |
| **Resume Extractor** | [`prompts/resume_extraction_prompt.py`](file:///d:/Official/Vettora/backend/app/prompts/resume_extraction_prompt.py) & [`services/llm_service.py`](file:///d:/Official/Vettora/backend/app/services/llm_service.py#L137-L167) | Parses resume text into `StructuredResume` containing `skills` (flat string array), `education`, `experience`, `projects`, `certifications`. |
| **Skill Normalizer** | [`services/skill_normalizer.py`](file:///d:/Official/Vettora/backend/app/services/skill_normalizer.py) | Maps simple string alias variations (e.g. `ReactJS` → `React`, `py` → `Python`, `k8s` → `Kubernetes`). |
| **Semantic Evaluator** | [`prompts/semantic_matching_prompt.py`](file:///d:/Official/Vettora/backend/app/prompts/semantic_matching_prompt.py) & [`services/llm_service.py`](file:///d:/Official/Vettora/backend/app/services/llm_service.py#L292-L332) | Calls LLM to produce `SemanticEvaluation` with `conceptual_matches`, `evidence`, and `semantic_score`. |
| **Scoring Engine** | [`services/scoring_service.py`](file:///d:/Official/Vettora/backend/app/services/scoring_service.py) | Executes mathematical scoring, experience calculation, education scoring, and merges deterministic and semantic scores. |
| **API Endpoints** | [`api/screen.py`](file:///d:/Official/Vettora/backend/app/api/screen.py) | Endpoints handling screening requests, MongoDB persistence, and evaluation retrieval. |

---

## 3. Detailed Technical Breakdown & Identified Pipeline Weaknesses

### Weakness 1: String-Literal Reliance in Deterministic Matching
- **Location**: `calculate_skill_score()` in [`scoring_service.py`](file:///d:/Official/Vettora/backend/app/services/scoring_service.py#L101-L136)
- **Mechanism**: Calculates `matched_req` by testing `s in c_skills` where `c_skills` is a set of flat skill strings.
- **Impact**: When a JD requires `"Computer Science fundamentals"`, but the candidate lists `"Data Structures & Algorithms"`, `"Object-Oriented Programming"`, `"DBMS"`, `"Operating Systems"`, and `"Computer Networks"`, `matched_req` evaluates to `[]` (empty list). This causes `bin_req_score` and `bin_skills_score` to drop to **0%**.

### Weakness 2: Flat Skill List vs. Multi-Section Resume Evidence
- **Location**: `extract_structured_resume_with_llm()` in [`llm_service.py`](file:///d:/Official/Vettora/backend/app/services/llm_service.py#L79-L134)
- **Mechanism**: Resume evidence is extracted as isolated strings into `resume.skills`. Coursework mentioned in `education` or project tech stacks in `projects` are not linked as structured evidence items with section origin, evidence type (`coursework`, `project`, `explicit_skill`), or confidence.
- **Impact**: Broad requirements (e.g. `Computer Science fundamentals`) fail to inspect coursework listed under education degrees (e.g., `B.Tech CSE - Core Subjects: DSA, OOP, DBMS, OS, CN`).

### Weakness 3: Lack of Structured Requirement Modeling
- **Location**: `JobDescription` schema in [`schemas/job.py`](file:///d:/Official/Vettora/backend/app/schemas/job.py#L16-L26)
- **Mechanism**: Requirements are stored as plain string arrays (`required_skills: ["Computer Science fundamentals", "IT fundamentals"]`). There is no rich representation containing requirement category (`cs_fundamentals`, `technical`, `soft_skill`), importance level (`critical`, `core`, `supporting`), underlying concepts (`DSA`, `OOP`, `DBMS`), or alias rules.
- **Impact**: The engine treats `"Computer Science fundamentals"` as a single monolithic string rather than an umbrella requirement encompassing multiple sub-concepts.

### Weakness 4: Absence of Non-Equivalence Guardrails
- **Mechanism**: Standard semantic LLM matching prompt without explicit guardrails can either hallucinate equivalence (e.g., treating `Docker` as equivalent to `Kubernetes`, or `React` as equal to `Angular`) or fail to differentiate related tools from direct matches.
- **Impact**: Risk of inaccurate false positives where related but distinct technologies are treated as identical.

---

## 4. Presidio Case Failure Diagnostic Summary

When evaluating the Presidio Associate Engineer candidate (B.Tech CS student with DSA, OOP, DBMS, OS, CN, Java, Python, C++, REST APIs, stock analytics project):

1. **`calculate_skill_score()`**: Compares `"Computer Science fundamentals"` vs `["Java", "Python", "React", "DSA", "OOP", "DBMS", "OS", "CN"]` -> **0% Match**.
2. **`req_score` & `skills_score`**: Fall to 0.0%.
3. **Overall Weighted Score Math**:
   - `skills_score` (40%): 0.0 -> **0.0**
   - `experience` (25%): 100.0 -> **2.5**
   - `education` (15%): 100.0 -> **1.5**
   - `required_criteria` (10%): 0.0 -> **0.0**
   - `semantic_fit` (10%): 70.0 -> **0.7**
   - **Total Overall Score**: **4.7 / 10** (Weak Match label assigned incorrectly!).

---

## 5. Phase 1 Refactoring Plan & Architecture

To permanently resolve this class of failures without hardcoding single keyword aliases:

1. **Structured Requirement Representation**:
   Create `StructuredRequirement` schema with `requirement`, `category`, `importance`, `weight`, `concepts`, `aliases`, `related_skills`, `evidence_rules`, `confidence`.

2. **Structured Resume Evidence Representation**:
   Create `StructuredEvidence` schema with `skill`, `evidence_type` (`explicit_skill`, `coursework`, `project`, `experience`, `certification`, `education`), `evidence_strength`, `source_text`, `source_section`, `confidence`.

3. **Multi-Tier Matching Engine (`matching_engine.py`)**:
   Implement 5 distinct match classifications:
   - `DIRECT_MATCH` (1.0 weight)
   - `SEMANTIC_MATCH` (0.9 weight)
   - `HIERARCHICAL_CONCEPTUAL_MATCH` (computed coverage fraction of evidenced sub-concepts)
   - `RELATED_BUT_NOT_EQUIVALENT` (0.3 relation score - NOT treated as direct equivalence!)
   - `NO_EVIDENCE` (0.0 weight)

4. **Non-Equivalence Rules**:
   Strict guardrails preventing `Docker` = `Kubernetes`, `React` = `Angular`, `Machine Learning` = `Deep Learning`, `SQL` = `PostgreSQL`, `Git` = `GitHub Actions`.

5. **Traceable Explainability**:
   Every requirement match links directly back to `source_section` and `source_text` evidence from the candidate's resume.
