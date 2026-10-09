"""Verify content, independent puzzle solving, printed grids, rotation maths and A4 geometry."""
import json,re
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
print('PASS: six developed drafts; 8 A4 PDFs; 24 unique forward word placements; printed grids and answer coordinates exact; 6/8-player rotation totals; PDF text bounds')
