"""Scarica dal FMI lo storico SDR Valuation (TSV) e aggiorna lo storico locale.
Dati non verificati/non riconoscibili non sovrascrivono lo storico esistente.
Esecuzione via GitHub Actions. Il FMI puo' cambiare l'HTML e il TSV.
"""
import csv
import calendar
import datetime as dt
import io
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

SOURCE = 'https://www.imf.org/external/np/fin/data/rms_sdrv.aspx'
ROOT = pathlib.Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'history.json'
LATEST = ROOT / 'rates.json'
DATE_PATTERNS = ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y', '%A, %B %d, %Y', '%A, %b %d, %Y', '%A, %d %B %Y', '%d %B %Y', '%d %b %Y', '%d-%b-%Y', '%d-%b-%y', '%d-%B-%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y%m%d', '%d.%m.%Y')


def number(s):
    s = str(s).strip().replace('\u00a0','').replace(',','')
    if re.fullmatch(r'[+-]?\d+(?:\.\d+)?',s):
        return float(s)
    return None


def day(s):
    s = re.sub(r'\s+', ' ', str(s).strip().strip('\"')).replace('Sept ', 'Sep ')
    s = re.sub(r'^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?:day)?,?\s+', '', s, flags=re.I)
    s = re.sub(r'(\d)(?:st|nd|rd|th)\b', r'\1', s, flags=re.I)
    for fmt in DATE_PATTERNS:
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def fetch_tsv():
    # Meccanismo di esportazione TSV della pagina SDR Valuation (ASP.NET WebForms).
    # E' distinto dall'archivio dei tassi rappresentativi del FMI.
    encoded = urllib.parse.urlencode({'__EVENTTARGET': 'lbnTSV', '__EVENTARGUMENT': ''}).encode('ascii')
    req = urllib.request.Request(SOURCE, data=encoded,
        headers={'User-Agent': 'Mozilla/5.0 (compatible; DSP-Historical-Converter/2.0)',
                 'Content-Type':'application/x-www-form-urlencoded','Accept':'text/tab-separated-values,text/plain,*/*'}, method='POST')
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read(25_000_000).decode('utf-8-sig', 'replace')


def parse_tsv(raw):
    if '<html' in raw[:500].lower() or 'Report date' not in raw[:3000]:
        raise ValueError('Il FMI non ha restituito lo storico TSV atteso')
    # In alcune versioni del sito il TSV e' una sequenza di tabelle senza colonne
    # regolari, con una riga data seguita dalle cinque righe delle valute.
    rows = [[c.strip() for c in r] for r in csv.reader(io.StringIO(raw), delimiter='\t')]
    blocks = []
    current = None
    today = dt.datetime.now(dt.timezone.utc).date()
    for cells in rows:
        if not any(cells): continue
        first = cells[0].strip().strip('"')
        val_date = day(first)
        if val_date is None:
            # Alcune versioni del TSV antepongono colonne vuote o l'etichetta 'Report date'.
            val_date = next((d for c in cells[:4] if (d := day(c)) is not None), None)
        if val_date and val_date <= today and val_date >= dt.date(1999, 1, 1):
            if current: blocks.append(current)
            current = {'date': val_date.isoformat(), 'usd_per_dsp': None, 'usd_per_eur': None, 'sum': []}
            continue
        if not current: continue
        label = re.sub(r'[^a-z0-9$=]', '', first.casefold())
        if not label:
            label = next((re.sub(r'[^a-z0-9$=]', '', c.casefold()) for c in cells[1:3] if c.strip()), '')
        values = [number(c) for c in cells[1:]]
        values = [x for x in values if x is not None]
        if label == 'euro' and len(values) >= 3:
            current['usd_per_eur'] = values[1]
            current['sum'].append(values[2])
        elif label in ('chineseyuan','japaneseyen','u.k.pound','u.k.poundsterling','u.s.dollar','poundsterling','ukpound','usdollar') and len(values) >= 3:
            current['sum'].append(values[2])
        elif label in ('sdr1=us$','sdr1=us$1.00','sdr1=us$1','sdr1=us$1.0') and values:
            current['usd_per_dsp'] = values[0]
    if current: blocks.append(current)
    output={}
    for item in blocks:
        e=item['usd_per_eur']; u=item['usd_per_dsp']
        # Preferisce il totale preciso (somma degli equivalenti) al valore
        # finale arrotondato del riepilogo, se le 5 righe sono presenti.
        if len(item['sum']) == 5:
            precise = round(sum(item['sum']), 9)
            if u is None or abs(precise-u)<0.0001: u=precise
            else: continue
        if e is None or u is None or not (0.3<e<3 and 0.5<u<3): continue
        output[item['date']]={'usd_per_dsp':u,'usd_per_eur':e}
    if len(output)<20:
        # Solo dati FMI pubblici: queste righe permettono di correggere il parser
        # anche se il layout del file viene cambiato dal sito.
        preview = '\n'.join(repr(row[:220]) for row in raw.splitlines()[:18])
        observed = [(b['date'], b['usd_per_dsp'], b['usd_per_eur'], len(b['sum'])) for b in blocks[:8]]
        raise ValueError(f'Archivio incompleto: {len(output)} record validi (minimo 20); blocchi data riconosciuti={len(blocks)}.\nPrime 18 righe ricevute dal FMI:\n{preview}\nPrimi blocchi: {observed}')
    return output


def main():
    new=parse_tsv(fetch_tsv())
    stored={}
    if HISTORY.exists():
        old=json.loads(HISTORY.read_text('utf-8'))
        stored=old.get('rates',{})
    stored.update(new)
    updated=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    merged={'source': SOURCE, 'updated_at':updated, 'rates':dict(sorted(stored.items()))}
    HISTORY.write_text(json.dumps(merged,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    latest_date=max(merged['rates'])
    latest=dict(merged['rates'][latest_date], valuation_date=latest_date, updated_at=updated, source=SOURCE)
    if LATEST.exists():
        prev=json.loads(LATEST.read_text('utf-8'))
        if prev.get('valuation_date','')>latest_date:
            latest=prev
    LATEST.write_text(json.dumps(latest,indent=2)+'\n',encoding='utf-8')
    print('Storico FMI aggiornato:',len(merged['rates']),'rilevazioni, ultime:',latest_date)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('Impossibile aggiornare lo storico; dati esistenti conservati:',repr(exc),file=sys.stderr)
        sys.exit(1)
