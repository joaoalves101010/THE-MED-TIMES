"""Explicit editorial configuration. Never infer a publication date from UTC now."""
from pathlib import Path
from datetime import date,datetime
from zoneinfo import ZoneInfo
import json,re,os
ROOT=Path(__file__).resolve().parent
CONFIG_PATH=Path(os.environ.get('TMT_EDITION_CONFIG',ROOT/'edition.json')).resolve()
CONFIG=json.loads(CONFIG_PATH.read_text())
assert CONFIG['schemaVersion']==1
assert re.fullmatch(r'\d{3,}',CONFIG['editionId'])
assert CONFIG['timezone']=='America/Sao_Paulo'
assert CONFIG['publicationTime']=='08:00'
LOCAL_DATE=date.fromisoformat(CONFIG['localDate']);TZ=ZoneInfo(CONFIG['timezone'])
cutoff=datetime.fromisoformat(CONFIG['sourceCutoff']);assert cutoff.tzinfo and cutoff.astimezone(TZ).date()<=LOCAL_DATE
assert date.fromisoformat(CONFIG['recentSince'])<=LOCAL_DATE
EDITION_ID=CONFIG['editionId'];DATE_ISO=LOCAL_DATE.isoformat();EDITION_LABEL=CONFIG['editionLabel'];RECENT_SINCE=CONFIG['recentSince']
MONTHS=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
WEEKDAYS=['Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo']
def long_date(value):
 d=date.fromisoformat(value) if isinstance(value,str) else value
 return f'{d.day} de {MONTHS[d.month-1]} de {d.year}'
DATE_LONG=long_date(LOCAL_DATE);DATE_SHORT=f'{LOCAL_DATE.day} de {MONTHS[LOCAL_DATE.month-1]}'
DATE_WEEKDAY=f'{WEEKDAYS[LOCAL_DATE.weekday()]}, {DATE_LONG}';DATE_WEEKDAY_SHORT=f'{WEEKDAYS[LOCAL_DATE.weekday()]}, {DATE_SHORT}'
DATE_DOTTED=LOCAL_DATE.strftime('%d.%m.%Y');YEAR=str(LOCAL_DATE.year)
BASELINE=(EDITION_ID=='003' and DATE_ISO=='2026-10-24')
