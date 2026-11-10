# Convertitore DSP → EUR (sito web)

Pagina web indipendente per convertire DSP (SDR) in euro, in base ai valori pubblicati dall'FMI.
Non affiliata né approvata dal Fondo Monetario Internazionale.

## Pubblicazione gratuita su GitHub Pages

1. Crea un account gratuito su https://github.com se necessario.
2. Crea un repository **pubblico** chiamato `convertitore-dsp` (ramo `main`).
3. Carica **tutti i file e le cartelle** del pacchetto nel repository, inclusa la cartella nascosta `.github/workflows/`.
   Alternativa più affidabile: usa GitHub Desktop e fai `Commit` + `Push` dell'intera cartella.
4. Nel repository vai su **Settings → Pages → Build and deployment → Source: GitHub Actions**.
5. In **Settings → Actions → General → Workflow permissions**, seleziona **Read and write permissions** e salva.
6. In **Actions**, apri `Pubblica convertitore e aggiorna tassi` e seleziona **Run workflow** (se necessario abilita le Actions).
7. Dopo il completamento, il sito si trova all'indirizzo `https://TUO-USERNAME.github.io/convertitore-dsp/`.

La procedura pianificata gira nei giorni feriali circa alle 16:15 UTC (l'orario esatto non è garantito). Poiché il sito FMI non fornisce un'API stabile della tabella giornaliera, un cambiamento del formato può interrompere l'aggiornamento; in tal caso i dati precedenti restano visibili e la pagina segnala quando sono vecchi.

## Prima pubblicazione

`rates.json` contiene **tassi iniziali di esempio forniti dalla precedente versione desktop**, datati 10/11/2026, non una nuova verifica live. Avvia l'aggiornamento nella scheda Actions e confronta il risultato con il sito FMI prima di diffonderlo ai colleghi.

## Sicurezza e licenze

Non raccoglie importi digitati né invia le conversioni a un server: i calcoli avvengono nel browser. Il logo FMI è un marchio istituzionale; verifica le condizioni d'uso e non presentare lo strumento come ufficiale. Questo pacchetto non include una dichiarazione di licenza sui marchi FMI.
