#!/usr/bin/env python3
"""Build 96-article expanded edition and two immutable historical editions."""
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit
import json,re,shutil,math
from templates import shell,e
from press_renderer import PressRenderer
from compositions import PLANS,story_indices
from edition_config import CONFIG,EDITION_ID,DATE_ISO,DATE_LONG,DATE_DOTTED,EDITION_LABEL,RECENT_SINCE,BASELINE,long_date
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'dist';SRC=ROOT/'src/editions';CURRENT=SRC/EDITION_ID;OUT.mkdir(exist_ok=True)
# Portable source assets; immutable historical filenames must never be replaced.
shutil.copytree(ROOT/'src/assets',OUT/'assets',dirs_exist_ok=True)
for directory in ('fontes','creditos','sobre','edicao'):(OUT/directory).mkdir(parents=True,exist_ok=True)
SECTIONS=[('pesquisa','Pesquisa','Estudos, métodos e os limites de cada descoberta.'),('clinica','Clínica','Raciocínio, evidência e cuidado à beira do leito.'),('saude-publica','Saúde pública','Populações, políticas e acesso ao cuidado.'),('formacao','Formação','Aprender medicina, construir repertório, seguir adiante.'),('inovacao','Inovação','Tecnologia em saúde, do conceito à avaliação.'),('instituicoes','Instituições','Programas e experiências: regras antes de expectativas.')]
# Legacy editions001/002 reference these root files: preserve their exact UI bytes.
for filename in ('styles.css','app.js'):
 shutil.copy(ROOT/'src/historical-ui'/filename,OUT/filename)
 stem,suffix=filename.rsplit('.',1);shutil.copy(ROOT/'src'/filename,OUT/(stem+'-reading.'+suffix))
# Restore archived article content before generating the separate current namespace.
for edition in ('001','002'):
 source=SRC/edition
 for path in (source/'articles').iterdir():
  shutil.copytree(path,OUT/'artigos'/path.name,dirs_exist_ok=True)
  page=OUT/'artigos'/path.name/'index.html';text=page.read_text()
  text=text.replace('href="../../"',f'href="../../edicoes/{edition}/"').replace('href="../../?',f'href="../../edicoes/{edition}/?').replace('action="../../"',f'action="../../edicoes/{edition}/"')
  page.write_text(text)
 archive=(source/'home.html').read_text()
 def archived_url(m):
  attr,url=m.group(1),m.group(2)
  if url.startswith(('http:','https:','#','data:','/','./')) or not url:return m.group(0)
  return f'{attr}="../../{url}"'
 archive=re.sub(r'(href|src)="([^"]*)"',archived_url,archive)
 kind='ilustrações conceituais de IA' if edition=='001' else 'fotografias reais com créditos'
 archive=archive.replace('<main id="conteudo">',f'<main id="conteudo"><div class="archive-notice"><strong>Arquivo · Edição {edition} · 24 de outubro de 2026</strong><span>Edição preservada, com {kind}. <a href="../../">Ler a edição atual →</a></span></div>')
 archive=archive.replace('id="edition-data"','id="edition-data" data-root="../../"')
 dest=OUT/'edicoes'/edition;dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(archive)
for history in CONFIG.get('history',[]):
 if history.get('kind')!='snapshot':continue
 eid=history['editionId'];snapshot=SRC/eid/'snapshot'
 assert snapshot.is_dir(),f'Missing immutable archive {eid}'
 shutil.copytree(snapshot,OUT/'edicoes'/eid,dirs_exist_ok=True)
 namespace=snapshot/('edicao-'+eid)
 if namespace.exists():shutil.copytree(namespace,OUT/namespace.name,dirs_exist_ok=True)
missing=[key for key,_,_ in SECTIONS if not (CURRENT/(key+'.json')).exists()]
if missing:raise SystemExit('Awaiting researched section data: '+', '.join(missing)+'. Archive scaffold preserved.')
if (CURRENT/'composition-plan.json').exists():
 plans=json.loads((CURRENT/'composition-plan.json').read_text());assert set(plans)==set(PLANS),'Missing editorial composition'
 for key,plan in plans.items():
  indices=[i for node in plan for i in story_indices(node)];assert sorted(indices)==list(range(9 if key=='home' else 16)),key
  def validate_node(node):
   if 'story' in node:
    assert node['role'] in ('lead','feature','major','standard','rail','brief','compact') and node['visual'] in ('none','top','middle','bottom','side')
    assert isinstance(node['words'],int) and 0<=node['words']<=250
   else:
    assert len(node['widths'])==len(node['columns']) and all(isinstance(w,(int,float)) and 0<w<=8 for w in node['widths'])
    for col in node['columns']:
     for child in col:validate_node(child)
  for node in plan:validate_node(node)
 PLANS.clear();PLANS.update(plans)
ALL=[];BY={}
def text_paragraph(v):
 if isinstance(v,str):return v
 return v.get('text',v.get('body',''))
for key,name,_ in SECTIONS:
 raw=json.loads((CURRENT/(key+'.json')).read_text());raw=raw.get('articles',[]) if isinstance(raw,dict) else raw
 assert len(raw)==16,f'{key}: expected 16, got {len(raw)}'
 rows=[]
 for item in raw:
  a=dict(item);a['section']=key;a['sectionName']=name;a['category']=a.get('category') or name
  a['id']=a.get('id') or a.get('slug');assert a['id'] and re.fullmatch('[a-z0-9-]+',a['id']),a.get('id')
  a['deck']=a.get('deck') or a.get('dek') or a.get('summary','');a['sourceUrl']=a.get('sourceUrl') or a.get('sourceURL');assert a['sourceUrl'] and urlsplit(a['sourceUrl']).scheme in ('https','http'),a['id']
  a['sourceName']=a.get('sourceName') or urlsplit(a['sourceUrl']).netloc
  a['paragraphs']=[text_paragraph(x) for x in a.get('paragraphs',a.get('body',[]))];assert len(a['paragraphs'])>=3 and all(a['paragraphs']),a['id']
  if a.get('date'):date.fromisoformat(a['date'])
  else:a['date']=None
  a['contentType']=a.get('contentType') or ('Notícia' if a['date'] else 'Guia de referência')
  a['url']='edicao-'+EDITION_ID+'/artigos/'+a['id']+'/'
  rows.append(a);ALL.append(a)
 BY[key]=rows
assert len(ALL)==96 and len({a['id'] for a in ALL})==96,'96 globally unique article IDs required'
assert len({a['title'].strip().casefold() for a in ALL})==96,'Duplicate article titles across primary sections'
PHOTOS=json.loads((SRC/'002/photos.json').read_text())
if (CURRENT/'photos.json').exists():
 extra=json.loads((CURRENT/'photos.json').read_text());PHOTOS.update(extra if isinstance(extra,dict) else {x['id']:x for x in extra})
PHOTO_BY_URL={x['sourceUrl']:x for x in PHOTOS.values() if x.get('cleared')}
DIAGRAMS={x['id']:x for x in json.loads((CURRENT/'diagrams.json').read_text())} if (CURRENT/'diagrams.json').exists() else {}
CONTEXT_PHOTOS={x['id']:x for x in json.loads((CURRENT/'context-photos.json').read_text())} if (CURRENT/'context-photos.json').exists() else {}
def photo(a):return PHOTO_BY_URL.get(a['sourceUrl'])
def date_label(a):
 if not a['date']:return 'Referência · data de publicação não informada'
 dt=date.fromisoformat(a['date']);news=str(a['contentType']).lower() in ('notícia','noticia','news')
 prefix=('Publicado hoje · ' if a['date']==DATE_ISO else 'Data da fonte · ') if news else 'Fonte de referência · '
 return prefix+dt.strftime('%d.%m.%Y')
def type_label(a):
 v=str(a['contentType']);return {'news':'Notícia','guide':'Guia de referência','program':'Guia de programa','reference':'Referência','noticia':'Notícia','guia':'Guia de referência','programa':'Guia de programa'}.get(v.lower(),v)
def reading_minutes(a):
 # Body, supplied deck and discussion only. A short synthesis is not inflated into an analysis.
 words=len(' '.join([a['deck'],*a['paragraphs'],a.get('implication',''),a.get('discussionPrompt','')]).split())
 return max(1,math.ceil(words/200))
def reading_label(a):return f"{reading_minutes(a)} min de leitura"
def link(a,p=''):return p+a['url']
def figure(a,p='',lead=False):
 ph=photo(a)
 if not ph:return ''
 return f'''<figure class="news-photo"><img src="{p}assets/{e(ph['filename'])}" alt="{e(ph['alt'])}" {'fetchpriority="high"' if lead else 'loading="lazy"'} width="1280" height="590"><figcaption>{e(ph['caption'])}<br><span>{e(ph['credit'])} · <a href="{e(ph['sourceUrl'])}" target="_blank" rel="noopener noreferrer">Fonte ↗</a> · <a href="{e(ph['licenseUrl'])}" target="_blank" rel="noopener noreferrer">CC BY-ND 3.0</a></span></figcaption></figure>'''
def lead_visual(a,p=''):
 visual=DIAGRAMS.get(a['id']) or CONTEXT_PHOTOS.get(a['id'])
 if not visual:return figure(a,p,True)
 if visual.get('kind')=='editorial-diagram':
  mobile=f'<source media="(max-width:600px)" srcset="{p}assets/{e(visual["mobileFilename"])}">' if visual.get('mobileFilename') else ''
  return f'''<figure class="context-visual editorial-diagram"><picture>{mobile}<img src="{p}assets/{e(visual['filename'])}" alt="{e(visual['alt'])}" width="{visual['width']}" height="{visual['height']}"></picture><figcaption><strong>Esquema editorial.</strong> {e(visual['caption'])}<br>{e(visual['credit'])} · <a href="{e(visual['sourceUrl'])}" target="_blank" rel="noopener noreferrer">Fonte do esquema ↗</a> · <a href="{p}assets/{e(visual['filename'])}" target="_blank" rel="noopener noreferrer">Ampliar esquema ↗</a></figcaption></figure>'''

 caption=re.sub(r'^Fotografia de contexto\s*[:.]\s*','',visual['caption'],flags=re.I)
 return f'''<figure class="context-visual documentary-context"><img src="{p}assets/{e(visual['filename'])}" alt="{e(visual['alt'])}" width="{visual['width']}" height="{visual['height']}"><figcaption><strong>Fotografia de contexto.</strong> {e(caption)}<br>{e(visual['credit'])} · <a href="{e(visual['sourceUrl'])}" target="_blank" rel="noopener noreferrer">Origem ↗</a> · <a href="{e(visual['licenseUrl'])}" target="_blank" rel="noopener noreferrer">{e(visual['license'])}</a></figcaption></figure>'''
def press_visual(a,p,mode):
 visual=DIAGRAMS.get(a['id'])
 if visual:
  filename=visual.get('compactFilename') or visual['filename']
  width=visual.get('compactWidth',visual['width']);height=visual.get('compactHeight',visual['height'])
  return f'''<figure class="press-figure press-diagram"><img src="{p}assets/{e(filename)}" alt="{e(visual['alt'])}" width="{width}" height="{height}"><figcaption><strong>Esquema editorial.</strong> {e(visual['caption'])}<br>{e(visual['credit'])} · <a href="{e(visual['sourceUrl'])}" target="_blank" rel="noopener noreferrer">Fonte ↗</a> · <a href="{p}assets/{e(visual['filename'])}" target="_blank" rel="noopener noreferrer">Ampliar ↗</a></figcaption></figure>'''
 result=lead_visual(a,p)
 return result.replace('context-visual documentary-context','press-figure press-photo').replace('class="news-photo"','class="press-figure press-photo"')
def summary(a,p='',picture=False,klass='',excerpt=True):
 return f'''<article class="story news-summary {klass}" data-article-id="{e(a['id'])}"><p class="kicker">{e(a['category'])} · {e(type_label(a))}</p><h2><a href="{link(a,p)}">{e(a['title'])}</a></h2><p class="dek">{e(a['deck'])}</p>{figure(a,p) if picture else ''}<p class="source-date">{e(date_label(a))}</p>{('<p class="body-preview">'+e(a['paragraphs'][0])+'</p>') if excerpt else ''}<a class="continue" href="{link(a,p)}">Ler a matéria e suas fontes →</a></article>'''
def lead_story(a,p=''):
 return f'''<article class="story section-lead" data-article-id="{e(a['id'])}"><p class="kicker">{e(type_label(a))} · {e(date_label(a))}</p><h2><a href="{link(a,p)}">{e(a['title'])}</a></h2><p class="dek">{e(a['deck'])}</p>{lead_visual(a,p)}<div class="lead-copy"><p>{e(a['paragraphs'][0])}</p><p>{e(a['paragraphs'][1])}</p></div><a class="continue" href="{link(a,p)}">Leia o contexto completo →</a></article>'''
# Each section is its own 16-story issue, not a filtered copy of the home.
for key,name,description in SECTIONS:
 rows=BY[key];p='../../'
 # Respect the supplied manual order; only public-health photo stories may take visual precedence.

 body=f'''<main id="conteudo"><header class="press-section-head"><h1>{e(name)}</h1><div><p>{e(description)}</p><span>16 matérias · Edição {EDITION_ID} · {DATE_LONG}</span></div></header><p class="press-section-note">Notícias e guias identificados pela natureza e pela data da fonte.</p>{PressRenderer(BY[key],p,press_visual,date_label,type_label,reading_label).render(key)}<section class="issue-note"><h2>Continue no jornal.</h2><p><a href="../../">Primeira página →</a> · <a href="../../fontes/">Fontes e critérios →</a></p></section></main>'''
 d=OUT/'editorias'/key;d.mkdir(parents=True,exist_ok=True);(d/'index.html').write_text(shell(name+' · 16 matérias',body,p,section=key))
# Front page selects eight distinct articles; all 96 remain searchable.
chosen=[]
for key,_,_ in SECTIONS:
 rows=BY[key];chosen.append(next((a for a in rows if str(a['contentType']).lower() in ('notícia','noticia','news') and a['date'] and a['date']>=RECENT_SINCE),rows[0]))
for key in ('pesquisa','inovacao'):
 chosen.append(next(a for a in BY[key] if a['id'] not in {x['id'] for x in chosen}))
# A cleared documentary photograph may add a ninth distinct front-page story.
photo_candidate=next((a for a in ALL if photo(a) and a['id'] not in {x['id'] for x in chosen}),None)
if photo_candidate:chosen.append(photo_candidate)
# Today's verified news gets first placement, then the latest dated research; guides remain labeled.
chosen.sort(key=lambda a:(str(a['contentType']).lower() in ('notícia','noticia','news'),a['date'] or ''),reverse=True)
if CONFIG.get('homeArticleIds'):
 lookup={a['id']:a for a in ALL};chosen=[lookup[i] for i in CONFIG['homeArticleIds']]
assert len(chosen)==9 and len({a['id'] for a in chosen})==9,'Explicit nine-story composition required'
(CURRENT/'home-selection.json').write_text(json.dumps([a['id'] for a in chosen],ensure_ascii=False))
lead=chosen[0]
index_links=''.join(f'<a href="editorias/{key}/"><strong>{name}</strong><span>16 matérias →</span></a>' for key,name,_ in SECTIONS)
front=f'''<main id="conteudo"><section id="front-page"><div class="section-label"><h1>Primeira página · Edição {EDITION_ID}</h1><span>{DATE_LONG} · {EDITION_LABEL}</span></div>{PressRenderer(chosen,"",press_visual,date_label,type_label,reading_label).render("home")}<nav class="section-index press-footer-index" aria-label="Os seis cadernos">{index_links}</nav><section class="issue-note"><h2>96 pautas.<br>Seis jornais para explorar.</h2><p>Cada editoria tem uma primeira página própria e 16 matérias distintas. A seleção inclui notícias verificadas e guias institucionais, sempre identificados. Datas antigas e páginas sem data não são disfarçadas de novidade. Atualização programada com checagem editorial; publicação condicionada à validação. <a href="edicao/">Consultar o arquivo →</a></p></section></section><section id="filtered-page" hidden><div class="section-label"><h1 id="results-heading">Busca na edição {EDITION_ID}</h1><span>96 matérias · 6 editorias</span></div><p class="search-scope">Busca restrita à edição {EDITION_ID} · <a href="edicao/">Consultar outras edições no arquivo →</a></p><p id="result-count" class="search-status" role="status" aria-live="polite"></p><div class="listing" id="results"></div><p class="empty" id="empty" hidden>Nenhuma matéria encontrada. Tente outro termo ou <a href="./">volte à primeira página</a>.</p></section></main><script id="edition-data" type="application/json">{json.dumps([{k:a[k] for k in ('id','url','section','category','title','deck','paragraphs')} for a in ALL],ensure_ascii=False).replace('</','<\\/')}</script>'''
front+=f'''<script id="edition-search-meta" type="application/json">{json.dumps({a['id']:{**{k:a[k] for k in ('date','contentType','sectionName')},'typeLabel':type_label(a),'dateLabel':date_label(a),'readingMinutes':reading_minutes(a)} for a in ALL},ensure_ascii=False).replace('</','<\\/')}</script>'''
if not BASELINE:front=front.replace('Atualização programada com checagem editorial; publicação condicionada à validação.','A edição é preparada e validada antes da publicação programada.')
(OUT/'index.html').write_text(shell(f'Edição {EDITION_ID} · Seis editorias, 96 matérias',front))
related_path=CURRENT/'reading-related.json'
if not related_path.exists():related_path=ROOT/'src'/('reading-related-'+EDITION_ID+'.json')
RELATED=json.loads(related_path.read_text()).get('articles',{}) if related_path.exists() else {}
LOOKUP={a['id']:a for a in ALL}
if RELATED:
 assert set(RELATED)==set(LOOKUP),'Related reading map must cover exactly this edition'
 for aid,items in RELATED.items():
  assert len(items)==2 and len({x['id'] for x in items})==2 and all(x['id'] in LOOKUP and x['id']!=aid and x.get('reason') for x in items),'Invalid editorial reading map'
for a in ALL:
 p='../../../';d=OUT/a['url'];d.mkdir(parents=True,exist_ok=True)
 refs=[{'name':a['sourceName'],'url':a['sourceUrl']}]
 for key in ('sources','additionalSources','supplementarySources'):
  for s in a.get(key,[]):
   if isinstance(s,str):s={'name':'Referência complementar','url':s}
   u=s.get('url',s.get('sourceUrl'))
   if u and u not in {r['url'] for r in refs}:refs.append({'name':s.get('name',s.get('title','Referência complementar')),'url':u})
 for key,name in [('secondarySourceUrl','Fonte complementar'),('studyUrl','Artigo científico original')]:
  if a.get(key) and a[key] not in {r['url'] for r in refs}:refs.append({'name':name,'url':a[key]})
 source_list=''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["name"])} ↗</a></li>' for s in refs)
 reflection=''
 if a['section']!='instituicoes' and (a.get('implication') or a.get('discussionPrompt')):
  reflection=f'<div class="limitations"><p class="kicker">Para levar à discussão</p>'+(f'<p>{e(a["implication"])}</p>' if a.get('implication') else '')+(f'<p><em>{e(a["discussionPrompt"])}</em></p>' if a.get('discussionPrompt') else '')+'</div>'
 status=a.get('status') or a.get('programStatus')
 if isinstance(status,dict):status='; '.join(f'{k}: {v}' for k,v in status.items())
 statusblock=f'<p class="program-status"><strong>Situação informada pela fonte:</strong> {e(status)}</p>' if status else ''
 if a.get('eligibility'):statusblock+=f'<p class="program-status"><strong>Elegibilidade:</strong> {e(a["eligibility"])}</p>'
 if a.get('deadline'):statusblock+=f'<p class="program-status"><strong>Prazo informado:</strong> {e(a["deadline"])}</p>'
 evidence=e(a.get('evidenceType') or type_label(a))
 checked=a.get('verifiedAt')
 check_label=('Conferência editorial · '+long_date(checked)) if checked else 'Data de conferência não informada'
 context_notes={
  'instituicoes':'Requisitos, prazos e calendários podem mudar. Confira o documento oficial e a elegibilidade antes de se candidatar.',
  'pesquisa':'A natureza do estudo e seus limites importam: resultados iniciais ou associações não demonstram, por si só, benefício clínico ou causalidade.',
  'clinica':'Referências e diretrizes devem ser lidas no seu contexto; esta síntese não substitui avaliação individual nem protocolo assistencial.',
  'saude-publica':'Indicadores, políticas e serviços pertencem ao período e ao contexto das fontes; sua aplicação pode variar entre locais.',
  'formacao':'Métodos e orientações devem ser consultados na versão oficial e contextualizados ao objetivo da formação.',
  'inovacao':'Protótipos e resultados de avaliação não equivalem, por si só, a disponibilidade clínica, eficácia ou autorização de uso.'}
 related=RELATED.get(a['id'])
 if not related:
  candidates=[x for x in BY[a['section']] if x['id']!=a['id']][:2]
  related=[{'id':x['id'],'reason':'Outra leitura de '+a['sectionName']} for x in candidates]
 related_html=''.join(f'<article><p class="kicker">{e(LOOKUP[x["id"]]["sectionName"])} · {e(type_label(LOOKUP[x["id"]]))}</p><h3><a href="{link(LOOKUP[x["id"]],p)}">{e(LOOKUP[x["id"]]["title"])}</a></h3><p>{e(x["reason"])}</p><span class="reading-time">{reading_label(LOOKUP[x["id"]])}</span></article>' for x in related)
 deck_html=f'<p class="article-dek">{e(a["deck"])}</p>' if a['deck'] and a['deck'].strip()!=a['title'].strip() else ''
 body=f'''<main id="conteudo"><div class="breadcrumb"><a href="../../../">Primeira página</a> / <a href="../../../editorias/{a['section']}/">{e(a['sectionName'])}</a> / Edição {EDITION_ID}</div><article data-current-article="{e(a['id'])}"><header class="article-header"><p class="kicker">{e(a['sectionName'])} · {e(type_label(a))}</p><h1>{e(a['title'])}</h1>{deck_html}<div class="article-meta"><span>Redação THE MED TIMES · Edição {EDITION_ID} · {DATE_LONG}</span><span>{e(date_label(a))}</span><span class="reading-time">{reading_label(a)} <span class="reading-estimate">· estimativa a 200 palavras/min</span></span></div>{statusblock}<div class="article-evidence" aria-label="Ficha editorial"><p><strong>Natureza da informação</strong><span>{evidence}</span></p><p><strong>Fonte de origem</strong><a href="{e(a['sourceUrl'])}" target="_blank" rel="noopener noreferrer">{e(a['sourceName'])} ↗</a></p><p><strong>{e(check_label)}</strong><a href="#fontes-da-materia">Consultar todas as fontes ↓</a></p></div></header><div class="real-article-photo">{figure(a,p,True)}</div><div class="article-layout"><aside class="article-aside" aria-label="Ferramentas de leitura"><div class="read-tools"><button type="button" data-print>Imprimir matéria ↗</button><button type="button" data-copy>Copiar link ↗</button></div><p id="tool-status" role="status" aria-live="polite"></p></aside><div class="article-body">{''.join('<p>'+e(t)+'</p>' for t in a['paragraphs'])}{reflection}<section class="sources" id="fontes-da-materia"><h2>Fontes & contexto</h2><ol>{source_list}</ol><p>{e(date_label(a))}. Síntese editorial em português, baseada nas referências indicadas. {e(context_notes[a['section']])}</p></section><p class="editorial-note">Conteúdo educativo, sem recomendação individual de diagnóstico ou tratamento. A redação contou com assistência de IA; não afirmamos revisão médica independente. Fotografias, quando presentes, são reais, mantidas integrais e creditadas. <a href="../../../sobre/#politica">Política editorial.</a></p></div></div></article><section class="related-reading" aria-labelledby="related-heading"><div class="related-heading"><h2 id="related-heading">{'Leituras relacionadas' if a['id'] in RELATED else 'Continue neste caderno'}</h2><span>Duas leituras desta edição</span></div><div class="related-stories">{related_html}</div></section><nav class="reading-return" aria-label="Voltar à leitura"><a data-return-origin href="../../../editorias/{a['section']}/">Voltar ao caderno de {e(a['sectionName'])} →</a><a href="../../../">Primeira página →</a></nav></main>'''
 (d/'index.html').write_text(shell(a['title'],body,p,a['deck'],article=True,section=a['section']))
# Utility-page bodies are preserved, but receive the current header and updated edition explanations.
def prior_main(filename):
 text=(SRC/'002'/filename).read_text();return text[text.index('<main '):text.index('</main>')+7]
sourcebody=prior_main('fontes.html').replace('Priorizamos notícias de hoje, 24 de outubro. Quando não há material suficiente e verificável, recorremos à semana de 19 a 24 de outubro e mostramos as datas, sem simular novidade.','Na primeira página, damos prioridade a notícias recentes com data verificável. Os cadernos também incluem guias de referência e páginas institucionais, claramente identificados e sem fingir que foram publicados hoje.').replace('para esta edição','para o projeto')
sourcebody=sourcebody.replace('Não há coleta automática, agenda de publicação ou promessa de edição diária. Novas edições exigem seleção e conferência.','Atualização programada com checagem editorial; publicação condicionada à validação. Novas edições exigem seleção e conferência; o diretório de fontes não é um feed ao vivo.')
(OUT/'fontes/index.html').write_text(shell('Fontes & critérios de seleção',sourcebody,'../'))
creditbody=prior_main('creditos.html').replace('A edição 002 não utiliza imagens geradas por IA.','As fotografias das edições 002 e 003 são reais e creditadas. A edição 003 também inclui esquemas vetoriais editoriais identificados, produzidos com assistência de IA. Eles não são fotografias, imagens clínicas nem reproduções das imagens dos estudos.').replace('<h2>Edição 001</h2>','<h2>O arquivo visual</h2>')
if not BASELINE:creditbody=creditbody.replace('As fotografias das edições 002 e 003 são reais e creditadas. A edição 003 também inclui esquemas vetoriais editoriais identificados, produzidos com assistência de IA.','As fotografias usadas pelo projeto são reais e creditadas. Os esquemas vetoriais editoriais são identificados como produzidos com assistência de IA.')
visual_credits=f'<h2>Esquemas e fotografias de contexto da edição {EDITION_ID}</h2>'
for visual in [*DIAGRAMS.values(),*CONTEXT_PHOTOS.values()]:
 visual_credits+=f'<section><h3>{e(next(a["title"] for a in ALL if a["id"]==visual["id"]))}</h3><p>{e(visual["caption"])}</p><p>{e(visual["credit"])}</p><p><a href="{e(visual["sourceUrl"])}" target="_blank" rel="noopener noreferrer">Fonte ou origem visual ↗</a>'+(f' · <a href="{e(visual["licenseUrl"])}" target="_blank" rel="noopener noreferrer">{e(visual["license"])}</a>' if visual.get('licenseUrl') else ' · Esquema vetorial original do projeto; não é fotografia nem imagem clínica.')+'</p></section>'
creditbody=creditbody.replace('<h2>O arquivo visual</h2>',visual_credits+'<h2>O arquivo visual</h2>')
(OUT/'creditos/index.html').write_text(shell('Créditos & condições de uso',creditbody,'../'))
about='''<main id="conteudo" class="about"><p class="kicker">Sobre o jornal</p><h1>Medicina, ciência<br>e descobertas.</h1><p>THE MED TIMES é um projeto editorial em português para estudantes de medicina e leitores interessados em compreender a ciência além da manchete.</p><p>A edição 003 reúne 96 matérias distintas em seis cadernos: Pesquisa, Clínica, Saúde pública, Formação, Inovação e Instituições. Cada caderno tem 16 pautas e sua própria primeira página. A capa apresenta uma seleção, não repete todos os cadernos.</p><h2 id="politica">Nosso compromisso editorial</h2><p><strong>Notícia não é guia.</strong> Conteúdos recentes trazem a data da fonte. Referências clínicas e programas institucionais são identificados como guias; fontes sem data não recebem uma data inventada.</p><p><strong>Fonte antes da manchete.</strong> Cada texto oferece links para sua origem. Comunicados institucionais não são apresentados como ensaios clínicos; metas de programas não são resultados alcançados.</p><p><strong>Regras antes de expectativas.</strong> Programas de observação, intercâmbio e formação dependem de elegibilidade, calendários, disponibilidade e condições da instituição. Uma descrição não equivale a uma chamada aberta nem garante admissão.</p><p><strong>Evidência com seus limites.</strong> Associação não implica causalidade. Identificamos limitações e evitamos converter um achado em prescrição individual.</p><p><strong>Esquemas editoriais.</strong> Representações vetoriais explicam fatos presentes nas fontes. São identificadas como esquemas com assistência de IA, não como fotografias ou imagens clínicas. Não acrescentam resultados experimentais.</p><p><strong>Imagens documentais.</strong> Fotografias das edições 002 e 003 têm fonte, autoria e condições de uso. São exibidas integralmente, sem filtros ou cortes. As ilustrações de IA da primeira edição permanecem identificadas no arquivo. <a href="../creditos/">Créditos fotográficos.</a></p><p><strong>Assistência de IA.</strong> O projeto contou com inteligência artificial na pesquisa, redação e implementação. Não afirmamos revisão médica independente. O conteúdo é educativo e não substitui avaliação profissional individual.</p><h2>Três edições, um mesmo dia editorial</h2><p>As edições 001, 002 e 003 pertencem a 24 de outubro de 2026. Representam etapas de expansão do jornal, não três dias diferentes. As duas primeiras foram preservadas integralmente e não são reescritas pela edição atual.</p><p>Atualização programada com checagem editorial; publicação condicionada à validação. Uma nova edição exige curadoria e conferência; se a validação falhar, a edição anterior permanece disponível. <a href="../fontes/">Fontes e critérios.</a></p><h2>Privacidade e leitura</h2><p>A busca da edição atual funciona no navegador e abrange as 96 matérias. As buscas nas edições arquivadas usam os respectivos acervos. Não há publicidade, contas, assinatura paga ou ferramentas de rastreamento.</p><p>As fontes Nimbus Roman e Nimbus Sans são distribuídas localmente com <a href="../assets/FONT-LICENSE.txt">licenças tipográficas</a>. A marca preserva os desenhos vetoriais aprovados.</p><p><a href="../edicao/">Consultar o arquivo de edições →</a></p></main>'''
if not BASELINE:
 about=about.replace('A edição 003 reúne',f'A edição {EDITION_ID} reúne')
 begin=about.index('<h2>Três edições, um mesmo dia editorial</h2>');end=about.index('<h2>Privacidade e leitura</h2>',begin)
 about=about[:begin]+f'<h2>Edições preservadas</h2><p>A edição {EDITION_ID} pertence a {DATE_LONG}. As edições anteriores mantêm suas datas e conteúdos no arquivo.</p><p>A publicação está programada para as 08:00, no horário de São Paulo, após preparação e validação editorial. Se uma edição não passar nas verificações, a edição anterior permanece disponível; não alteramos apenas a data para simular novidade.</p>'+about[end:]
(OUT/'sobre/index.html').write_text(shell('Sobre & política editorial',about,'../'))
from archive_previews import build_archive_previews
previews=build_archive_previews(ROOT,OUT,CONFIG)
entries=[{'editionId':EDITION_ID,'localDate':DATE_ISO,'label':EDITION_LABEL},*reversed(CONFIG.get('history',[]))]
cards=[]
for entry in entries:
 eid=entry['editionId'];preview=previews[eid];url='../' if eid==EDITION_ID else '../edicoes/'+eid+'/'
 cards.append(f'''<article><figure><a href="{url}" aria-label="Abrir a edição {eid}"><img src="../{e(preview['assetPath'])}" alt="Miniatura da composição da primeira página da edição {eid}" width="{preview['width']}" height="{preview['height']}" loading="lazy"></a><figcaption>{e(preview['proofLabel'])}</figcaption></figure><div><p class="kicker">{date.fromisoformat(entry['localDate']).strftime('%d.%m.%Y')} · {e(entry['label'])}</p><h2><a href="{url}">Edição {eid}{' · atual' if eid==EDITION_ID else ''}</a></h2><h3>{e(preview['mainHeadline'])}</h3><p>{e(preview['description'])}</p><a class="archive-open" href="{url}">Abrir esta edição →</a></div></article>''')
archivebody=f'<main id="conteudo"><div class="section-label"><h1>Arquivo de edições</h1><span>{len(entries)} edições disponíveis</span></div><p class="archive-intro">Primeiras páginas, datas e conteúdos preservados. As miniaturas são provas estáticas das composições, não capturas de navegador.</p><section class="archive-editions reading-archive">'+''.join(cards)+'</section></main>'
(OUT/'edicao/index.html').write_text(shell('Arquivo de edições',archivebody,'../'))
(OUT/'404.html').write_text(shell('Página não encontrada','<main id="conteudo" class="about"><p class="kicker">Página não encontrada</p><h1>Esta página não está na edição.</h1><p><a href="/">Voltar à primeira página →</a></p></main>','/'))
(CURRENT/'articles.json').write_text(json.dumps(ALL,ensure_ascii=False,indent=2))
print(f'Edition{EDITION_ID} complete: {len(ALL)} unique articles; 6 section papers with 16 articles each; {len(chosen)} home teasers; editions001/002 preserved.')
