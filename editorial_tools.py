"""Portable editorial content hashes and review requirements; no publishing."""
from pathlib import Path
from datetime import datetime,time,timedelta,timezone
from zoneinfo import ZoneInfo
import hashlib,json,re
TZ=ZoneInfo('America/Sao_Paulo')
PROJECT='the-med-times'
SECTIONS=('pesquisa','clinica','saude-publica','formacao','inovacao','instituicoes')
REQUIRED_QA=('articleSourcesReviewed','editorialLabelsReviewed','imageRightsReviewed','compositionsReviewed','mobileSourceChecked')
CONTENT_FIELDS=('id','section','category','title','deck','date','contentType','sourceName','sourceUrl','paragraphs','implication','discussionPrompt','programStatus','eligibility','deadline','supplementarySources','additionalSources','studyUrl')
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest_bytes(value):return hashlib.sha256(value).hexdigest()
def article_digest(a):return digest_bytes(canonical({k:a[k] for k in CONTENT_FIELDS if k in a}))
