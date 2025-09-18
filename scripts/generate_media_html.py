import csv
from collections import defaultdict
from datetime import datetime

INPUT_CSV = '../data/media.csv'
OUTPUT_HTML = '../pages/media.html'

CARD_TEMPLATE = '''
<li>
    <article class="pub-card" style="display: flex; align-items: flex-start; gap: 24px; padding: 18px 24px; background: #fff; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 18px;">
        <div class="media-bookmark" style="flex: 0 0 120px; display: flex; align-items: center; justify-content: center;">
            {image_html}
        </div>
        <div class="media-details" style="flex: 1;">
            <header>
                <h4 style="margin-bottom: 8px;">{title}</h4>
                <span class="pub-date" style="display: block; color: #555; margin-bottom: 8px;">{date_str}</span>
            </header>
            <p class="pub-authors" style="margin-bottom: 12px;">{authors}</p>
            <div class="pub-links" style="margin-top: 1em; display: flex; gap: 12px;">
                <a class="badge-link" href="{url}" target="_blank" rel="noopener">Blog</a>
                {github_html}
            </div>
        </div>
    </article>
</li>
'''

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
            image_url = (row.get('image') or '').strip()
            image_html = f'<img src="{image_url}" alt="{row["title"]} bookmark" style="width:180px; height:auto; max-height:140px; object-fit:cover; border-radius:10px; margin-bottom:8px;">' if image_url else ''
            github_url = (row.get('github') or '').strip()
            github_html = f'<a class="badge-link" href="{github_url}" target="_blank" rel="noopener">Github Repository</a>' if github_url else ''
            # Bold 'Llinas, B.', 'Llinás, B.', and 'Brian Llinas' in authors
            authors = row['authors']
            authors = authors.replace('Llinas, B.', '<strong>Llinas, B.</strong>')
            authors = authors.replace('Llinás, B.', '<strong>Llinás, B.</strong>')
            authors = authors.replace('Brian Llinas', '<strong>Brian Llinas</strong>')
            entries.append({
                'title': row['title'],
                'authors': authors,
                'date': row['date'],
                'date_str': date_str,
                'year': year,
                'url': row['url'],
                'image_html': image_html,
                'github_html': github_html
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

def render_html(grouped):
    html = []
    html.append('<section class="pub-section">')
    html.append('<h3>Media & Other Outreach</h3>')
    for year, items in grouped.items():
        html.append(f'<h4 style="margin-top:2em;">{year}</h4>')
        html.append('<ol class="pub-list">')
        for entry in items:
            html.append(CARD_TEMPLATE.format(**entry))
        html.append('</ol>')
    html.append('</section>')
    return '\n'.join(html)

def main():
    entries = read_media_csv(INPUT_CSV)
    grouped = group_by_year(entries)
    html_section = render_html(grouped)

    # Read the existing media.html and replace the section
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
