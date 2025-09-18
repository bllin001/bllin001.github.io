import csv
from collections import defaultdict
from datetime import datetime

INPUT_CSV = '../data/publications.csv'
OUTPUT_HTML = '../pages/publications.html'

CARD_TEMPLATE = '''
<li>
    <article class="pub-card">
        <header>
            <span class="pub-source">{source}</span>
            <h4>{title}</h4>
        </header>
        <p class="pub-authors">{authors}</p>
        <p class="pub-meta">{meta_str}{url_html}</p>
        {notes_html}
        {links_html}
    </article>
</li>
'''

def parse_year(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.year
    except Exception:
        try:
            dt = datetime.strptime(date_str, '%B %d, %Y')
            return dt.year
        except Exception:
            try:
                dt = datetime.strptime(date_str, '%Y')
                return dt.year
            except Exception:
                return 'Unknown'

def read_publications_csv(csv_path):
    entries = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row.get('year') or parse_year(row.get('date', ''))
            # Use type from CSV
            pub_type = row.get('type', 'Other')
            source = row.get('journal') or row.get('conference') or row.get('symposium') or row.get('source') or ''
            meta = []
            for key in ['journal', 'conference', 'symposium', 'year']:
                if row.get(key):
                    meta.append(row[key])
            meta_str = ', '.join(meta)
            url_html = ''
            links_html = ''
            if row.get('url'):
                url_html = f'. DOI: <a href="{row["url"]}" target="_blank" rel="noopener">{row["url"]}</a>'
                links_html = f'<div class="pub-links"><a class="badge-link" href="{row["url"]}" target="_blank" rel="noopener">Publication</a></div>'
            notes_html = ''
            if row.get('notes'):
                notes_html = f'<p class="pub-notes">{row["notes"]}</p>'
            entries.append({
                'title': row['title'],
                'authors': row['authors'],
                'year': year,
                'source': source,
                'type': pub_type,
                'meta_str': meta_str,
                'url_html': url_html,
                'notes_html': notes_html,
                'links_html': links_html
            })
    return entries

def group_by_type(entries):
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry['type']].append(entry)
    # Optional: custom order for types
    type_order = [
        'Peer-Reviewed Journal Article',
        'Peer-Reviewed Conference Paper',
        'Non-Peer-Reviewed Conference Presentation',
        'Other'
    ]
    sorted_types = [t for t in type_order if t in grouped] + [t for t in grouped if t not in type_order]
    return {t: grouped[t] for t in sorted_types}

def render_html(grouped):
    # Full HTML template
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('    <meta charset="UTF-8">')
    html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('    <title>Publications | Brian Llinás</title>')
    html.append('    <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32x32.png">')
    html.append('    <link rel="stylesheet" href="../style.css">')
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
    # Publication sections
    for pub_type, items in grouped.items():
        html.append(f'            <section class="pub-section">')
        html.append(f'                <h3>{pub_type}s</h3>')
        html.append('                <ol class="pub-list">')
        for entry in items:
            html.append(CARD_TEMPLATE.format(**entry))
        html.append('                </ol>')
        html.append('            </section>')
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
    html.append('</body>')
    html.append('</html>')
    return '\n'.join(html)

def main():
    entries = read_publications_csv(INPUT_CSV)
    grouped = group_by_type(entries)
    html_section = render_html(grouped)

    # Read the existing publications.html and replace the section
    with open(OUTPUT_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    start = html.find('<section class="pub-section">')
    end = html.find('</section>', start)
    if start != -1 and end != -1:
        new_html = html[:start] + html_section + html[end+10:]
    else:
        new_html = html
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_section)

if __name__ == '__main__':
    main()
