"""Build exact vector campaign layouts from approved site assets; no API calls.

Requires Pillow and Node sharp. Run with NODE_PATH pointing to installed modules.
Never connects to Pinterest or changes a scheduler. Every output remains a draft.
"""
import base64
import hashlib
import io
import json
import subprocess
import textwrap
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from PIL import Image, ImageFont
from book_assets import cover_path, preview_path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'marketing/2026-10-growth'
ASSETS = ROOT / 'assets/campaigns/2026-10-growth'
SOCIAL = ROOT / 'assets/social'
ORIGIN = 'https://kyle-zerobaseduk.github.io/kd-publishing/'
BOOKS = {b['id']: b for b in json.loads((ROOT/'catalogue/books.json').read_text())}
TOPICS = {
 'football': ('first-time-football-coach', 'football/u8-small-squad-training-session', 'small_squad_session_2026', '#173e35', '#eaf0df', 'Grassroots football coaching'),
 'nostalgia': ('british-nostalgia', 'puzzles/british-nostalgia-word-search-printable', 'nostalgia_printable_2026', '#173d48', '#f5ecd6', 'British nostalgia and word searches'),
 'humour': ('i-deleted-the-honest-version', 'workplace-humour/secret-santa-gifts-work-colleagues-uk', 'secret_santa_2026', '#4b2930', '#fae4dc', 'Work colleague gift ideas'),
 'christmas': ('cozy-christmas-word-search', None, 'christmas_puzzles_2026', '#234738', '#f1eddf', 'Christmas puzzles and gifts'),
 'dementia': ('easy-word-search-for-dementia', None, 'gentle_word_search_2026', '#193c59', '#fff3d0', 'Large-print word searches')
}

def text(x, y, value, size=32, color='#18333c', weight='normal', family='DejaVu Sans'):
 return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'

def lines(x,y,value,width,size,color,weight='normal',leading=1.18,max_width=None):
 rows=textwrap.wrap(value,width=width,break_long_words=False)
 if max_width:
  font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if weight=='bold' else '')+'.ttf',size)
  rows=[];row=''
  for word in value.split():
   candidate=(row+' '+word).strip()
   if row and font.getlength(candidate)>max_width:rows.append(row);row=word
   else:row=candidate
  if row:rows.append(row)
  assert all(font.getlength(row)<=max_width for row in rows)
 return ''.join(text(x,y+i*size*leading,row,size,color,weight) for i,row in enumerate(rows)),y+len(rows)*size*leading

def image(path,x,y,w,h):
 with Image.open(ROOT/path) as im:
  buffer=io.BytesIO();im.convert('RGB').save(buffer,format='PNG')
 data=base64.b64encode(buffer.getvalue()).decode()
 return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'

def grid(x,y,cell=31):
 data=json.loads((ROOT/'content/resources/british-nostalgia-grid.json').read_text())
 return ''.join(text(x+c*cell,y+r*cell,ch,cell*.65,'#18333c',family='DejaVu Sans Mono') for r,row in enumerate(data['grid']) for c,ch in enumerate(row))

def pitch(x,y,w,h):
 s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#eaf0df" stroke="#173e35" stroke-width="3"/>'
 for dx,dy in [(0.16,.22),(.64,.22),(.38,.48),(.79,.62),(.12,.78),(.58,.85)]:
  for offset in [0,32]:s+=f'<circle cx="{x+dx*w+offset}" cy="{y+dy*h}" r="8" fill="#173e35"/>'
 return s

def render(svg,dest):
 script="const sharp=require('sharp');const fs=require('fs');const s=sharp(fs.readFileSync(0));(process.argv[1].endsWith('.webp')?s.webp({quality:90}):s.jpeg({quality:91,mozjpeg:true})).toFile(process.argv[1]).catch(e=>{console.error(e);process.exit(1)});"
 subprocess.run(['node','-e',script,str(dest)],input=svg.encode(),check=True)

def pin_svg(topic,kind,headline,n):
 bid,resource,campaign,ink,paper,board=TOPICS[topic];book=BOOKS[bid]
 dark=n%3==0; bg=ink if dark else paper; fg=paper if dark else ink
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1500" viewBox="0 0 1000 1500"><rect width="1000" height="1500" fill="{bg}"/>'
 s+=text(65,80,'K.D.PUBLISHING',26,fg,'bold')
 label='FREE PRINTABLE' if kind=='resource' and topic!='humour' else 'FREE GIFT GUIDE' if kind=='resource' else 'LOOK INSIDE THE BOOK'
 s+=text(65,150,label,23,fg)
 title,end=lines(65,245,headline,23,68,fg,'bold',max_width=870);s+=title
 assert end<540,(headline,end)
 s+=f'<rect x="65" y="540" width="870" height="655" rx="18" fill="#ffffff"/>'
 if kind=='resource' and topic=='nostalgia':
  s+=text(115,599,'From the original free puzzle',26,ink)
  s+=grid(250,650,34)
  s+=text(115,1160,'A4 puzzle + separate answers',27,ink)
 elif kind=='resource' and topic=='football':
  s+=text(115,605,'60 minutes. Five, six or eight players.',29,ink,'bold')
  s+=pitch(125,655,750,350)
  for i,t in enumerate(['Dribbling gates · passing choices','Small-sided games · calm finish','Free A4 session card']):s+=text(115,1060+i*47,t,30,ink)
 elif kind=='resource' and topic=='humour':
  for i,t in enumerate(['01   Start with the person','02   Check the agreed budget','03   Think about the setting','04   Keep the joke comfortable']):s+=text(115,650+i*106,t,32,ink,'bold')
  s+=text(115,1135,'A free guide from K.D.Publishing',29,ink)
 else:
  if n%2:
   s+=image(cover_path(book),145,572,710,590)
  else:
   s+=image(cover_path(book),95,605,350,520)
   s+=image(preview_path(book,book['previewPages'][0]),475,580,425,555)
   s+=text(480,1160,'Actual interior sample',22,ink)
 sub='Download the free puzzle + answers' if kind=='resource' and topic=='nostalgia' else 'Read the plan. Save the session card.' if kind=='resource' and topic=='football' else 'Read the free colleague-gift guide' if kind=='resource' else 'Explore genuine pages before you buy'
 s+=text(65,1270,sub,33,fg,'bold')
 s+=text(65,1325,'Visit the K.D.Publishing website',27,fg)
 if kind=='resource':s+=text(65,1380,'Free resource · related books sold separately',22,fg)
 else:s+=text(65,1380,'Paperback · Amazon UK link on the book page',22,fg)
 s+=f'<path d="M65 1420 H935" stroke="{fg}" stroke-width="1"/>'
 s+=text(65,1460,'BOOKS TO EXPLORE. REAL PAGES TO PREVIEW.',20,fg)
 return s+'</svg>'

def social_svg(topic):
 bid,resource,campaign,ink,paper,board=TOPICS[topic]
 title={'football':'Free U8 small-squad session','nostalgia':'Free British nostalgia word search','humour':'Secret Santa gifts for colleagues'}[topic]
 detail={'football':'60-minute plan + A4 session card','nostalgia':'Original A4 puzzle + separate answers','humour':'A practical UK guide to choosing well'}[topic]
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><rect width="1200" height="630" fill="{paper}"/>'
 s+=text(55,75,'K.D.PUBLISHING',25,ink,'bold')
 t,end=lines(55,195,title,21,54,ink,'bold',max_width=615);s+=t
 t,end=lines(55,450,detail,28,29,ink,max_width=615);s+=t
 s+=text(55,575,'Free resource · books sold separately',22,ink)
 s+='<rect x="725" y="75" width="420" height="480" rx="16" fill="#fff"/>'
 if topic=='nostalgia':s+=grid(764,135,24)
 elif topic=='football':
  s+=pitch(750,120,365,320);s+=text(762,500,'Five, six or eight players',24,ink)
 else:
  for i,t in enumerate(['The person','The budget','The setting','The right tone']):s+=text(765,170+i*100,t,32,ink,'bold')
 return s+'</svg>'

def main():
 brief=json.loads((FOLDER/'brief.json').read_text());ASSETS.mkdir(parents=True,exist_ok=True);SOCIAL.mkdir(exist_ok=True)
 rows=[]
 for n,(topic,kind,headline,title,description) in enumerate(brief['pins'],1):
  bid,resource,campaign,ink,paper,board=TOPICS[topic]
  asset=f'assets/campaigns/2026-10-growth/pin-{n:02}.jpg';render(pin_svg(topic,kind,headline,n),ROOT/asset)
  path=f'resources/{resource}/' if kind=='resource' else f'books/{bid}/'
  url=ORIGIN+path+'?'+urlencode(dict(utm_source='pinterest',utm_medium='social',utm_campaign=campaign,utm_content=f'growth30_pin_{n:02}'))
  alt=f'{headline} {"Free resource from" if kind=="resource" else "Cover and/or genuine interior preview from"} '+('K.D.Publishing.' if kind=='resource' else BOOKS[bid]['title']+'.')
  digest=hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()
  rows.append(dict(id=f'KD30-{n:02}',day=n,topic=topic,bookId=bid,landingType=kind,title=title,description=description,altText=alt,link=url,imageUrl=ORIGIN+asset,imagePath=asset,imageSha256=digest,boardTheme=board,boardId=None,scheduledFor=None,approvedForPublishing=False,status='draft',dedupeKey=hashlib.sha256((url.split('?')[0]+digest+' '.join(title.casefold().split())).encode()).hexdigest()))
 for topic in ['football','nostalgia','humour']:
  slug=TOPICS[topic][1].split('/')[-1];render(social_svg(topic),SOCIAL/(slug+'.webp'))
 manifest={k:v for k,v in brief.items() if k!='pins'};manifest['pins']=rows
 (FOLDER/'queue.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 md=['# 30-day Pinterest calendar','', 'Draft only. Day 1 is the first owner-approved publishing day. No dates or schedules have been activated. Start with one distinct Pin per day; review at days 7, 14, 21 and 30. Board themes are suggestions, not verified board IDs.','', '| Day | Pin | Topic | Title | Destination |','| --- | --- | --- | --- | --- |']
 md += [f'| {r["day"]} | {r["id"]} | {r["topic"]} | {r["title"]} | [{r["landingType"]}]({r["link"]}) |' for r in rows]
 md+=['','## Copy and alt text','']
 for r in rows:
  md += [f'### {r["id"]}: {r["title"]}','',r['description'],'',f'Alt text: {r["altText"]}','',f'Image: {r["imageUrl"]}','',f'Destination: {r["link"]}','']
 (FOLDER/'calendar.md').write_text('\n'.join(md)+'\n')
 print(f'Built {len(rows)} draft Pins, three resource sharing images, JSON queue and readable calendar; no external publishing.')

if __name__=='__main__':main()
