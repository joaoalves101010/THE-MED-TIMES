#!/usr/bin/env python3
"""Sealed, content-addressed edition covers. Pure stdlib snapshot validation/replay.

Rendering is a preparation-only operation. This module never publishes or performs
network I/O. A public manifest becomes visible only with the journal's deployment.
"""
from datetime import date
from pathlib import Path
import hashlib, json, re, shutil
import xml.etree.ElementTree as ET

LABEL = 'Prévia editorial · composição vetorial da edição publicada'
WIDTH, HEIGHT = 1000, 1480
FONT_LICENSE_SHA256 = 'f32df582a2aab128c07b2f7e36e7b928dc5f6bd82657b905c04f91459f9e5cf9'
METHODS = {'approved-dense-cover-import', 'dynamic-dense-cover-v1'}
HEX64 = re.compile(r'[0-9a-f]{64}')
IMAGE = re.compile(r'assets/edition-covers/edition-(\d{3,})-([0-9a-f]{64})\.svg')
FONT_CREDIT = 'Liberation 2.1.5 · SIL Open Font License 1.1 · tipografia em curvas · https://github.com/liberationfonts/liberation-fonts/blob/main/LICENSE'

def require(ok, message):
    if not ok: raise ValueError(message)

def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path, value):
    path=Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def exact(obj, keys, label):
    require(isinstance(obj, dict) and set(obj)==set(keys), 'Invalid cover '+label+' fields')
def plain(value, label, maximum=4000):
    require(isinstance(value,str) and 0<len(value)<=maximum and not any(ord(c)<32 for c in value), 'Invalid cover '+label)

def validate_manifest(meta):
    exact(meta, {'schemaVersion','editionId','date','image','label','credits'}, 'manifest')
    require(type(meta['schemaVersion']) is int and meta['schemaVersion']==1, 'Invalid cover schema')
    require(isinstance(meta['editionId'],str) and re.fullmatch(r'\d{3,9}',meta['editionId']) and int(meta['editionId'])>0, 'Invalid cover edition')
    require(isinstance(meta['date'],str) and re.fullmatch(r'20\d{2}-\d{2}-\d{2}',meta['date']) and date.fromisoformat(meta['date']).isoformat()==meta['date'], 'Invalid cover date')
    exact(meta['image'], {'path','sha256','width','height'}, 'image')
    image=meta['image'];m=IMAGE.fullmatch(image.get('path',''))
    require(m and m[1]==meta['editionId'] and m[2]==image['sha256'], 'Unsafe or non-content-addressed cover path')
    require(type(image['width']) is int and type(image['height']) is int and (image['width'],image['height'])==(WIDTH,HEIGHT), 'Invalid cover dimensions')
    plain(meta['label'],'label',160)
    require(isinstance(meta['credits'],list) and 1<=len(meta['credits'])<=10, 'Invalid cover credits')
    for credit in meta['credits']:plain(credit,'credit',1000)
    require(len(canonical(meta))<=16*1024, 'Cover manifest exceeds 16 KiB')
    return meta

def validate_record(record):
    exact(record, {'schemaVersion','editionId','date','image','label','credits','source'}, 'record')
    validate_manifest({k:v for k,v in record.items() if k!='source'})
    exact(record['source'], {'inputSha256','articleIds','renderMethod'}, 'source')
    source=record['source']
    require(isinstance(source['inputSha256'],str) and HEX64.fullmatch(source['inputSha256']), 'Invalid cover input hash')
    ids=source['articleIds']
    require(isinstance(ids,list) and len(ids)==9 and len(set(ids))==9 and all(isinstance(i,str) and re.fullmatch(r'[a-z0-9-]+',i) for i in ids), 'Invalid cover article IDs')
    require(source['renderMethod'] in METHODS, 'Invalid cover rendering method')
    return record

def validate_svg(blob, meta):
    require(sha(blob)==meta['image']['sha256'], 'Cover image hash mismatch')
    require(len(blob)<=3*1024*1024, 'Cover image exceeds 3 MiB')
    require(b'<!DOCTYPE' not in blob.upper() and b'<!ENTITY' not in blob.upper() and b'<?' not in blob, 'Unsafe SVG declaration/processing instruction')
    root=ET.fromstring(blob)
    require(root.tag=='{http://www.w3.org/2000/svg}svg', 'Cover is not SVG')
    require(root.get('width')==str(WIDTH) and root.get('height')==str(HEIGHT) and root.get('viewBox')==f'0 0 {WIDTH} {HEIGHT}', 'Cover SVG dimensions differ')
    allowed={'svg','g','path','defs','rect','use','image','title','desc','line','polyline','polygon','circle','ellipse','clipPath'}
    attributes={'width','height','viewBox','role','aria-labelledby','id','d','fill','aria-label','transform','href','x','y','stroke','stroke-width','fill-rule','preserveAspectRatio','data-photo','opacity','fill-opacity','stroke-linecap','stroke-linejoin','clip-path','points','r','cx','cy','rx','ry','x1','x2','y1','y2'}
    for node in root.iter():
        require(node.tag.startswith('{http://www.w3.org/2000/svg}'), 'Foreign SVG namespace')
        tag=node.tag.rsplit('}',1)[-1]
        require(tag in allowed, 'Unsafe/unexpected SVG element: '+tag)
        for name,value in node.attrib.items():
            local=name.rsplit('}',1)[-1]
            require(local in attributes and (name==local or name=='{http://www.w3.org/1999/xlink}href'), 'Active/unknown SVG attribute')
            if local not in {'aria-label','aria-labelledby','data-photo','href'}:
                require('\\' not in value, 'Escaped SVG presentation value')
                if re.search(r'url\s*\(',value,re.I):require(re.fullmatch(r'url\(#[A-Za-z0-9_.:-]+\)',value), 'External SVG presentation reference')
            if local=='href':
                require((tag=='use' and re.fullmatch(r'#[A-Za-z0-9_.:-]+',value)) or (tag=='image' and re.fullmatch(r'data:image/(?:jpeg|png|webp);base64,[A-Za-z0-9+/=]+',value)), 'External/active SVG reference')
    return root

def load_data(root, cfg, articles=None):
    root=Path(root);eid=cfg['editionId'];current=root/'src/editions'/eid
    articles=articles if articles is not None else read(current/'articles.json')
    require(len(articles)==96 and len({a['id'] for a in articles})==96, 'Cover needs exact 96-article edition')
    ids=cfg['homeArticleIds'];require(len(ids)==9 and len(set(ids))==9, 'Cover needs exact nine home IDs')
    lookup={a['id']:a for a in articles};require(all(i in lookup for i in ids), 'Cover home ID is absent from current edition')
    require(read(current/'home-selection.json')==ids, 'Cover home selection differs from config')
    photos=[];photo_path=current/'context-photos.json'
    if photo_path.exists():
        values=read(photo_path);values=list(values.values()) if isinstance(values,dict) else values
        for photo in values:
            if photo.get('id') not in ids or photo.get('cleared') is not True:continue
            require(photo.get('kind')=='context-photograph', 'Cover photograph must be explicitly identified')
            name=photo.get('filename','');require(re.fullmatch(r'[A-Za-z0-9_.-]+\.(?:png|webp|jpg|jpeg)',name), 'Unsafe cover photograph filename')
            for field in ('caption','credit','license','licenseUrl','sourceUrl'):plain(photo.get(field),'photo '+field)
            # Never carry machine locations into a public provenance digest/record.
            photos.append({k:v for k,v in photo.items() if k!='localPath'})
    # At most two photographs: preferred central/right slots, then selection order.
    priority=[ids[8],ids[7],*ids]
    photos.sort(key=lambda p:priority.index(p['id']));photos=photos[:2]
    photos.sort(key=lambda p:p['id'])
    dt=date.fromisoformat(cfg['localDate']);months=('janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro').split()
    return {'editionId':eid,'localDate':cfg['localDate'],'dateLabel':f"{('Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo')[dt.weekday()]}, {dt.day} de {months[dt.month-1]} de {dt.year}", 'articles':[lookup[i] for i in ids], 'photos':photos,
            'sourceAssetsSha256':{p['filename']:sha((root/'dist/assets'/p['filename']).read_bytes()) for p in photos}}

def input_hash(data):return sha(canonical(data))
def metadata(data, blob, method):
    digest=sha(blob);eid=data['editionId']
    result={'schemaVersion':1,'editionId':eid,'date':data['localDate'],
            'image':{'path':f'assets/edition-covers/edition-{eid}-{digest}.svg','sha256':digest,'width':WIDTH,'height':HEIGHT},
            'label':LABEL,'credits':[FONT_CREDIT,*[f"{p['caption'].strip()} {p['credit']} · {p['license']}. Origem: {p['sourceUrl']}. Licença: {p['licenseUrl']}" for p in data['photos']]],
            'source':{'inputSha256':input_hash(data),'articleIds':[a['id'] for a in data['articles']],'renderMethod':method}}
    validate_record(result);validate_svg(blob,result);return result

def record_path(root,eid):return Path(root)/'src/edition-covers'/f'edition-{eid}.json'
def persist(root, data, blob, method):
    root=Path(root);record=metadata(data,blob,method);target=root/'dist'/record['image']['path'];meta=record_path(root,data['editionId'])
    if meta.exists():require(read(meta)==record, 'Immutable edition cover record already exists with different content')
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():require(target.read_bytes()==blob, 'Immutable edition cover asset collision')
    else:target.write_bytes(blob)
    if not meta.exists():write(meta,record)
    return record

def verify_cover(root, cfg=None, articles=None, require_manifest=True):
    root=Path(root);cfg=cfg or read(root/'edition.json');data=load_data(root,cfg,articles)
    require(sha((root/'dist/assets/EDITION-COVER-FONT-LICENSE.txt').read_bytes())==FONT_LICENSE_SHA256, 'Cover OFL license differs from approved notice')
    record=validate_record(read(record_path(root,cfg['editionId'])))
    require(record['editionId']==cfg['editionId'] and record['date']==cfg['localDate'], 'Stale cover edition/date')
    require(record['source']['articleIds']==cfg['homeArticleIds'], 'Stale cover selection')
    require(record['source']['inputSha256']==input_hash(data), 'Cover is not bound to current editorial source')
    blob=(root/'dist'/record['image']['path']).read_bytes()
    require(metadata(data,blob,record['source']['renderMethod'])==record, 'Cover record/credits differ from current source')
    manifest={k:v for k,v in record.items() if k!='source'}
    if require_manifest:require(read(root/'dist/edition-cover.json')==manifest, 'Public cover manifest differs from sealed edition')
    return manifest

def build_edition_cover(root, cfg, articles=None, allow_render=False):
    root=Path(root);path=record_path(root,cfg['editionId']);data=load_data(root,cfg,articles)
    if not path.exists():
        require(allow_render, 'Missing sealed cover snapshot; render and review in private preparation first')
        from cover_renderer import render_cover
        blob,proof=render_cover(data,root/'cover-source',root/'dist/assets')
        persist(root,data,blob,'dynamic-dense-cover-v1')
    manifest=verify_cover(root,cfg,articles,require_manifest=False)
    write(root/'dist/edition-cover.json',manifest)
    return manifest

def verify_prepared_cover(root, cfg=None):
    root=Path(root);cfg=cfg or read(root/'edition.json');result=verify_cover(root,cfg)
    record=read(record_path(root,cfg['editionId']));data=load_data(root,cfg)
    if record['source']['renderMethod']=='dynamic-dense-cover-v1':
        from cover_renderer import render_cover
        blob,_=render_cover(data,root/'cover-source',root/'dist/assets')
        require(sha(blob)==record['image']['sha256'], 'Prepared cover is not deterministic renderer output')
    else:
        approvals=read(root/'cover-source/approved-imports.json')
        require(approvals.get(cfg['editionId'])=={'inputSha256':input_hash(data),'imageSha256':record['image']['sha256']}, 'Unapproved imported cover')
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args();print(json.dumps(verify_cover(args.root),ensure_ascii=False,indent=2))
