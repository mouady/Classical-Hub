from app.features.dataset.dataset_types import DatasetType
from app.features.flamapy.services import FlamapyService


class UVLDatasetType(DatasetType):
    name = "uvl"
    label = "UVL"
    extensions = (".uvl",)

    def validate(self, path: str) -> list[str]:
        return FlamapyService.validate_uvl_path(path)
