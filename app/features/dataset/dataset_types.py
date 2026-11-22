from abc import ABC, abstractmethod


class DatasetType(ABC):
    name: str
    label: str
    extensions: tuple[str, ...]

    def accepts(self, filename: str) -> bool:
        return bool(filename) and filename.lower().endswith(self.extensions)

    def accepted_files(self) -> str:
        return ",".join(self.extensions)

    @abstractmethod
    def validate(self, path: str) -> list[str]:
        raise NotImplementedError


DEFAULT_DATASET_TYPE = "uvl"

_registry: dict[str, DatasetType] = {}


def register_dataset_type(dataset_type: DatasetType) -> None:
    _registry[dataset_type.name] = dataset_type


def get_dataset_type(name: str) -> DatasetType | None:
    return _registry.get(name)


def dataset_types() -> list[DatasetType]:
    return list(_registry.values())
