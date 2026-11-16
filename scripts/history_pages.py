"""Render the archive from sourced editorial records. Standard library only."""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import html
import json
import re
import unicodedata


def render(ctx):
    root, base, github = ctx['ROOT'], ctx['BASE'], ctx['GITHUB']
    catalog = sorted(ctx['catalog'], key=lambda e: e['title'].casefold())
    research = json.loads((root / 'data/research.json').read_text(encoding='utf-8'))
    games, sources, date = research['games'], research['sources'], research['reviewed']
    entries = {e['id']: e for e in catalog}
    h = lambda value: html.escape(str(value), quote=True)
    def slug(value):
        return re.sub('[^a-z0-9]+', '-', unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()).strip('-')
    def game(e, prefix=''):
        return prefix + 'games/' + e['id'] + '/index.html'
    def person(name, prefix=''):
        return prefix + 'creators/index.html#person-' + slug(name)
    def studio(name, prefix=''):
        return prefix + 'creators/index.html#studio-' + slug(name)

    people, studios = defaultdict(list), defaultdict(list)
    for e in catalog:
        for credit in games[e['id']]['credits']:
            people[credit['name']].append((e, credit))
        for role in games[e['id']]['studio_roles']:
            studios[role['name']].append((e, role))

    def save(path, title, description, body, prefix='', active='', scripts=()):
        path = Path(path)
        nav = f'<header class="site-header"><div class="shell nav"><a class="brand" href="{prefix}index.html" aria-label="ExEn Archive home"><i aria-hidden="true"><b></b><b></b><b></b><b></b></i><span>ExEn <em>/</em> ARCHIVE</span></a><nav class="top-nav" aria-label="Main navigation">'
        for key, label, url in [('catalog', 'Catalog', 'index.html#catalog'), ('history', 'Platform history', 'history/index.html'), ('creators', 'Creators', 'creators/index.html'), ('sources', 'Sources', 'sources/index.html')]:
            current = ' aria-current="page"' if active == key else ''
            nav += f'<a href="{prefix}{url}"{current}>{label}</a>'
        nav += '</nav></div></header>'
        footer = f'<footer class="site-footer"><div class="shell"><div class="foot"><div><a class="brand" href="{prefix}index.html">ExEn / ARCHIVE</a><p class="footer-vision">{h(research["premise"])}</p></div><div class="foot-links"><a href="{prefix}about/index.html">Methods &amp; credits</a><a href="{github}">GitHub ↗</a><a href="https://wakkatobakka.github.io/">Wakka’s Workshop ↗</a></div></div><nav class="archive-family" aria-label="Other game archives"><span>Other archives</span>'
        for name, repo in [('BREW', 'qualcomm-brew-archive'), ('DoJa', 'doja-archive'), ('J2ME', 'j2me-archive'), ('N-Gage', 'ngage-archive'), ('Zeebo', 'zeebo-archive')]:
            footer += f'<a href="https://wakkatobakka.github.io/{repo}/">{name} ↗</a>'
        footer += '</nav></div></footer>'
        script = ''.join(f'<script src="{prefix}assets/{s}" defer></script>' for s in scripts)
        content = ctx['head'](title, description, base + str(path).replace('index.html', ''), prefix)
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(content + nav + '<main id="main">' + body + '</main>' + footer + script + '</body></html>\n', encoding='utf-8')

    def used(gid):
        g, refs = games[gid], ['listing-' + gid]
        refs += g['summary_sources']
        for key in ('overview', 'development', 'release', 'notes'):
            refs += [sid for p in g['entry'][key] for sid in p['sources']]
        refs += [q['source'] for q in g['entry']['quotes']]
        refs += [c['source'] for c in g['credits']]
        refs += [s['source'] for s in g['studio_roles']]
        refs += [m['source'] for m in g.get('media', [])]
        return list(dict.fromkeys(refs))

    def cites(ids, refs):
        return '<span class="citations">' + ''.join(f'<a href="#source-{h(sid)}" aria-label="Source {refs.index(sid) + 1}">[{refs.index(sid) + 1}]</a>' for sid in dict.fromkeys(ids)) + '</span>' if ids else ''

    def paragraphs(items, refs):
        return '<div class="entry-prose">' + ''.join(f'<p>{h(p["text"])}{cites(p["sources"], refs)}</p>' for p in items) + '</div>' if items else ''

    def quotes(items, refs, section):
        result = ''
        for q in items:
            if q['section'] != section:
                continue
            translation = f'<span class="translation-credit">{h(q["translation"])}</span>' if q.get('translation') else ''
            result += f'<figure class="source-quote"><blockquote><p>“{h(q["text"])}”</p></blockquote><figcaption>{h(q["speaker"])} · {h(q["attribution"])}{translation}{cites([q["source"]], refs)}</figcaption></figure>'
        return result

    def media(items, refs, prefix='../../'):
        result = ''
        for m in items:
            dimensions = f' width="{int(m["width"])}" height="{int(m["height"])}"' if m.get('width') and m.get('height') else ''
            url = prefix + m['path']
            wide = ' wide-media' if m['kind'] != 'screenshot' else ''
            image_size = min(512, int(m.get('width', 128)) * 2)
            result += f'<figure class="archive-figure{wide}"><div class="artifact" data-kind="{h(m["kind"])}" style="--image-size:{image_size}px"><a class="image-open" href="{h(url)}" data-image="{h(url)}" data-caption="{h(m["caption"])}" aria-label="Enlarge: {h(m["caption"])}"><img src="{h(url)}" alt="{h(m["alt"])}"{dimensions} loading="lazy"></a></div><figcaption>{h(m["caption"])}{cites([m["source"]], refs)}<span class="image-credit">{h(m["credit"])}</span></figcaption><a class="enlarge" href="{h(url)}" data-image="{h(url)}" data-caption="{h(m["caption"])}">Enlarge image <span aria-hidden="true">+</span></a></figure>'
        return result

    def bibliography(refs):
        result = '<section class="entry-section bibliography" id="sources"><h2>Sources</h2><ol>'
        for sid in refs:
            s = sources[sid]
            published = h(s['published']) + ' · ' if s.get('published') else ''
            result += f'<li id="source-{h(sid)}"><a href="{h(s["url"])}" target="_blank" rel="noopener noreferrer">{h(s["title"])} ↗</a><small>{published}{h(s["kind"])}</small>'
            if s.get('note'):
                result += f'<p>{h(s["note"])}</p>'
            result += '</li>'
        return result + '</ol></section>'

    def viewer():
        return '<dialog id="image-viewer" aria-labelledby="viewer-title"><div class="viewer-toolbar"><strong id="viewer-title">Archive image</strong><div><button type="button" id="viewer-zoom" aria-pressed="false">Zoom in</button><button type="button" id="viewer-close">Close</button></div></div><div class="viewer-canvas" id="viewer-canvas"><img id="viewer-image" alt=""></div><p class="viewer-help">Zoom in to examine the image. Swipe or scroll to move around it.</p></dialog>'

    def card(e):
        g = games[e['id']]
        year = g['entry'].get('sort_year', e['year'])
        history = str(bool(g['entry']['development'] or g['entry']['release'])).lower()
        has_credits = str(bool(g['credits'])).lower()
        names = ' '.join(c['name'] + ' ' + c['role'] for c in g['credits'])
        teams = ' '.join(s['name'] for s in g['studio_roles'])
        search = ' '.join([e['title'], str(e['year']), e['genre'] or '', e['developer'] or '', e['publisher'] or '', names, teams])
        genres = '|'.join(x.strip() for x in (e['genre'] or '').split('/') if x.strip())
        return f'<a class="record" href="{game(e)}" data-name="{h(e["title"])}" data-year="{year}" data-genres="{h(genres)}" data-research="{g["status"]}" data-has-history="{history}" data-has-credits="{has_credits}" data-search="{h(search)}"><div><div class="record-top"><span class="record-year">{year} / ExEn</span></div><h3>{h(e["title"])}</h3><p class="record-summary">{h(g["summary"])}</p></div><div class="record-bottom"><small>{h(e["genre"] or "Mobile game")}</small><span class="arrow" aria-hidden="true">↗</span></div></a>'

    features = [('crash-bandicoot', 'Kaolink’s 2002 interview, sketches and level plans.'), ('tomb-raider-the-osiris-codex', 'IOMO’s original mobile game and BeTomorrow’s ExEn adaptation.'), ('flynn-s-adventures', 'The Nightmare Busters connection and its creators.')]
    featurecards = ''
    for gid, description in features:
        g = games[gid]
        art = ''
        if g.get('media'):
            m = g['media'][0]
            art = f'<div class="feature-image"><img src="{h(m["path"])}" alt="{h(m["alt"])}" loading="lazy"></div>'
        featurecards += f'<a class="feature-card" href="{game(entries[gid])}">{art}<div><h3>{h(entries[gid]["title"])}</h3><p>{h(description)}</p><span class="text-link">Read the entry ↗</span></div></a>'
    yearopts = ''.join(f'<option value="{y}">{y} ({n})</option>' for y, n in sorted(Counter(games[e['id']]['entry'].get('sort_year', e['year']) for e in catalog).items()))
    genres = sorted({x.strip() for e in catalog for x in (e['genre'] or '').split('/') if x.strip()})
    genreopts = ''.join(f'<option value="{h(x)}">{h(x)}</option>' for x in genres)
    handset = '<div class="hero-art" role="img" aria-label="Illustration of a feature phone with an ExEn display"><div class="handset"><div class="handset-display"><div class="screen-top"><span>INFUSIO / GAME</span><span>▮▮▯</span></div><div class="screen-big">Ex<span>En</span></div><div class="screen-small">46 GAMES</div><div class="screen-bottom"><b></b><b></b><b></b><b></b><b></b></div></div><div class="handset-dpad"><i></i><b></b></div></div></div>'
    home = f'''<section class="shell hero archive-home"><div><div class="eyebrow"><span class="pulse"></span> WAKKA’S MOBILE GAME ARCHIVES</div><h1>Games made for<br><em>ExEn phones.</em></h1><p class="hero-lede">Browse 46 games, meet their creators, and explore interviews, production artwork and contemporary coverage.</p><div class="buttons"><a class="btn btn-primary" href="#catalog">Browse the catalog ↓</a><a class="btn btn-secondary" href="history/index.html">About ExEn ↗</a></div><p class="small-flag">{h(research['premise'])}</p></div>{handset}</section>
<section class="statband" aria-label="Archive contents"><div class="shell stats"><div class="stat"><strong class="mint">46</strong><span>game entries</span></div><div class="stat"><strong class="amber">{len(people)}</strong><span>named contributors</span></div><div class="stat"><strong>{len(studios)}</strong><span>studios &amp; organisations</span></div><div class="stat"><strong>2001–06</strong><span>catalog years</span></div></div></section>
<section class="shell featured-section"><div class="section-heading"><h2>Start with a game</h2></div><div class="feature-grid">{featurecards}</div></section>
<section class="shell explore-paths"><a href="history/index.html"><h2>Platform history</h2><p>In-Fusio, the handsets, the developer tools and the route to players.</p><span class="text-link">Read about ExEn ↗</span></a><a href="creators/index.html"><h2>Creators</h2><p>Programmers, artists, designers, composers, producers and testers, with links to their games.</p><span class="text-link">Browse people and studios ↗</span></a></section>
<section class="catalog-wrap" id="catalog"><div class="shell"><div class="catalog-header"><h2>Catalog</h2><p class="sub">Search by game, person, studio or role.</p></div><noscript><p>All 46 entries are available below. Filters require JavaScript.</p></noscript><div class="filters" id="catalog-filters" hidden><div class="filter search-filter"><label for="game-search">Search the archive</label><input type="search" id="game-search" placeholder="Try Crash, BeTomorrow, or music…" autocomplete="off"></div><div class="filter"><label for="year-filter">ExEn year</label><select id="year-filter"><option value="">All years</option>{yearopts}</select></div><div class="filter"><label for="genre-filter">Genre</label><select id="genre-filter"><option value="">All genres</option>{genreopts}</select></div><div class="filter"><label for="research-filter">Coverage</label><select id="research-filter"><option value="">All entries</option><option value="history">With development coverage</option><option value="credits">With personal credits</option><option value="listing">Catalog details</option></select></div><div class="filter"><label for="sort-by">Sort by</label><select id="sort-by"><option value="title">Title A–Z</option><option value="oldest">Oldest first</option><option value="newest">Newest first</option></select></div></div><div class="results-row"><span id="result-count" aria-live="polite">46 of 46 game entries</span><button class="reset-filters" id="reset-filters" type="button" hidden>Clear filters</button></div><div class="catalog-grid" id="game-list">{''.join(card(e) for e in catalog)}</div><p class="empty-state" id="no-results" hidden>No matching games. Try another name or clear the filters.</p><details class="catalog-data"><summary>Catalog scope and data downloads</summary><p>This collection began with 46 My Abandonware ExEn listings. Years normally follow those entries. Crash uses its documented 2002 French release; its later US listing is retained in the entry’s catalog details.</p><div class="buttons"><a class="btn btn-secondary" href="data/catalog.csv" download>Catalog CSV ↓</a><a class="btn btn-secondary" href="data/research.json" download>Histories &amp; credits JSON ↓</a><a class="btn btn-secondary" href="data/credits.csv" download>Contributor CSV ↓</a></div><a class="text-link" href="about/index.html">Methods and credits ↗</a></details></div></section>'''
    save('index.html', 'ExEn games and their history', 'An archive of ExEn games, original creators, development histories, images and sources.', home, active='catalog', scripts=('app.js',))

    for index, e in enumerate(catalog):
        gid, g = e['id'], games[e['id']]
        entry, refs = g['entry'], used(gid)
        blocks, toc = [], []
        def add(section_id, title, content):
            if not content:
                return
            toc.append((section_id, title))
            blocks.append(f'<section class="entry-section" id="{section_id}"><h2>{title}</h2>{content}</section>')
        primary = [m for m in g.get('media', []) if m.get('placement') == 'game']
        production = [m for m in g.get('media', []) if m.get('placement') == 'development']
        gallery = [m for m in g.get('media', []) if m.get('placement', 'gallery') == 'gallery']
        add('the-game', 'The game', paragraphs(entry['overview'], refs) + media(primary, refs))
        development = paragraphs(entry['development'], refs) + quotes(entry['quotes'], refs, 'development') + media(production, refs)
        add('development', 'Development', development)

        credits = defaultdict(list)
        for c in g['credits']:
            credits[c['name']].append(c)
        def rows(names):
            result = '<div class="people-list">'
            for name in names:
                work = credits[name]
                roles = ' · '.join(dict.fromkeys(c['role'] for c in work))
                teams = ' · '.join(dict.fromkeys(c['team'] for c in work if c['team'] != 'ExEn credits'))
                teamtext = f'<small>{h(teams)}</small>' if teams else ''
                result += f'<div class="person-row"><h3><a href="{person(name, "../../")}">{h(name)}</a></h3><div><p>{h(roles)}{cites([c["source"] for c in work], refs)}</p>{teamtext}</div></div>'
            return result + '</div>'
        creative = [n for n, cs in credits.items() if any(re.search(r'program|design|art|graphic|music|code|concept|gameplay', c['role'], re.I) for c in cs)]
        other = [n for n in credits if n not in creative]
        if len(credits) <= 8:
            creative, other = list(credits), []
        peoplebody = rows(creative) if creative else ''
        if other:
            peoplebody += f'<details class="more-credits"><summary>More credits ({len(other)})</summary>{rows(other)}</details>'
        if g['studio_roles']:
            studioitems = ''.join(f'<li><a href="{studio(s["name"], "../../")}">{h(s["name"])}</a><span>{h(s["role"])}{cites([s["source"]], refs)}</span></li>' for s in g['studio_roles'])
            peoplebody += f'<div class="studio-block"><h3>Studios and production</h3><ul class="studio-roles">{studioitems}</ul></div>'
        if gid == 'crash-bandicoot':
            peoplebody = '<p class="section-note">Participants in the December 2002 interview.</p>' + peoplebody
        add('creators', 'People', peoplebody)
        release_intro = [p for p in entry['release'] if not p.get('after_quote')]
        release_tail = [p for p in entry['release'] if p.get('after_quote')]
        add('reception', 'Release and reception', paragraphs(release_intro, refs) + quotes(entry['quotes'], refs, 'reception') + paragraphs(release_tail, refs))
        add('gallery', 'Gallery', '<div class="archive-gallery">' + media(gallery, refs) + '</div>' if gallery else '')
        toc.append(('sources', 'Sources'))
        blocks.append(bibliography(refs))
        if entry['notes']:
            blocks.append('<details class="record-notes"><summary>Edition and research notes</summary>' + paragraphs(entry['notes'], refs) + '</details>')
        facts = [('Catalogued ExEn year', e['year']), ('Genre', e['genre'] or 'Not recorded'), ('Listed developer', e['developer'] or 'Not recorded'), ('Listed publisher', e['publisher'] or 'Not recorded'), ('Research reviewed', date)]
        factrows = ''.join(f'<div><dt>{h(k)}</dt><dd>{h(v)}</dd></div>' for k, v in facts)
        blocks.append(f'<details class="record-notes"><summary>Catalog and original file details</summary><dl class="facts">{factrows}</dl><p><a href="{h(e["source_url"])}" target="_blank" rel="noopener noreferrer">Original game listing at My Abandonware ↗</a></p><p><strong>Not inspected for this archive.</strong> Original package integrity and present-day playability have not been tested as part of this research.</p></details>')
        related = []
        for othergame in catalog:
            shared = set(credits) & {c['name'] for c in games[othergame['id']]['credits']}
            if othergame['id'] != gid and shared:
                related.append((len(shared), othergame, sorted(shared)))
        related.sort(key=lambda item: (-item[0], item[1]['title']))
        if related:
            links = ''.join(f'<li><a href="{game(othergame, "../../")}">{h(othergame["title"])}</a><small>{h(", ".join(names[:2]))}{" and others" if len(names) > 2 else ""}</small></li>' for _, othergame, names in related[:3])
            blocks.append(f'<aside class="entry-related" aria-label="Other games with shared contributors"><h2>Also in this archive</h2><p>Games with contributors in common.</p><ul>{links}</ul></aside>')
        prev, following = catalog[(index - 1) % len(catalog)], catalog[(index + 1) % len(catalog)]
        blocks.append(f'<nav class="detail-links" aria-label="Adjacent games"><a href="{game(prev, "../../")}">← {h(prev["title"])}</a><a href="{game(following, "../../")}">{h(following["title"])} →</a></nav>')
        year = entry.get('display_year', str(e['year']))
        facts = entry.get('hero_facts', [('Developer', e['developer']), ('Publisher', e['publisher'])])
        quick = ''.join(f'<div><dt>{h(k)}</dt><dd>{h(v)}</dd></div>' for k, v in facts if v)
        quick_markup = f'<dl class="quick-facts">{quick}</dl>' if quick else ''
        herocites = cites(g['summary_sources'], refs)
        jumps = ''.join(f'<a href="#{sid}">{title}</a>' for sid, title in toc)
        body = f'<header class="shell detail-hero"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../../index.html">ExEn Archive</a><span aria-hidden="true">/</span><a href="../../index.html#catalog">Catalog</a><span aria-hidden="true">/</span><span aria-current="page">{h(e["title"])}</span></nav><div class="chips"><span class="chip">{h(year)}</span><span class="chip mint">ExEn</span></div><h1>{h(e["title"])}</h1><p class="detail-deck">{h(g["summary"])}{herocites}</p>{quick_markup}</header><div class="shell entry-layout"><nav class="entry-contents" aria-label="In this entry"><h2>In this entry</h2><div>{jumps}</div></nav><article class="game-entry" id="history">{"".join(blocks)}</article></div>{viewer()}'
        save(Path('games') / gid / 'index.html', e['title'], g['summary'], body, prefix='../../', scripts=('entry.js',))

    platform = research['platform']
    refs = list(dict.fromkeys([sid for p in platform for sid in p['sources']] + [q['source'] for p in platform for q in p.get('quotes', [])]))
    body = '<article class="narrow article platform-history"><div class="eyebrow">EXEN / PLATFORM HISTORY</div><h1>Making games for ExEn</h1><p class="lede">In-Fusio’s game platform, the phones it ran on, and the developers working with it.</p>'
    for p in platform:
        body += f'<section class="entry-section"><h2>{h(p["heading"])}</h2>' + paragraphs([p], refs) + quotes(p.get('quotes', []), refs, 'development') + '</section>'
    body += '<nav class="reading-routes" aria-label="Related game histories">' + ''.join(f'<a href="{game(entries[gid], "../")}">{h(entries[gid]["title"])} ↗</a>' for gid, _ in features) + '</nav>' + bibliography(refs) + '</article>'
    save('history/index.html', 'Platform history', 'The history of ExEn, In-Fusio, the handsets, developer tools and game distribution.', body, prefix='../', active='history')

    creatorcards = ''
    for name, work in sorted(people.items(), key=lambda item: slug(item[0])):
        roles = ' · '.join(dict.fromkeys(c['role'] for _, c in work))
        count = len({e['id'] for e, _ in work})
        items = ''.join(f'<li><a href="{game(e, "../")}#creators">{h(e["title"])}</a><span>{h(c["role"])} · <a href="{h(sources[c["source"]]["url"])}" target="_blank" rel="noopener noreferrer">source ↗</a></span></li>' for e, c in work)
        search = name + ' ' + roles + ' ' + ' '.join(e['title'] for e, _ in work)
        creatorcards += f'<article class="creator-card" id="person-{slug(name)}" data-search="{h(search)}"><span class="source-kind">{count} GAME{"S" if count != 1 else ""}</span><h2>{h(name)}</h2><p>{h(roles)}</p><details><summary>Games and contributions</summary><ul>{items}</ul></details></article>'
    studiocards = ''
    for name, work in sorted(studios.items(), key=lambda item: slug(item[0])):
        items = ''.join(f'<li><a href="{game(e, "../")}">{h(e["title"])}</a><span>{h(s["role"])} · <a href="{h(sources[s["source"]]["url"])}" target="_blank" rel="noopener noreferrer">source ↗</a></span></li>' for e, s in work)
        search = name + ' ' + ' '.join(e['title'] for e, _ in work)
        studiocards += f'<article class="creator-card" id="studio-{slug(name)}" data-search="{h(search)}"><span class="source-kind">STUDIO / ORGANISATION</span><h2>{h(name)}</h2><p>{len(work)} games</p><details><summary>Games and roles</summary><ul>{items}</ul></details></article>'
    body = f'<section class="shell index-hero"><div class="eyebrow">EXEN / CREATORS</div><h1>People and studios</h1><p class="lede">{len(people)} named contributors, with their roles and games.</p><div class="creator-tools" hidden><label for="creator-search">Find a person, role, game or studio</label><input id="creator-search" type="search" placeholder="Try Mathieu Thibaut or testing…"><span id="creator-count" aria-live="polite"></span></div><nav class="record-jumps" aria-label="Creator index sections"><a href="#people">People ({len(people)})</a><a href="#studios">Studios ({len(studios)})</a></nav></section><section class="shell creator-section" id="people"><h2>People</h2><div class="creator-grid">{creatorcards}</div></section><section class="shell creator-section" id="studios"><h2>Studios and organisations</h2><div class="creator-grid">{studiocards}</div><p id="creator-empty" class="empty-state" hidden>No matching people or studios.</p></section>'
    save('creators/index.html', 'Creators', 'ExEn programmers, artists, designers, composers, producers, testers and studios.', body, prefix='../', active='creators', scripts=('creators.js',))

    backrefs = defaultdict(set)
    for gid in games:
        for sid in used(gid):
            backrefs[sid].add(gid)
    body = f'<article class="shell article source-index"><div class="eyebrow">EXEN / SOURCES</div><h1>Sources</h1><p class="lede">{len(sources)} references for the games, people, images and platform history.</p><p>Research reviewed {h(date)}. Each game also has its own source list.</p><div class="source-register">'
    for kind in sorted({s['kind'] for s in sources.values()}):
        body += f'<section><h2>{h(kind)}</h2><ul>'
        for sid, s in sources.items():
            if s['kind'] != kind:
                continue
            links = ' '.join(f'<a href="{game(entries[gid], "../")}">{h(entries[gid]["title"])}</a>' for gid in sorted(backrefs[sid]))
            published = h(s['published']) + ' · ' if s.get('published') else ''
            note = f'<p>{h(s["note"])}</p>' if s.get('note') else ''
            body += f'<li id="source-{h(sid)}"><a href="{h(s["url"])}" target="_blank" rel="noopener noreferrer">{h(s["title"])}</a><small>{published}Reviewed {h(s["reviewed"])}</small>{note}<div class="source-backrefs">{links or "Platform history"}</div></li>'
        body += '</ul></section>'
    body += '</div><a class="btn btn-secondary" href="../data/research.json" download>Download histories and credits JSON ↓</a></article>'
    save('sources/index.html', 'Sources', 'Sources for ExEn game histories, creator credits, archival images and platform history.', body, prefix='../', active='sources')

    credited = sum(bool(g['credits']) for g in games.values())
    body = f'''<article class="narrow article"><div class="eyebrow">EXEN / METHODS &amp; CREDITS</div><h1>About the archive</h1><p class="lede">{h(research['premise'])}</p><section class="entry-section"><h2>The collection</h2><p>Wakka’s ExEn archive began with 46 games listed by My Abandonware. It brings together game descriptions, development accounts, personal credits, contemporary coverage and archival images. {credited} entries currently include named contributors.</p><p>All original game-page URLs have been retained. The collection is a starting point, rather than a complete ExEn release list.</p></section><section class="entry-section"><h2>Writing and attribution</h2><p>Direct quotations retain the source’s wording and name the speaker or writer. Translated quotations identify the translation. Summaries are written for this archive and link to their sources.</p><p>Credit records distinguish the ExEn adaptation from earlier games and other phone editions. The creator index contains selected roles from interviews and MobyGames credit transcriptions; it is not a complete staff directory.</p><p>Company announcements describe plans and availability at the time of publication. Later interviews are attributed recollections.</p></section><section class="entry-section"><h2>Images</h2><p>Historical images have captions, source links and reproduction or contributor credits. An ExEn screenshot is identified by its source platform label. Magazine images retain their publication references. Screenshots from a different version are not substituted for the ExEn game.</p></section><section class="entry-section"><h2>Dates and original files</h2><p>Catalog years refer to the ExEn entry in the source collection. Individual histories explain earlier releases or differences between editions. Crash, for example, has French magazine coverage from 2002–03 and a later US catalog listing.</p><p>No original game packages were downloaded, inspected, hashed or tested during this archive research. Original-file details stay separate from game history.</p></section><section class="entry-section"><h2>Source communities</h2><p>My Abandonware provides the original collection and platform-labelled image galleries. MobyGames supplies credit records, game descriptions and contributor indexes. Crash Bandicoot Zone reproduces and translates the <i>Mobiles Magazine</i> material. Other credited sources include Rare Gamer, Tomb Raider Chronicles, NoRecess, Dr JVtek and Terre de Jeux.</p><p>Individual entries identify additional reviewers, artists, publishers and researchers. Game files remain at their original source links.</p></section><section class="entry-section"><h2>Corrections and additions</h2><p><a href="{github}/issues/new?template=catalog-correction.yml">Send a correction or source</a> with the game title, edition and supporting reference. Wakka reviews changes before publication.</p></section><div class="buttons"><a class="btn btn-primary" href="../index.html#catalog">Browse the games</a><a class="btn btn-secondary" href="../sources/index.html">Sources</a></div></article>'''
    save('about/index.html', 'Methods and credits', 'Collection scope, writing, source attribution, images and original-file details.', body, prefix='../')
    save('404.html', 'Page not found', 'Find a game in the ExEn archive.', f'<section class="narrow article"><h1>Page not found</h1><p class="lede">Browse the catalog to find the game you were looking for.</p><a class="btn btn-primary" href="{base}">ExEn catalog →</a></section>', prefix=base)
    with (root / 'data/credits.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['game_id', 'game_title', 'person', 'role', 'team', 'scope', 'source_url'])
        writer.writeheader()
        for e in catalog:
            for c in games[e['id']]['credits']:
                writer.writerow(dict(game_id=e['id'], game_title=e['title'], person=c['name'], role=c['role'], team=c['team'], scope=c['scope'], source_url=sources[c['source']]['url']))
    paths = ['', 'about/', 'history/', 'creators/', 'sources/'] + ['games/' + e['id'] + '/' for e in catalog]
    (root / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{h(base + p)}</loc><lastmod>{date}</lastmod></url>\n' for p in paths) + '</urlset>\n', encoding='utf-8')
    print(f'Built 46 game entries, {len(people)} people, {len(studios)} studios, {len(sources)} sources and {len(paths) + 1} HTML pages.')
