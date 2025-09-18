import csv
from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
INPUT_CSV = PROJECT_ROOT / 'data' / 'publications.csv'
OUTPUT_HTML = PROJECT_ROOT / 'pages' / 'publications.html'

TYPE_CONFIG = {
    'peer-reviewed journal article': {
        'heading': 'Peer-Reviewed Journal Articles',
        'label': 'Peer-Reviewed Journal Article',
        'pill': 'Journal Article',
        'order': 0,
    },
    'peer-reviewed conference paper': {
        'heading': 'Peer-Reviewed Conference Papers',
        'label': 'Peer-Reviewed Conference Paper',
        'pill': 'Conference Paper',
        'order': 1,
    },
    'non-peer-reviewed conference presentation': {
        'heading': 'Non-Peer-Reviewed Conference Presentations',
        'label': 'Non-Peer-Reviewed Conference Presentation',
        'pill': 'Conference Presentation',
        'order': 2,
    },
    'book chapter': {
        'heading': 'Book Chapters',
        'label': 'Book Chapter',
        'pill': 'Book Chapter',
        'order': 3,
    },
    'other': {
        'heading': 'Other Publications',
        'label': 'Other Publication',
        'pill': 'Other',
        'order': 99,
    },
}

CARD_TEMPLATE = '''
<li>
    <article class="pub-card">
        <header class="pub-card__header">
            {source_html}
            <div class="pub-card__badges">
                <span class="pub-pill pub-pill--year">{year_label}</span>
                <span class="pub-pill pub-pill--type">{type_pill}</span>
            </div>
        </header>
        <h4 class="pub-card__title">{title_html}</h4>
        <p class="pub-authors">{authors}</p>
        {meta_html}
        {notes_html}
        {links_html}
    </article>
</li>
'''


def normalize_type(raw_type):
    normalized = (raw_type or '').strip().lower()
    if not normalized:
        normalized = 'other'
    config = TYPE_CONFIG.get(normalized)
    if config:
        return normalized, config

    label = (raw_type or 'Other Publication').strip()
    label = label if label else 'Other Publication'
    heading = label if label.endswith('s') else f'{label}s'
    return normalized, {
        'heading': heading,
        'label': label,
        'pill': label,
        'order': TYPE_CONFIG['other']['order'],
    }


def parse_year(value):
    raw = (value or '').strip()
    if not raw:
        return None
    for fmt in ('%Y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y'):
        try:
            return datetime.strptime(raw, fmt).year
        except ValueError:
            continue
    return None


def ensure_url(value):
    url = (value or '').strip()
    if not url:
        return ''
    if url.startswith(('http://', 'https://')):
        return url
    return f'https://{url}'


def format_doi_link(doi, fallback_url):
    doi = (doi or '').strip()
    if not doi:
        return '', fallback_url
    doi_link = doi
    if not doi_link.startswith('http'):
        doi_link = f'https://doi.org/{doi}'
    doi_display = doi
    if doi_display.startswith('http'):
        doi_display = doi_display.split('doi.org/')[-1]
    return f'DOI: <a href="{doi_link}" target="_blank" rel="noopener">{escape(doi_display)}</a>', fallback_url or doi_link


def emphasize_authors(authors):
    emphasized = escape(authors or '')
    emphasized = emphasized.replace('Llinas, B.', '<strong>Llinas, B.</strong>')
    emphasized = emphasized.replace('Llinás, B.', '<strong>Llinás, B.</strong>')
    emphasized = emphasized.replace('Brian Llinas', '<strong>Brian Llinas</strong>')
    return emphasized


def build_entry(row):
    title = escape((row.get('title') or '').strip())
    url = ensure_url(row.get('url'))
    doi_meta, primary_url = format_doi_link(row.get('doi'), url)

    year_value = None
    if row.get('year'):
        year_value = parse_year(row['year'])
    if year_value is None:
        year_value = parse_year(row.get('date'))
    year_label = str(year_value) if year_value else 'Unknown'

    type_key, type_config = normalize_type(row.get('type'))

    conference = (row.get('conference') or '').strip()
    conference_long = (row.get('conference_long') or '').strip()
    publisher = (row.get('publisher') or '').strip()
    journal = (row.get('journal') or '').strip()
    symposium = (row.get('symposium') or '').strip()
    source = conference or journal or symposium or (row.get('source') or '').strip()
    source_html = f'<span class="pub-card__source">{escape(source)}</span>' if source else ''

    publishers = []
    # Keep journal and symposium in their original positions
    for value in (journal, symposium):
        if value and value != source and escape(value) not in publishers:
            publishers.append(escape(value))
    # Add conference_long and publisher after journal/symposium
    if conference_long:
        publishers.append(escape(conference_long))
    if publisher:
        publishers.append(escape(publisher))

    meta_parts = []
    meta_parts.append(escape(type_config['label']))
    meta_parts.extend(publishers)
    if year_label != 'Unknown':
        meta_parts.append(year_label)
    if doi_meta:
        meta_parts.append(doi_meta)
    meta_html = f'<p class="pub-meta">{" • ".join(meta_parts)}</p>' if meta_parts else ''

    notes_html = ''
    if row.get('notes'):
        notes_html = f'<p class="pub-notes">{escape(row["notes"])}</p>'

    links = []
    primary_link = primary_url
    if primary_link:
        links.append(f'<a class="badge-link" href="{primary_link}" target="_blank" rel="noopener">View Publication</a>')

    link_columns = [
        ('pdf', 'PDF'),
        ('slides', 'Slides'),
        ('poster', 'Poster'),
        ('code', 'Code Repository'),
        ('supplement', 'Supplementary Material'),
    ]

    for column, label in link_columns:
        link_value = ensure_url(row.get(column))
        if link_value:
            css_class = 'badge-link badge-secondary' if label != 'PDF' else 'badge-link'
            links.append(f'<a class="{css_class}" href="{link_value}" target="_blank" rel="noopener">{label}</a>')

    links_html = f'<div class="pub-links">{"".join(links)}</div>' if links else ''

    title_html = title
    if primary_link:
        title_html = f'<a class="pub-title" href="{primary_link}" target="_blank" rel="noopener">{title}</a>'

    return {
        'title_html': title_html,
        'authors': emphasize_authors(row.get('authors', '')),
        'meta_html': meta_html,
        'notes_html': notes_html,
        'links_html': links_html,
        'source_html': source_html,
        'type_key': type_key,
        'type_heading': type_config['heading'],
        'type_label': type_config['label'],
        'type_pill': type_config['pill'],
        'type_order': type_config['order'],
        'year_value': year_value,
        'year_label': year_label,
        'sort_title': title.lower(),
    }


def read_publications_csv(csv_path):
    entries = []
    with open(csv_path, newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            entries.append(build_entry(row))
    return entries


def group_by_type(entries):
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry['type_key']].append(entry)

    ordered_keys = sorted(
        grouped.keys(),
        key=lambda key: grouped[key][0]['type_order'],
    )

    result = []
    for key in ordered_keys:
        items = sorted(
            grouped[key],
            key=lambda item: (
                -(item['year_value'] or 0),
                item['sort_title'],
            ),
        )
        result.append((items[0]['type_heading'], items))
    return result


def group_by_year(entries):
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry['year_label']].append(entry)

    def sort_key(label):
        try:
            return (-int(label), '')
        except ValueError:
            return (float('inf'), label)

    ordered_labels = sorted(grouped.keys(), key=sort_key)

    result = []
    for label in ordered_labels:
        items = sorted(
            grouped[label],
            key=lambda item: (
                item['type_order'],
                item['sort_title'],
            ),
        )
        result.append((label, items))
    return result


def render_html(type_groups, year_groups):
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('    <meta charset="UTF-8">')
    html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('    <title>Publications | Brian Llinás</title>')
    html.append('    <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32x32.png">')
    html.append('    <link rel="stylesheet" href="../style.css">')
    html.append('    <style>')
    html.append('      .toggle-btn { margin: 24px 0 16px 0; padding: 10px 28px; font-size: 1em; border-radius: 999px; border: 1px solid #d0d9e4; background: #fff; color: #22364a; cursor: pointer; font-weight: 600; transition: all 0.2s ease; }')
    html.append('      .toggle-btn + .toggle-btn { margin-left: 12px; }')
    html.append('      .toggle-btn.active { background: #22364a; color: #fff; box-shadow: 0 12px 24px rgba(34, 54, 74, 0.25); }')
    html.append('      .pub-toggle-section { display: none; }')
    html.append('      .pub-toggle-section.active { display: block; }')
    html.append('    </style>')
    html.append('</head>')
    html.append('<body style="background:#f7f8fa;">')
    html.append('    <header style="background:#2c3e50; padding:20px 0; color:#fff;">')
    html.append('        <div class="container" style="background:none; box-shadow:none; padding:0; max-width:1100px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;">')
    html.append('            <a href="../pages/about.html" style="display:inline-block; margin-right:24px; text-decoration:none; color:#fff; font-size:1.6em; font-weight:700; letter-spacing:1px; background:#22364a; padding:8px 28px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); transition:background 0.2s;">Brian Llinás</a>')
    html.append('            <nav style="display:flex; gap:24px; flex-wrap:wrap;">')
    html.append('                 <a href="about.html" style="color:#fff; text-decoration:none; font-weight:bold;">About Me</a>')
    html.append('                 <a href="publications.html" style="color:#fff; text-decoration:none; font-weight:bold; border-bottom:3px solid #f1c40f; padding-bottom:4px;">Publication</a>')
    html.append('                 <a href="media.html" style="color:#fff; text-decoration:none; font-weight:bold;">Media & Outreach</a>')
    html.append('                 <a href="cv.html" style="color:#fff; text-decoration:none; font-weight:bold;">CV</a>')
    html.append('            </nav>')
    html.append('        </div>')
    html.append('    </header>')
    html.append('    <main class="pubs-main">')
    html.append('        <div class="pubs-container">')
    html.append('            <div style="text-align:center;">')
    html.append('                <button class="toggle-btn active" id="toggleYear">Group by Year</button>')
    html.append('                <button class="toggle-btn" id="toggleType">Group by Type</button>')
    html.append('            </div>')
    html.append('            <div class="pub-toggle-section" id="sectionType">')
    for heading, items in type_groups:
        html.append('                <section class="pub-section">')
        html.append(f'                    <h3>{heading}</h3>')
        html.append('                    <ol class="pub-list">')
        for entry in items:
            html.append(CARD_TEMPLATE.format(**entry))
        html.append('                    </ol>')
        html.append('                </section>')
    html.append('            </div>')
    html.append('            <div class="pub-toggle-section active" id="sectionYear">')
    for label, items in year_groups:
        html.append('                <section class="pub-section">')
        html.append(f'                    <h3>{label}</h3>')
        html.append('                    <ol class="pub-list">')
        for entry in items:
            html.append(CARD_TEMPLATE.format(**entry))
        html.append('                    </ol>')
        html.append('                </section>')
    html.append('            </div>')
    html.append('        </div>')
    html.append('    </main>')
    html.append('    <footer class="site-footer">')
    html.append('        <div class="footer-top">')
    html.append('            <div>')
    html.append('                 <strong>© 2024–2025 Brian Llinás</strong><br>')
    html.append('                 bllin001@odu.edu')
    html.append('            </div>')
    html.append('            <div class="footer-links">')
    html.append('                 <a href="/">Home</a>')
    html.append('                 <a href="about.html">About</a>')
    html.append('                 <a href="publications.html">Publication</a>')
    html.append('                 <a href="media.html">Media & Outreach</a>')
    html.append('                 <a href="cv.html">CV</a>')
    html.append('                <a href="https://www.linkedin.com/in/brianllinas" target="_blank" rel="noopener">LinkedIn</a>')
    html.append('                <a href="https://github.com/bllin001" target="_blank" rel="noopener">GitHub</a>')
    html.append('            </div>')
    html.append('        </div>')
    html.append('        <div class="footer-bottom">')
    html.append('            <div class="footer-bottom-inner">')
    html.append('                <span>Site maintained by Brian Llinás.</span>')
    html.append('                <span>Template available on <a href="https://github.com/bllin001/bllin001.github.io" target="_blank" rel="noopener">GitHub</a>.</span>')
    html.append('            </div>')
    html.append('        </div>')
    html.append('    </footer>')
    html.append('    <script>')
    html.append('      const btnType = document.getElementById("toggleType");')
    html.append('      const btnYear = document.getElementById("toggleYear");')
    html.append('      const sectionType = document.getElementById("sectionType");')
    html.append('      const sectionYear = document.getElementById("sectionYear");')
    html.append('      btnType.addEventListener("click", function() {')
    html.append('        btnType.classList.add("active");')
    html.append('        btnYear.classList.remove("active");')
    html.append('        sectionType.classList.add("active");')
    html.append('        sectionYear.classList.remove("active");')
    html.append('      });')
    html.append('      btnYear.addEventListener("click", function() {')
    html.append('        btnYear.classList.add("active");')
    html.append('        btnType.classList.remove("active");')
    html.append('        sectionYear.classList.add("active");')
    html.append('        sectionType.classList.remove("active");')
    html.append('      });')
    html.append('    </script>')
    html.append('</body>')
    html.append('</html>')
    return '\n'.join(html)


def main():
    entries = read_publications_csv(INPUT_CSV)
    type_groups = group_by_type(entries)
    year_groups = group_by_year(entries)
    html = render_html(type_groups, year_groups)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as handle:
        handle.write(html)


if __name__ == '__main__':
    main()
