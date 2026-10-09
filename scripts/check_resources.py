"""Verify content, independent puzzle solving, printed grids, rotation maths and A4 geometry."""
import json,re
from pathlib import Path
from collections import Counter
from pypdf import PdfReader
from resource_content import ROOT,ALL_RESOURCES,SIX,EIGHT,route
from build_resources import selected
assert len(ALL_RESOURCES)==6 and sum(r['priority']==1 for r in ALL_RESOURCES)==3
for r in selected():
 assert r['ownerApproved'] is False # Review drafts never masquerade as owner approval.
 markup=(ROOT/route(r)).read_text()
 assert 'data-resource' in markup or not r['downloads']
 assert len(r['sections'])>=5 and len(r['relatedBookIds']) in [1,2]
 assert r['seoTitle']+' | K.D.Publishing' in markup or '&amp;' in markup
 for d in r['downloads']:
  p=ROOT/d['path'];reader=PdfReader(p)
  assert len(reader.pages)==1 and not reader.is_encrypted
  page=reader.pages[0];w,h=map(float,[page.mediabox.width,page.mediabox.height])
  assert abs(w-595.276)<.01 and abs(h-841.89)<.01
  text=page.extract_text();assert 'K.D.Publishing editorial' in text and r['slug'] in text
  assert p.stat().st_size<100_000
for name in [n for n in ['british-nostalgia','christmas'] if any(n in r['slug'] for r in selected())]:
 data=json.loads((ROOT/f'content/resources/{name}-grid.json').read_text());grid=data['grid'];n=data['size']
 assert len(grid)==n==15 and all(re.fullmatch('[A-Z]{15}',row) for row in grid)
 puzzle=PdfReader(ROOT/f'assets/resources/{name}-puzzle.pdf').pages[0]
 solution=PdfReader(ROOT/f'assets/resources/{name}-solution.pdf').pages[0]
 def printed_grid(page):
  chars=[]
  def visit(text,cm,tm,font,size):
   if size==20 and re.fullmatch(r'[A-Z]\s*',text):chars.append(text.strip())
  page.extract_text(visitor_text=visit)
  return ''.join(chars)
 assert printed_grid(puzzle)==printed_grid(solution)==''.join(grid),name
 for item in data['words']:
  word=item['word'];hits=[]
  # Independent exhaustive scan, including forbidden directions, to catch unlisted duplicates.
  for row in range(n):
   for col in range(n):
    for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
     coords=[(row+k*dy,col+k*dx) for k in range(len(word))]
     if all(0<=y<n and 0<=x<n for y,x in coords) and ''.join(grid[y][x] for y,x in coords)==word:hits.append([[y+1,x+1] for y,x in coords])
  assert hits==[item['cells']],(name,word,hits)
  assert item['start']==item['cells'][0] and item['end']==item['cells'][-1]
  assert item['direction'] in [[0,1],[1,0],[1,1]]
  txt=solution.extract_text();assert f"{item['label']}: ({item['start'][0]},{item['start'][1]}) to ({item['end'][0]},{item['end'][1]})" in txt
  sizes=[]
  puzzle.extract_text(visitor_text=lambda t,cm,tm,font,size:sizes.append(size) if item['label'] in t else None)
  assert 18 in sizes,(item['label'],sizes)
 assert {p['label'] for p in data['words']}=={p for r in ALL_RESOURCES if r['cluster']=='puzzles' and name in r['slug'] for s in r['sections'] for p in s.get('items',[])}
for rows,players,expected in [(SIX,'ABCDEF',[40,40,30,30,30,30]),(EIGHT,'ABCDEFGH',[25]*8)]:
 totals=Counter()
 for start,end,on,off in rows:
  assert len(set(on))==5 and not set(on)&set(off) and set(on+off)==set(players)
  for player in on:totals[player]+=end-start
 assert [totals[p] for p in players]==expected and sum(totals.values())==200
 r=next(r for r in ALL_RESOURCES if 'rotation-guide' in r['slug'])
 tables=[s['table'] for s in r['sections'] if s.get('table')]
 table=tables[0] if len(players)==6 else tables[1]
 assert table['rows']==[[f'{a}–{b}',' '.join(on),' '.join(off)] for a,b,on,off in rows]
# Coordinate bounds on every text run; keep footer distinct from body.
for pdf in (ROOT/'assets/resources').glob('*.pdf'):
 reader=PdfReader(pdf)
 def bounds(t,cm,tm,font,size):
  if t.strip():assert 15<=tm[4]<=550 and 10<=tm[5]<=800,(pdf,t,tm)
 for p in reader.pages:p.extract_text(visitor_text=bounds)
for r in ALL_RESOURCES:
 if r['slug'] in ('u8-small-squad-training-session','first-u7-u8-training-session-checklist'):
  times=next(s['table']['rows'] for s in r['sections'] if s.get('table'))
  windows=[tuple(map(int,re.match(r'(\d+)–(\d+)',row[0]).groups())) for row in times]
  assert windows[0][0]==0 and windows[-1][1]==60
  assert all(a[1]==b[0] for a,b in zip(windows,windows[1:]))
  assert sum(b-a for a,b in windows)==60
print(f'PASS: {len(selected())} selected developed drafts; {sum(len(r["downloads"]) for r in selected())} A4 PDFs; unique forward word placements, printed grids and answer coordinates exact; rotation totals; 60-minute schedules; PDF text bounds')

# Selected release must contain exactly its articles, non-empty hubs and downloads.
from html.parser import HTMLParser
from xml.etree import ElementTree
chosen=selected()
expected_routes={'resources/','resources/football/','resources/puzzles/','resources/workplace-humour/'}|{str(Path(route(r)).parent)+'/' for r in chosen}
assert {str(p.parent.relative_to(ROOT))+'/' for p in (ROOT/'resources').rglob('index.html')}==expected_routes
assert {p.relative_to(ROOT).as_posix() for p in (ROOT/'assets/resources').glob('*.pdf')}=={d['path'] for r in chosen for d in r['downloads']}
assert all(any(r['cluster']==cluster for r in chosen) for cluster in ('football','puzzles','workplace-humour'))
class LinkScope(HTMLParser):
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   for key,value in attrs:
    if key=='href':assert not any(r['slug'] in value for r in ALL_RESOURCES if r not in chosen),(self.page,value)
for p in ROOT.rglob('index.html'):
 parser=LinkScope();parser.page=p;parser.feed(p.read_text())
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
sitemap=[n.text for n in ElementTree.parse(ROOT/'sitemap.xml').findall('.//s:loc',ns)]
expected={'https://kyle-zerobaseduk.github.io/kd-publishing/'+p.relative_to(ROOT).as_posix().removesuffix('index.html') for p in ROOT.rglob('index.html')}
assert len(sitemap)==len(expected) and set(sitemap)==expected
print(f'PASS exact release scope: {len(chosen)} articles, 4 non-empty hubs, {len([d for r in chosen for d in r["downloads"]])} downloads; no unreleased links; sitemap equals canonical page set')
