#!/usr/bin/env python3
"""Verify catalog parity, generated records, and local links. Stdlib only."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import csv
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags, self.ids, self.refs = [], set(), []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate HTML id: {attrs['id']}"
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.refs.append(attrs[key])

data = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
assert len(data) == 46 and len({e['id'] for e in data}) == 46
assert len({e['source_url'] for e in data}) == 46
with (ROOT / 'data/catalog.csv').open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len(data)
for record, row in zip(data, rows):
    assert all(row[k] == ('' if record.get(k) is None else str(record.get(k))) for k in row), record['id']
    assert record['platform'] == 'ExEn' and record['evidence_level'] == 'catalog-listing'
    assert not record['package_inspected'] and not record['runtime_tested'] and not record['sha256']

paths = [ROOT / 'index.html', ROOT / 'about/index.html', ROOT / '404.html', *ROOT.glob('games/*/index.html')]
assert len(paths) == 49
pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in paths}
refs = 0
for path, page in pages.items():
    assert any(tag == 'title' for tag, _ in page.tags) and sum(tag == 'h1' for tag, _ in page.tags) == 1, path
    for raw in page.refs:
        url = urlparse(raw)
        if url.scheme or url.netloc:
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if target.is_dir():
            target /= 'index.html'
        assert target.is_relative_to(ROOT.resolve()), f'Link outside repository: {raw}'
        assert target.exists(), f'Broken link in {path.relative_to(ROOT)}: {raw}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'Broken anchor: {raw}'
        refs += 1

home = pages[(ROOT / 'index.html').resolve()]
cards = [a for tag, a in home.tags if tag == 'a' and a.get('class') == 'record']
assert len(cards) == 46 and {a['data-name'] for a in cards} == {e['title'] for e in data}
assert {'game-search', 'year-filter', 'genre-filter', 'sort-by', 'reset-filters'} <= home.ids
for record in data:
    text = (ROOT / 'games' / record['id'] / 'index.html').read_text(encoding='utf-8')
    assert record['source_url'] in text and 'Not inspected' in text
assert (ROOT / 'assets/social-preview.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
sitemap = ET.parse(ROOT / 'sitemap.xml')
assert len(sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')) == 48
print(f'PASS: 46 records, CSV/JSON parity, 49 HTML pages, 48 sitemap URLs, {refs} local links and anchors.')
