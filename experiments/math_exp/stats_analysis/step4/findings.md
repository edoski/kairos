# Step 4 — anomalie da discutere con Alessio

Risultati dell'esecuzione sul dataset Ethereum
`e7b17cfb-320d-4e6c-93c1-06dbc24f312d`, SHA-256
`4a8482552e3730ad68243a042eaa92b112450b36411f11a18947e9682d2e62e0`.
Periodo: 3 dicembre 2025–22 luglio 2026; 230 giornate complete.

## 1. La stazionarietà delle fee dipende dalla scala temporale

Nei test locali **19 confronti ADF/KPSS su 36 rifiutano entrambe le ipotesi nulle**:
non è una conferma della stazionarietà. Accade per base fee e log base fee in
tutte e tre le finestre, per tutte le log priority fee e la dispersione, e per
le priority fee originali nelle finestre centrale e finale.

Le finestre contengono 8192 blocchi contigui ciascuna, a inizio, centro e fine
campione; coprono circa 27–29 ore l'una, non tutto il periodo. Nella finestra
centrale la lettura rimane invariata con intercetta/trend e 1, 10 o 30 lag.

Sulle **medie giornaliere dell'intero periodo**, log base fee, log p50 e
dispersione sono compatibili con non stazionarietà; X e log p90 danno invece
esiti discordanti. Questo quadro può riflettere cambiamenti di livello o
specificazione inadeguata: non dimostra da solo una radice unitaria.
I p-value ADF/KPSS sono esplorativi, senza correzione per confronti multipli;
i p-value KPSS ai limiti 0,01 e 0,10 sono soglie tabulate.

**Da discutere:** trattare le fee come globalmente stazionarie rischia di
mescolare periodi diversi. Le differenze risultano più stabili, ma X è
limitato in [0, 2] e la base fee ha una ricorrenza deterministica: non va
differenziato tutto automaticamente.

## 2. Cinque segnali di cambiamento delle medie si concentrano ad aprile

| Variabile, media giornaliera | Data candidata UTC | Media prima | Media dopo | p bootstrap/Holm |
| --- | --- | ---: | ---: | ---: |
| X | 8 aprile 2026 | 1,01456 | 1,01058 | 0,010 |
| log base fee | 17 aprile 2026 | 18,1451 | 19,1048 | 0,010 |
| log priority fee p50 | 13 aprile 2026 | 15,1840 | 17,0506 | 0,010 |
| log priority fee p90 | 15 aprile 2026 | 20,5173 | 20,8546 | 0,038 |
| Dispersione log p90−p50 | 12 aprile 2026 | 5,3410 | 3,8026 | 0,010 |

I log sono `log(1 + fee in wei/gas)`. Le medie sono quelle dei segmenti
precedente e successivo alla data candidata, non finestre di 14 giorni.
Il cambiamento di X è piccolo in termini assoluti, circa −0,004.

Metodo: ricerca del maggiore spostamento di media, almeno 14 giorni per
segmento, 499 bootstrap circolari con blocchi da 7 giorni, correzione Holm
tra le cinque serie. La risoluzione minima del p-value bootstrap è 0,002.
Le date localizzano il massimo contrasto fra due segmenti; non sono date
causali certe né dimostrano un cambiamento permanente.
Il metodo è esplorativo, assume dipendenza di breve periodo e non è
Bai–Perron; la sensibilità alla lunghezza dei blocchi bootstrap non è verificata.

## 3. Il gas limit non mostra un salto comparabile attorno alle date

Nelle finestre di 14 giorni prima e dopo il 13 aprile, la media del gas limit
resta circa **59,99 milioni**. La media delle transazioni per blocco passa da
**346,46 a 295,48**, mentre la base fee media passa da **0,139 a 0,795 gwei/gas**.
Queste associazioni interne al dataset non identificano una causa economica,
un aggiornamento di protocollo o un errore nei dati.

**Da discutere:** approfondire il periodo di aprile prima di adottare un unico
kernel di transizione valido per tutto il campione. Nessuna causa esterna è
stata verificata in questo step.

Fonti: [notebook](dataset_ethereum.ipynb),
[test locali](../../../../outputs/notebook_diagnostics/ethereum/step4/stationarity_tests.csv),
[test giornalieri](../../../../outputs/notebook_diagnostics/ethereum/step4/daily_stationarity_tests.csv),
[cambiamenti di media](../../../../outputs/notebook_diagnostics/ethereum/step4/mean_shift_tests.csv),
[attività attorno alle date](../../../../outputs/notebook_diagnostics/ethereum/step4/break_activity_context.csv).
