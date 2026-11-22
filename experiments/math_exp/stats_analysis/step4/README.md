# Step 4 — Stazionarietà e cambiamenti strutturali

Il [notebook Ethereum](dataset_ethereum.ipynb) implementa il punto 4 della
[checklist](../../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md).
Eseguire prima lo step 1 e poi tutte le celle in un kernel nuovo del progetto.

Ogni controllo ha una cella Markdown con obiettivo e una cella di codice.
ADF e KPSS coprono livelli, log, dispersione e differenze in tre finestre
contigue di 8192 blocchi. Sono inclusi sensibilità a trend/lag e Phillips–Perron.
ADF e KPSS sulle medie giornaliere e sulle loro differenze coprono anche tutto
il periodo, a una scala diversa. I p-value locali sono esplorativi; le soglie
tabulate KPSS sono esplicite.

I cambiamenti di media sono studiati su tutti i giorni completi con ricerca
della data, bootstrap circolare a blocchi da 7 giorni e correzione Holm tra le
serie. Non è il test Bai–Perron: è un controllo di un singolo cambiamento medio
per serie e non copre break intragiornalieri. CUSUM è una diagnostica ausiliaria,
non robusta alla dipendenza seriale. Attività e gas limit vengono confrontati
nei 14 giorni prima e dopo ogni data candidata, senza attribuzioni causali.

I risultati numerici sono in `outputs/notebook_diagnostics/ethereum/step4/`.
`findings.md` viene aggiunto soltanto in presenza di anomalie verificate nell'esecuzione.
Non modifica i dati né decide automaticamente quali serie differenziare.
