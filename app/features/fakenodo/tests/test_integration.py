"""
Integration tests for the fakenodo feature — HTTP-level via Flask test client.

Covers every endpoint and validates the critical DOI business rules end-to-end.
Requires the Flask app to be running (via the ``test_client`` fixture).
"""

import io

import pytest

from app.features.fakenodo.services import fakenodo_service

pytestmark = pytest.mark.integration

_BASE = "/fakenodo/api/deposit/depositions"


@pytest.fixture(autouse=True)
def clean_fakenodo():
    fakenodo_service.reset()
    yield
    fakenodo_service.reset()


# ---------------------------------------------------------------------------
# POST / — create deposition
# ---------------------------------------------------------------------------


def test_create_deposition_returns_201(test_client):
    res = test_client.post(_BASE, json={"metadata": {"title": "DS"}})
    assert res.status_code == 201
    body = res.get_json()
    assert body["id"] == 1
    assert body["doi"] is None
    assert "conceptdoi" in body


# ---------------------------------------------------------------------------
# GET / — list depositions
# ---------------------------------------------------------------------------


def test_list_depositions_empty(test_client):
    res = test_client.get(_BASE)
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_depositions_returns_all(test_client):
    test_client.post(_BASE, json={})
    test_client.post(_BASE, json={})
    res = test_client.get(_BASE)
    assert res.status_code == 200
    assert len(res.get_json()) == 2


# ---------------------------------------------------------------------------
# GET /<id> — get deposition
# ---------------------------------------------------------------------------


def test_get_deposition_found(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    res = test_client.get(f"{_BASE}/{dep_id}")
    assert res.status_code == 200
    assert res.get_json()["id"] == dep_id


def test_get_deposition_not_found(test_client):
    res = test_client.get(f"{_BASE}/999")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# PUT /<id> — update metadata
# ---------------------------------------------------------------------------


def test_update_deposition_returns_200(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    res = test_client.put(f"{_BASE}/{dep_id}", json={"metadata": {"title": "New"}})
    assert res.status_code == 200
    assert res.get_json()["metadata"]["title"] == "New"


def test_update_deposition_not_found(test_client):
    res = test_client.put(f"{_BASE}/999", json={"metadata": {}})
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# POST /<id>/files — upload file
# ---------------------------------------------------------------------------


def test_upload_file_returns_201(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    res = test_client.post(
        f"{_BASE}/{dep_id}/files",
        data={"file": (io.BytesIO(b"features { A }"), "model.uvl")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["filename"] == "model.uvl"


def test_upload_file_not_found(test_client):
    res = test_client.post(
        f"{_BASE}/999/files",
        data={"file": (io.BytesIO(b"x"), "x.uvl")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# POST /<id>/actions/publish — publish
# ---------------------------------------------------------------------------


def test_publish_returns_202_and_doi(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    test_client.post(
        f"{_BASE}/{dep_id}/files",
        data={"file": (io.BytesIO(b"data"), "a.uvl")},
        content_type="multipart/form-data",
    )
    res = test_client.post(f"{_BASE}/{dep_id}/actions/publish")
    assert res.status_code == 202
    body = res.get_json()
    assert body["doi"] is not None
    assert body["submitted"] is True


def test_publish_not_found(test_client):
    res = test_client.post(f"{_BASE}/999/actions/publish")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /<id>
# ---------------------------------------------------------------------------


def test_delete_returns_204(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    res = test_client.delete(f"{_BASE}/{dep_id}")
    assert res.status_code == 204


def test_delete_not_found(test_client):
    res = test_client.delete(f"{_BASE}/999")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Critical business-rule tests
# ---------------------------------------------------------------------------


def test_create_upload_and_publish_assigns_doi(test_client):
    res = test_client.post(_BASE, json={"metadata": {"title": "Test Dataset"}})
    assert res.status_code == 201
    dep_id = res.get_json()["id"]
    concept_doi = res.get_json()["conceptdoi"]
    assert res.get_json()["doi"] is None

    res_file = test_client.post(
        f"{_BASE}/{dep_id}/files",
        data={"file": (io.BytesIO(b"features { A }"), "model.uvl")},
        content_type="multipart/form-data",
    )
    assert res_file.status_code == 201

    res_pub = test_client.post(f"{_BASE}/{dep_id}/actions/publish")
    assert res_pub.status_code == 202
    assert res_pub.get_json()["doi"] is not None
    assert res_pub.get_json()["conceptdoi"] == concept_doi


def test_edit_metadata_only_keeps_same_doi(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    test_client.post(
        f"{_BASE}/{dep_id}/files",
        data={"file": (io.BytesIO(b"data"), "a.uvl")},
        content_type="multipart/form-data",
    )
    first_doi = test_client.post(f"{_BASE}/{dep_id}/actions/publish").get_json()["doi"]

    test_client.put(f"{_BASE}/{dep_id}", json={"metadata": {"title": "Updated Title"}})
    res_repub = test_client.post(f"{_BASE}/{dep_id}/actions/publish")
    assert res_repub.status_code == 202
    assert res_repub.get_json()["doi"] == first_doi


def test_new_file_and_newversion_creates_new_doi_with_same_concept_doi(test_client):
    create_res = test_client.post(_BASE, json={}).get_json()
    v1_id = create_res["id"]
    concept_doi = create_res["conceptdoi"]

    test_client.post(
        f"{_BASE}/{v1_id}/files",
        data={"file": (io.BytesIO(b"v1"), "v1.uvl")},
        content_type="multipart/form-data",
    )
    v1_doi = test_client.post(f"{_BASE}/{v1_id}/actions/publish").get_json()["doi"]

    v2_res = test_client.post(f"{_BASE}/{v1_id}/actions/newversion")
    assert v2_res.status_code == 201
    v2_id = v2_res.get_json()["id"]
    assert v2_id != v1_id
    assert "links" in v2_res.get_json()

    test_client.post(
        f"{_BASE}/{v2_id}/files",
        data={"file": (io.BytesIO(b"v2"), "v2.uvl")},
        content_type="multipart/form-data",
    )
    v2_pub = test_client.post(f"{_BASE}/{v2_id}/actions/publish").get_json()

    assert v2_pub["doi"] != v1_doi
    assert v2_pub["conceptdoi"] == concept_doi


# ---------------------------------------------------------------------------
# GET /records/<id>
# ---------------------------------------------------------------------------


def test_get_record_returns_200(test_client):
    dep_id = test_client.post(_BASE, json={}).get_json()["id"]
    res = test_client.get(f"/fakenodo/records/{dep_id}")
    assert res.status_code == 200


def test_get_record_not_found(test_client):
    res = test_client.get("/fakenodo/records/999")
    assert res.status_code == 404
