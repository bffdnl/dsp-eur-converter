# Convertitore DSP → Euro (storico FMI)

Sito statico per **GitHub Pages**, con scelta di una data storica e conversione DSP/EUR sulla base delle rilevazioni [SDR Valuation FMI](https://www.imf.org/external/np/fin/data/rms_sdrv.aspx).

## Installazione sul repository `bffdnl/dsp-eur-converter`

**Caricare il contenuto di questa cartella nella radice del repository**, non lo ZIP né un'ulteriore cartella contenitore. In particolare:

- `index.html`, `logo.png`, `history.json`, `rates.json`, `README.md`
- `scripts/update_history.py`, `scripts/update_rates.py`
- `.github/workflows/deploy.yml`

**Il workflow `deploy.yml` deve stare in `.github/workflows/` alla radice del repository.** Se nel repository sono presenti altri workflow per GitHub Pages che distribuiscono contenuti diversi, disabilitarli per evitare conflitti.

Aprire `Settings → Pages → Source: GitHub Actions`. In `Actions` avviare `Pubblica sito e aggiorna storico FMI → Run workflow`. Il sito previsto è https://bffdnl.github.io/dsp-eur-converter/.

## Come vengono gestiti i tassi

- All'avvio della pagina vengono letti i file locali `history.json` e `rates.json` generati dal workflow: il browser del collega non deve collegarsi direttamente al FMI.
- Lo script `scripts/update_history.py` invia al FMI una richiesta di esportazione TSV dello storico (`__EVENTTARGET=lbnTSV`) e analizza le righe giornaliere con il valore in USD del DSP e il cambio EUR/USD dello stesso giorno. Se la struttura non è riconosciuta o ci sono meno di 20 date valide, **non sovrascrive lo storico**.
- `scripts/update_rates.py` prova anche a leggere la quotazione più recente dalla pagina giornaliera. Se fallisce, il workflow conserva i dati già presenti.
- Lo storico inizialmente è **vuoto**: **la funzione storica diventa operativa soltanto dopo che il workflow riesce a scaricare e interpretare lo storico del FMI.** Non sono inseriti tassi storici inventati.
- La conversione è `importo DSP × (USD per DSP / USD per EUR)`.
- Se manca la data richiesta, viene usata la quotazione con **minore distanza in giorni** fra quelle presenti. In caso di pari distanza, si preferisce la **data precedente**. La data realmente utilizzata è mostrata in modo esplicito.
- **Fuori dall'intervallo dell'archivio è ammesso solo uno scarto massimo di 7 giorni** (weekend/festività); il sito non usa un cambio di mesi o anni prima.
- Le cifre derivano dai valori/arrotondamenti del FMI e potrebbero non coincidere perfettamente con altre tabelle di tassi rappresentativi.

## Verifiche consigliate

1. Aprire la scheda `Actions` ed esaminare il log dei passi **Scarica storico FMI** e **Aggiorna tasso corrente**. Un workflow verde significa che il sito è stato distribuito, **non garantisce** che il download FMI sia riuscito.
2. Aprire `history.json` e verificare che `rates` contenga molte date, non `{}`.
3. Scegliere una data presente nell'archivio e confrontare la conversione con il FMI.
4. Provare un sabato o una domenica: il sito deve evidenziare la data effettiva utilizzata.

## Limiti

Il download in TSV del FMI è un meccanismo web non documentato come API stabile. L'integrazione **non è stata testata dal vivo contro il server FMI in questo ambiente**. Se il FMI cambia il formato dei dati, servirà aggiornare `update_history.py`. Non usare valori non verificati per adempimenti ufficiali.

Il sigillo FMI potrebbe essere soggetto a restrizioni d'uso. Questo strumento non è ufficiale e non implica approvazione del FMI.
