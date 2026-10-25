"""Content-aware newspaper modules; body excerpts preserve complete source sentences."""
import re,html
from compositions import PLANS
E=lambda x:html.escape(str(x),quote=True)

def excerpt(a,budget):
 if not budget:return []
 picked=[];used=0
 for paragraph in a['paragraphs']:
  current=[]
  for sentence in re.split(r'(?<=[.!?])\s+',paragraph):
   n=len(sentence.split())
   if used+n>budget and (picked or current):
    if current:picked.append(' '.join(current))
    return picked
   current.append(sentence);used+=n
  if current:picked.append(' '.join(current))
 return picked

class PressRenderer:
 def __init__(self,rows,prefix,visual,date_label,type_label,reading_label=None):
  self.rows=rows;self.p=prefix;self.visual=visual;self.date_label=date_label;self.type_label=type_label;self.reading_label=reading_label
 def story(self,node):
  a=self.rows[node['story']];role=node['role'];image=self.visual(a,self.p,node['visual']) if node['visual']!='none' else ''
  title=f'<h2><a href="{self.p+a["url"]}">{E(a["title"])}</a></h2>'
  kicker=f'<p class="press-kicker">{E(a["category"])} · {E(self.type_label(a))}</p>'
  deck=f'<p class="press-deck">{E(a["deck"])}</p>' if a['deck'] and a['deck'].strip()!=a['title'].strip() else ''
  text=excerpt(a,node['words']);body='<div class="press-copy">'+''.join('<p>'+E(t)+'</p>' for t in text)+'</div>'
  meta=f'<p class="press-date">{E(self.date_label(a))}'+(' · '+E(self.reading_label(a)) if self.reading_label else '')+'</p>'
  read=f'<a class="press-read" href="{self.p+a["url"]}">Ler matéria →</a>'
  top=image if node['visual']=='top' else ''
  if node['visual']=='side' and image:
   middle='<div class="press-story-split"><div>'+deck+body+'</div><div>'+image+'</div></div>'
  elif node['visual']=='middle':middle=deck+image+body
  else:middle=deck+body+(image if node['visual']=='bottom' else '')
  return f'<article class="press-story press-{role}{" press-italic" if node.get("italic") else ""}" data-article-id="{E(a["id"])}" data-words="{len(" ".join(text).split())}" data-role="{role}">{top}{kicker}{title}{middle}{meta}{read}</article>'
 def group(self,node,depth=0,prioritize=False):
  widths=node['widths'];classes='press-band' if depth==0 else 'press-nest'
  indexed=list(enumerate(node['columns'],1))
  # Reading order starts with the lead package. Desktop physical columns stay fixed.
  if prioritize:
   def weight(pair):
    return max(({'lead':7,'feature':6,'major':5,'standard':4,'rail':3,'brief':2,'compact':1}.get(x.get('role'),0) for x in pair[1]),default=0)
   indexed.sort(key=weight,reverse=True)
  columns=''.join(f'<div class="press-stack" data-desktop-column="{position}" style="--press-column:{position}">'+''.join(self.story(x) if 'story' in x else self.group(x,depth+1) for x in col)+'</div>' for position,col in indexed)
  label=f'<div class="press-band-label"><h2>{E(node["label"])}</h2></div>' if node.get('label') else ''
  signature='-'.join(map(str,widths));return label+f'<div class="{classes} press-cols-{len(widths)}" style="--press-tracks:{" ".join(str(n)+"fr" for n in widths)}" data-composition="{signature}">{columns}</div>'
 def render(self,key):return f'<div class="press-composition press-composition-{key}" data-editorial-design="{key}">'+''.join(self.group(x,prioritize=(i==0)) for i,x in enumerate(PLANS[key]))+'</div>'
