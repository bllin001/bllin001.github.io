# Personal Website Workspace

## Structure

- `pages/` — All HTML pages (about, publications, media, cv, etc.)
- `assets/` — Images, PDFs, and other static resources
- `data/` — Data files (e.g., `publications.csv`)
- `scripts/` — Automation scripts (e.g., `generate_publications_html.py`)

## Workflow

1. **Update Content**
   - Edit HTML pages in `pages/` for static content.
   - Add or update publication data in `data/publications.csv`.

2. **Automate Publications Page**
   - Run the script:
     ```bash
     cd scripts
     python generate_publications_html.py
     ```
   - This will regenerate `pages/publications.html` with the latest publication data.

3. **Add Assets**
   - Place images, PDFs, and other files in the `assets/` directory.

4. **Version Control**
   - Use clear commit messages for changes.
   - Optionally, add generated files to `.gitignore` if you don't want to track them.

## Naming Conventions
- Use lowercase and hyphens for filenames (e.g., `about.html`, `media.html`).

## Customization
- Update navigation and layout in each HTML file as needed.
- For more automation or templating, consider migrating to Jekyll or another static site generator.

---
For questions or improvements, contact the repository owner.
