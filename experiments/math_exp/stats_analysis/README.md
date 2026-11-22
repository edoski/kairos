# Analisi statistica Ethereum — step 1–11

Gli undici notebook implementano i punti della checklist, seguendo la
[Statistical Analysis Checklist](../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md).
Ogni punto ha una cella Markdown con titolo e breve obiettivo, seguita dal codice.
I commenti spiegano le scelte che incidono sull'interpretazione; nessuna riga del
dataset viene eliminata automaticamente perché estrema.

| Step | Notebook | Contenuto | Findings |
| --- | --- | --- | --- |
| 1 | [Integrità e preprocessing](step1/dataset_ethereum.ipynb) | Integrità, unità, trasformazioni, estremi e deadline | [Anomalie](step1/findings.md) |
| 2 | [Descrittive](step2/dataset_ethereum.ipynb) | Quantili, forma, serie temporali, distribuzioni, Q–Q e relazioni | [Anomalie](step2/findings.md) |
| 3 | [Ricorrenza EIP-1559](step3/dataset_ethereum.ipynb) | Aritmetica intera e tutte le coppie padre–figlio | Nessuna discrepanza |
| 4 | [Stazionarietà e break](step4/dataset_ethereum.ipynb) | ADF, KPSS, Phillips–Perron, sensibilità e cambiamenti di media | [Anomalie](step4/findings.md) |
| 5 | [Dipendenza e lag](step5/dataset_ethereum.ipynb) | ACF/PACF, Ljung–Box, AR, confronti e previsioni rolling | [Anomalie](step5/findings.md) |
| 6 | [Volatilità](step6/dataset_ethereum.ipynb) | Innovazioni, ARCH, stato ritardato, GARCH e asimmetria | [Anomalie](step6/findings.md) |
| 7 | [Code ed estremi](step7/dataset_ethereum.ipynb) | IQR, Q–Q, Jarque–Bera, cluster, Student-t e GPD esplorativa | [Anomalie](step7/findings.md) |
| 8 | [Dipendenza congiunta](step8/dataset_ethereum.ipynb) | Cross-lag, residui, congestione, p50/p90 e dispersione | [Anomalie](step8/findings.md) |
| 9 | [Sufficienza dello stato](step9/dataset_ethereum.ipynb) | Stato osservabile, lag aggiuntivi, transazioni, intervalli e periodi | [Anomalie](step9/findings.md) |
| 10 | [Candidati stocastici](step10/dataset_ethereum.ipynb) | Utilizzo bounded, GARCH, regimi osservati, miscela e kernel congiunto | [Anomalie](step10/findings.md) |
| 11 | [Validazione e Bellman](step11/dataset_ethereum.ipynb) | Score probabilistici rolling, calibrazione e politiche held-out | [Anomalie](step11/findings.md) |

## Ambiente e dati

Dalla radice del repository:

```bash
uv sync --locked
```

In VS Code selezionare `.venv/bin/python` come kernel e riavviarlo dopo
l'installazione. Il gruppo `dev` comprende le librerie statistiche e Jupyter;
non usare un kernel Anaconda di un altro ambiente.

Il dataset Ethereum è l'UUID `e7b17cfb-320d-4e6c-93c1-06dbc24f312d`,
con **1.654.536 blocchi**, dal 23.935.694 al 25.590.229. Manifest e Parquet
originali sono verificati con Blockweaver. Le fee sono in **wei/gas**;
le conversioni descrittive usano **gwei/gas**, i log usano wei/gas.

Se mancano i dati, estrarre dall'[archivio Zenodo](https://zenodo.org/records/22094893/files/kairos-ccnc-2027-datasets.tar.gz)
la cartella `KAIROS-CCNC-2027/outputs/datasets` in
`outputs/zenodo-22094893/datasets`. In alternativa impostare
`KAIROS_DATASETS_DIR` alla cartella `datasets` che contiene le directory UUID.

## Ordine di esecuzione e risultati

1. Eseguire lo step 1 con `EXPORT_DIAGNOSTICS=True`.
2. Eseguire gli step 2–5, ciascuno in un kernel nuovo.
3. Eseguire gli step 6 e 7 dopo lo step 5: usano le innovazioni esportate.
4. Lo step 8 dipende solo dallo step 1 e può essere eseguito separatamente.
5. Eseguire gli step 9–11 in kernel nuovi. Lo step 9 rilegge lo step 1; il 10
   usa anche le diagnostiche dello step 7; l'11 importa gli helper del 10 e
   ristima i candidati sui dati dello step 1.

Gli artefatti numerici sono in `outputs/notebook_diagnostics/ethereum/stepN/`.
I notebook salvano tabelle e figure dell'esecuzione reale; dopo una modifica al
preprocessing rieseguire gli step dipendenti. I `findings.md`, accanto ai notebook,
raccolgono soltanto anomalie osservate, evidenze e domande da discutere con Alessio.
Lo step 3 non ha un file findings quando non emergono discrepanze.

Verifica del 21 novembre 2026: tutti gli undici notebook eseguiti dall'inizio alla
fine in kernel nuovi del progetto; formato, struttura delle celle e Ruff verificati.
Figure salvate ispezionate visivamente. L'anteprima HTML locale integrale non è
stata ispezionata: il browser blocca gli URL `file:`. L'esportazione HTML è stata
verificata come generazione; per la lettura completa aprire i notebook in VS Code
con il kernel del progetto.

Lo step 1 riusa il riscontro RPC salvato, riconciliando i valori con il dataset:
**7 conferme e 4 casi irrisolti**. Non rappresenta una nuova verifica di rete né
una fonte indipendente. `REFRESH_RPC=True` ritenta solo i casi irrisolti, conservando
le conferme precedenti. L'assenza di risposta non viene classificata come errore.

## Ambito e interpretazione

Descrittive e ricorrenza usano tutto il dataset. Lo step 4 combina finestre
consecutive a scala blocco con aggregati giornalieri dell'intero periodo;
il controllo dei break riguarda cambiamenti di media e non sostituisce
una ricerca completa di break multipli Bai–Perron.

Gli step 5–8 stimano i modelli sugli ultimi **30.000 blocchi consecutivi**,
dal **18 al 22 luglio 2026**, con separazione cronologica training/validation/testing.
Le distribuzioni descrittive degli step 7–8 possono usare l'intero campione,
come indicato nelle celle. Le conclusioni dei modelli restano locali a questa
finestra: i p-value esplorativi e i vantaggi fuori campione non dimostrano
stabilità nei sette mesi. I lag non vengono stimati su serie decimate.

Al decision origin dopo il closed parent sono disponibili soltanto dati chiusi:
`base_log_fee_return[n]` e `block_interval_next[n]` guardano a n+1 e sono esiti,
non regressori disponibili a n. I modelli lineari dell'utilizzo sono diagnostici;
non sono un kernel generativo capace di rispettare automaticamente il supporto [0, 2].

Gli step 9–11 usano tre finestre disgiunte di 30.000 blocchi ciascuna,
all'inizio, al centro e alla fine del dataset: **3–8 dicembre 2025**,
**27–31 marzo 2026**, **18–22 luglio 2026**. Ogni periodo separa 20.000 blocchi
training, 5.000 validation e 5.000 testing. Si riusano tutte le osservazioni
consecutive per i lag e i forecast; non sono sette mesi di valutazione continua.

Lo step 11 valuta cinque candidati con **150.000 previsioni rolling**, ciascuna
su 256 campioni congiunti. La scelta è locale alla validation di ogni periodo.
I kernel stocastici dello step 10 omettono B esplicito; lo step 9 analizza invece
lo stato completo e suoi ampliamenti. Nessun confronto dimostra la proprietà
di Markov o la validità globale della distribuzione di transizione.

Il benchmark di Bellman dello step 11 usa il kernel empirico congiunto training,
griglia e quadratura finite, gas limit futuro fisso e fallback esplicito fuori
dominio. Confronta K=2/3/5 sulle stesse origini e offerte osservabili dal parent.
I costi assumono inclusione: offerte ex ante e proxy P50 retrospettivo restano
separati. La riduzione del costo medio risk-neutral non coincide con la media
dei risparmi percentuali per origine. Dettagli e limiti nei README dei tre step.
