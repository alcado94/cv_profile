#!/usr/bin/env python3
"""
Generate all CV outputs based on a single templates config.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from builder import MacCVBuilder
from template_config import (
    load_templates_config,
    normalize_templates_config,
    apply_language_suffix,
    build_switcher_templates,
    DEFAULT_CONFIG_PATH,
)


def get_lang_suffix(json_path: Path) -> str:
    """
    Detect language suffix based on JSON filename.

    Args:
        json_path: Path to the JSON file.

    Returns:
        Language suffix ("_en", "_es" or empty string).
    """
    name_upper = json_path.stem.upper()
    if name_upper.endswith("_EN"):
        return "_en"
    if name_upper.endswith("_ES"):
        return "_es"
    return ""


def build_templates_with_suffix(
    templates: List[Dict[str, Any]], lang_suffix: str
) -> List[Dict[str, Any]]:
    """
    Apply language suffix to output filenames.

    Args:
        templates: Normalized templates config.
        lang_suffix: Language suffix to apply.

    Returns:
        Templates list with updated output names.
    """
    output_templates = []
    for entry in templates:
        updated = entry.copy()
        updated["output"] = apply_language_suffix(entry.get("output", ""), lang_suffix)
        output_templates.append(updated)
    return output_templates


def build_switcher_context(
    templates: List[Dict[str, Any]], lang_suffix: str
) -> List[Dict[str, str]]:
    """
    Build switcher context for a given language.

    Args:
        templates: Normalized templates config.
        lang_suffix: Language suffix to apply.

    Returns:
        List of templates for the switcher.
    """
    switcher_templates = build_switcher_templates(templates)
    for entry in switcher_templates:
        entry["output"] = apply_language_suffix(entry.get("output", ""), lang_suffix)
    return switcher_templates


def render_public_readme(
    templates: List[Dict[str, Any]],
    output_path: Path,
    profile_name: str,
    profile_surnames: str,
) -> None:
    """
    Generate README.md for GitHub Pages from config.

    Args:
        templates: Templates list with output filenames.
        output_path: Destination README path.
        profile_name: Profile first name.
        profile_surnames: Profile surnames.
    """
    generated_at = datetime.utcnow().strftime("%d/%m/%Y a las %H:%M UTC")
    entries = []

    for entry in templates:
        versions_config = entry.get("versions", {})
        if not versions_config.get("show"):
            continue
        title = versions_config.get("title", entry.get("name", ""))
        description = versions_config.get("description", "")
        output_file = entry.get("output", "")
        entries.append(f"- **[{title}]({output_file})** - {description}")

    readme_content = "\n".join(
        [
            f"# CV - {profile_name} {profile_surnames}",
            "",
            "Este sitio contiene mi CV generado automaticamente usando GitHub Actions y templates Jinja2.",
            "",
            "## 📋 Formatos Disponibles",
            "",
            *entries,
            "",
            "## Actualizacion Automatica",
            "",
            "Este CV se actualiza automaticamente cada vez que se modifica:",
            "- Los datos del CV (`cv_profile/CV/MAC.json`)",
            "- Los templates (`cv_profile/templates/`)",
            "- El script generador (`cv_profile/src/`)",
            "",
            "## Tecnologias Utilizadas",
            "",
            "- **Formato de datos**: [MAC (Manfred Awesomic CV)](https://github.com/getmanfred/mac)",
            "- **Generacion**: Python + Jinja2",
            "- **Despliegue**: GitHub Actions + GitHub Pages",
            "- **Templates**: HTML/CSS responsivo",
            "",
            "---",
            "",
            f"Generado automaticamente el {generated_at}",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(readme_content, encoding="utf-8")


def main() -> None:
    """CLI entrypoint for generating outputs."""
    parser = argparse.ArgumentParser(
        description="Generate CV outputs from a single templates config"
    )
    parser.add_argument(
        "--data-dir",
        default="CV",
        help="Directorio con archivos JSON (default: CV)",
    )
    parser.add_argument(
        "--template-dir",
        default="templates",
        help="Directorio de templates (default: templates)",
    )
    parser.add_argument(
        "--output-dir",
        default="public",
        help="Directorio de salida (default: public)",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Ruta al archivo de configuración de templates",
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    template_dir = Path(args.template_dir)
    output_dir = Path(args.output_dir)
    config_path = args.config

    if not data_dir.exists():
        print(f"ERROR: No se encontró el directorio de datos: {data_dir}")
        sys.exit(1)

    templates_config = normalize_templates_config(
        load_templates_config(config_path, required=True)
    )

    json_files = sorted(data_dir.glob("*.json"))
    if not json_files:
        print("ERROR: No se encontraron archivos JSON en el directorio CV.")
        sys.exit(1)

    for json_file in json_files:
        lang_suffix = get_lang_suffix(json_file)
        builder = MacCVBuilder(
            str(json_file),
            template_dir=str(template_dir),
            templates_config_path=config_path,
        )

        output_templates = build_templates_with_suffix(templates_config, lang_suffix)
        switcher_context = build_switcher_context(templates_config, lang_suffix)
        extra_context = {"templates_switcher": switcher_context}

        for entry in output_templates:
            template_name = entry.get("template")
            output_name = entry.get("output")
            if not template_name or not output_name:
                continue

            template_path = template_dir / template_name
            if not template_path.exists():
                print(f"ADVERTENCIA: Template no encontrado: {template_path}")
                continue

            output_path = output_dir / output_name
            print(f"Generando: {output_path}")
            builder.render_template(
                template_name,
                str(output_path),
                extra_context=extra_context,
            )

        profile = builder.cv_data.get("aboutMe", {}).get("profile", {})
        profile_name = profile.get("name", "")
        profile_surnames = profile.get("surnames", "")
        if not lang_suffix:
            readme_path = output_dir / "README.md"
            render_public_readme(
                output_templates,
                readme_path,
                profile_name,
                profile_surnames,
            )

    print(f"\nArchivos generados en: {output_dir}")


if __name__ == "__main__":
    main()
