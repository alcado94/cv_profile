"""
Utilities for loading and preparing template configuration.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


DEFAULT_CONFIG_PATH = Path("config/templates.json")


def load_templates_config(config_path: str, required: bool = True) -> Dict[str, Any]:
    """
    Load templates configuration from JSON file.

    Args:
        config_path: Path to the templates config JSON file.
        required: Whether missing config should be treated as an error.

    Returns:
        Parsed configuration dictionary.
    """
    path = Path(config_path)
    if not path.exists():
        message = f"ERROR: No se encontró el archivo de configuración: {path}"
        if required:
            print(message)
            sys.exit(1)
        print(f"ADVERTENCIA: {message}")
        return {"templates": []}

    try:
        with path.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Error al parsear JSON en {path}: {exc}")
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: No se pudo leer el archivo {path}: {exc}")
        sys.exit(1)

    if not isinstance(data, dict):
        print("ERROR: La configuración de templates debe ser un objeto JSON.")
        sys.exit(1)

    if "templates" not in data or not isinstance(data["templates"], list):
        print("ERROR: La configuración debe incluir una lista 'templates'.")
        sys.exit(1)

    return data


def normalize_templates_config(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize templates config and apply default values.

    Args:
        config: Raw templates configuration.

    Returns:
        A normalized list of template entries.
    """
    templates = config.get("templates", [])
    normalized: List[Dict[str, Any]] = []

    for entry in templates:
        if not isinstance(entry, dict):
            continue
        normalized_entry = entry.copy()
        normalized_entry.setdefault("switcher", False)
        normalized_entry.setdefault("versions", {"show": False})
        normalized_entry.setdefault("release", {"include": False})
        normalized.append(normalized_entry)

    if any("order" in entry for entry in normalized):
        normalized.sort(key=lambda item: item.get("order", 0))

    return normalized


def apply_language_suffix(filename: str, lang_suffix: str) -> str:
    """
    Apply language suffix to a filename before its extension.

    Args:
        filename: Base filename (e.g., index.html).
        lang_suffix: Language suffix (e.g., _en).

    Returns:
        Filename with suffix applied.
    """
    if not lang_suffix:
        return filename

    path = Path(filename)
    if path.suffix:
        return f"{path.stem}{lang_suffix}{path.suffix}"

    return f"{filename}{lang_suffix}"


def build_switcher_templates(templates: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Build the list of templates to be used in the switcher.

    Args:
        templates: Normalized templates configuration.

    Returns:
        A list with name and output fields for the switcher.
    """
    switcher_templates = []
    for entry in templates:
        if entry.get("switcher"):
            switcher_templates.append(
                {
                    "id": entry.get("id", ""),
                    "name": entry.get("name", ""),
                    "output": entry.get("output", ""),
                }
            )
    return switcher_templates
