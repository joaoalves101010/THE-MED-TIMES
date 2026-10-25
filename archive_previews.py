#!/usr/bin/env python3
"""Faithful, labeled static cover proofs; no browser/screenshot claims.

The renderer reads the actual cover DOM, its editorial grid tracks and all visible
text/images. It uses the project's fonts and approximates desktop typography with
Pillow. Historical proofs are write-once, current proofs are content addressed.
No historical HTML, CSS, JavaScript, photographs or other source assets are edited.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import hashlib, io, json, re, shutil

PROOF_LABEL = 'Miniatura da composição · prova estática, não captura de navegador'
VOID = {'img','meta','link','br','input','hr','source','wbr','area','base','embed','param','track','col'}

class Node:
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    @property
    def classes(self): return set(self.attrs.get('class','').split())
    def text(self):
        return re.sub(r'\s+', ' ', ' '.join(c.text() if isinstance(c,Node) else c for c in self.children)).strip()
    def nodes(self): return [c for c in self.children if isinstance(c,Node)]
    def find(self, pred):
        if pred(self): return self
        for c in self.nodes():
            found=c.find(pred)
            if found:return found
    def all(self, pred):
        result=[self] if pred(self) else []
        for c in self.nodes():result.extend(c.all(pred))
        return result

class Tree(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True); self.root=Node('root'); self.stack=[self.root]; self.feed(markup)
    def handle_starttag(self, tag, attrs):
        node=Node(tag,attrs); self.stack[-1].children.append(node)
        if tag=='br':self.stack[-1].children.append(' ')
        if tag not in VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):self.stack[-1].children.append(data)

def sha(data):return hashlib.sha256(data).hexdigest()

class CoverProof:
    """Small deterministic typesetter for existing three newspaper compositions."""
    def __init__(self,root,dist,markup,white=False):
        global Image, ImageDraw, ImageFont
        from PIL import Image, ImageDraw, ImageFont
        self.root,self.dist=Path(root),Path(dist); self.tree=Tree(markup).root
        self.paper='#ffffff' if white else '#f7f4ed';self.ink='#20241f';self.line='#a6a69b'; self.fonts={};self.assets={}
        self.canvas=Image.new('RGB',(1360,20000),self.paper);self.draw=ImageDraw.Draw(self.canvas)
    def font(self,size,bold=False,sans=False,italic=False):
        key=(size,bold,sans,italic)
        if key not in self.fonts:
            name='NimbusSans-Bold' if sans and bold else 'NimbusSans-Regular' if sans else 'NimbusRoman-Italic' if italic else 'NimbusRoman-Bold' if bold else 'NimbusRoman-Regular'
            path=self.dist/'assets'/(name+'.otf'); self.assets[name+'.otf']=sha(path.read_bytes())
            self.fonts[key]=ImageFont.truetype(str(path),round(size))
        return self.fonts[key]
    def text(self,text,x,y,w,size=17,line=None,bold=False,sans=False,italic=False,color=None,center=False):
        font=self.font(size,bold,sans,italic);line=line or size*1.35;lines=[];cur=''
        for word in text.split():
            new=(cur+' '+word).strip()
            if cur and font.getlength(new)>w:lines.append(cur);cur=word
            else:cur=new
        if cur:lines.append(cur)
        for i,s in enumerate(lines):
            dx=(w-font.getlength(s))/2 if center else 0
            self.draw.text((round(x+dx),round(y+i*line)),s,font=font,fill=color or self.ink)
        return len(lines)*line
    def rule(self,x,y,w,double=False):
        self.draw.line((round(x),round(y),round(x+w),round(y)),fill=self.line,width=1)
        if double:self.draw.line((round(x),round(y+3),round(x+w),round(y+3)),fill=self.ink,width=1)
    def picture(self,node,x,y,w):
        src=node.attrs.get('src','');name=Path(urlsplit(src).path).name;path=self.dist/'assets'/name
        if not path.is_file():raise ValueError('Cover asset missing: '+src)
        data=path.read_bytes();self.assets[name]=sha(data)
        if name.lower().endswith('.svg'):
            import fitz
            doc=fitz.open(stream=data,filetype='svg');pix=doc[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=True)
            im=Image.frombytes('RGBA',(pix.width,pix.height),pix.samples)
        else:im=Image.open(io.BytesIO(data)).convert('RGBA')
        h=round(w*im.height/im.width);im=im.resize((round(w),h),Image.Resampling.LANCZOS)
        self.canvas.paste(im,(round(x),round(y)),im)
        return h
    def grid(self,node,x,y,w,weights=None):
        children=node.nodes()
        if not children:return 0
        if 'front-grid' in node.classes:
            lead=[c for c in children if 'lead' in c.classes];rails=[c for c in children if c not in lead]
            children=rails[:1]+lead+rails[1:];weights=[1,2.8,1]
        else:
            # Accessible reading order may differ from the preserved desktop columns.
            def column(c):
                raw=c.attrs.get('data-desktop-column') or c.attrs.get('data-column')
                if raw:return int(raw)
                m=re.search(r'(?:--press-column|grid-column)\s*:\s*(\d+)',c.attrs.get('style',''))
                return int(m.group(1)) if m else children.index(c)+1
            children=sorted(children,key=column)
        if weights is None:
            match=re.search(r'--press-tracks:([^;]+)',node.attrs.get('style',''))
            weights=[float(v) for v in re.findall(r'([\d.]+)fr',match.group(1))] if match else [1]*len(children)
        if len(weights)!=len(children):weights=[1]*len(children)
        gap=22;total=sum(weights);offset=0;heights=[];rules=[]
        for i,(child,weight) in enumerate(zip(children,weights)):
            cw=(w-gap*(len(children)-1))*weight/total;pad=21 if i else 0
            heights.append(self.render_node(child,x+offset+pad,y,cw-pad));
            if i:rules.append(x+offset)
            offset+=cw+gap
        height=max(heights)
        for rx in rules:self.draw.line((round(rx),round(y),round(rx),round(y+height)),fill=self.line,width=1)
        return height
    def render_node(self,node,x,y,w,role=None):
        cls=node.classes
        if node.tag in ('script','style','button','input') or 'hidden' in node.attrs:return 0
        if node.tag=='img':return self.picture(node,x,y,w)
        grids={'press-band','press-nest','press-story-split','front-grid','bottom-grid','news-opening','news-secondary','banner-summary'}
        if cls & grids:
            weights=[2.25,1] if 'news-opening' in cls else [1.15,1.35,1] if 'bottom-grid' in cls else None
            return self.grid(node,x,y,w,weights)+26
        if node.tag=='article':role=node.attrs.get('data-role') or ('lead' if cls & {'lead','news-lead','news-banner'} else 'standard')
        if node.tag in ('h1','h2','h3'):
            sizes={'lead':46,'feature':42,'major':34,'standard':28,'rail':26,'brief':24,'compact':22}
            size=sizes.get(role,28)
            if 'news-banner' in cls:size=52
            if node.tag=='h1' and not role:size=18
            return self.text(node.text(),x,y,w,size,size*1.06,bold=True)+13
        if node.tag=='figcaption':return self.text(node.text(),x,y,w,10,14,sans=True,color='#62665e')+12
        if node.tag=='p' or (node.tag=='a' and cls & {'continue','press-read'}):
            if cls & {'kicker','press-kicker','byline','press-date','source-date','press-read','continue'}:
                return self.text(node.text(),x,y,w,10,14,sans=True,bold=bool(cls & {'kicker','press-kicker','press-read','continue'}),color='#495c43' if cls & {'kicker','press-kicker'} else '#62665e')+9
            if cls & {'dek','intro','press-deck'}:
                size=21 if role in ('lead','feature') else 17 if role in ('brief','compact') else 19
                return self.text(node.text(),x,y,w,size,size*1.25,italic='intro' in cls)+14
            return self.text(node.text(),x,y,w,16,21.76)+10
        if cls & {'section-label','press-band-label','edition-dateline'}:
            self.rule(x,y,w,double='press-band-label' in cls)
            h=self.text(node.text(),x,y+12,w,13,18,sans=True,bold=True)
            self.rule(x,y+h+23,w)
            return h+42
        if 'section-index' in cls or 'issue-note' in cls:return 0 # Thumbnail is the editorial cover, not its utility footer.
        if not node.nodes() and node.text():return self.text(node.text(),x,y,w,15)+10
        yy=y
        for i,child in enumerate(node.nodes()):
            if i and ('press-stack' in cls or 'news-rail' in cls) and child.tag in ('article','div'):
                yy+=15;self.rule(x,yy,w);yy+=20
            yy+=self.render_node(child,x,yy,w,role)
        return yy-y
    def render(self):
        x,w,y=42,1276,18
        y+=self.text('PROVA ESTÁTICA DE COMPOSIÇÃO · não é captura de navegador',x,y,w,11,15,sans=True,color='#62665e')+14
        mast=self.tree.find(lambda n:'masthead' in n.classes)
        if not mast:raise ValueError('Actual cover masthead missing')
        logo=mast.find(lambda n:n.tag=='img' and 'masthead-logo' in n.classes)
        left=mast.find(lambda n:'edition-box' in n.classes);right=mast.find(lambda n:'masthead-right' in n.classes)
        if left:self.text(left.text(),x,y+18,140,16,20,italic=True,center=True)
        if logo:self.picture(logo,214,y,932)
        if right:self.text(right.text(),1178,y+18,140,15,19,center=True)
        y+=134
        tagline=mast.find(lambda n:'tagline' in n.classes)
        if tagline:y+=self.text(tagline.text(),x,y,w,15,20,center=True)+12
        self.rule(x,y,w,True);y+=12
        datebar=self.tree.find(lambda n:'datebar' in n.classes)
        if datebar:y+=self.text(datebar.text(),x,y,w,11,15,sans=True,center=True)+12
        self.rule(x,y,w);y+=16
        nav=self.tree.find(lambda n:'navrow' in n.classes)
        if nav:y+=self.text(nav.text(),x,y,w,12,16,sans=True,center=True)+12
        self.rule(x,y,w,True);y+=15
        front=self.tree.find(lambda n:n.attrs.get('id')=='front-page')
        if not front:raise ValueError('Actual front-page section missing')
        y+=self.render_node(front,x,y,w)+15
        self.rule(x,y,w,True);y+=20
        y+=self.text('Miniatura calculada a partir do HTML da capa, com suas matérias, imagens e colunas. Tipografia aproximada; não valida a interface.',x,y,w,11,15,sans=True,color='#62665e')+20
        im=self.canvas.crop((0,0,1360,round(y)))
        return im.resize((680,round(im.height/2)),Image.Resampling.LANCZOS)

def main_headline(tree):
    for selector in ('news-banner','lead','press-lead','press-feature','news-lead'):
        area=tree.find(lambda n:selector in n.classes)
        if area:
            heading=area.find(lambda n:n.tag in ('h1','h2'))
            if heading:return heading.text()
    front=tree.find(lambda n:n.attrs.get('id')=='front-page')
    headings=front.all(lambda n:n.tag in ('h1','h2'))
    return headings[1].text() if len(headings)>1 else headings[0].text()

def build_archive_previews(root,dist,config):
    """Return metadata keyed by edition; call after writing the current index.html.

    All generated files live in a NEW namespace. Existing historical preview bytes
    are verified and reused, never overwritten. Each new current design has a new
    filename, so next-day archiving cannot silently change its preview.
    """
    root,dist=Path(root),Path(dist);store=root/'src/archive-previews';store.mkdir(parents=True,exist_ok=True)
    target=dist/'assets/archive-previews';target.mkdir(parents=True,exist_ok=True)
    current=config['editionId'];entries=[*config.get('history',[]),{'editionId':current,'localDate':config['localDate'],'label':config['editionLabel']}]
    result={}
    descriptions={
      '001':'A estreia reúne seis leituras sobre ciência e cuidado, com ilustrações conceituais de IA identificadas.',
      '002':'Sete notícias na atualização da noite: DUO-E na abertura e fotografias documentais sobre serviços do SUS.',
      '003':'A primeira edição ampliada reúne 96 matérias em seis cadernos, com formação internacional e pesquisa na capa.',
      '004':'A capa de 25 de outubro reúne cateterismo no Araguaia, UTIs conectadas e regras para formação internacional.'}
    for item in entries:
        eid=item['editionId'];historical=eid!=current;record_file=store/('edition-'+eid+'.json')
        # The published snapshot needs no graphics toolchain: reuse a proof only
        # when its actual HTML/CSS/assets and image hashes still match. A changed
        # edition must render a new proof; never hide stale evidence behind a cache.
        cached=False
        if not historical and record_file.exists():
            meta=json.loads(record_file.read_text());image_file=store/meta['filename']
            css_file=dist/meta['sourceCssRoute']
            cached=(sha((dist/'index.html').read_bytes())==meta['sourceHtmlSha256']
                and css_file.is_file() and sha(css_file.read_bytes())==meta['sourceCssSha256']
                and image_file.is_file() and sha(image_file.read_bytes())==meta['imageSha256']
                and all((dist/'assets'/name).is_file() and sha((dist/'assets'/name).read_bytes())==digest
                    for name,digest in meta['sourceAssetsSha256'].items()))
        if cached:
            pass
        elif historical and record_file.exists():
            meta=json.loads(record_file.read_text());image_file=store/meta['filename']
            if sha(image_file.read_bytes())!=meta['imageSha256']:raise ValueError('Historical preview changed: '+eid)
        else:
            source=dist/('edicoes/'+eid+'/index.html') if historical else dist/'index.html'
            markup=source.read_text()
            cover_tree=Tree(markup).root
            css_link=cover_tree.find(lambda n:n.tag=='link' and n.attrs.get('rel')=='stylesheet')
            if not css_link:raise ValueError('Actual cover stylesheet missing: '+eid)
            css_url=urlsplit(css_link.attrs['href'])
            if css_url.scheme or css_url.netloc:raise ValueError('Cover stylesheet must be local')
            css_path=dist/css_url.path.lstrip('/') if css_url.path.startswith('/') else source.parent/css_url.path
            css=css_path.read_bytes()
            renderer=CoverProof(root,dist,markup,white=not historical)
            im=renderer.render();buf=io.BytesIO();im.save(buf,format='PNG',optimize=True);image_bytes=buf.getvalue()
            digest=sha(image_bytes);filename=f'edition-{eid}-{digest[:16]}.png';image_file=store/filename
            if image_file.exists():
                if image_file.read_bytes()!=image_bytes:raise ValueError('Preview filename collision')
            else:image_file.write_bytes(image_bytes)
            meta={'schemaVersion':1,'editionId':eid,'localDate':item['localDate'],'label':item['label'],
              'filename':filename,'width':im.width,'height':im.height,'mainHeadline':main_headline(renderer.tree),
              'description':descriptions.get(eid,f'A edição apresenta {main_headline(renderer.tree)}'),
              'proofLabel':PROOF_LABEL,'renderMethod':'static-dom-typesetting-pillow-v1','browserScreenshot':False,
              'sourceHtmlSha256':sha(markup.encode()),'sourceCssSha256':sha(css),'sourceCssRoute':str(css_path.resolve().relative_to(dist.resolve())),'sourceAssetsSha256':renderer.assets,
              'imageSha256':digest,'sourceRoute':str(source.relative_to(dist))}
            # Historical record creation is exclusive; the current record may point
            # to a newer content-addressed design before becoming historical.
            serialized=json.dumps(meta,ensure_ascii=False,indent=2)+'\n'
            if historical:
                with record_file.open('x') as handle:handle.write(serialized)
            else:record_file.write_text(serialized)
        dest=target/meta['filename']
        if dest.exists() and sha(dest.read_bytes())!=meta['imageSha256']:raise ValueError('Deployed preview filename collision')
        if not dest.exists():shutil.copyfile(image_file,dest)
        result[eid]={**meta,'assetPath':'assets/archive-previews/'+meta['filename']}
    return result

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    print(json.dumps(build_archive_previews(root,root/'dist',json.loads((root/'edition.json').read_text())),ensure_ascii=False,indent=2))
