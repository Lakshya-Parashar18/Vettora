import json
from pathlib import Path
from typing import Dict, List, Optional

TAXONOMY_FILE = Path(__file__).parent.parent / "data" / "taxonomy.json"


class SkillOntology:
    def __init__(self):
        self.concepts: Dict[str, dict] = {}
        self.alias_map: Dict[str, str] = {}
        self._load_taxonomy()

    def _load_taxonomy(self):
        if not TAXONOMY_FILE.exists():
            return

        try:
            with open(TAXONOMY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.concepts = data.get("concepts", {})

            # Build alias map (lowercase alias -> concept_id)
            for cid, cdata in self.concepts.items():
                self.alias_map[cid.lower()] = cid
                self.alias_map[cdata["name"].lower()] = cid
                for syn in cdata.get("synonyms", []):
                    self.alias_map[syn.lower()] = cid
                for abbr in cdata.get("abbreviations", []):
                    self.alias_map[abbr.lower()] = cid
        except Exception as e:
            print(f"[Warning] Failed to load taxonomy.json: {e}")

    def resolve_concept_id(self, query: str) -> Optional[str]:
        if not query:
            return None
        return self.alias_map.get(query.strip().lower())

    def get_concept(self, query: str) -> Optional[dict]:
        cid = self.resolve_concept_id(query)
        if cid and cid in self.concepts:
            return self.concepts[cid]
        return None

    def get_child_concepts(self, query: str) -> List[str]:
        cdata = self.get_concept(query)
        if not cdata:
            return []
        child_ids = cdata.get("narrower_concepts", [])
        return [self.concepts[cid]["name"] for cid in child_ids if cid in self.concepts]

    def get_parent_concepts(self, query: str) -> List[str]:
        cdata = self.get_concept(query)
        if not cdata:
            return []
        parent_ids = cdata.get("broader_concepts", [])
        return [self.concepts[pid]["name"] for pid in parent_ids if pid in self.concepts]

    def get_related_skills(self, query: str) -> List[str]:
        cdata = self.get_concept(query)
        if not cdata:
            return []
        related_ids = cdata.get("related_skills", [])
        return [self.concepts[rid]["name"] for rid in related_ids if rid in self.concepts]

    def is_parent_child_relationship(self, parent_query: str, child_query: str) -> bool:
        parent_id = self.resolve_concept_id(parent_query)
        child_id = self.resolve_concept_id(child_query)

        if not parent_id or not child_id:
            return False

        parent_cdata = self.concepts.get(parent_id, {})
        child_cdata = self.concepts.get(child_id, {})

        if child_id in parent_cdata.get("narrower_concepts", []):
            return True
        if parent_id in child_cdata.get("broader_concepts", []):
            return True

        return False

    def is_related_relationship(self, query_a: str, query_b: str) -> bool:
        id_a = self.resolve_concept_id(query_a)
        id_b = self.resolve_concept_id(query_b)

        if not id_a or not id_b or id_a == id_b:
            return False

        cdata_a = self.concepts.get(id_a, {})
        return id_b in cdata_a.get("related_skills", [])


# Singleton instance
ontology_engine = SkillOntology()
