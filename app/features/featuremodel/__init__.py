from flask import Flask
from splent_framework.assets.asset_registry import register_asset
from splent_framework.blueprints.base_blueprint import BaseBlueprint

featuremodel_bp = BaseBlueprint("featuremodel", __name__, template_folder="templates")


def init_feature(app: Flask) -> None:
    """Declare this feature's javascript with the framework asset registry."""
    register_asset("js", "featuremodel.assets", subfolder="js", filename="scripts.js")

    from app.features.dataset.dataset_types import register_dataset_type
    from app.features.featuremodel.dataset_type import UVLDatasetType

    register_dataset_type(UVLDatasetType())
