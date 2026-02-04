#!/usr/bin/env python3
"""
CV Builder usando Jinja2 para el formato MAC de Manfred
Procesa templates con datos del CV según el esquema JSON de Manfred
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from template_config import (
    load_templates_config,
    normalize_templates_config,
    apply_language_suffix,
    build_switcher_templates,
    DEFAULT_CONFIG_PATH,
)

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    print("ERROR: jinja2 no está instalado. Instálalo con: pip install jinja2")
    sys.exit(1)


class MacCVBuilder:
    """Constructor de CV usando el formato MAC de Manfred y templates Jinja2"""

    def __init__(
        self,
        data_file: str,
        template_dir: str = "templates",
        show_photo: bool = True,
        language: Optional[str] = None,
        templates_config_path: Optional[str] = None,
    ):
        """
        Inicializa el builder con los datos del CV y el directorio de templates

        Args:
            data_file: Ruta al archivo JSON con los datos del CV (formato MAC)
            template_dir: Directorio donde están los templates Jinja2
            show_photo: Si mostrar o no la foto de perfil (default: True)
            language: Idioma para los textos de las plantillas ("es" o "en", default: None - detectar del JSON)
            templates_config_path: Ruta al archivo de configuración de templates (default: config/templates.json)
        """
        self.data_file = Path(data_file)
        self.template_dir = Path(template_dir)
        self.show_photo = show_photo
        self.cv_data = self._load_cv_data()
        self.templates_config_path = templates_config_path or str(DEFAULT_CONFIG_PATH)
        self.templates_config = normalize_templates_config(
            load_templates_config(self.templates_config_path, required=False)
        )
        self.lang_suffix = self._detect_lang_suffix()

        # Detectar idioma del archivo JSON o usar el proporcionado
        if language is None:
            detected_language = self.cv_data.get("settings", {}).get("language", "ES")
            self.language = detected_language.lower()
        else:
            self.language = language.lower()

        # Asegurar que el idioma es válido
        if self.language not in ["es", "en"]:
            print(
                f"ADVERTENCIA: Idioma '{self.language}' no soportado, usando español por defecto"
            )
            self.language = "es"

        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Agregar filtros personalizados
        self._add_custom_filters()

    def _load_cv_data(self) -> Dict[str, Any]:
        """Carga los datos del CV desde el archivo JSON"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo {self.data_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Error al parsear JSON: {e}")
            sys.exit(1)

    def _detect_lang_suffix(self) -> str:
        """
        Detecta el sufijo de idioma a partir del nombre del archivo JSON.

        Returns:
            Sufijo de idioma ("_en", "_es" o cadena vacía).
        """
        basename = self.data_file.stem
        uppercase_name = basename.upper()

        if uppercase_name.endswith("_EN"):
            return "_en"
        if uppercase_name.endswith("_ES"):
            return "_es"

        return ""

    def _build_switcher_templates(self) -> List[Dict[str, str]]:
        """
        Construye la lista de templates para el selector flotante.

        Returns:
            Lista de templates con nombre y ruta de salida.
        """
        switcher_templates = build_switcher_templates(self.templates_config)
        for entry in switcher_templates:
            output_name = entry.get("output", "")
            entry["output"] = apply_language_suffix(output_name, self.lang_suffix)
        return switcher_templates

    def _add_custom_filters(self):
        """Añade filtros personalizados para Jinja2"""

        def format_date(date_str: str, format_output: str = "%B %Y") -> str:
            """Formatea una fecha del formato YYYY-MM-DD a un formato legible"""
            if not date_str:
                return "Presente"
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj.strftime(format_output)
            except ValueError:
                return date_str

        def get_experience_duration(
            start_date: str, end_date: Optional[str] = None
        ) -> str:
            """Calcula la duración de una experiencia"""
            if not start_date:
                return ""

            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = (
                    datetime.strptime(end_date, "%Y-%m-%d")
                    if end_date
                    else datetime.now()
                )

                months = (end.year - start.year) * 12 + (end.month - start.month)
                years = months // 12
                remaining_months = months % 12

                if years > 0 and remaining_months > 0:
                    return f"{years} año{'s' if years > 1 else ''} y {remaining_months} mes{'es' if remaining_months > 1 else ''}"
                elif years > 0:
                    return f"{years} año{'s' if years > 1 else ''}"
                else:
                    return (
                        f"{remaining_months} mes{'es' if remaining_months > 1 else ''}"
                    )
            except ValueError:
                return ""

        def filter_by_type(items: List[Dict], item_type: str) -> List[Dict]:
            """Filtra elementos por tipo"""
            return [item for item in items if item.get("type") == item_type]

        def get_competences_by_type(
            competences: List[Dict], comp_type: str
        ) -> List[str]:
            """Obtiene competencias por tipo"""
            return [
                comp["name"] for comp in competences if comp.get("type") == comp_type
            ]

        def tojson_filter(value: Any) -> str:
            """Convierte un valor a JSON para usar en templates"""
            return json.dumps(value, ensure_ascii=True)

        # Registrar filtros
        self.jinja_env.filters["format_date"] = format_date
        self.jinja_env.filters["experience_duration"] = get_experience_duration
        self.jinja_env.filters["filter_by_type"] = filter_by_type
        self.jinja_env.filters["get_competences_by_type"] = get_competences_by_type
        self.jinja_env.filters["tojson"] = tojson_filter

    def get_template_context(self) -> Dict[str, Any]:
        """
        Prepara el contexto con los datos del CV para los templates
        Añade datos procesados y utilidades
        """
        context = self.cv_data.copy()

        # Añadir datos procesados
        context["generated_date"] = datetime.now().strftime("%d/%m/%Y")
        context["schema_version"] = context.get("settings", {}).get(
            "MACVersion", "unknown"
        )
        context["show_photo"] = self.show_photo
        context["language"] = self.language
        context["templates_config"] = self.templates_config
        context["templates_switcher"] = self._build_switcher_templates()

        # Añadir textos traducidos
        context["texts"] = self._get_translated_texts()

        # Procesar experiencia laboral
        if "experience" in context and "jobs" in context["experience"]:
            context["total_experience_years"] = self._calculate_total_experience()

        # Procesar links relevantes
        if "aboutMe" in context and "relevantLinks" in context["aboutMe"]:
            context["links_by_type"] = self._group_links_by_type()

        # Agrupar skills por categorías
        if "knowledge" in context and "hardSkills" in context["knowledge"]:
            context["skills_by_category"] = self._group_skills_by_category()

        return context

    def _get_translated_texts(self) -> Dict[str, str]:
        """Devuelve los textos traducidos según el idioma seleccionado"""
        if self.language == "en":
            return {
                "contact": "Contact",
                "languages": "Languages",
                "certifications": "Certifications",
                "skills": "Skills",
                "profile": "Profile",
                "work_experience": "Work Experience",
                "education": "Education",
                "present": "Present",
                "email": "Email",
                "phone": "Phone",
                "location": "Location",
                "about_me": "ABOUT ME",
                "professional_experience": "PROFESSIONAL EXPERIENCE",
                "total_experience": "Total experience",
                "years": "years",
                "knowledge": "KNOWLEDGE",
                "technical_skills": "Technical skills",
                "training": "Training",
                "in_progress": "In progress",
                "native": "Native",
                "professional": "Professional",
                "advanced": "Advanced",
                "intermediate": "Intermediate",
                "basic": "Basic",
            }
        else:  # Spanish (default)
            return {
                "contact": "Contacto",
                "languages": "Idiomas",
                "certifications": "Certificaciones",
                "skills": "Habilidades",
                "profile": "Perfil",
                "work_experience": "Experiencia Laboral",
                "education": "Educación",
                "present": "Presente",
                "email": "Email",
                "phone": "Teléfono",
                "location": "Ubicación",
                "about_me": "SOBRE MÍ",
                "professional_experience": "EXPERIENCIA PROFESIONAL",
                "total_experience": "Experiencia total",
                "years": "años",
                "knowledge": "CONOCIMIENTOS",
                "technical_skills": "Habilidades técnicas",
                "training": "Formación",
                "in_progress": "En curso",
                "native": "Nativo",
                "professional": "Profesional",
                "advanced": "Avanzado",
                "intermediate": "Intermedio",
                "basic": "Básico",
            }

    def _calculate_total_experience(self) -> float:
        """Calcula el total de años de experiencia"""
        total_months = 0

        for job in self.cv_data.get("experience", {}).get("jobs", []):
            for role in job.get("roles", []):
                start_date = role.get("startDate")
                end_date = role.get("finishDate")

                if start_date:
                    try:
                        start = datetime.strptime(start_date, "%Y-%m-%d")
                        end = (
                            datetime.strptime(end_date, "%Y-%m-%d")
                            if end_date
                            else datetime.now()
                        )
                        months = (end.year - start.year) * 12 + (
                            end.month - start.month
                        )
                        total_months += months
                    except ValueError:
                        continue

        return round(total_months / 12, 1)

    def _group_links_by_type(self) -> Dict[str, List[Dict]]:
        """Agrupa los links relevantes por tipo"""
        links_by_type = {}

        for link in self.cv_data.get("aboutMe", {}).get("relevantLinks", []):
            link_type = link.get("type", "other")
            if link_type not in links_by_type:
                links_by_type[link_type] = []
            links_by_type[link_type].append(link)

        return links_by_type

    def _group_skills_by_category(self) -> Dict[str, List[str]]:
        """Agrupa las hard skills por categorías técnicas"""
        categories = {
            "MLOps": [],
            "ML/AI": [],
            "DevOps": [],
            "Programming": [],
            "Web Development": [],
            "Big Data": [],
            "Databases": [],
            "Others": [],
        }

        # Definir mapeo de tecnologías a categorías
        skill_mapping = {
            # MLOps
            "MLflow": "MLOps",
            "Airflow": "MLOps",
            "Kubeflow": "MLOps",
            "Seldon Core": "MLOps",
            "dbt": "MLOps",
            # ML/AI
            "PyTorch": "ML/AI",
            "Scikit-learn": "ML/AI",
            "Pandas": "ML/AI",
            "Numpy": "ML/AI",
            "LangChain": "ML/AI",
            "LangGraph": "ML/AI",
            "PydanticAI": "ML/AI",
            "Keras": "ML/AI",
            # DevOps
            "Docker": "DevOps",
            "Kubernetes": "DevOps",
            "Azure": "DevOps",
            "AWS": "DevOps",
            "Terraform": "DevOps",
            "Ansible": "DevOps",
            "GitHub Actions": "DevOps",
            "Github Actions": "DevOps",
            "Nginx": "DevOps",
            "Grafana": "DevOps",
            "Gitlab CI": "DevOps",
            "Git": "DevOps",
            # Programming
            "Python": "Programming",
            "Java": "Programming",
            "JavaScript": "Programming",
            "C#": "Programming",
            "NodeJS": "Programming",
            "SQL": "Programming",
            # Web Development
            "Django": "Web Development",
            "Fastapi": "Web Development",
            "FastAPI": "Web Development",
            "Vue": "Web Development",
            "AngularJS": "Web Development",
            "HTML": "Web Development",
            "CSS": "Web Development",
            # Big Data
            "Spark": "Big Data",
            "Kafka": "Big Data",
            "Elasticsearch": "Big Data",
            "Hive": "Big Data",
            "ELK": "Big Data",
            "Kibana": "Big Data",
            "Hadoop": "Big Data",
            "Databricks": "Big Data",
            "Sqoop": "Big Data",
            # Databases
            "PostgreSQL": "Databases",
            "MySQL": "Databases",
            "InfluxDB": "Databases",
        }

        # Obtener skills tecnológicas
        tech_skills = [
            skill["skill"]["name"]
            for skill in self.cv_data.get("knowledge", {}).get("hardSkills", [])
            if skill.get("skill", {}).get("type") == "technology"
        ]

        # Agrupar skills según el mapeo
        for skill_name in tech_skills:
            category = skill_mapping.get(skill_name, "Others")
            categories[category].append(skill_name)

        # Remover categorías vacías y ordenar skills dentro de cada categoría
        return {
            category: sorted(skills)
            for category, skills in categories.items()
            if skills
        }

    def _convert_challenges_markdown_to_html(self):
        """
        Convierte todos los challenges de roles de jobs de markdown a HTML en self.cv_data.
        """
        # Intenta importar markdown, si no está disponible, omite la conversión
        try:
            import markdown
        except ImportError:
            print(
                "El paquete 'markdown' no está instalado. No se realizará la conversión de markdown a HTML."
            )
            return

        jobs = self.cv_data.get("experience", {}).get("jobs", [])
        for job in jobs:
            for role in job.get("roles", []):
                for challenge in role.get("challenges", []):
                    desc = challenge.get("description")
                    if desc:
                        # Convertir markdown a HTML
                        html = markdown.markdown(desc, extensions=["extra"])
                        challenge["description_html"] = html

    def render_template(
        self,
        template_name: str,
        output_file: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Renderiza un template con los datos del CV

        Args:
            template_name: Nombre del archivo de template
            output_file: Archivo de salida (opcional)
            extra_context: Contexto adicional a inyectar en el template

        Returns:
            El contenido renderizado
        """
        try:
            template = self.jinja_env.get_template(template_name)
            context = self.get_template_context()
            if extra_context:
                context.update(extra_context)
            self._convert_challenges_markdown_to_html()

            rendered = template.render(**context)

            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(rendered)
                print(f"CV generado en: {output_path}")

            return rendered

        except Exception as e:
            print(f"ERROR al renderizar template: {e}")
            sys.exit(1)

    def render_string_template(
        self, template_string: str, extra_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Renderiza un template desde string

        Args:
            template_string: Template como string
            extra_context: Contexto adicional a inyectar en el template

        Returns:
            El contenido renderizado
        """
        try:
            template = self.jinja_env.from_string(template_string)
            context = self.get_template_context()
            if extra_context:
                context.update(extra_context)
            return template.render(**context)
        except Exception as e:
            print(f"ERROR al renderizar template string: {e}")
            sys.exit(1)

    def list_templates(self) -> List[str]:
        """Lista todos los templates disponibles"""
        if not self.template_dir.exists():
            return []

        templates = []
        for file_path in self.template_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                relative_path = file_path.relative_to(self.template_dir)
                templates.append(str(relative_path))

        return sorted(templates)

    def validate_schema(self) -> bool:
        """
        Valida si los datos del CV cumplen con el esquema MAC usando el $schema especificado en el propio archivo.
        """
        import urllib.request
        import jsonschema

        schema_url = self.cv_data.get("$schema")
        if not schema_url:
            print("ERROR: No se encontró la clave '$schema' en los datos del CV.")
            return False

        try:
            with urllib.request.urlopen(schema_url) as response:
                schema = json.load(response)
        except Exception as e:
            print(f"ERROR: No se pudo descargar el esquema desde {schema_url}: {e}")
            return False

        try:
            jsonschema.validate(instance=self.cv_data, schema=schema)
            print("✓ Esquema MAC validado correctamente con el $schema proporcionado")
            return True
        except jsonschema.ValidationError as ve:
            print(f"ERROR: El archivo no cumple el esquema MAC: {ve.message}")
            return False
        except Exception as e:
            print(f"ERROR: Fallo al validar el esquema: {e}")
            return False


def main():
    """Función principal para usar desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description="CV Builder usando Jinja2 para el formato MAC de Manfred"
    )
    parser.add_argument(
        "data_file", help="Archivo JSON con los datos del CV (formato MAC)"
    )
    parser.add_argument(
        "-t",
        "--template",
        required=False,
        default="modern_cv.html",
        help="Nombre del template a usar",
    )
    parser.add_argument("-o", "--output", help="Archivo de salida")
    parser.add_argument(
        "--template-dir",
        default="templates",
        help="Directorio de templates (default: templates)",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Lista todos los templates disponibles",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Valida el esquema MAC del archivo de datos",
    )
    parser.add_argument(
        "--no-photo",
        action="store_true",
        help="No mostrar la foto de perfil en el CV generado",
    )
    parser.add_argument(
        "--lang",
        choices=["es", "en"],
        default=None,
        help="Idioma para los textos de las plantillas (es=español, en=inglés). Si no se especifica, se detecta del archivo JSON",
    )

    args = parser.parse_args()

    # Crear el builder
    builder = MacCVBuilder(
        args.data_file,
        args.template_dir,
        show_photo=not args.no_photo,
        language=args.lang,
    )

    # Validar esquema si se solicita
    if args.validate:
        if not builder.validate_schema():
            sys.exit(1)

    # Listar templates si se solicita
    if args.list_templates:
        templates = builder.list_templates()
        if templates:
            print("Templates disponibles:")
            for template in templates:
                print(f"  - {template}")
        else:
            print("No se encontraron templates en el directorio")
        return

    # Renderizar template
    try:
        rendered = builder.render_template(args.template, args.output)
        if not args.output:
            print(rendered)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
