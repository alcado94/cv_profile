# Agent Guidelines for CV Profile Repository

This repository is a tool to generate a professional CV from a JSON data source (Manfred Awesomic CV format - MAC) using Python and Jinja2 templates.

## 1. Build, Lint, and Test Commands

There are no formal unit tests in this repository. Verification is done by running the builder script and validating the JSON schema.

### Setup
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Generation Commands
To generate the CV (default template):
```bash
python3 src/builder.py CV/MAC.json -o dist/cv.html
```

To generate using a specific template:
```bash
python3 src/builder.py CV/MAC.json -t modern_cv.html -o dist/cv.html
```

To list available templates:
```bash
python3 src/builder.py CV/MAC.json --list-templates
```

### Validation
To validate the JSON data against the MAC schema:
```bash
python3 src/builder.py CV/MAC.json --validate
```

### Verification Steps for Agents
After modifying `src/builder.py` or the JSON data:
1.  **Validate Schema:** Always run the `--validate` command to ensure the JSON remains valid.
2.  **Dry Run:** Generate the HTML to ensuring no runtime errors occur in the Python script or Jinja2 rendering.

## 2. Code Style & Conventions

### Python Code (`src/builder.py`)
-   **Style:** Adhere to PEP 8.
-   **Type Hinting:** Use `typing` module (List, Dict, Optional, Any) for function signatures.
-   **Docstrings:** All classes and functions must have docstrings explaining purpose, arguments, and return values.
-   **Imports:**
    -   Standard library imports first (e.g., `json`, `argparse`, `sys`, `pathlib`).
    -   Third-party imports second (e.g., `jinja2`, `markdown`, `jsonschema`).
-   **Error Handling:**
    -   Use `try/except` blocks for file operations and external library calls.
    -   Print user-friendly error messages to stdout/stderr and exit with status 1 on critical errors.
    -   Do not just print the stack trace unless debugging.

### Data (`CV/MAC.json`)
-   **Format:** Strict JSON.
-   **Schema:** Must conform to the MAC (Manfred Awesomic CV) schema.
-   **Dates:** Use `YYYY-MM-DD` format.
-   **Descriptions:** Can contain Markdown. The builder converts this to HTML automatically.

### Project Structure
-   `/CV`: Contains the data files (`MAC.json`).
-   `/src`: Contains the logic (`builder.py`).
-   `/templates`: Contains Jinja2 templates (`.html`, `.txt`).
-   `/doc`: Documentation and assets.

## 3. Workflow for Modifying CV Data
When asked to update CV information:
1.  **Read:** Read `CV/MAC.json` to understand the current structure and location of the data to be changed.
2.  **Edit:** Modify `CV/MAC.json` directly.
    -   If adding a job, ensure all required fields (company, role, dates) are present.
    -   If updating descriptions, keep them concise and use Markdown if needed.
3.  **Validate:** Run `python3 src/builder.py CV/MAC.json --validate` to ensure integrity.
