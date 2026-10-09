"""Resource content shared by HTML, printables and validators. No publication approval implied."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLUSTERS={'football':'Grassroots football coaching','puzzles':'Word searches & puzzles','workplace-humour':'Workplace humour & gifts'}
ALL_RESOURCES=sorted([json.loads(p.read_text()) for p in (ROOT/'content/resources').glob('*.json') if not p.name.endswith('-grid.json')],key=lambda r:(r['priority'],r['cluster'],r['slug']))
def route(r): return f"resources/{r['cluster']}/{r['slug']}/index.html"
SIX=[(0,10,'ABDEF','C'),(10,20,'ABCEF','D'),(20,30,'ABCDF','E'),(30,40,'ABCDE','F')]
EIGHT=[(i*5,(i+1)*5,*pair) for i,pair in enumerate([('DEFGH','ABC'),('AEFGH','BCD'),('ABFGH','CDE'),('ABCGH','DEF'),('ABCDH','EFG'),('ABCDE','FGH'),('BCDEF','GHA'),('CDEFG','HAB')])]
