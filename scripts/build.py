#!/usr/bin/env python3
"""Build a fully static GitHub Pages ExEn catalog from data/catalog.json.

No network, paid services, dependencies or game files needed; Python 3 stdlib only.
"""
from pathlib import Path
import csv, html, json, collections
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
BASE='https://wakkatobakka.github.io/exen-game-archive/'
GITHUB='https://github.com/Wakkatobakka/exen-game-archive'
SOURCE='https://www.myabandonware.com/browse/platform/exen/'
BREW='https://wakkatobakka.github.io/qualcomm-brew-archive/'
ZEEBO='https://wakkatobakka.github.io/zeebo-archive/'
DATE='2026-10-29'

catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
assert len({e['id'] for e in catalog})==len(catalog), 'Duplicated ids'
assert all(e['source_url'].startswith('https://www.myabandonware.com/game/') for e in catalog)
assert all(not e['package_inspected'] and not e['sha256'] for e in catalog), 'Update inspected-file counts and copy when binaries are verified.'
N=len(catalog)
counts=dict(sorted(collections.Counter(e['year'] for e in catalog).items()))
bytitle=sorted(catalog,key=lambda e:e['title'].casefold())

def h(value):return html.escape(str(value),quote=True)

def head(title,desc,canonical,root):
    name=h(title+' | ExEn Archive')
    desc=h(desc)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="theme-color" content="#090d17"><meta name="description" content="{desc}">
<meta property="og:type" content="website"><meta property="og:title" content="{name}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{h(canonical)}">
<meta property="og:image" content="{BASE}assets/social-preview.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{h(canonical)}"><link rel="icon" type="image/svg+xml" href="{root}assets/favicon.svg">
<link rel="stylesheet" href="{root}assets/styles.css"><title>{name}</title>
</head><body><a class="skip" href="#main">Skip to content</a>
'''

def nav(root,active=''):
    return f'''<header class="site-header"><div class="shell nav">
<a class="brand" href="{root}index.html" aria-label="ExEn Archive home"><i aria-hidden="true"><b></b><b></b><b></b><b></b></i><span>ExEn <em>/</em> ARCHIVE</span></a>
<nav aria-label="Main navigation" class="top-nav">
<a href="{root}index.html#catalog"{' aria-current="page"' if active=='catalog' else ''}>Catalog</a>
<a href="{root}about/index.html"{' aria-current="page"' if active=='about' else ''}>Field notes</a>
<a class="nav-source" href="{SOURCE}" target="_blank" rel="noopener noreferrer">Original listings ↗</a>
</nav></div></header>'''

def footer(root):
    return f'''<footer class="site-footer"><div class="shell foot"><div>
<a class="brand" href="{root}index.html"><i aria-hidden="true"><b></b><b></b><b></b><b></b></i><span>ExEn <em>/</em> ARCHIVE</span></a>
<p>An independent ExEn catalog by Wakkatobakka. Original preservation and listing credits belong to their source communities. Game files remain at their source.</p>
</div><div class="foot-links"><a href="{root}about/index.html">Methods &amp; credits</a><a href="{BREW}">BREW Archive ↗</a><a href="{ZEEBO}">Zeebo Archive ↗</a><a href="{GITHUB}" rel="noopener">GitHub ↗</a></div></div></footer>'''

def page(title,desc,canonical,root,body,active='',script=''):
    return head(title,desc,canonical,root)+nav(root,active)+'<main id="main">'+body+'</main>'+footer(root)+script+'</body></html>\n'

def link(e):return f'games/{e["id"]}/index.html'

# Homepage: every listing is real HTML so crawlability and basic offline use do not depend on JavaScript.
featured_titles=['Crash Bandicoot',"Banjo-Kazooie: Grunty's Revenge Missions",'Mutant Alert','Age of Empires II Mobile','South Park','Tomb Raider: The Osiris Codex']
feature_cards='\n'.join('''<a class="spotlight-card" href="{path}"><span class="art-no">0{no} / ExEn <span class="arrow" aria-hidden="true">↗</span></span><div><h3>{title}</h3><p>{year} · {label}</p></div></a>'''.format(
    path=link(e),no=i,title=h(e['title']),year=e['year'],label=h(e['genre'] or 'Mobile gaming'))
    for i,title in enumerate(featured_titles,1) for e in catalog if e['title']==title)
record_cards='\n'.join('''<a class="record" href="{path}" data-name="{name}" data-year="{year}" data-genres="{genres}" data-search="{search}">
<div><div class="record-top"><span class="record-year">{year} / ExEn</span><span class="record-status">SOURCE-LISTED</span></div><h3>{title}</h3></div>
<div class="record-bottom"><small>{label}</small><span class="arrow" aria-hidden="true">↗</span></div></a>'''.format(
    path=link(e),name=h(e['title']),year=e['year'],genres=h('|'.join(g.strip() for g in (e['genre'] or '').split('/') if g.strip())),search=h(' '.join([e['title'],str(e['year']),e['genre'] or '',e['developer'] or '',e['publisher'] or ''])),
    title=h(e['title']),label=h(e['genre'] or 'Genre pending verification')) for e in bytitle)
year_options='\n'.join(f'<option value="{year}">{year} ({num})</option>' for year,num in counts.items())

genres=sorted({g.strip() for e in catalog for g in (e['genre'] or '').split('/') if g.strip()})
genre_options=''.join(f'<option value="{h(g)}">{h(g)}</option>' for g in genres)
home=f'''
<section class="shell hero"><div><div class="eyebrow"><span class="pulse"></span> WAKKATOBAKKA'S EARLY MOBILE HISTORY INDEX</div>
<h1>The platform faded.<br><em>The catalog shouldn't.</em></h1>
<p class="hero-lede">Before app stores and touchscreen controls, there was ExEn: a different branch of mobile gaming. Explore {N} documented titles, follow their source trails, and help turn fragile listings into durable preservation records.</p>
<div class="buttons"><a class="btn btn-primary" href="#catalog">Explore {N} titles <span aria-hidden="true">↘</span></a>
<a class="btn btn-secondary" href="{SOURCE}" rel="noopener noreferrer" target="_blank">Browse the source ↗</a></div>
<p class="small-flag"><strong>Catalog scope:</strong> {N} source-linked listings. Original packages have not been inspected for this index.</p></div>
<div class="hero-art" role="img" aria-label="Illustration of a retro mobile phone showing the ExEn logo"><div class="handset"><div class="handset-display"><div class="screen-top"><span>INFUSIO / GAME</span><span>▮▮▯</span></div><div class="screen-big">Ex<span>En</span></div><div class="screen-small">{N} TITLES INDEXED</div><div class="screen-bottom"><b></b><b></b><b></b><b></b><b></b></div></div><div class="handset-dpad"><i></i><b></b></div></div><div class="art-label">SMALL SCREENS<span>LONG MEMORIES</span></div></div></section>
<section class="statband"><div class="shell stats"><div class="stat"><strong class="mint">{N}</strong><span>documented game listings</span></div><div class="stat"><strong class="amber">{N}</strong><span>individual source-linked records</span></div><div class="stat"><strong>2001–06</strong><span>years represented in source index</span></div><div class="stat"><strong>4</strong><span>source catalog pages checked</span></div></div></section>
<section class="shell intro"><div><div class="kicker">A PARALLEL HISTORY</div><h2>Another way phones learned to play.</h2></div><div><p>Developed by French company In-Fusio, ExEn brought downloadable games to compatible feature phones years before smartphones took over. Publishers and developers brought familiar characters alongside more experimental, phone-first games.</p>
<p>The surviving listings give these games a starting point: names, dates, credits where documented, and a source to follow. This catalog puts those trails in one place alongside the BREW and Zeebo archives.</p>
<a class="text-link" href="about/index.html">Read the methods and platform history ↗</a></div></section>
<section class="shell spotlight"><div class="spotlight-header"><div><div class="kicker">SOME FAMILIAR STRANGERS</div><h2>Big names. Tiny screens.</h2></div><p>A few places to start exploring this unlikely corner of mobile history.</p></div><div class="spotlight-grid">{feature_cards}</div></section>
<section id="catalog" class="catalog-wrap"><div class="shell"><div class="catalog-header"><div class="kicker">THE DOCUMENTED INDEX</div><h2>Find something forgotten.</h2><p class="sub">All {N} ExEn entries currently listed in the source collection. Search by title, developer, or genre; narrow the list by year; then follow any record back to its source.</p></div>
<noscript><p class="no-script">All {N} records are shown below. Search, filters, and sorting are available with JavaScript enabled.</p></noscript>
<div class="filters" id="catalog-filters" hidden><div class="filter search-filter"><label for="game-search">Search titles, developers, and genres</label><input id="game-search" type="search" placeholder="Try Crash, IOMO, 2003…" autocomplete="off"></div>
<div class="filter"><label for="year-filter">Release year</label><select id="year-filter"><option value="">All years</option>{year_options}</select></div>
<div class="filter"><label for="genre-filter">Genre</label><select id="genre-filter"><option value="">All genres</option>{genre_options}<option value="unknown">Not yet recorded</option></select></div>
<div class="filter"><label for="sort-by">Sort by</label><select id="sort-by"><option value="title">Title A–Z</option><option value="oldest">Oldest first</option><option value="newest">Newest first</option></select></div></div>
<div class="results-row"><span id="result-count" aria-live="polite"><strong>{N} of {N}</strong> listed games</span><button class="reset-filters" id="reset-filters" type="button" hidden>Clear filters</button></div>
<div class="catalog-grid" id="game-list">{record_cards}</div><div class="empty-state" id="no-results" hidden>No matching titles. Try a different search or year.</div>
<div class="metadata-downloads"><div><h3>Take the catalog with you.</h3><p>Download the recorded names, dates, credits, and source links.</p></div><div class="buttons"><a class="btn btn-secondary" href="data/catalog.csv" download>Catalog CSV ↓</a><a class="btn btn-secondary" href="data/catalog.json" download>Catalog JSON ↓</a></div></div>
</div></section>'''
(ROOT/'index.html').write_text(page('The Lost Catalog',f'{N} documented ExEn games with source links, clear verification states, and individual preservation records.',BASE,'',home,active='catalog',script='<script src="assets/app.js" defer></script>'),encoding='utf-8')

about=f'''
<article class="narrow article"><div class="eyebrow"><span class="pulse"></span> THE FIELD NOTES</div>
<h1>Every record needs a trail.</h1>
<p class="lede">This project is a companion to the <a href="{BREW}">Qualcomm BREW Archive</a> and <a href="{ZEEBO}">Zeebo Archive</a>. It follows the same preservation-first philosophy, but it begins with different evidence. Each record keeps the source and its research status visible.</p>
<div class="panel"><div class="kicker">CURRENT EVIDENCE</div><p><strong>{N} catalog listings.</strong> As reviewed on {DATE}, My Abandonware's ExEn browse section displays {N} titles across four pages. Every title here links to its individual source record.</p><p><strong>Zero inspected game packages.</strong> No original ExEn files were obtained, read, emulated, hashed, or hosted during this catalog build. We never use a website's download button as proof that a specific package is intact or compatible.</p></div>
<h2>What was ExEn?</h2>
<p>ExEn — short for <strong>Execution Engine</strong> — was a mobile game runtime developed by the French company In-Fusio. It was used on compatible feature phones, especially in the early 2000s, to distribute downloadable games. It existed alongside J2ME, BREW, and other handset platforms.</p>
<p>Contemporary reporting gives useful context: an <a href="https://www.mobileuserexperience.com/in-fusio-launches-3d-mobile-gaming/5682/" target="_blank" rel="noopener noreferrer">August 2002 industry report</a> discusses ExEn-equipped handsets and In-Fusio's downloadable games; a <a href="https://www.lightreading.com/business-management/panasonic-plays-with-in-fusio" target="_blank" rel="noopener noreferrer">September 2002 announcement</a> describes ExEn 2.0 on Panasonic devices; and a <a href="https://gamedev.net/tutorials/programming/general-and-gameplay-programming/the-clash-of-mobile-platforms-j2me-exen-moph-r1944" target="_blank" rel="noopener noreferrer">contemporary developer comparison</a> documents how ExEn fit into the fragmented market.</p>
<h2>How these {N} records were built</h2>
<ul><li>Reviewed the <a href="{SOURCE}" target="_blank" rel="noopener noreferrer">ExEn browse index</a>, including its <a href="https://www.myabandonware.com/browse/platform/exen/page/2/">second</a>, <a href="https://www.myabandonware.com/browse/platform/exen/page/3/">third</a>, and <a href="https://www.myabandonware.com/browse/platform/exen/page/4/">fourth</a> pages.</li>
<li>Recorded the exact title, ExEn-specific source-listed year, and direct game-page URL for each entry. Be aware that the year at the top of a multi-platform game page can refer to a different edition; our year comes from the ExEn index.</li>
<li>Added publisher, developer, genre, and notes only for selected entries where those details were individually reviewed. Unknowns are intentionally left blank.</li>
<li>Wrote our own descriptions. We did not copy screenshots, box art, original game files, third-party reviews, or source-site prose.</li>
<li>Marked every entry as <strong>source-listed / package not inspected</strong>. A listing is not proof of byte-level preservation, completeness, compatibility, or gameplay.</li></ul>
<h2>What a verified record would require</h2>
<p>For a specific lawfully obtained ExEn package, a future reviewer can capture its original filename, byte size, SHA-256 checksum, file structure, software/version clues, evidence location, and an explicitly documented runtime test. Only after file inspection should a record's verification state change.</p>
<p>Some game pages cover several platforms or editions. Those are not interchangeable: the ExEn build must be identified separately from J2ME, BREW, or other releases.</p>
<h2>Rights and sourcing</h2>
<p>Game titles and factual metadata are presented for identification and historical research. Game copyright remains with the respective rights holders. <strong>“Abandonware” is not itself a copyright license.</strong> This site does not host games, facilitate automated fetching, or claim permission to redistribute third-party packages. External source links point to independently operated sites; availability and terms may change.</p>
<p>Found an error, missing credit, or broken link? <a href="{GITHUB}/issues/new?template=catalog-correction.yml">Report it to Wakka</a> with the title and a supporting source where possible. Wakka reviews reports and publishes updates. The <a href="{GITHUB}/blob/main/data/SOURCES.md">source register</a> lists original references and this index's review date.</p>
<div class="buttons"><a class="btn btn-primary" href="../index.html#catalog">Browse the catalog ↗</a><a class="btn btn-secondary" href="{BREW}">Visit the BREW Archive ↗</a></div>
</article>
'''
(ROOT/'about/index.html').write_text(page('Methods and platform history','Sources, verification limits, and an introduction to the In-Fusio ExEn game runtime.',BASE+'about/','../',about,'about'),encoding='utf-8')

# Individual indexable pages, each with source URL and honest evidence level.
for i,e in enumerate(bytitle):
    previous=bytitle[(i-1)%N];following=bytitle[(i+1)%N]
    detail_note=e['note'] or f"The ExEn collection includes {e['title']} with a source-listed year of {e['year']}. No package-specific evidence has yet been recorded."
    genre=e['genre'] or 'Not yet researched'
    developer=e['developer'] or 'Not yet researched'
    publisher=e['publisher'] or 'Not yet researched'
    year=e['year']
    description=f"Source-linked preservation record for {e['title']} ({year}, ExEn). Catalog listing documented; original package not yet inspected."
    body=f'''
<section class="shell detail-hero"><div class="breadcrumbs"><a href="../../index.html">Home</a><span>/</span><a href="../../index.html#catalog">Catalog</a><span>/</span><span>{h(e['title'])}</span></div>
<div class="eyebrow"><span class="pulse"></span> EXEN GAME RECORD / {str(i+1).zfill(2)} OF {N}</div>
<h1>{h(e['title'])}</h1><p class="detail-deck">A surviving catalog reference for a {year} ExEn mobile game. Follow the original listing, explore the recorded details, and see the current research status below.</p>
<div class="chips"><span class="chip">ExEn</span><span class="chip">{year}</span><span class="chip mint">Source-listed</span></div></section>
<section class="shell detail-layout"><div class="article-panel"><h2>What we know</h2><p>{h(detail_note)}</p>
<div class="facts"><div><dt>Platform</dt><dd>In-Fusio ExEn</dd></div><div><dt>Source-listed year</dt><dd>{year}</dd></div>
<div><dt>Genre</dt><dd>{h(genre)}</dd></div><div><dt>Publisher</dt><dd>{h(publisher)}</dd></div>
<div><dt>Developer</dt><dd>{h(developer)}</dd></div><div><dt>Source reviewed</dt><dd>{DATE}</dd></div></div>
<p class="fact-note">Credits and genres appear only where checked on the linked source page. The listed year refers specifically to the ExEn entry, not necessarily other platform editions.</p>
<hr><h2>Package evidence</h2><div class="caution"><strong>Not inspected.</strong> No original binary was obtained for this project. Package filename, byte size, SHA-256 fingerprint, ExEn engine version, device compatibility, and gameplay status remain unverified.</div>
<div class="facts"><div><dt>Original filename</dt><dd>Unknown</dd></div><div><dt>SHA-256</dt><dd>Not recorded</dd></div><div><dt>File size</dt><dd>Not measured</dd></div><div><dt>Runtime test</dt><dd>Not conducted</dd></div></div>
<hr><h2>Help fill in the history</h2><p>Have original credits, handset details, or package evidence for this ExEn edition? <a href="{GITHUB}/issues/new?template=catalog-correction.yml">Suggest a correction</a> with a source so the record can improve.</p>
<div class="detail-links"><a href="../../games/{previous['id']}/index.html">← {h(previous['title'])}</a><a href="../../games/{following['id']}/index.html">{h(following['title'])} →</a></div></div>
<aside class="side-panel" aria-label="Evidence and source"><div class="eyebrow"><span class="pulse"></span> ORIGINAL REFERENCE</div>
<h2 style="margin-top:18px">Follow the source</h2><p>Find the original game page, platform details, and available files at My Abandonware. Check the ExEn edition on multi-platform pages.</p>
<a class="source-url" target="_blank" rel="noopener noreferrer" href="{h(e['source_url'])}">{h(e['source_url'])} ↗</a>
<div class="buttons"><a class="btn btn-primary" target="_blank" rel="noopener noreferrer" href="{h(e['source_url'])}">Open source record ↗</a></div>
<div class="side-meta"><h3>Evidence level</h3><p>Bibliographic listing confirmed. Package integrity and playability not assessed.</p></div>
<div class="side-meta"><h3>Source directory</h3><a class="source-url" href="{SOURCE}" target="_blank" rel="noopener noreferrer">Browse all ExEn listings ↗</a></div></aside></section>
'''
    sub=ROOT/'games'/e['id'];sub.mkdir(parents=True,exist_ok=True)
    (sub/'index.html').write_text(page(e['title'],description,BASE+f'games/{e["id"]}/','../../',body),encoding='utf-8')

# Machine-readable metadata is independent of the static HTML.
fields=['id','title','year','platform','genre','publisher','developer','note','source_name','source_url','source_collection_url','source_reviewed','evidence_level','package_inspected','package_filename','package_size_bytes','sha256','runtime_tested','runtime_result']
with (ROOT/'data/catalog.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:e.get(k) for k in fields} for e in catalog)

# All pages are crawlable. Sitemap uses the repo name assumed in README.
urls=[BASE,BASE+'about/']+[BASE+f'games/{e["id"]}/' for e in bytitle]
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{h(url)}</loc><lastmod>{DATE}</lastmod></url>\n' for url in urls)+'</urlset>\n'
(ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n',encoding='utf-8')
(ROOT/'.nojekyll').write_text('',encoding='utf-8')
notfound=f'''<section class="narrow article"><div class="eyebrow">NO SIGNAL / 404</div><h1>Lost in the static.</h1><p class="lede">This URL wasn't in the catalog. Try the complete ExEn index instead.</p><a class="btn btn-primary" href="{BASE}">Return to the archive →</a></section>'''
(ROOT/'404.html').write_text(page('Page not found','No ExEn archive page found.',BASE,BASE,notfound),encoding='utf-8')
print('Built',N,'detail pages + home, about, 404 and sitemap,',len(urls),'URLs')
