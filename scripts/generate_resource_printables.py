"""Original deterministic puzzles and A4 football sheets. Never reads book interiors."""
import json,random,string
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfdoc import PDFString
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from resource_content import ROOT,SIX,EIGHT,ALL_RESOURCES
OUT=ROOT/'assets/resources'; OUT.mkdir(parents=True,exist_ok=True)
W,H=A4; M=44
ORIGIN='https://kyle-zerobaseduk.github.io/kd-publishing/'

def footer(c,slug,cluster):
 c.setFillColorRGB(0,0,0);c.setFont('Helvetica',8)
 c.drawString(M,30,'K.D.Publishing editorial · Version 1 · 9 October 2026')
 c.drawString(M,18,ORIGIN+f'resources/{cluster}/{slug}/')

def sheet(name,title,slug,cluster):
 c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=A4,invariant=1,pageCompression=1)
 c.setTitle(title);c.setAuthor('K.D.Publishing editorial');c._doc.Catalog.Lang=PDFString('en-GB')
 c.setFillColorRGB(0,0,0);c.setFont('Helvetica-Bold',20)
 lines=simpleSplit(title,'Helvetica-Bold',20,W-2*M)
 y=H-M
 for line in lines:c.drawString(M,y,line);y-=25
 footer(c,slug,cluster)
 return c,y-10

def para(c,text,y,size=11,width=None):
 c.setFont('Helvetica',size)
 for line in simpleSplit(text,'Helvetica',size,width or W-2*M):c.drawString(M,y,line);y-=size*1.35
 return y-7

def heading(c,text,y):
 c.setFont('Helvetica-Bold',13);c.drawString(M,y,text);return y-20

def make_puzzle(words,seed,n=15):
 # Forward-only directions; independent scanner validates all eight for ambiguity.
 for attempt in range(500):
  rng=random.Random(seed+attempt);grid=[['']*n for _ in range(n)];placed=[]
  for label in sorted(words,key=lambda x:-len(x.replace(' ',''))):
   word=label.replace(' ','');opts=[]
   for dr,dc in [(0,1),(1,0),(1,1)]:
    for row in range(n):
     for col in range(n):
      cells=[(row+k*dr,col+k*dc) for k in range(len(word))]
      if all(0<=r<n and 0<=c<n and grid[r][c] in ('',ch) for (r,c),ch in zip(cells,word)):opts.append((dr,dc,cells))
   if not opts:break
   dr,dc,cells=rng.choice(opts)
   for (r,c),ch in zip(cells,word):grid[r][c]=ch
   placed.append(dict(label=label,word=word,start=[cells[0][0]+1,cells[0][1]+1],end=[cells[-1][0]+1,cells[-1][1]+1],direction=[dr,dc],cells=[[r+1,c+1] for r,c in cells]))
  if len(placed)!=len(words):continue
  for row in grid:
   for i,ch in enumerate(row):
    if not ch:row[i]=rng.choice(string.ascii_uppercase)
  result={'size':n,'seed':seed+attempt,'grid':[''.join(row) for row in grid],'words':sorted(placed,key=lambda p:words.index(p['label']))}
  if all(len(find_all(result,p['word']))==1 for p in placed):return result
 raise ValueError('Could not place unique puzzle')

def find_all(data,word):
 n=data['size'];found=[]
 for r in range(n):
  for c in range(n):
   for dr in [-1,0,1]:
    for dc in [-1,0,1]:
     if not(dr or dc):continue
     cells=[(r+k*dr,c+k*dc) for k in range(len(word))]
     if all(0<=a<n and 0<=b<n for a,b in cells) and ''.join(data['grid'][a][b] for a,b in cells)==word:found.append([[a+1,b+1] for a,b in cells])
 return found

def puzzle_pdf(name,title,data,slug,solution=False):
 c,y=sheet(name,title,slug,'puzzles')
 y=para(c,'Read right, down or diagonally down-right. No backwards words. Ignore spaces.',y,11)
 if solution:y=para(c,'Rows count from the top; columns from the left. Grey paths mark all answers.',y,11)
 n=data['size'];cell=29;left=(W-n*cell)/2;top=y-8
 c.setFont('Helvetica',20)
 if solution:
  c.setStrokeColorRGB(.8,.8,.8);c.setLineWidth(17);c.setLineCap(1)
  for p in data['words']:
   (r1,c1),(r2,c2)=p['start'],p['end']
   c.line(left+(c1-.5)*cell,top-(r1-.5)*cell,left+(c2-.5)*cell,top-(r2-.5)*cell)
 c.setFillColorRGB(0,0,0)
 for r,row in enumerate(data['grid']):
  for col,ch in enumerate(row):c.drawCentredString(left+(col+.5)*cell,top-(r+.5)*cell-7,ch)
 y=top-n*cell-24
 if solution:
  c.setFont('Helvetica',10.5)
  for i,p in enumerate(data['words']):
   col=i//6;line=i%6
   c.drawString(M+col*255,y-line*19,f"{p['label']}: ({p['start'][0]},{p['start'][1]}) to ({p['end'][0]},{p['end'][1]})")
 else:
  c.setFont('Helvetica',18)
  for i,p in enumerate(data['words']):
   col=i//6;line=i%6;c.drawString(M+col*260,y-line*25,p['label'])
  c.setFont('Helvetica',9);c.drawString(M,60,'Free for personal / non-commercial group printing. Keep attribution; do not resell or rehost.')
 assert y-5*(19 if solution else 25)>65,(name,y)
 c.save()

specs=[('british-nostalgia',['MILK FLOAT','JUKEBOX','TELEGRAM','VINYL','THERMOS','JUMBLE SALE','PENNY','CARAVAN','LIDO','RECORD PLAYER','TYPEWRITER','POSTCARD'],2716,'British nostalgia','british-nostalgia-word-search-printable'),('christmas',['BAUBLES','TINSEL','CAROLS','MINCE PIES','CRACKERS','HOLLY','CANDLE','PUDDING','STOCKING','PRESENTS','WREATH','SNOWFLAKE'],8109,'Christmas word search','christmas-word-search-adults-printable')]
for name,words,seed,title,slug in specs:
 data=make_puzzle(words,seed)
 (ROOT/'content/resources'/f'{name}-grid.json').write_text(json.dumps(data,indent=2)+'\n')
 puzzle_pdf(name+'-puzzle',title,data,slug)
 puzzle_pdf(name+'-solution',title+' — answers',data,slug,True)

c,y=sheet('u8-small-squad-session-card','U8 small-squad session · 60 minutes','u8-small-squad-training-session','football')
y=para(c,'Five or six players (eight-player option). Focus: close control, finding space, deciding to dribble or pass. Timings include explanations, drinks and resets.',y)
y=heading(c,'Before children arrive',y)
y=para(c,'Size 3 ball each + two spares; 16 flat cones; two-colour bibs; watch; water. Start with a 20 × 15 m training area, six 1 m gates and four cone goals. Check surface, footwear, covered shin pads, supervision and emergency arrangements.',y)
for time,title,text in [('0–8','Arrival and ball warm-up','One ball each. Dribble, turn and stop. Gentle changes of speed; no laps or elimination.'),('8–20','Find a different gate','Everyone dribbles. Three short rounds; find a free gate. Widen gates or space if crowded.'),('20–23','Drink and demonstrate','Check comfort. Show the next game briefly; water is available throughout.'),('23–35','Keep it or share it','6: three pairs. 5: pair + trio. 8: four pairs. Pass or dribble through gates. Last 4 min optional opposition: 6 = two 2v1; 5 = 2v2 + helper; 8 = two 2v2. Rotate roles each minute.'),('35–38','Drink and reset','Keep four cone goals. Put spare balls with coach; supervise both areas if splitting.'),('38–55','Short games','5: 2v2 + rotating helper on team in possession. 6: 3v3. 8: two 2v2 games with adult support. Short bouts with recovery and role changes. Dribble through goals to score.'),('55–60','Slow finish and reflect','Gentle dribbling/walking. Ask: Where did you find space? Collect kit; agreed handover.')]:
 y=heading(c,time+' · '+title,y);y=para(c,text,y,10.5)
y=para(c,'Cues: little touches in traffic; look for a free gate; move after passing. Shorten or simplify for fatigue, cold, distress or confusion. Stop for injury. No heading, fitness punishments or forced repeated sprints.',y,10.5)
y=para(c,'Original editorial training plan, not FA-endorsed or field-tested with your group. England U7 match format is 3v3; U8 is 5v5 (2026/27). Suggested areas/timings are not match requirements. Full source notes and adaptations on the webpage.',y,9)
assert y>48,y;c.save()

c,y=sheet('first-session-checklist','First U7/U8 session · checklist','first-u7-u8-training-session-checklist','football')
for title,items in [('Before the day',['Confirm venue, time, surface, qualified support and club safeguarding / first-aid arrangements.','Tell families: named water, appropriate boots, covered shin pads and suitable clothing.','Check attendance, relevant needs privately, emergency contacts and collection procedure.','Pack a size 3 ball each, spares, flat cones, bibs and a watch.']),('Before play',['Walk the surface and run-off area; secure any portable goals.','Mark boundaries and a visible resting / drinking place. Count children in.','Assign adult duties for arrivals, late arrivals and any toilet / welfare needs.']),('A suggested first hour',['0–10: greet, learn names, free dribbling. 10–20: find a different gate.','20–25: drink and demonstrate. 25–35: pair / trio gate passing or dribbling.','35–40: drink and reset. 40–55: short 2v2 / 3v3 games.','55–60: reflect, collect kit and hand over using the club’s procedure.']),('During and after',['Show one action, give one cue and start. No heading practices.','Offer water / rest; simplify or stop for fatigue, cold, injury or distress.','Record one success, one difficulty and one next-session adjustment.'])]:
 y=heading(c,title,y)
 for text in items:c.rect(M,y-1,7,7);y=para(c,'     '+text,y,11)
y=para(c,'England 2026/27: U7 entry match format 3v3; U8 5v5. This checklist suggests training organisation, not an official fixture or FA-endorsed plan. Verify local and national-association requirements.',y,10)
y=heading(c,'Notes for next week',y)
for i in range(3):c.line(M,y,W-M,y);y-=25
assert y>48,y;c.save()

c,y=sheet('u8-rotation-template','U8 5v5 · adaptable rotation sheet','u8-5v5-substitution-rotation-guide','football')
y=para(c,'Match: __________________  Date: __________  Minutes: ____  Players: ____',y)
y=para(c,'Confirm competition rules, periods, referee permission and any additional-player arrangements. Optional plan; include goalkeeper time in totals.',y)
y=heading(c,'Plan windows; record what actually happens',y)
cols=[M,105,225,325,435,W-M];headers=['Window','5 playing','Resting','GK','Actual time']
c.setFont('Helvetica-Bold',10)
for i,h in enumerate(headers):c.drawString(cols[i]+4,y,h)
y-=12
for i in range(9):
 c.line(M,y,W-M,y)
 if i<8:
  for x in cols:c.line(x,y,x,y-32)
 y-=32
y-=5;y=heading(c,'Player-minute reconciliation (goalkeeper included)',y)
c.setFont('Helvetica-Bold',11);c.drawString(M,y,'Player name');c.drawString(235,y,'Planned minutes');c.drawString(370,y,'Actual minutes');y-=15
for i in range(8):c.line(M,y,W-M,y);y-=22
y=para(c,'Expected total = 5 × actual standard 5v5 match minutes. Adjust if numbers changed. Reasons / follow-up: ___________________________________________',y,10)
assert y>48,y;c.save()

c,y=sheet('u8-rotation-examples','U8 5v5 · checked worked examples','u8-5v5-substitution-rotation-guide','football')
y=para(c,'40-minute illustration only. Confirm actual periods and substitution rules. Obtain referee permission; adapt to children’s needs and record actual minutes.',y)
for label,rows in [('Six players · fewer changes',SIX),('Eight players · equal 25-minute shares',EIGHT)]:
 y=heading(c,label,y);c.setFont('Helvetica-Bold',11);c.drawString(M,y,'Minutes');c.drawString(150,y,'Playing (five children)');c.drawString(390,y,'Resting');y-=20
 c.setFont('Helvetica',12)
 for start,end,on,off in rows:c.drawString(M,y,f'{start}–{end}');c.drawString(150,y,' '.join(on));c.drawString(390,y,' '.join(off));y-=21
 y-=6
 if rows==SIX:y=para(c,'A/B: 40 minutes; C/D/E/F: 30 each. Total 200. Rotate full-match roles at the next comparable fixture. Optional GK: A first half; B second.',y,10.5)
 else:y=para(c,'A–H: 25 minutes each. Total 200. Optional 10-minute GK turns: D, A, B, C in that order. Goalkeeper minutes count towards each total.',y,10.5)
y=para(c,'The FA handbook recommends equal playing time where possible, at least 50% as best practice. Competition requirements must be checked. These tables are optional editorial plans, not FA-endorsed. A fixed full-game keeper changes the outfield-time arithmetic.',y,10)
assert y>48,y;c.save()
print('Generated 8 deterministic A4 PDFs and two unique puzzle grids')
