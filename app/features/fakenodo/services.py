"""
FakenodoService — in-memory simulation of the Zenodo Depositions API.

Designed for development and testing: registered only under ``features_dev``
in ``pyproject.toml`` so it is never loaded in production.

Business rules implemented:
1. Create deposition  → new incremental id, conceptdoi, doi = None.
2. Update metadata    → overwrites metadata without changing doi or dirty_files.
3. Upload file        → appends file entry and sets dirty_files = True.
4. New version        → clones deposition keeping same conceptdoi/conceptrecid,
                        resets doi to None and dirty_files to False.
5. Publish            → assigns doi only when doi is None OR dirty_files is True;
                        if only metadata was edited the doi is kept intact.
6. Get / List / Delete → standard CRUD with 404 guard.
"""


class FakenodoService:
    def __init__(self):
        self.depositions: dict = {}
        self.next_id: int = 1
        self.next_concept_id: int = 1000
        self.next_doi_id = 1

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset state between tests."""
        self.depositions = {}
        self.next_id = 1
        self.next_concept_id = 1000
        self.next_doi_id = 1

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_deposition(self, metadata: dict | None = None) -> dict:
        dep_id = self.next_id
        self.next_id += 1
        concept_id = self.next_concept_id
        self.next_concept_id += 1

        deposition = {
            "id": dep_id,
            "conceptrecid": str(concept_id),
            "conceptdoi": f"10.5072/zenodo.{concept_id}",
            "doi": None,
            "metadata": metadata or {},
            "files": [],
            "submitted": False,
            "dirty_files": False,
        }
        self.depositions[dep_id] = deposition
        return deposition

    def get_deposition(self, dep_id: int) -> dict | None:
        return self.depositions.get(dep_id)

    def list_depositions(self) -> list:
        return list(self.depositions.values())

    def update_metadata(self, dep_id: int, metadata: dict) -> dict | None:
        dep = self.depositions.get(dep_id)
        if not dep:
            return None
        dep["metadata"] = metadata
        # Rule 2: editing only metadata does NOT set dirty_files
        return dep

    def add_file(self, dep_id: int, filename: str) -> dict | None:
        dep = self.depositions.get(dep_id)
        if not dep:
            return None
        dep["files"].append({"filename": filename})
        dep["dirty_files"] = True  # Rule 3
        return dep

    def new_version(self, dep_id: int) -> dict | None:
        old_dep = self.depositions.get(dep_id)
        if not old_dep:
            return None

        new_id = self.next_id
        self.next_id += 1

        new_dep = {
            "id": new_id,
            # Rule 4: keep same concept identifiers
            "conceptrecid": old_dep["conceptrecid"],
            "conceptdoi": old_dep["conceptdoi"],
            "doi": None,
            "metadata": dict(old_dep["metadata"]),
            "files": list(old_dep["files"]),
            "submitted": False,
            "dirty_files": False,
        }
        self.depositions[new_id] = new_dep
        return new_dep

    def publish(self, dep_id):
        dep = self.depositions.get(dep_id)
        if not dep:
            return None

        if dep["doi"] is None or dep["dirty_files"]:
            dep["doi"] = f"10.5072/zenodo.{self.next_doi_id}"
            self.next_doi_id += 1

        dep["submitted"] = True
        dep["dirty_files"] = False
        return dep

    def delete_deposition(self, dep_id: int) -> bool:
        return self.depositions.pop(dep_id, None) is not None


# Module-level singleton shared by routes and tests
fakenodo_service = FakenodoService()
