"""Importa lo storico SDR Valuation del FMI nel formato TSV storico.

Nel TSV la data si ripete su ogni riga-valuta, mentre le righe di totale
hanno la data vuota. Si escludono le date prima dell'introduzione dell'euro.
Tra il 1999 e il 30/09/2016 il paniere ha quattro valute; dal 01/10/2016 ne ha cinque.
Non modifica i JSON esistenti se l'importazione non supera le verifiche.
"""
import csv
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


def number(value):
    s = str(value).strip().replace('\u00a0', '').replace(',', '')
    if re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)', s):
        return float(s)
    return None


def date_of(value):
    s = str(value).strip().strip('"')
    for fmt in ('%d-%b-%Y', '%d-%B-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def fetch_tsv():
    # L'endpoint di esportazione deriva dal pulsante TSV della pagina FMI.
    payload = urllib.parse.urlencode({'__EVENTTARGET': 'lbnTSV', '__EVENTARGUMENT': ''}).encode('ascii')
    req = urllib.request.Request(SOURCE, data=payload, method='POST', headers={
        'User-Agent': 'Mozilla/5.0 (compatible; DSP-Converter/3.0)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/tab-separated-values,text/plain,*/*',
    })
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read(30_000_000).decode('utf-8-sig', 'replace')


def parse_tsv(raw):
    if '<html' in raw[:500].lower() or 'Report date' not in raw[:3000]:
        raise ValueError('Il FMI non ha restituito la tabella TSV attesa')
    out = {}
    active_date = None
    euro_rate = None
    equivalents = []
    summary = None
    today = dt.datetime.now(dt.timezone.utc).date()
    dates_seen = 0

    def finalize():
        if active_date is None or euro_rate is None:
            return
        # Il paniere del DSP comprendeva quattro valute fino al 30/09/2016.
        # Dal 01/10/2016 include anche lo yuan cinese (cinque valute).
        required_count = 4 if active_date < dt.date(2016, 10, 1) else 5
        if len(equivalents) != required_count:
            return
        usd_dsp = round(sum(equivalents), 9)
        if summary is not None and abs(usd_dsp - summary) > 0.0002:
            return
        if not (0.3 < euro_rate < 3 and 0.5 < usd_dsp < 3):
            return
        out[active_date.isoformat()] = {
            'usd_per_dsp': usd_dsp,
            'usd_per_eur': euro_rate,
        }

    for row in csv.reader(io.StringIO(raw), delimiter='\t'):
        cells = [c.strip() for c in row]
        cells.extend([''] * max(0, 6 - len(cells)))
        d = date_of(cells[0])
        if d is not None:
            if d != active_date:
                finalize()
                active_date = d if dt.date(1999, 1, 1) <= d <= today else None
                euro_rate, equivalents, summary = None, [], None
                dates_seen += 1
            if active_date is None:
                continue
            currency = re.sub(r'\s+', ' ', cells[1].casefold()).strip()
            # Righe valuta: data | nome valuta | ammontare | cambio | equivalente USD | variazione
            equivalent = number(cells[4])
            if currency in ('euro', 'chinese yuan', 'japanese yen', 'u.k. pound', 'u.s. dollar') and equivalent is not None:
                equivalents.append(equivalent)
            if currency == 'euro':
                euro_rate = number(cells[3])
            continue

        if active_date is None:
            continue
        # Riepilogo: [vuoto] [vuoto] [vuoto] 'SDR1 = US$' valore [vuoto].
        # Cerchiamo in QUALSIASI cella per evitare variazioni di tabulazione.
        for i, cell in enumerate(cells):
            label = re.sub(r'\s+', '', cell.casefold())
            if label.startswith('sdr1=us$'):
                summary = next((v for c in cells[i+1:] if (v := number(c)) is not None), None)
                break
    finalize()
    if len(out) < 20:
        snippet = '\n'.join(repr(line[:180]) for line in raw.splitlines()[:16])
        raise ValueError(f'Archivio incompleto: {len(out)} date valide; blocchi distinti visti={dates_seen}. Prime righe:\n{snippet}')
    return out


def main():
    new = parse_tsv(fetch_tsv())
    previous = {}
    if HISTORY.exists():
        previous = json.loads(HISTORY.read_text(encoding='utf-8')).get('rates', {})
    previous.update(new)
    updated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    rates = dict(sorted(previous.items()))
    latest_date = max(rates)
    history_out = {'source': SOURCE, 'updated_at': updated, 'rates': rates}
    latest_out = dict(rates[latest_date], valuation_date=latest_date, updated_at=updated, source=SOURCE)
    # Scriviamo solo dopo aver superato tutte le verifiche.
    HISTORY.write_text(json.dumps(history_out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if LATEST.exists():
        existing_latest = json.loads(LATEST.read_text(encoding='utf-8'))
        if existing_latest.get('valuation_date', '') > latest_date:
            latest_out = existing_latest
    LATEST.write_text(json.dumps(latest_out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Storico FMI importato: {len(new)} rilevazioni dal TSV; {len(rates)} record totali. Ultima data: {latest_date}.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Errore aggiornamento storico FMI: {error!r}', file=sys.stderr)
        sys.exit(1)
