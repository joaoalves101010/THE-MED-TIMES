#!/usr/bin/env python3
"""Create a pending review template or validate a future edition; never publish.

Uses previous article source data, not private release evidence. Validation does
not fetch sources: a real editorial source check remains a required input.
"""
from pathlib import Path
from datetime import datetime,date,time,timedelta,timezone
from urllib.parse import urljoin,urlsplit,urlunsplit
import argparse,json,re,shutil,subprocess,sys,os
from editorial_tools import *
from renewal_policy import POLICY_VERSION,validate_renewal
ROOT=Path(__file__).resolve().parent

def read_articles(folder):
 rows=[]
 for section in SECTIONS:
  a=json.loads((Path(folder)/(section+'.json')).read_text());assert isinstance(a,list) and len(a)==16,section
  for item in a:
   assert item.get('section')==section and len(item.get('paragraphs',[]))>=3,'Invalid source article'
   assert len(' '.join(item['paragraphs']).split())>=70,'Article is only a stub'
   assert item.get('sourceUrl','').startswith('https://'),'Missing HTTPS source'
  rows+=a
 assert len({a['id'] for a in rows})==96 and len({a['title'].casefold() for a in rows})==96,'Duplicate article'
 return rows

def review_template(args):
 articles=read_articles(args.input)
 old=json.loads((ROOT/'edition.json').read_text())
 doc={'policyVersion':POLICY_VERSION,'novelty':{'previousEditionId':old['editionId'],'semanticReviewCompleted':False,'method':'','relevantArchivesReviewed':False,'archiveReviewNotes':''},'schemaVersion':1,'releaseDate':args.date,'sourceCutoff':args.cutoff,'reviewer':'','completedAt':None,'qa':{k:False for k in REQUIRED_QA},'relevantUpdateIds':[],
      'articles':{a['id']:{'status':'pending','contentSha256':article_digest(a),'sourceUrl':a['sourceUrl'],'reviewedAt':None,'sourceCheckedAt':None,'reason':'','novelty':{'topicKey':'','isNewTopic':False,'comparedAgainstAllPreviousTopics':False,'comparedAgainstAllCandidateTopics':False,'differenceFromPrevious':''}} for a in articles}}
 output=Path(args.output).resolve()
 assert not output.is_relative_to(ROOT/'dist'),'Review records must stay outside public dist'
 assert not output.exists(),'Refusing to overwrite an existing review'
 output.write_text(json.dumps(doc,ensure_ascii=False,indent=2));print('Pending review template written; it does not authorize readiness.')

def validate(args):
 old=json.loads((ROOT/'edition.json').read_text());target=date.fromisoformat(args.date);edition=args.edition
 assert re.fullmatch(r'\d{3,}',edition) and int(edition)>int(old['editionId']),'Edition must advance'
 assert target>date.fromisoformat(old['localDate']),'Daily edition date must advance'
 now=datetime.now(timezone.utc)
 articles=read_articles(args.input);review=json.loads(Path(args.review).read_text());cutoff=datetime.fromisoformat(review['sourceCutoff'])
 assert review['releaseDate']==args.date and review.get('reviewer'),'Wrong/missing editorial review'
 assert cutoff.tzinfo and cutoff<=now and cutoff.astimezone(TZ).date()==target,'Cutoff must be real and on target local date'
 assert now.astimezone(TZ).date()==target,'Prepare on target São Paulo date, not UTC-derived date'
 done=datetime.fromisoformat(review['completedAt']);assert done.tzinfo and cutoff<=done<=now,'Invalid review completion timestamp'
 assert all(review.get('qa',{}).get(k) is True for k in REQUIRED_QA),'Editorial QA incomplete'
 assert set(review['articles'])=={a['id'] for a in articles},'Review does not cover exactly 96 articles'
 previous=json.loads((ROOT/'src/editions'/old['editionId']/'articles.json').read_text());previous={a['id']:a for a in previous}
 renewal=validate_renewal(articles,list(previous.values()),review,old['editionId'])
 for a in articles:
  r=review['articles'][a['id']];assert r['contentSha256']==article_digest(a) and r['sourceUrl']==a['sourceUrl'],'Review hash/source mismatch'
  assert r['status']=='verified' and r.get('reason'),'Unreviewed article'
  checked=datetime.fromisoformat(r['reviewedAt']);assert checked.tzinfo and checked<=now and checked.astimezone(TZ).date()==target,'Stale/future editorial review'
  fetched=datetime.fromisoformat(r['sourceCheckedAt']);assert fetched.tzinfo and fetched<=cutoff and fetched.astimezone(TZ).date()==target,'Invalid source-check time'
  a['verifiedAt']=fetched.astimezone(TZ).date().isoformat()
  if a.get('date'):
   assert date.fromisoformat(a['date'])<=cutoff.astimezone(TZ).date(),'Future publication date'
   if a['date']!=args.date and str(a.get('contentType','')).lower() in ('notícia','noticia','news'):
    assert not re.search(r'\b(?:hoje|amanhã|ontem)\b',' '.join([a['title'],a['deck'],*a['paragraphs']]),re.I),'Stale relative-date language; use the original absolute date'
  assert not re.search(r'\b(?:TODO|TBD)\b|(?i:lorem ipsum)',' '.join(a['paragraphs'])),'Placeholder content'
 home=json.loads((Path(args.input)/'home-selection.json').read_text());assert len(home)==9 and len(set(home))==9 and set(home)<={a['id'] for a in articles},'Need explicit nine-story editorial selection'
 print(json.dumps({'status':'editorial-input-valid','published':False,'editionId':edition,'localDate':args.date,'renewal':renewal},ensure_ascii=False,indent=2))

def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 t=sub.add_parser('template');t.add_argument('--input',required=True);t.add_argument('--date',required=True);t.add_argument('--cutoff',required=True);t.add_argument('--output',required=True);t.set_defaults(func=review_template)
 v=sub.add_parser('validate');v.add_argument('--edition',required=True);v.add_argument('--date',required=True);v.add_argument('--input',required=True);v.add_argument('--review',required=True);v.set_defaults(func=validate)
 args=parser.parse_args();args.func(args)
if __name__=='__main__':main()
