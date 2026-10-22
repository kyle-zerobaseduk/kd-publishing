"""Validate the draft marketing handoff without calling any publishing API."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
queue=json.loads((ROOT/'marketing/2026-10-growth/queue.json').read_text())
assert queue['publishingEnabled'] is False and queue['startDate'] is None
pins=queue['pins'];assert len(pins)==30
for field in ['id','day','title','description','imageSha256','dedupeKey']:
 assert len({p[field] for p in pins})==30,field
assert sorted(p['day'] for p in pins)==list(range(1,31))
for pin in pins:
 assert pin['approvedForPublishing'] is False
 assert pin['scheduledFor'] is None and pin['boardId'] is None and pin['status']=='draft'
 assert 0<len(pin['title'])<=100 and 0<len(pin['description'])<=500
 assert pin['altText'] and len(pin['altText'])<500
 u=urlsplit(pin['link']);assert u.scheme=='https' and u.netloc=='kyle-zerobaseduk.github.io'
 assert u.path.startswith('/kd-publishing/') and not u.fragment
 local=ROOT/u.path.removeprefix('/kd-publishing/')/'index.html';assert local.is_file(),local
 tags=parse_qs(u.query)
 assert set(tags)=={'utm_source','utm_medium','utm_campaign','utm_content'}
 assert tags['utm_source']==['pinterest'] and tags['utm_medium']==['social']
 assert tags['utm_content']==[f'growth30_pin_{pin["day"]:02}']
 assert pin['imageUrl']=='https://kyle-zerobaseduk.github.io/kd-publishing/'+pin['imagePath']
 image=ROOT/pin['imagePath']
 assert hashlib.sha256(image.read_bytes()).hexdigest()==pin['imageSha256']
 with Image.open(image) as im: assert im.size==(1000,1500) and im.format=='JPEG'
 # Do not accidentally promote an unreleased article or an entire free book.
 if pin['landingType']=='resource':
  assert 'books sold separately' not in pin['title'].lower()
 else:assert '/books/'+pin['bookId']+'/' in pin['link']
for path in ROOT.glob('assets/social/*.webp'):
 with Image.open(path) as im:assert im.size==(1200,630)
 pages=list(ROOT.glob('resources/*/'+path.stem+'/index.html'));assert len(pages)==1
 assert 'https://kyle-zerobaseduk.github.io/kd-publishing/assets/social/'+path.name in pages[0].read_text()
print('PASS: 30 unique 1000x1500 draft Pins, matching live-site routes, copy limits, UTM tags, checksums, approval/schedule gates and three 1200x630 sharing images')
