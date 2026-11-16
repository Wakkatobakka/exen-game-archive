#!/usr/bin/env python3
"""Verify catalog parity, generated records, and local links. Stdlib only."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import csv
import json
import re
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
research = json.loads((ROOT / 'data/research.json').read_text(encoding='utf-8'))
assert len(data) == 46 and len({e['id'] for e in data}) == 46
assert len({e['source_url'] for e in data}) == 46
with (ROOT / 'data/catalog.csv').open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len(data)
for record, row in zip(data, rows):
    assert all(row[k] == ('' if record.get(k) is None else str(record.get(k))) for k in row), record['id']
    assert record['platform'] == 'ExEn' and record['evidence_level'] == 'catalog-listing'
    assert not record['package_inspected'] and not record['runtime_tested'] and not record['sha256']

assert set(research['games']) == {e['id'] for e in data}
quote_words = {}
image_count = 0
for gid, record in research['games'].items():
    assert record['summary'] and record['sections'] and record['entry']['overview'], gid
    entry = record['entry']
    assert record['summary'] == entry['deck'], gid
    paragraphs = [p for key in ('overview', 'development', 'release', 'notes') for p in entry[key]]
    assert all(p['text'] and p['sources'] for p in paragraphs), gid
    referenced = [*record['summary_sources'], *[sid for s in record['sections'] for sid in s['sources']], *[sid for p in paragraphs for sid in p['sources']], *[q['source'] for q in entry['quotes']], *[c['source'] for c in record['credits']], *[s['source'] for s in record['studio_roles']], *[m['source'] for m in record.get('media', [])]]
    assert all(sid in research['sources'] for sid in referenced), gid
    assert all(c['name'] and c['role'] and c['scope'] for c in record['credits']), gid
    for quote in entry['quotes']:
        assert quote['text'] and quote['speaker'] and quote['attribution'], gid
        assert quote['section'] in ('development', 'reception'), gid
        url = research['sources'][quote['source']]['url']
        count = len(re.findall(r"\b[\w’'-]+\b", quote['text']))
        if quote.get('translation'):
            count += sum(len(re.findall(r"\b[\w’'-]+\b", t)) for t in re.findall('“([^”]+)”', quote['translation']))
        quote_words[url] = quote_words.get(url, 0) + count
    for image in record.get('media', []):
        assert image['alt'] and image['caption'] and image['credit'], gid
        assert image['width'] > 0 and image['height'] > 0, gid
        path = (ROOT / image['path']).resolve()
        assert path.is_relative_to(ROOT.resolve()) and path.is_file(), image['path']
        assert path.suffix in ('.png', '.webp', '.jpg', '.jpeg', '.gif'), image['path']
        assert image['placement'] in ('game', 'development', 'gallery'), gid
        if image['kind'] == 'screenshot':
            assert image['platform'] == 'ExEn' and image['platform_evidence'], gid
        image_count += 1
assert all(count <= 25 for count in quote_words.values()), quote_words
for source in research['sources'].values():
    assert source['url'].startswith('https://') and source['kind'] and source['reviewed']
assert sum(bool(g['credits']) for g in research['games'].values()) == 35
assert len({c['name'] for g in research['games'].values() for c in g['credits']}) == 94
with (ROOT / 'data/credits.csv').open(encoding='utf-8', newline='') as f:
    credit_rows = list(csv.DictReader(f))
assert len(credit_rows) == sum(len(g['credits']) for g in research['games'].values())
for row in credit_rows:
    assert any(c['name']==row['person'] and c['role']==row['role'] and research['sources'][c['source']]['url']==row['source_url'] for c in research['games'][row['game_id']]['credits'])

paths = [ROOT / 'index.html', ROOT / 'about/index.html', ROOT / '404.html', ROOT / 'history/index.html', ROOT / 'creators/index.html', ROOT / 'sources/index.html', *ROOT.glob('games/*/index.html')]
assert len(paths) == 52
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
assert {'game-search', 'year-filter', 'genre-filter', 'research-filter', 'sort-by', 'reset-filters'} <= home.ids
for record in data:
    text = (ROOT / 'games' / record['id'] / 'index.html').read_text(encoding='utf-8')
    assert record['source_url'] in text and 'Not inspected' in text
    assert 'aria-label="In this entry"' in text and 'id="the-game"' in text
    assert 'id="sources"' in text and 'Catalog and original file details' in text
    assert 'The drawings are' not in text and 'The personal credits are still missing' not in text
    assert 'Small limits.' not in text and 'FOLLOW THE EVIDENCE' not in text
assert (ROOT / 'assets/social-preview.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
sitemap = ET.parse(ROOT / 'sitemap.xml')
assert len(sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')) == 51
print(f'PASS: 46 entries, 94 people, {image_count} attributed images, source references and CSV parity, 52 HTML pages, 51 sitemap URLs, {refs} local links and anchors.')
