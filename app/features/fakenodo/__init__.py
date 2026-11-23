from flask import Flask
from splent_framework.blueprints.base_blueprint import BaseBlueprint

fakenodo_bp = BaseBlueprint("fakenodo", __name__, url_prefix="/fakenodo", template_folder="templates")


def init_feature(app: Flask) -> None:  # noqa: ARG001
    """No JS assets needed for fakenodo."""
    pass
