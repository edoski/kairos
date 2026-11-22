# Step 9 — Sufficienza predittiva dello stato

Il [notebook Ethereum](dataset_ethereum.ipynb) implementa gli otto punti della
[checklist, sezione 9](../../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md).
Ogni punto ha una cella Markdown con obiettivo e il relativo codice.
Eseguire prima lo step 1, poi tutte le celle con Python 3.11 del progetto.

Lo stato baseline usa `log(B_n)`, `X[n−1]` e `log1p(p50[n−1])` per prevedere
`X[n]` e `log1p(p50[n])`. La base fee `B_n` è ricostruita dai dati del closed
parent con la funzione esistente `kairos.temporal._forming_child_base_fee` e
confrontata esattamente con l'osservata. Non si usano utilizzo, priority fee,
numero di transazioni o timestamp del blocco target come regressori.
Le fee originali sono in wei/gas; l'intervallo osservabile è in secondi.

Sono fissate tre finestre disgiunte da 30.000 blocchi consecutivi, all'inizio,
al centro e alla fine del dataset. Ogni finestra ha 20.000 righe training,
5.000 validation e 5.000 testing; le prime dieci righe training forniscono i
lag, lasciando 19.990 target training comuni a tutte le specifiche.

I confronti aggiungono separatamente X al lag 2, p50 al lag 2, entrambi,
log1p del numero di transazioni del parent e l'intervallo precedente del
parent. I lag congiunti fino a 5 e 10 sono considerati solo se Ljung–Box(50)
sui residui baseline training segnala dipendenza. AIC, BIC e LR usano una
likelihood gaussiana condizionata di lavoro; i coefficienti aggiunti sono
anche verificati con Wald HAC a 50 lag.

Le previsioni rolling a un blocco sono ristimate ogni 1.000 origini sui
10.000 target precedenti. Gli input di ogni origine usano la storia già
osservata; nessun fit include il target corrente o quelli successivi.
La validation seleziona il MSE minimo; il testing misura il modello scelto
e tutte le specifiche già fissate, senza riselezionare. L'audit dei fit rende
controllabile la separazione temporale. Un self-check modifica target futuri
per verificare che le previsioni precedenti non cambino.

Si confrontano i tre periodi e due fasce osservabili di congestione del
parent. La soglia di congestione alta è il 95° percentile di X laggato nel
solo training di ciascun periodo. Gli effetti per fascia sono descrittivi;
i confronti su tutti i 5.000 target hanno anche intervalli HAC della
differenza di perdita. P-value e confronti multipli restano esplorativi.

CSV, previsioni Parquet e JSON con identità e hash della fonte sono in
`outputs/notebook_diagnostics/ethereum/step9/`. `findings.md` viene aggiunto
soltanto per anomalie osservate nell'esecuzione reale.

Questi modelli lineari verificano la media predittiva e segnalano eventuali
previsioni fuori da [0, 2]. Non costituiscono un kernel generativo per X e
non dimostrano la proprietà di Markov. La generalizzazione oltre i tre
brevi periodi richiede ulteriori evidenze.
