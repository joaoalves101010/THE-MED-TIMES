from edition_config import CONFIG,EDITION_ID,EDITION_LABEL,DATE_LONG
#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import date
from collections import Counter
import json,re,html,subprocess
root=Path(__file__).parent/'dist';src=root.parent/'src/editions';errors=[];count=0
class Check(HTMLParser):
 def handle_starttag(self,tag,attrs):
  global count
  a=dict(attrs)
  for k in ('href','src','srcset','action'):
   if k not in a:continue
   url=urlsplit(a[k])
   if url.scheme or url.netloc or not url.path:continue
   target=root/unquote(url.path.lstrip('/')) if url.path.startswith('/') else page.parent/unquote(url.path)
   if target.is_dir():target=target/'index.html'
   count+=1
   if not target.exists():errors.append(f'{page.relative_to(root)}: missing {a[k]}')
for page in root.rglob('*.html'):
 parser=Check();parser.feed(page.read_text());assert '<html lang="pt-BR">' in page.read_text()
articles=json.loads((src/EDITION_ID/'articles.json').read_text());assert len(articles)==96
assert len({a['id'] for a in articles})==96
assert len({a['title'].casefold() for a in articles})==96
counts=Counter(a['section'] for a in articles);assert len(counts)==6 and set(counts.values())=={16}
for sec,n in counts.items():
 text=(root/'editorias'/sec/'index.html').read_text();ids=re.findall(r'data-article-id="([^"]+)"',text)
 assert len(ids)==16 and len(set(ids))==16,sec
 assert set(ids)=={a['id'] for a in articles if a['section']==sec},sec
for a in articles:
 assert len(a['paragraphs'])>=3
 if a['date']:date.fromisoformat(a['date'])
 text=(root/a['url']/'index.html').read_text()
 assert all(html.escape(p,quote=True) in text for p in a['paragraphs'])
 if not a['date']:assert 'data de publicação não informada' in text
 assert 'Nº '+EDITION_ID in text
 assert not any(image in text for image in ('gait-wearable.webp','neuron-biomarkers.webp','lab-diagnostics.webp'))
for edition,expected in [('001',6),('002',7)]:
 old=json.loads((src/edition/'articles.json').read_text());assert len(old)==expected
 archived=(root/'edicoes'/edition/'index.html').read_text();assert 'data-root="../../"' in archived and 'Nº '+edition in archived
 for a in old:
  text=(root/'artigos'/a['id']/'index.html').read_text();assert all(html.escape(p,quote=True) in text for p in a['paragraphs'])
  assert f'../../edicoes/{edition}/' in text
for history in CONFIG.get('history',[]):
 if history.get('kind')!='snapshot':continue
 eid=history['editionId'];snapshot=src/eid/'snapshot';deployed=root/'edicoes'/eid
 assert snapshot.exists() and deployed.exists()
 for file in snapshot.rglob('*'):
  if file.is_file():assert file.read_bytes()==(deployed/file.relative_to(snapshot)).read_bytes(),str(file)
 old_articles=json.loads((src/eid/'articles.json').read_text())
 for a in old_articles:
  text=(root/a['url']/'index.html').read_text();assert all(html.escape(p,quote=True) in text for p in a['paragraphs'])
current=(root/'index.html').read_text();teasers=re.findall(r'data-article-id="([^"]+)"',current);assert 7<=len(teasers)<=10 and len(teasers)==len(set(teasers))
embedded=re.search(r'<script id="edition-data" type="application/json">(.*?)</script>',current,re.S);assert len(json.loads(embedded.group(1)))==96
assert 'Nº '+EDITION_ID in current and EDITION_LABEL in current and DATE_LONG in current
for key in counts:assert 'editorias/'+key+'/' in current
photos=json.loads((src/'002/photos.json').read_text());assert len(photos)==2
assert all(x['cleared'] and x['licenseUrl'] and x['license']=='CC BY-ND 3.0' for x in photos.values())
for page in root.rglob('*.html'):
 text=page.read_text()
 if 'class="article-page"' in text:
  assert 'compact-masthead' in text and 'THE MED TIMES' in text and 'article-evidence' in text
 else:assert 'Ciência para ler.<br>Medicina para pensar.' in text and 'Uma leitura crítica<br>do mundo da saúde.' in text
 assert not any(x in text for x in ('/workspace/','file://','sediment://','Invalid Date','NaN'))
for pathname in ['index.html',*[f'editorias/{sec}/index.html' for sec in counts]]:
 text=(root/pathname).read_text();assert 'data-editorial-design=' in text and 'class="press-band ' in text
 assert 'class="continuous-columns"' not in text and 'class="opening-lead"' not in text
signatures=set();all_roles=set()
for name in ['home',*counts]:
 page=root/'index.html' if name=='home' else root/'editorias'/name/'index.html'
 text=page.read_text();assert f'data-editorial-design="{name}"' in text
 signature=tuple(re.findall(r'data-composition="([^"]+)"',text));assert len(signature)>=2
 signatures.add(signature);roles=set(re.findall(r'data-role="([^"]+)"',text));assert len(roles)>=3
 all_roles|=roles
assert len(signatures)==7,'Seven genuinely distinct nested editorial compositions required'
assert {'lead','feature','major','standard','rail','brief','compact'}<=all_roles
css=(root/'styles-reading.css').read_text();assert '.press-story-split' in css and 'grid-template-columns:var(--press-tracks)' in css
assert '@media(max-width:700px)' in css and '.press-band,.press-nest,.press-story-split{display:block}' in css
for visual in json.loads((src/EDITION_ID/'diagrams.json').read_text()):
 assert (root/'assets'/visual['filename']).exists() and (root/'assets'/visual['mobileFilename']).exists() and (root/'assets'/visual['compactFilename']).exists()
for visual in json.loads((src/EDITION_ID/'context-photos.json').read_text()):
 assert visual['cleared'] and visual['licenseUrl'] and (root/'assets'/visual['filename']).exists()
for page in root.glob('editorias/*/index.html'):
 text=page.read_text()
 if 'aedes-aegypti.webp' in text:assert 'não implica endosso' in text
for script in ('app.js','app-reading.js'):subprocess.run(['node','--check',str(root/script)],check=True)
print(f'{len(list(root.rglob("*.html")))} pages; {count} local refs checked; {len(errors)} errors')
print('96 unique articles / six full section papers with 16 each / '+str(len(teasers))+' home teasers / search96 / archives001+002 preserved')
for er in errors:print(er)
raise SystemExit(bool(errors))
