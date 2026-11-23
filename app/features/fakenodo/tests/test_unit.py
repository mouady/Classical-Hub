"""
Unit tests for FakenodoService — pure logic, no Flask app, no database.

Covers:
- Basic CRUD (create, get, list, delete).
- File upload marks dirty_files = True.
- Update metadata does NOT touch dirty_files or existing doi.
- Publish assigns a doi the first time and when files changed.
- Publish keeps the same doi when only metadata was edited.
- New version: same conceptdoi, new id, fresh doi.
"""

import pytest

from app.features.fakenodo.services import FakenodoService

pytestmark = pytest.mark.unit


@pytest.fixture()
def svc():
    s = FakenodoService()
    yield s
    s.reset()


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_create_returns_deposition_with_incremental_id(svc):
    dep1 = svc.create_deposition()
    dep2 = svc.create_deposition()
    assert dep1["id"] == 1
    assert dep2["id"] == 2


def test_create_doi_is_none_before_publish(svc):
    dep = svc.create_deposition({"title": "My Dataset"})
    assert dep["doi"] is None
    assert dep["submitted"] is False
    assert dep["dirty_files"] is False


def test_create_stores_metadata(svc):
    dep = svc.create_deposition({"title": "T"})
    assert dep["metadata"] == {"title": "T"}


def test_create_different_concept_ids(svc):
    dep1 = svc.create_deposition()
    dep2 = svc.create_deposition()
    assert dep1["conceptdoi"] != dep2["conceptdoi"]
    assert dep1["conceptrecid"] != dep2["conceptrecid"]


# ---------------------------------------------------------------------------
# Get / List / Delete
# ---------------------------------------------------------------------------


def test_get_returns_none_for_missing(svc):
    assert svc.get_deposition(99) is None


def test_get_returns_created_deposition(svc):
    dep = svc.create_deposition()
    assert svc.get_deposition(dep["id"]) is dep


def test_list_depositions_empty(svc):
    assert svc.list_depositions() == []


def test_list_depositions_returns_all(svc):
    svc.create_deposition()
    svc.create_deposition()
    assert len(svc.list_depositions()) == 2


def test_delete_existing_returns_true(svc):
    dep = svc.create_deposition()
    assert svc.delete_deposition(dep["id"]) is True
    assert svc.get_deposition(dep["id"]) is None


def test_delete_missing_returns_false(svc):
    assert svc.delete_deposition(999) is False


# ---------------------------------------------------------------------------
# Update metadata
# ---------------------------------------------------------------------------


def test_update_metadata_changes_metadata(svc):
    dep = svc.create_deposition({"title": "Old"})
    svc.update_metadata(dep["id"], {"title": "New"})
    assert svc.get_deposition(dep["id"])["metadata"]["title"] == "New"


def test_update_metadata_does_not_set_dirty_files(svc):
    dep = svc.create_deposition()
    svc.update_metadata(dep["id"], {"title": "X"})
    assert svc.get_deposition(dep["id"])["dirty_files"] is False


def test_update_metadata_keeps_existing_doi(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "a.uvl")
    svc.publish(dep["id"])
    doi_before = dep["doi"]
    svc.update_metadata(dep["id"], {"title": "Updated"})
    assert svc.get_deposition(dep["id"])["doi"] == doi_before


def test_update_metadata_returns_none_for_missing(svc):
    assert svc.update_metadata(99, {}) is None


# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------


def test_add_file_sets_dirty_files(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "model.uvl")
    assert svc.get_deposition(dep["id"])["dirty_files"] is True


def test_add_file_appends_entry(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "a.uvl")
    svc.add_file(dep["id"], "b.uvl")
    assert len(svc.get_deposition(dep["id"])["files"]) == 2


def test_add_file_returns_none_for_missing(svc):
    assert svc.add_file(99, "x.uvl") is None


# ---------------------------------------------------------------------------
# Publish
# ---------------------------------------------------------------------------


def test_publish_assigns_doi_first_time(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "m.uvl")
    result = svc.publish(dep["id"])
    assert result["doi"] is not None
    assert result["submitted"] is True
    assert result["dirty_files"] is False


def test_publish_keeps_doi_when_only_metadata_edited(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "m.uvl")
    svc.publish(dep["id"])
    doi_v1 = dep["doi"]

    svc.update_metadata(dep["id"], {"title": "Updated"})
    svc.publish(dep["id"])
    assert dep["doi"] == doi_v1  # Rule 5: doi unchanged


def test_publish_generates_new_doi_when_file_added_after_first_publish(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "v1.uvl")
    svc.publish(dep["id"])
    doi_v1 = dep["doi"]

    svc.add_file(dep["id"], "v2.uvl")
    svc.publish(dep["id"])
    assert dep["doi"] != doi_v1  # dirty_files was True → new doi


def test_publish_returns_none_for_missing(svc):
    assert svc.publish(99) is None


# ---------------------------------------------------------------------------
# New version
# ---------------------------------------------------------------------------


def test_new_version_creates_new_id(svc):
    dep = svc.create_deposition()
    new_dep = svc.new_version(dep["id"])
    assert new_dep["id"] != dep["id"]


def test_new_version_keeps_conceptdoi(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "v1.uvl")
    svc.publish(dep["id"])
    new_dep = svc.new_version(dep["id"])
    assert new_dep["conceptdoi"] == dep["conceptdoi"]


def test_new_version_doi_is_none(svc):
    dep = svc.create_deposition()
    svc.publish(dep["id"])
    new_dep = svc.new_version(dep["id"])
    assert new_dep["doi"] is None


def test_new_version_dirty_files_is_false(svc):
    dep = svc.create_deposition()
    svc.add_file(dep["id"], "v1.uvl")
    svc.publish(dep["id"])
    new_dep = svc.new_version(dep["id"])
    assert new_dep["dirty_files"] is False


def test_new_version_returns_none_for_missing(svc):
    assert svc.new_version(99) is None


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def test_reset_clears_all_state(svc):
    svc.create_deposition()
    svc.create_deposition()
    svc.reset()
    assert svc.list_depositions() == []
    assert svc.next_id == 1
