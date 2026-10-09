"""Build reviewable branch pages. Release mode priority exports only launch resources.

Owner approval is required before merge/deployment, never fabricated in content.
"""
import json,os,shutil
from resource_content import ALL_RESOURCES, CLUSTERS, ROOT,route

def selected():
 mode=os.environ.get('KD_RESOURCE_RELEASE',json.loads((ROOT/'content/resource-release.json').read_text())['mode'])
 if mode not in ('all','priority'): raise ValueError('KD_RESOURCE_RELEASE must be all or priority')
 return [r for r in ALL_RESOURCES if mode=='all' or r['priority']==1]

def render_resource(r):
 from build import e,titleblock,cards,BOOKS
 pre='../../../'
 body=f'<nav class="breadcrumbs container" aria-label="Breadcrumb"><a href="{pre}">Home</a> / <a href="../../">Resources</a> / <a href="../">{e(CLUSTERS[r["cluster"]])}</a> / <span>{e(r["title"])}</span></nav>'
 body+=titleblock(CLUSTERS[r['cluster']],r['title'],r['summary'])
 body+=f'<article class="container prose section resource-article"><p class="resource-byline">By {e(r["author"])} · Editorially reviewed <time datetime="{r["reviewedDate"]}">9 October 2026</time></p>'
 if r['downloads']:
  body+='<section class="resource-downloads" aria-labelledby="downloads"><h2 id="downloads">Free printables</h2>'
  for d in r['downloads']:
   size=(ROOT/d['path']).stat().st_size
   body+=f'<p><a class="text-link" href="{pre}{e(d["path"])}" data-resource-download="{e(r["slug"])}" data-asset-id="{e(d["path"].split("/")[-1])}">{e(d["label"])}</a><br><small>PDF · {max(1,round(size/1024))} KB · {e(d["printNotes"])}</small></p>'
  body+='<p>The PDF opens directly. You can then save or print it.</p></section>'
 for i,s in enumerate(r['sections']):
  body+=f'<section><h2 id="section-{i+1}">{e(s["heading"])}</h2>'
  body+=''.join(f'<p>{e(p)}</p>' for p in s['paragraphs'])
  if s.get('items'):body+='<ul>'+''.join(f'<li>{e(p)}</li>' for p in s['items'])+'</ul>'
  if s.get('table'):
   t=s['table'];body+=f'<div class="resource-table-wrap" tabindex="0" role="region" aria-label="{e(s["heading"])} table; scroll horizontally if needed"><table><caption>{e(s["heading"])}</caption><thead><tr>'+''.join(f'<th scope="col">{e(h)}</th>' for h in t['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{e(v)}</td>' for v in row)+'</tr>' for row in t['rows'])+'</tbody></table></div>'
  if r['slug']=='u8-small-squad-training-session' and i==1:
   body+='''<figure class="pitch-layout"><svg viewBox="0 0 480 330" role="img" aria-labelledby="pitch-title pitch-desc"><title id="pitch-title">Suggested gate-game layout</title><desc id="pitch-desc">A 20 by 15 metre training rectangle with six one-metre gates spread across it. All players dribble freely; there is no queue or assigned route.</desc><rect x="25" y="25" width="430" height="255" fill="#edf0e8" stroke="#18333c" stroke-width="2"/>'''+''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="#18333c"/><circle cx="{x+30}" cy="{y}" r="7" fill="#18333c"/>' for x,y in [(85,75),(290,75),(175,145),(355,165),(65,220),(260,235)])+'''<text x="240" y="310" text-anchor="middle" font-size="18" fill="#18333c">20 × 15 m · six gates · one ball each</text></svg><figcaption>Suggested starting layout, not an official match pitch. Move gates or enlarge the space if traffic builds up.</figcaption></figure>'''
  body+='</section>'
 if r['cluster']=='puzzles':body+='<section><h2>Using this free printable</h2><p>You may print copies for personal use and non-commercial community activity groups. Keep the attribution. Do not sell the files or upload them elsewhere; share this webpage so people can find the current version.</p></section>'
 if r['sources']:
  body+='<section><h2>Sources and rule checks</h2><p>Official guidance checked on 9 October 2026. The activities and planning examples are original editorial recommendations; they are not FA-endorsed.</p><ul>'+''.join(f'<li><a href="{e(s["url"])}">{e(s["label"])}</a></li>' for s in r['sources'])+'</ul></section>'
 related=[x for x in selected() if x['cluster']==r['cluster'] and x['slug']!=r['slug']]
 if related:
  body+='<section><h2>Related resources</h2><ul>'+''.join(f'<li><a href="../{x["slug"]}/">{e(x["title"])}</a></li>' for x in related)+'</ul></section>'
 body+='<p>Spotted an error or a printing problem? <a href="../../../contact/">Contact K.D.Publishing</a>.</p></article>'
 body+='<section class="container section"><div class="section-heading"><div><span class="eyebrow">Explore further</span><h2>Related books from K.D.Publishing</h2></div></div><p>These are our own books. View genuine interior samples before deciding whether they suit you.</p>'
 book_by_id={b['id']:b for b in BOOKS}
 # Simple contextual links keep the primary page focused on its resource.
 for bid in r['relatedBookIds']:
  b=book_by_id[bid];body+=f'<p><a class="text-link" href="{pre}books/{bid}/" data-related-book="{bid}" data-resource-id="{r["slug"]}">{e(b["shortTitle"])}</a> · View book details and interior samples</p>'
 return body+'</section>'

def build_resources():
 from build import shell,titleblock,e,url,BOOKS
 rows=selected()
 # Remove managed stale routes when making a priority-only release. Source records stay for later development.
 for r in ALL_RESOURCES:
  if r not in rows:
   dest=ROOT/route(r)
   if dest.parent.exists():shutil.rmtree(dest.parent)
   for d in r['downloads']:
    (ROOT/d['path']).unlink(missing_ok=True)
 for cluster,label in CLUSTERS.items():
  subset=[r for r in rows if r['cluster']==cluster]
  main=titleblock('Free resources',label,'Practical resources to use today, with optional links to relevant books.')+'<section class="container prose section resource-article">'+''.join(f'<section><h2><a href="{r["slug"]}/">{e(r["title"])}</a></h2><p>{e(r["summary"])}</p></section>' for r in subset)+'</section>'
  shell(f'resources/{cluster}/index.html',label,f'Browse K.D.Publishing {label.lower()}: original guides and useful free printables.',main)
 main=titleblock('Useful things, freely available','Resources','Football session plans, printable puzzles and thoughtful workplace gift advice. Use each resource without buying a book.')+'<section class="container prose section resource-article">'+''.join(f'<section><h2><a href="{cluster}/">{e(label)}</a></h2><ul>'+''.join(f'<li><a href="{cluster}/{r["slug"]}/">{e(r["title"])}</a></li>' for r in rows if r['cluster']==cluster)+'</ul></section>' for cluster,label in CLUSTERS.items())+'</section>'
 shell('resources/index.html','Free resources: football, puzzles and gifts','Explore original football coaching guides, free A4 word searches with answers and practical workplace gift advice from K.D.Publishing.',main)
 for r in rows:
  canonical=url(route(r)); crumbs=[('Home',url('')),('Resources',url('resources/')),(CLUSTERS[r['cluster']],url(f'resources/{r["cluster"]}/')),(r['title'],canonical)]
  # No claimed publication date while content remains awaiting owner release.
  schemas=[{'@context':'https://schema.org','@type':'Article','headline':r['title'],'description':r['summary'],'inLanguage':'en-GB','url':canonical,'mainEntityOfPage':canonical,'author':{'@type':'Organization','name':'K.D.Publishing editorial'},'publisher':{'@type':'Organization','name':'K.D.Publishing'}},{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i,'name':n,'item':u} for i,(n,u) in enumerate(crumbs,1)]}]
  structured=''.join('<script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('<','\\u003c')+'</script>' for s in schemas)
  shell(route(r),r['seoTitle'],r['description'],render_resource(r),resource={'id':r['slug'],'cluster':r['cluster']},extra_structured=structured)
 return ['resources/index.html']+[f'resources/{c}/index.html' for c in CLUSTERS]+[route(r) for r in rows]

def book_resources(bid,pre):
 from build import e
 rows=[r for r in selected() if bid in r['relatedBookIds']]
 if not rows:return ''
 return '<section class="container section book-resources"><h2>Free related resources</h2><ul>'+''.join(f'<li><a href="{pre}{route(r).removesuffix("index.html")}">{e(r["title"])}</a></li>' for r in rows)+'</ul></section>'
