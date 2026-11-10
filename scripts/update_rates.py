"""Aggiorna rates.json dalla pagina pubblica SDR Valuation dell'FMI.
La pagina HTML non costituisce un'API stabile: in caso di errore NON sovrascrive i dati.
"""
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.request
from bs4 import BeautifulSoup

SOURCE = 'https://www.imf.org/external/np/fin/data/rms_sdrv.aspx'
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'rates.json'
MONTHS = {m: i for i, m in enumerate('January February March April May June July August September October November December'.split(), 1)}
CURRENCIES = ('chinese yuan', 'euro', 'japanese yen', 'u.k. pound', 'u.s. dollar')

def num(value):
    match = re.search(r'[+-]?\d+(?:[.,]\d+)?', value.replace('\xa0', ' '))
    if not match: raise ValueError('Numero non trovato: ' + value[:50])
    return float(match.group().replace(',', '.'))

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ', strip=True)
    point = text.lower().find('sdr rates as of')
    if point == -1: raise ValueError('Intestazione SDR rates as of assente')
    date_match = re.search(r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})', text[point:point+1500], re.I)
    if not date_match: raise ValueError('Data FMI non identificata')
    month, day, year = date_match.groups()
    date = dt.date(int(year), MONTHS[month.title()], int(day))
    today = dt.datetime.now(dt.timezone.utc).date()
    if date > today + dt.timedelta(days=1) or date < today-dt.timedelta(days=14):
        raise ValueError('Data FMI fuori intervallo: '+date.isoformat())
    equivalents = {}; euro_rate = None
    for row in soup.find_all('tr'):
        cells = row.find_all(['td','th'], recursive=False)
        if len(cells)<4: continue
        name=cells[0].get_text(' ',strip=True).lower()
        for currency in CURRENCIES:
            if currency in name:
                amount,rate,value=(num(cells[i].get_text(' ',strip=True)) for i in (1,2,3))
                if min(amount,rate,value)<=0: raise ValueError('Dato non positivo')
                equivalents[currency]=value
                if currency=='euro': euro_rate=rate
    if len(equivalents)!=5 or euro_rate is None: raise ValueError('Non sono presenti tutte le cinque valute')
    total=sum(equivalents.values())
    if not (0.5<total<3 and 0.3<euro_rate<3): raise ValueError('Valori non plausibili')
    return {'usd_per_dsp':round(total,9),'usd_per_eur':euro_rate,'valuation_date':date.isoformat(),'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source':SOURCE}

def main():
    request=urllib.request.Request(SOURCE,headers={'User-Agent':'Mozilla/5.0 (compatible; DSP-Euro-Web/1.0)','Accept':'text/html'})
    with urllib.request.urlopen(request,timeout=25) as response:
        body=response.read(4_000_000).decode('utf-8',errors='replace')
    data=parse(body)
    if OUT.exists():
        old=json.loads(OUT.read_text(encoding='utf-8'))
        if data['valuation_date']<old.get('valuation_date',''):
            raise ValueError('Il FMI ha fornito una data precedente a quella salvata')
        if data['valuation_date']==old.get('valuation_date','') and abs(data['usd_per_dsp']-old['usd_per_dsp'])<1e-9 and abs(data['usd_per_eur']-old['usd_per_eur'])<1e-9:
            print('Nessun nuovo tasso'); return
    OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Nuovo tasso salvato:', data)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('Aggiornamento non riuscito; tassi conservati:',exc,file=sys.stderr)
        sys.exit(1)
