import csv
from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
INPUT_CSV = PROJECT_ROOT / 'data' / 'media.csv'
OUTPUT_HTML = PROJECT_ROOT / 'pages' / 'media.html'
CSS_VERSION = '20250129'

CARD_TEMPLATE = '''
<article class="media-card">
    <a class="media-card__figure" href="{url}" target="_blank" rel="noopener">
        {image_html}
    </a>
    <div class="media-card__body">
        <div class="media-card__meta">
            <span class="media-card__source">{source}</span>
            <span class="media-card__date">{date_str}</span>
        </div>
        <h4 class="media-card__title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h4>
        <p class="media-card__authors">{authors}</p>
        <div class="media-card__actions">
            <a class="badge-link" href="{url}" target="_blank" rel="noopener">{primary_label}</a>
            {github_html}
        </div>
    </div>
</article>
'''

PLATFORM_NAMES = {
    'storymodelers.org': 'Storymodelers',
    'www.storymodelers.org': 'Storymodelers',
    'ws-dl.blogspot.com': 'WS-DL Blog',
    'medium.com': 'Medium',
}


def humanize_source(url):
    if not url:
        return 'External Link', 'Visit'
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith('m.'):
        netloc = netloc[2:]
    if netloc.startswith('mobile.'):
        netloc = netloc[7:]
    if netloc in PLATFORM_NAMES:
        return PLATFORM_NAMES[netloc], 'Blog'

    stripped = netloc.replace('www.', '')
    parts = stripped.split('.')
    base = parts[-2] if len(parts) > 1 else parts[0]
    title = base.replace('-', ' ').replace('_', ' ').title()
    return title, 'Visit'

def parse_date(date_str):
    try:
        # Try ISO format first
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.year, dt.strftime('%B %d, %Y')
    except Exception:
        # Fallback: just extract year
        try:
            dt = datetime.strptime(date_str, '%B %d, %Y')
            return dt.year, date_str
        except Exception:
            # If all fails, try to extract year
            for fmt in ('%Y', '%Y-%m-%d', '%b %d, %Y'):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.year, date_str
                except Exception:
                    continue
            return 'Unknown', date_str

def read_media_csv(csv_path):
    entries = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year, date_str = parse_date(row['date'])
            title = escape(row['title'])
            url = row['url'].strip().strip('"')
            source, primary_label = humanize_source(url)
            image_url = (row.get('image') or '').strip()
            image_html = f'<img class="media-card__image" src="{image_url}" alt="{title} preview" loading="lazy">' if image_url else '<div class="media-card__image media-card__image--placeholder"></div>'
            github_url = (row.get('github') or '').strip()
            github_html = ''
            if github_url:
                github_clean = github_url.strip('"')
                github_html = f'<a class="badge-link badge-secondary" href="{github_clean}" target="_blank" rel="noopener">GitHub Repository</a>'
            # Bold 'Llinas, B.', 'Llinás, B.', and 'Brian Llinas' in authors
            authors = escape(row['authors'])
            authors = authors.replace('Llinas, B.', '<strong>Llinas, B.</strong>')
            authors = authors.replace('Llinás, B.', '<strong>Llinás, B.</strong>')
            authors = authors.replace('Brian Llinas', '<strong>Brian Llinas</strong>')
            entries.append({
                'title': title,
                'authors': authors,
                'date': row['date'],
                'date_str': date_str,
                'year': year,
                'url': url,
                'image_html': image_html,
                'github_html': github_html,
                'source': source,
                'primary_label': primary_label
            })
    return entries

def group_by_year(entries):
    grouped = defaultdict(list)
    for entry in entries:
        year_str = str(entry['year'])
        grouped[year_str].append(entry)
    # Sort years: numeric years descending, then 'Unknown' at the end
    def sort_key(item):
        year = item[0]
        try:
            return (-int(year), '')
        except ValueError:
            return (float('inf'), year)
    return dict(sorted(grouped.items(), key=sort_key))

def render_media_page(grouped):
    section_parts = []
    section_parts.append('<section class="pub-section">')
    section_parts.append('<h3>Media & Other Outreach</h3>')
    section_parts.append('<style>')
    section_parts.append('.media-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 28px; margin-top: 24px; list-style: none; padding: 0; }')
    section_parts.append('.media-card { background: #fff; border-radius: 24px; box-shadow: 0 16px 40px rgba(23, 68, 107, 0.08); overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s ease, box-shadow 0.2s ease; }')
    section_parts.append('.media-card:hover { transform: translateY(-4px); box-shadow: 0 22px 50px rgba(23, 68, 107, 0.14); }')
    section_parts.append('.media-card__figure { display: block; position: relative; overflow: hidden; aspect-ratio: 4 / 3; background: linear-gradient(135deg, #dbe9fb, #f2f4f8); }')
    section_parts.append('.media-card__image { width: 100%; height: 100%; object-fit: cover; display: block; }')
    section_parts.append('.media-card__image--placeholder { display: flex; align-items: center; justify-content: center; color: #7d8aa1; font-size: 0.85em; background: linear-gradient(135deg, #dfe7f5, #f2f5fb); }')
    section_parts.append('.media-card__body { display: flex; flex-direction: column; gap: 12px; padding: 22px 24px 24px; min-height: 220px; }')
    section_parts.append('.media-card__meta { display: flex; justify-content: space-between; align-items: center; font-size: 0.85em; color: #6b7a90; letter-spacing: 0.01em; text-transform: uppercase; }')
    section_parts.append('.media-card__title { margin: 0; font-size: 1.08em; line-height: 1.35; color: #1d2e45; }')
    section_parts.append('.media-card__title a { color: inherit; text-decoration: none; }')
    section_parts.append('.media-card__title a:hover { color: #17446b; }')
    section_parts.append('.media-card__authors { margin: 0; color: #2f3b4c; line-height: 1.6; font-size: 0.98em; }')
    section_parts.append('.media-card__actions { margin-top: auto; display: flex; gap: 10px; flex-wrap: wrap; }')
    section_parts.append('@media (max-width: 640px) { .media-card__body { padding: 20px; } }')
    section_parts.append('</style>')
    for year, items in grouped.items():
        section_parts.append(f'<h4 style="margin-top:2em;">{year}</h4>')
        section_parts.append('<div class="media-grid">')
        for entry in items:
            section_parts.append(CARD_TEMPLATE.format(**entry))
        section_parts.append('</div>')
    section_parts.append('</section>')

    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('    <meta charset="UTF-8">')
    html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('    <title>Media & Outreach</title>')
    html.append(f'    <link rel="stylesheet" href="../style.css?v={CSS_VERSION}">')
    html.append('</head>')
    html.append('<body style="background:#f7f8fa;">')
    html.append('    <header class="site-header">')
    html.append('        <div class="site-header__inner">')
    html.append('            <a class="site-logo" href="about.html">Brian Llinás</a>')
    html.append('            <nav class="site-nav">')
    html.append('                <a class="site-nav__link" href="about.html">About Me</a>')
    html.append('                <a class="site-nav__link" href="publications.html">Publication</a>')
    html.append('                <a class="site-nav__link site-nav__link--active" href="media.html">Media & Outreach</a>')
    html.append('                <a class="site-nav__link" href="cv.html">CV</a>')
    html.append('            </nav>')
    html.append('        </div>')
    html.append('    </header>')
    html.append('    <main class="pubs-main">')
    html.append('        <div class="pubs-container">')
    html.append('            ' + '\n            '.join(section_parts))
    html.append('        </div>')
    html.append('    </main>')
    html.append('    <footer class="site-footer">')
    html.append('        <div class="footer-top">')
    html.append('            <div>')
    html.append('                <strong>© 2024–2025 Brian Llinás</strong><br>')
    html.append('                bllin001@odu.edu')
    html.append('            </div>')
    html.append('            <div class="footer-links">')
    html.append('                <a href="about.html">About</a>')
    html.append('                <a href="publications.html">Publication</a>')
    html.append('                <a href="media.html">Media & Outreach</a>')
    html.append('                <a href="cv.html">CV</a>')
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
    return '\n'.join(html) + '\n'


def main():
    entries = read_media_csv(INPUT_CSV)
    grouped = group_by_year(entries)
    html_page = render_media_page(grouped)

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_page)

if __name__ == '__main__':
    main()
