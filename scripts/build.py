#!/usr/bin/env python3
"""Build the static ExEn archive. Python standard library; no network required."""
from pathlib import Path
import csv
import html
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://wakkatobakka.github.io/exen-game-archive/'
GITHUB = 'https://github.com/Wakkatobakka/exen-game-archive'
catalog = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
assert len(catalog) == len({e['id'] for e in catalog}) == 46

def head(title, description, canonical, prefix):
    h = lambda value: html.escape(str(value), quote=True)
    name = h(title + ' | ExEn Archive')
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="theme-color" content="#090d17">
<meta name="description" content="{h(description)}"><title>{name}</title>
<meta property="og:type" content="website"><meta property="og:title" content="{name}">
<meta property="og:description" content="{h(description)}"><meta property="og:url" content="{h(canonical)}">
<meta property="og:image" content="{BASE}assets/social-preview.png"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{h(canonical)}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
<link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="stylesheet" href="{prefix}assets/history.css">
</head><body><a class="skip" href="#main">Skip to content</a>'''

with (ROOT / 'data/catalog.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(catalog[0]))
    writer.writeheader()
    writer.writerows(catalog)

from history_pages import render
render(globals())
