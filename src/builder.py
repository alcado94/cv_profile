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

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    print("ERROR: jinja2 no está instalado. Instálalo con: pip install jinja2")
    sys.exit(1)


class MacCVBuilder:
    """Constructor de CV usando el formato MAC de Manfred y templates Jinja2"""
    
    def __init__(self, data_file: str, template_dir: str = "templates"):
        """
        Inicializa el builder con los datos del CV y el directorio de templates
        
        Args:
            data_file: Ruta al archivo JSON con los datos del CV (formato MAC)
            template_dir: Directorio donde están los templates Jinja2
        """
        self.data_file = Path(data_file)
        self.template_dir = Path(template_dir)
        self.cv_data = self._load_cv_data()
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Agregar filtros personalizados
        self._add_custom_filters()
    
    def _load_cv_data(self) -> Dict[str, Any]:
        """Carga los datos del CV desde el archivo JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo {self.data_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Error al parsear JSON: {e}")
            sys.exit(1)
    
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
        
        def get_experience_duration(start_date: str, end_date: Optional[str] = None) -> str:
            """Calcula la duración de una experiencia"""
            if not start_date:
                return ""
            
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
                
                months = (end.year - start.year) * 12 + (end.month - start.month)
                years = months // 12
                remaining_months = months % 12
                
                if years > 0 and remaining_months > 0:
                    return f"{years} año{'s' if years > 1 else ''} y {remaining_months} mes{'es' if remaining_months > 1 else ''}"
                elif years > 0:
                    return f"{years} año{'s' if years > 1 else ''}"
                else:
                    return f"{remaining_months} mes{'es' if remaining_months > 1 else ''}"
            except ValueError:
                return ""
        
        def filter_by_type(items: List[Dict], item_type: str) -> List[Dict]:
            """Filtra elementos por tipo"""
            return [item for item in items if item.get('type') == item_type]
        
        def get_competences_by_type(competences: List[Dict], comp_type: str) -> List[str]:
            """Obtiene competencias por tipo"""
            return [comp['name'] for comp in competences if comp.get('type') == comp_type]
        
        # Registrar filtros
        self.jinja_env.filters['format_date'] = format_date
        self.jinja_env.filters['experience_duration'] = get_experience_duration
        self.jinja_env.filters['filter_by_type'] = filter_by_type
        self.jinja_env.filters['get_competences_by_type'] = get_competences_by_type
    
    def get_template_context(self) -> Dict[str, Any]:
        """
        Prepara el contexto con los datos del CV para los templates
        Añade datos procesados y utilidades
        """
        context = self.cv_data.copy()
        
        # Añadir datos procesados
        context['generated_date'] = datetime.now().strftime("%d/%m/%Y")
        context['schema_version'] = context.get('settings', {}).get('MACVersion', 'unknown')
        
        # Procesar experiencia laboral
        if 'experience' in context and 'jobs' in context['experience']:
            context['total_experience_years'] = self._calculate_total_experience()
        
        # Procesar links relevantes
        if 'aboutMe' in context and 'relevantLinks' in context['aboutMe']:
            context['links_by_type'] = self._group_links_by_type()

        return context
    
    def _calculate_total_experience(self) -> float:
        """Calcula el total de años de experiencia"""
        total_months = 0
        
        for job in self.cv_data.get('experience', {}).get('jobs', []):
            for role in job.get('roles', []):
                start_date = role.get('startDate')
                end_date = role.get('finishDate')
                
                if start_date:
                    try:
                        start = datetime.strptime(start_date, "%Y-%m-%d")
                        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
                        months = (end.year - start.year) * 12 + (end.month - start.month)
                        total_months += months
                    except ValueError:
                        continue
        
        return round(total_months / 12, 1)
    
    def _group_links_by_type(self) -> Dict[str, List[Dict]]:
        """Agrupa los links relevantes por tipo"""
        links_by_type = {}
        
        for link in self.cv_data.get('aboutMe', {}).get('relevantLinks', []):
            link_type = link.get('type', 'other')
            if link_type not in links_by_type:
                links_by_type[link_type] = []
            links_by_type[link_type].append(link)
        
        return links_by_type
    
    def render_template(self, template_name: str, output_file: Optional[str] = None) -> str:
        """
        Renderiza un template con los datos del CV
        
        Args:
            template_name: Nombre del archivo de template
            output_file: Archivo de salida (opcional)
            
        Returns:
            El contenido renderizado
        """
        try:
            template = self.jinja_env.get_template(template_name)
            context = self.get_template_context()

            
            rendered = template.render(**context)
            
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(rendered)
                print(f"CV generado en: {output_path}")
            
            return rendered
            
        except Exception as e:
            print(f"ERROR al renderizar template: {e}")
            sys.exit(1)
    
    def render_string_template(self, template_string: str) -> str:
        """
        Renderiza un template desde string
        
        Args:
            template_string: Template como string
            
        Returns:
            El contenido renderizado
        """
        try:
            template = Template(template_string, environment=self.jinja_env)
            context = self.get_template_context()
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
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(self.template_dir)
                templates.append(str(relative_path))
        
        return sorted(templates)
    
    def validate_schema(self) -> bool:
        """Valida si los datos del CV cumplen con el esquema básico MAC"""
        required_sections = ['settings', 'aboutMe']
        
        for section in required_sections:
            if section not in self.cv_data:
                print(f"ERROR: Sección requerida '{section}' no encontrada")
                return False
        
        # Validar settings
        settings = self.cv_data.get('settings', {})
        if 'language' not in settings:
            print("ERROR: 'language' requerido en settings")
            return False
        
        # Validar aboutMe
        about_me = self.cv_data.get('aboutMe', {})
        if 'profile' not in about_me:
            print("ERROR: 'profile' requerido en aboutMe")
            return False
        
        profile = about_me.get('profile', {})
        required_profile_fields = ['name', 'surnames', 'title']
        for field in required_profile_fields:
            if field not in profile:
                print(f"ERROR: '{field}' requerido en aboutMe.profile")
                return False
        
        print("✓ Esquema MAC básico validado correctamente")
        return True


def main():
    """Función principal para usar desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description="CV Builder usando Jinja2 para el formato MAC de Manfred"
    )
    parser.add_argument(
        "data_file", 
        help="Archivo JSON con los datos del CV (formato MAC)"
    )
    parser.add_argument(
        "-t", "--template", 
        required=True,
        help="Nombre del template a usar"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Archivo de salida"
    )
    parser.add_argument(
        "--template-dir", 
        default="templates",
        help="Directorio de templates (default: templates)"
    )
    parser.add_argument(
        "--list-templates", 
        action="store_true",
        help="Lista todos los templates disponibles"
    )
    parser.add_argument(
        "--validate", 
        action="store_true",
        help="Valida el esquema MAC del archivo de datos"
    )
    
    args = parser.parse_args()
    
    # Crear el builder
    builder = MacCVBuilder(args.data_file, args.template_dir)
    
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
