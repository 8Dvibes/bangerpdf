"""
packs — Pack management: discover, scaffold, and validate render packs.

Starter packs are bundled in bangerpdf/packs_data/ and discovered via
importlib.resources. Users scaffold a new project by running
`bangerpdf init <pack> <dir>`, which copies the starter pack contents
and optionally applies brand overrides.

Usage:
    from bangerpdf.packs import list_packs, init_pack, validate_data
    packs = list_packs()
    init_pack("demo", "/tmp/my-project")
"""

import importlib.resources
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from bangerpdf.brand import BrandKit, brand_to_yaml


@dataclass
class PackInfo:
    """Metadata about an installed starter pack."""
    name: str
    description: str
    version: str
    document_count: int
    path: Path

    def __str__(self) -> str:
        return f"{self.name} (v{self.version}) - {self.description} [{self.document_count} doc(s)]"


def _packs_root() -> Path:
    """Locate the bundled packs_data directory using importlib.resources."""
    # Python 3.12+: importlib.resources.files()
    try:
        ref = importlib.resources.files("bangerpdf.packs_data")
        # Convert to a concrete path
        root = Path(str(ref))
        if root.is_dir():
            return root
    except (TypeError, ModuleNotFoundError):
        pass

    # Fallback: relative to this file
    fallback = Path(__file__).parent / "packs_data"
    if fallback.is_dir():
        return fallback

    raise FileNotFoundError(
        "Cannot locate bangerpdf/packs_data/. "
        "Is bangerpdf installed correctly?"
    )


def list_packs() -> list[PackInfo]:
    """Discover installed starter packs in packs_data/.

    Returns a list of PackInfo for each subdirectory that contains a pack.yaml.
    """
    root = _packs_root()
    packs = []

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        pack_yaml = child / "pack.yaml"
        if not pack_yaml.exists():
            continue

        try:
            with open(pack_yaml) as f:
                manifest = yaml.safe_load(f)
            if not isinstance(manifest, dict):
                continue
        except yaml.YAMLError:
            continue

        packs.append(PackInfo(
            name=manifest.get("name", child.name),
            description=manifest.get("description", ""),
            version=manifest.get("version", "0.0"),
            document_count=len(manifest.get("documents", [])),
            path=child,
        ))

    return packs


def _find_pack(pack_name: str) -> PackInfo:
    """Find a pack by name, raising ValueError if not found."""
    packs = list_packs()
    for p in packs:
        if p.name == pack_name:
            return p

    available = [p.name for p in packs]
    raise ValueError(
        f"Pack '{pack_name}' not found. Available packs: {available}"
    )


def init_pack(
    pack_name: str,
    target_dir: str | Path,
    brand_overrides: dict[str, Any] | None = None,
) -> Path:
    """Copy a starter pack to the target directory and apply brand overrides.

    Args:
        pack_name: Name of the starter pack (must exist in packs_data/).
        target_dir: Where to scaffold the project.
        brand_overrides: Optional dict of brand overrides like
                         {"brand": {"name": "Acme", "primary": "#FF0000"}}.

    Returns:
        The resolved target directory path.
    """
    pack = _find_pack(pack_name)
    target = Path(target_dir).resolve()

    if target.exists() and any(target.iterdir()):
        raise ValueError(f"Target directory {target} already exists and is not empty.")

    # Copy the entire pack directory
    shutil.copytree(str(pack.path), str(target))

    # Apply brand overrides if provided
    if brand_overrides:
        brand_yaml_path = target / "brand-kit.yaml"
        if brand_yaml_path.exists():
            with open(brand_yaml_path) as f:
                existing = yaml.safe_load(f) or {}
        else:
            existing = {}

        # Deep merge the overrides
        for section in ("brand", "print"):
            if section in brand_overrides:
                if section not in existing:
                    existing[section] = {}
                existing[section].update(brand_overrides[section])

        with open(brand_yaml_path, "w") as f:
            yaml.dump(existing, f, default_flow_style=False, sort_keys=False)

    print(f"Scaffolded '{pack_name}' pack to {target}")
    print(f"  Documents: {pack.document_count}")
    print(f"  Next: cd {target} && bangerpdf build")

    return target


def validate_data(pack_dir: str | Path) -> list[str]:
    """Validate data.json against data.schema.json if present.

    Returns a list of error messages (empty = valid).
    """
    pack_dir = Path(pack_dir).resolve()
    data_path = pack_dir / "data.json"
    schema_path = pack_dir / "data.schema.json"

    errors = []

    if not data_path.exists():
        errors.append(f"data.json not found in {pack_dir}")
        return errors

    # Load data
    try:
        with open(data_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"data.json is invalid JSON: {e}")
        return errors

    # If no schema, just validate it's a dict
    if not schema_path.exists():
        if not isinstance(data, dict):
            errors.append(f"data.json must be a JSON object, got {type(data).__name__}")
        return errors

    # Validate against schema using jsonschema if available
    try:
        import jsonschema

        with open(schema_path) as f:
            schema = json.load(f)

        validator = jsonschema.Draft7Validator(schema)
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            path_str = ".".join(str(p) for p in error.absolute_path) or "(root)"
            errors.append(f"{path_str}: {error.message}")

    except ImportError:
        # jsonschema not installed, skip schema validation
        print(
            "  NOTE: jsonschema not installed, skipping schema validation. "
            "Install with: pip install jsonschema",
            file=sys.stderr,
        )

    except json.JSONDecodeError as e:
        errors.append(f"data.schema.json is invalid JSON: {e}")

    return errors
