"""Policy v2: complete daily topic renewal, with editorial semantic review.
Deterministic duplicate checks are necessary, not a claim to understand all aliases.
"""
import re,unicodedata
from urllib.parse import urlsplit,unquote,parse_qsl,urlencode
from editorial_tools import canonical,digest_bytes
POLICY_VERSION=2

def normalized_text(value):
 value=unicodedata.normalize('NFKD',value.casefold())
 return ' '.join(re.findall(r'\w+', ''.join(c for c in value if not unicodedata.combining(c))))

def normalized_url(value):
 u=urlsplit(value);assert u.scheme in ('http','https') and u.hostname,'Invalid primary source URL'
 # Preserve known article identity parameters, never tracking/query aliases.
 identity={'id','article','articleid','article_id','story','storyid','story_id','pid','p','doi'}
 query=urlencode(sorted((k.casefold(),v) for k,v in parse_qsl(u.query) if k.casefold() in identity))
 return (u.hostname.lower().removeprefix('www.')+unquote(u.path).rstrip('/')).casefold()+('?' + query if query else '')

def fingerprint(a):
 return {'id':a['id'],'source':normalized_url(a['sourceUrl']),
 'title':normalized_text(a['title']),'body':digest_bytes(normalized_text(' '.join(a['paragraphs'])).encode())}

def validate_renewal(articles,previous,review,previous_edition):
 assert review.get('policyVersion')==POLICY_VERSION,'Daily renewal policy v2 required'
 novelty=review.get('novelty',{})
 assert novelty.get('previousEditionId')==previous_edition,'Novelty compared against wrong edition'
 assert novelty.get('semanticReviewCompleted') is True,'Whole-edition semantic novelty review required'
 assert novelty.get('relevantArchivesReviewed') is True and len(novelty.get('archiveReviewNotes','').split())>=8,'Review relevant archives to prevent topic rotation'
 assert len(novelty.get('method','').split())>=8,'Explain semantic comparison method; aliases/rewrites are not new topics'
 assert len(articles)==len(previous)==96,'Renewal requires 96 current and previous topics'
 old=[fingerprint(a) for a in previous];new=[fingerprint(a) for a in articles]
 for field in ('id','source','title','body'):
  values=[r[field] for r in new]
  assert len(set(values))==96,'Duplicate candidate '+field
  assert not set(values)&{r[field] for r in old},'Reused previous '+field
 assert set(review.get('relevantUpdateIds',[]))=={a['id'] for a in articles},'All 96 topics must be new; partial-update release rejected'
 keys=[]
 for a in articles:
  r=review['articles'][a['id']]
  assert r.get('status')=='verified','Carry-forward forbidden under daily renewal policy'
  n=r.get('novelty',{})
  assert n.get('isNewTopic') is True and n.get('comparedAgainstAllPreviousTopics') is True and n.get('comparedAgainstAllCandidateTopics') is True,'Explicit topic-level semantic review required'
  assert len(n.get('differenceFromPrevious','').split())>=8,'Explain why this is a new topic, not an alias or rewrite'
  key=normalized_text(n.get('topicKey',''));assert key,'Original topic key required';keys.append(key)
 assert len(set(keys))==96,'Duplicate semantic topic keys'
 return {'policyVersion':POLICY_VERSION,'previousEditionId':previous_edition,'newTopicCount':96,'reusedTopicCount':0,
 'previousContentDigest':digest_bytes(canonical(sorted(old,key=lambda r:r['id']))),
 'currentContentDigest':digest_bytes(canonical(sorted(new,key=lambda r:r['id'])))}
