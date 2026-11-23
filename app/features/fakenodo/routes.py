"""
Fakenodo HTTP routes — mirrors the Zenodo Depositions REST API.

URL prefix: /fakenodo  (defined in __init__.py)
Base path:  /fakenodo/api/deposit/depositions

Configure ZENODO_API_URL=http://localhost:5000/fakenodo/api/deposit/depositions
in your .env to point uvlhub at this mock instead of the real Zenodo.
"""

from flask import jsonify, request

from app.features.fakenodo import fakenodo_bp
from app.features.fakenodo.services import fakenodo_service

_BASE = "/api/deposit/depositions"


@fakenodo_bp.route(_BASE, methods=["POST"])
def create_deposition():
    data = request.get_json(silent=True) or {}
    dep = fakenodo_service.create_deposition(data.get("metadata"))
    return jsonify(dep), 201


@fakenodo_bp.route(_BASE, methods=["GET"])
def list_depositions():
    return jsonify(fakenodo_service.list_depositions()), 200


@fakenodo_bp.route(f"{_BASE}/<int:dep_id>", methods=["GET"])
def get_deposition(dep_id):
    dep = fakenodo_service.get_deposition(dep_id)
    if not dep:
        return jsonify({"message": "Deposition not found"}), 404
    return jsonify(dep), 200


@fakenodo_bp.route(f"{_BASE}/<int:dep_id>", methods=["PUT"])
def update_deposition(dep_id):
    data = request.get_json(silent=True) or {}
    dep = fakenodo_service.update_metadata(dep_id, data.get("metadata", {}))
    if not dep:
        return jsonify({"message": "Deposition not found"}), 404
    return jsonify(dep), 200


@fakenodo_bp.route(f"{_BASE}/<int:dep_id>/files", methods=["POST"])
def upload_file(dep_id):
    uploaded = request.files.get("file")
    filename = uploaded.filename if uploaded else (request.form.get("name") or "file.uvl")
    dep = fakenodo_service.add_file(dep_id, filename)
    if not dep:
        return jsonify({"message": "Deposition not found"}), 404
    return jsonify({"id": f"file_{len(dep['files'])}", "filename": filename}), 201


@fakenodo_bp.route(f"{_BASE}/<int:dep_id>/actions/newversion", methods=["POST"])
def new_version(dep_id):
    new_dep = fakenodo_service.new_version(dep_id)
    if not new_dep:
        return jsonify({"message": "Deposition not found"}), 404
    # Provide links.latest_draft so zenodo/services.py can extract the new id
    response_body = dict(new_dep)
    response_body["links"] = {
        "latest_draft": (
            f"{request.host_url.rstrip('/')}/fakenodo/api/deposit/depositions/{new_dep['id']}"
        )
    }
    return jsonify(response_body), 201


@fakenodo_bp.route(f"{_BASE}/<int:dep_id>/actions/publish", methods=["POST"])
def publish_deposition(dep_id):
    dep = fakenodo_service.publish(dep_id)
    if not dep:
        return jsonify({"message": "Deposition not found"}), 404
    return jsonify(dep), 202


@fakenodo_bp.route(f"{_BASE}/<int:dep_id>", methods=["DELETE"])
def delete_deposition(dep_id):
    deleted = fakenodo_service.delete_deposition(dep_id)
    if not deleted:
        return jsonify({"message": "Deposition not found"}), 404
    return "", 204


@fakenodo_bp.route("/records/<int:dep_id>", methods=["GET"])
def get_record(dep_id):
    """Convenience endpoint so view_dataset.html links don't return 404."""
    dep = fakenodo_service.get_deposition(dep_id)
    if not dep:
        return jsonify({"message": "Record not found"}), 404
    return jsonify(dep), 200
