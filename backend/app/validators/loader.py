import importlib
import importlib.metadata
import importlib.util
import pkgutil
from pathlib import Path
from types import ModuleType

from app.validators.errors import ValidatorLoaderError
from app.validators.registry import ValidatorRegistry


class ValidatorLoader:
    def __init__(self, registry: ValidatorRegistry) -> None:
        self.registry = registry

    def discover_from_package(self, package: str) -> list[str]:
        modules = []
        try:
            package_module = importlib.import_module(package)
        except ModuleNotFoundError:
            return modules

        modules.extend(self._load_module(package_module))
        package_path = getattr(package_module, "__path__", None)
        if not package_path:
            return modules

        for module_info in pkgutil.walk_packages(package_path, prefix=f"{package}."):
            module = importlib.import_module(module_info.name)
            modules.extend(self._load_module(module))
        return modules

    def discover_from_paths(self, paths: list[str], module_prefix: str = "uv_validator_ext") -> list[str]:
        modules = []
        for index, path in enumerate(paths):
            file_path = Path(path)
            if not file_path.exists() or not file_path.is_file() or file_path.suffix != ".py":
                continue
            module_name = f"{module_prefix}_{index}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules.extend(self._load_module(module))
        return modules

    def discover_from_entrypoints(self, group: str = "tkk_uv.validators") -> list[str]:
        modules = []
        try:
            entries = importlib.metadata.entry_points(group=group)
        except TypeError:
            entries = importlib.metadata.entry_points().select(group=group)

        for entry in entries:
            module = entry.load()
            if isinstance(module, ModuleType):
                modules.extend(self._load_module(module))
                continue

            register_fn = getattr(module, "register_validators", None)
            if callable(register_fn):
                register_fn(self.registry)
                modules.append(getattr(module, "__name__", entry.name))
        return modules

    def _load_module(self, module: ModuleType) -> list[str]:
        register_fn = getattr(module, "register_validators", None)
        if register_fn is None:
            return []
        if not callable(register_fn):
            raise ValidatorLoaderError(f"register_validators must be callable in module {module.__name__}")
        register_fn(self.registry)
        return [module.__name__]
