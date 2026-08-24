from typing import List

SKILL_ALIASES = {
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node.js": "Node.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "vue js": "Vue.js",
    "mongo db": "MongoDB",
    "mongodb": "MongoDB",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws lambda": "AWS Lambda",
    "gcp": "Google Cloud Platform",
}


def normalize_skill(skill_name: str) -> str:
    if not skill_name or not skill_name.strip():
        return ""
    cleaned = skill_name.strip()
    key = cleaned.lower()
    return SKILL_ALIASES.get(key, cleaned)


def normalize_skills(skills: List[str]) -> List[str]:
    normalized_list = []
    seen = set()

    for skill in skills:
        norm = normalize_skill(skill)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            normalized_list.append(norm)

    return normalized_list
