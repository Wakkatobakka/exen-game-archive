"""One-time, manually source-verified index seed. See data/SOURCES.md."""
import json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[
('007 Ice Racer',2002,'007-ice-racer-yy3'),
('Age of Empires II Mobile',2005,'age-of-empires-ii-mobile-wh8'),
('Arthur & Les: Pirates',2005,'arthur-les-pirates-yz6'),
("Banjo-Kazooie: Grunty's Revenge Missions",2005,'banjo-kazooie-grunty-s-revenge-missions-yz7'),
('Bomb Jack',2003,'bomb-jack-5h4'),
('Bomb Squad',2006,'bomb-squad-yy5'),
('Charmed',2003,'charmed-yy6'),
('Crash Bandicoot',2005,'crash-bandicoot-yy7'),
('Crazy Cobra 2',2004,'crazy-cobra-2-yy8'),
('Eagle Squadron',2004,'eagle-squadron-yy9'),
('Fighter Pilot Evolved',2006,'fighter-pilot-evolved-yya'),
("Flynn's Adventures",2004,'flynn-s-adventures-w8u'),
('Football Fans',2005,'football-fans-yz8'),
('Ghost Hunter',2004,'ghost-hunter-yyc'),
('I.F. Ski Jumping',2005,'i-f-ski-jumping-yyd'),
('IF Extreme Ski',2006,'if-extreme-ski-yye'),
('IF Ping Pong',2006,'if-ping-pong-yyf'),
('IF Racing',2002,'if-racing-yyg'),
('IF Racing 2',2004,'if-racing-2-yz9'),
('IF Reversi',2006,'if-reversi-yyq'),
('IF Sudoku',2006,'if-sudoku-yza'),
('Jungle Run',2004,'jungle-run-yyh'),
('Malibu Ride 2',2006,'malibu-ride-2-yyi'),
('Midtown Madness 3 Mobile',2005,'midtown-madness-3-mobile-w4l'),
('Monkey Business',2006,'monkey-business-yyk'),
('MotoGP',2005,'motogp-w42'),
('Mutant Alert',2003,'mutant-alert-yym'),
('Panko',2001,'panko-yyn'),
('Pikubi',2004,'pikubi-yyo'),
('Pikubi 2: Rainbow Attack!',2006,'pikubi-2-rainbow-attack-yyp'),
('Sexy Breaker Bikini',2005,'sexy-breaker-bikini-yzb'),
('SexyBreaker Manga',2005,'sexybreaker-manga-yys'),
('Shado Fighter',2004,'shado-fighter-vz1'),
('South Park',2003,'south-park-yyu'),
('Sphere Madness',2004,'sphere-madness-yyv'),
('Sphere Madness 2',2006,'sphere-madness-2-yyw'),
('Spyro',2003,'spyro-yyx'),
('Star Wars: Revenge of the Sith',2005,'star-wars-revenge-of-the-sith-yyy'),
('The Terminator',2003,'the-terminator-vgm'),
('Tomb Raider: Elixir of Life',2005,'tomb-raider-elixir-of-life-vgb'),
('Tomb Raider: Quest for Cinnabar',2005,'tomb-raider-quest-for-cinnabar-vge'),
('Tomb Raider: The Osiris Codex',2004,'tomb-raider-the-osiris-codex-vga'),
('Tour De France',2005,'tour-de-france-vfh'),
('Worms',2005,'worms-ve7'),
('X-Mas: Tales',2004,'x-mas-tales-yzc'),
('Zoo Tycoon 2 Mobile',2005,'zoo-tycoon-2-mobile-vel'),
]
assert len(rows)==46
# These additional facts were specifically checked on the linked game pages,
# rather than assumed from the franchise/genre. No original descriptions copied.
extras={
'007 Ice Racer':dict(genre='Action / Racing',publisher='In-Fusio',developer='In-Fusio',note='An early licensed driving/action game listed for ExEn.'),
'Age of Empires II Mobile':dict(genre='Strategy',publisher='In-Fusio',developer='In-Fusio',note='A separately listed ExEn version of the mobile strategy adaptation.'),
"Banjo-Kazooie: Grunty's Revenge Missions":dict(genre='Action / Mini-games',publisher='In-Fusio',developer='Rare, Ltd.',note='A Banjo-Kazooie mini-game release with an ExEn edition listed alongside J2ME.'),
'Bomb Jack':dict(publisher='In-Fusio',note='The source lists an ExEn edition among several different platform versions.'),
'Crash Bandicoot':dict(genre='Action / Platform',publisher='In-Fusio',developer='Kaolink SAS',note='A side-scrolling Crash adaptation developed for the ExEn phone ecosystem.'),
'IF Extreme Ski':dict(genre='Sports',publisher='In-Fusio',developer='Devalley Entertainment',note='A skiing and stunt-focused sports title cataloged for ExEn.'),
'IF Ping Pong':dict(genre='Sports',publisher='In-Fusio',developer='In-Fusio',note='An ExEn table-tennis game from the later years represented in this index.'),
'Midtown Madness 3 Mobile':dict(publisher='In-Fusio',developer='BeTomorrow',note='An ExEn edition documented separately from the J2ME versions.'),
'Mutant Alert':dict(genre='Action / Shooter',publisher='In-Fusio',developer='In-Fusio',note='A first-person shooter entry listed for the ExEn platform.'),
'Pikubi 2: Rainbow Attack!':dict(genre='Action / Platform',publisher='In-Fusio',developer='Devalley Entertainment',note='Also listed under the alternate title GoGo 2: Rainbow Attack!.'),
'South Park':dict(genre='Action / Mini-games',publisher='In-Fusio',developer='In-Fusio',note='A licensed mini-game release with an ExEn version listed alongside J2ME.'),
'Tomb Raider: The Osiris Codex':dict(genre='Action / Platform',publisher='Eidos Interactive Limited',developer='IOMO',note='The ExEn edition is listed for 2004, distinct from an earlier J2ME release.'),
}

def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode('ascii').lower()
    return re.sub(r'-+','-',re.sub('[^a-z0-9]+','-',s)).strip('-')

entries=[]
for i,(title,year,page_slug) in enumerate(rows,1):
    d={
      'id':slug(title),
      'title':title,'year':year,'platform':'ExEn',
      'genre':None,'publisher':None,'developer':None,'note':None,
      'source_name':'My Abandonware',
      'source_url':'https://www.myabandonware.com/game/'+page_slug,
      'source_collection_url':'https://www.myabandonware.com/browse/platform/exen/',
      'source_reviewed':'2026-10-29',
      'evidence_level':'catalog-listing',
      'package_inspected':False,'package_filename':None,'package_size_bytes':None,
      'sha256':None,'runtime_tested':False,'runtime_result':None,
    }
    d.update(extras.get(title,{}))
    entries.append(d)
assert len({e['id'] for e in entries})==46
(ROOT/'data/catalog.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Seeded',len(entries),'documented ExEn listings')
