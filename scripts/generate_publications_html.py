


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
                'meta_str': meta_str,
                'url_html': url_html,
                'notes_html': notes_html,
                'links_html': links_html
            })
    return entries

def group_by_year(entries):
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry['year']].append(entry)
    return dict(sorted(grouped.items(), reverse=True))

def render_html(grouped):
    html = []
    html.append('<section class="pub-section">')
    html.append('<h3>Publications</h3>')
    for year, items in grouped.items():
        html.append(f'<h4 style="margin-top:2em;">{year}</h4>')
        html.append('<ol class="pub-list">')
        for entry in items:
            html.append(CARD_TEMPLATE.format(**entry))
        html.append('</ol>')
    html.append('</section>')
    return '\n'.join(html)

def main():
    entries = read_publications_csv(INPUT_CSV)
    grouped = group_by_year(entries)
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
        f.write(new_html)

if __name__ == '__main__':
    main()
