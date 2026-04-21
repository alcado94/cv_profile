# CV Profile

Este repositorio centraliza el currículum profesional y actúa como punto de sincronización con Manfred. La información se mantiene versionada en GitHub para dejar trazabilidad de cambios, hitos profesionales y actualizaciones del perfil.

<div align="center">
  <a href="https://github.com/getmanfred/mac">
    <img src="https://img.shields.io/static/v1?label=MAC%20Version&message=0.5&color=brightgreen&style=for-the-badge">
  </a>
</div>

## Propósito

- Mantener el CV en un formato estructurado y portable.
- Sincronizar el contenido con la plataforma de Manfred.
- Generar distintas salidas del currículum a partir de una única fuente de datos.
- Automatizar validación, generación y despliegue con GitHub Actions.

## Tecnologías

- `MAC (Manfred Awesomic CV)` como esquema JSON base: https://github.com/getmanfred/mac
- Python para validación y generación del contenido.
- Jinja2 para las plantillas.
- GitHub Actions para CI/CD.
- GitHub Pages para publicar la versión estática.

## Seguir El Esquema MAC

La fuente de verdad del currículum está en `CV/MAC.json` y `CV/MAC_EN.json`. Ambos archivos deben seguir el JSON Schema definido por el proyecto MAC.

Respetar este esquema es importante por tres motivos:

- garantiza compatibilidad con Manfred;
- evita errores al validar o renderizar el CV;
- permite sincronizar cambios automáticamente entre este repositorio y la plataforma.

No conviene añadir campos ad hoc ni cambiar la estructura fuera de lo permitido por MAC.

Referencia oficial:

- https://github.com/getmanfred/mac
- https://github.com/getmanfred/mac/blob/master/schema/schema.json

## Estructura Del Repositorio

- `CV/`: archivos fuente del currículum en formato MAC.
- `src/`: lógica de validación y generación.
- `templates/`: plantillas Jinja2 para las distintas vistas y exportaciones.
- `config/templates.json`: catálogo de salidas generadas.
- `.github/workflows/`: flujos de CI, despliegue y automatización con LLMs.
- `doc/`: documentación y recursos auxiliares.

## Comandos Útiles

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Validar el CV principal contra MAC:

```bash
python3 src/builder.py CV/MAC.json --validate
```

Validar la versión en inglés:

```bash
python3 src/builder.py CV/MAC_EN.json --validate
```

Generar una salida HTML individual:

```bash
python3 src/builder.py CV/MAC.json -t modern_cv.html -o dist/cv.html
```

Listar plantillas disponibles:

```bash
python3 src/builder.py CV/MAC.json --list-templates
```

Generar todas las variantes configuradas:

```bash
python3 src/generate_all.py --config config/templates.json --data-dir CV --template-dir templates --output-dir public
```

## CI/CD

El repositorio define dos flujos principales de automatización:

### Validación continua

`/.github/workflows/ci.yml` se ejecuta en:

- `pull_request` contra `main` y `master`;
- `push` a ramas distintas de `main` y `master`.

Este flujo:

- comprueba que `CV/MAC.json` sea JSON válido;
- valida el fichero contra el esquema MAC;
- genera todas las variantes configuradas en un directorio temporal;
- verifica que los archivos generados existan y no estén vacíos.

### Build Y Despliegue

`/.github/workflows/deploy-cv.yml` se ejecuta al hacer `push` en `main` o `master`.

Este flujo:

- instala dependencias;
- genera todas las variantes del CV en `public/`;
- añade metadatos HTML para la web publicada;
- publica el resultado en GitHub Pages;
- opcionalmente crea una release cuando el commit incluye `[release]`.

Sitio publicado:

- https://alcado94.github.io/cv_profile/

## Sincronización Con Manfred

Si este repositorio está conectado con Manfred, los cambios sobre los archivos MAC pueden sincronizarse con el perfil de la plataforma. Del mismo modo, las actualizaciones realizadas en Manfred pueden reflejarse en este repositorio según la configuración de sincronización del perfil.

## Actualización Del CV

Para actualizar el contenido:

1. Edita `CV/MAC.json` o `CV/MAC_EN.json`.
2. Mantén la estructura compatible con MAC.
3. Valida los archivos modificados.
4. Genera al menos una salida para comprobar el render.

## Impresión En PDF

La forma más simple de obtener un PDF es abrir la versión desplegada del CV en el navegador y usar la opción de impresión:

- `Ctrl+P` en Linux/Windows.
- `Cmd+P` en macOS.

Las vistas HTML están preparadas para producir una versión imprimible con formato profesional.

## Automatización Desde GitHub

El repositorio incluye automatizaciones en `.github/workflows/opencode.yml` para ejecutar cambios asistidos por LLM a partir de comentarios con `/oc` o `/opencode` en GitHub. Esto permite usar issues y comentarios como punto de entrada para tareas de mantenimiento y evolución del CV.

## Licencia

Los CVs incluidos en este repositorio contienen datos personales y profesionales, y no pueden procesarse automáticamente sin permiso explícito del titular conforme al RGPD.

El formato MAC es software abierto y se distribuye bajo licencia Creative Commons Attribution Share Alike 4.0 International.
