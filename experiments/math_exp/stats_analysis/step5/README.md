# Step 5 — Dipendenza seriale e scelta dei lag

Notebook: [dataset_ethereum.ipynb](dataset_ethereum.ipynb).

Riferimento: [Statistical Analysis Checklist](../../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md).

Il notebook ricarica lo step 1 e lavora sugli ultimi **30.000 blocchi contigui**:
20.000 training, 5.000 validation e 5.000 testing. Le prime dieci righe forniscono
i lag; AR(1), AR(2), AR(5) e AR(10) usano gli stessi target di training.

Ogni punto della checklist ha una sezione con scopo e codice: ACF/PACF di livelli,
log, differenze e residui; Ljung–Box a 5, 10, 20 e 50; contributo dei lag con Wald
HAC; LR, AIC e BIC gaussiani condizionati; previsioni a un blocco con finestra di
10.000 target e ristima ogni 1.000 origini. I lag sono scelti sul MSE validation;
il testing misura il risultato senza cambiare la selezione.

Gli output sono in `outputs/notebook_diagnostics/ethereum/step5/`. Il file
`mean_residuals.parquet` conserva blocco, timestamp, ruolo, innovazioni e numero
di lag; viene usato dagli step 6 e 7. I residui training sono in-sample,
validation e testing sono previsioni rolling fuori campione. `analysis_scope.json`
registra identità della fonte, intervallo e parametri.

I modelli lineari sono diagnostici: non costituiscono un kernel di transizione
per simulare l'utilizzo fuori da [0, 2]. I risultati valgono per la finestra
analizzata; p-value e confronti multipli richiedono interpretazione congiunta
con gli effetti predittivi. `findings.md` riporta solo anomalie effettivamente
osservate e verificate dopo l'esecuzione.
