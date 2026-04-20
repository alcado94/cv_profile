# Agent Guidelines for CV Profile Repository

This repository generates a professional CV from JSON data that follows the Manfred Awesomic CV (MAC) standard, using Python and Jinja2 templates.

## 1. MAC Standard

### Source of Truth
- MAC is the canonical data format for this repository.
- Official reference: `https://github.com/getmanfred/mac`
- The main CV data files in this repository are `CV/MAC.json` and `CV/MAC_EN.json`.
- Any change to CV content must preserve MAC compatibility. Do not introduce ad hoc fields or shape changes unless the MAC schema supports them.

### Required Validation Flow
Whenever you modify CV data, validate the edited file against the MAC schema before considering the task complete.

Validate the default CV:
```bash
python3 src/builder.py CV/MAC.json --validate
```

Validate the English CV when it changes:
```bash
python3 src/builder.py CV/MAC_EN.json --validate
```

### Generation Commands
Generate the default CV:
```bash
python3 src/builder.py CV/MAC.json -o dist/cv.html
```

Generate the English CV:
```bash
python3 src/builder.py CV/MAC_EN.json -o dist/cv_en.html
```

Generate using a specific template:
```bash
python3 src/builder.py CV/MAC.json -t modern_cv.html -o dist/cv.html
```

List available templates:
```bash
python3 src/builder.py CV/MAC.json --list-templates
```

### Verification Steps for Agents
After modifying `src/builder.py` or CV data:
1. Validate every changed MAC file with `--validate`.
2. Run at least one HTML generation command for each changed CV data file to catch rendering errors.
3. Treat generated files in `dist/` as build artifacts, not repository content.

## 2. Code Style and Conventions

### Python Code (`src/builder.py`)
- Style: Adhere to PEP 8.
- Type hinting: Use `typing` module types for function signatures.
- Docstrings: All classes and functions must explain purpose, arguments, and return values.
- Imports:
  - Standard library imports first.
  - Third-party imports second.
- Error handling:
  - Use `try/except` for file operations and external library calls.
  - Print user-friendly errors to stdout/stderr and exit with status 1 on critical failures.
  - Do not print stack traces unless debugging is explicitly needed.

### Data Files (`CV/MAC.json`, `CV/MAC_EN.json`)
- Format: Strict JSON.
- Schema: Must conform to the MAC schema.
- Dates: Use `YYYY-MM-DD` format.
- Descriptions: May contain Markdown that the builder converts to HTML.

### Project Structure
- `/CV`: CV data files.
- `/src`: Builder logic.
- `/templates`: Jinja2 templates.
- `/doc`: Documentation and assets.
- `/dist`: Generated output only. Do not commit files from this directory.

## 3. Writing Best Practices

Use a consistent editorial style for challenges, achievements, and role descriptions.

### Principles
- Clarity: Write direct sentences and remove filler words.
- No redundancy: Do not repeat information already covered by role, company, dates, or tech fields.
- Structure: Prefer action verb + change introduced + observable result.
- Results first: Emphasize impact, scope, reliability, speed, quality, or business outcome when that information is available.
- Consistency: Keep the same tone across the full CV, focused on contribution and outcomes.

### Writing Challenges and Achievements
- Start with a concrete action such as `Built`, `Improved`, `Automated`, `Reduced`, or `Led`.
- Mention the problem, system, or process being addressed.
- Close with the result when it is known.
- Keep bullets concise and specific.

### Examples
- Avoid: `Participated in several team projects.`
- Prefer: `Automated internal service deployments and reduced manual release errors.`

- Avoid: `Worked on backend improvements.`
- Prefer: `Improved API response times by simplifying data access paths and removing redundant queries.`

## 4. Workflow for Modifying CV Data

When asked to update CV information:
1. Read the relevant MAC file first to locate the exact section to change.
2. Edit only the necessary fields.
3. If adding a new role, ensure required MAC fields are present and dates use the expected format.
4. If editing descriptions or challenges, follow the writing guidance above.
5. Validate every modified MAC file.
6. Run a generation command for every modified MAC file as a dry run.

## 5. Repository Hygiene

- Keep compiled output out of version control.
- `dist/` must remain ignored.
- If generated files appear in the working tree, remove them from the commit unless the task explicitly requires build artifacts.
