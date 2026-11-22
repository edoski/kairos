# Step 6 — Eteroschedasticità e dinamiche della volatilità

Notebook: [dataset_ethereum.ipynb](dataset_ethereum.ipynb).

Riferimento: [Statistical Analysis Checklist](../../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md).

Eseguire prima gli step 1 e 5. Il notebook verifica la fonte e ricarica le
innovazioni delle medie selezionate nello step 5. Usa 5.000 residui validation
per stimare la varianza e i successivi 5.000 testing per misurarla.

Le sezioni coprono residui e quadrati, deviazione standard mobile, ARCH-LM e
Ljung–Box dei quadrati a 5, 10, 20 e 50 lag; associazioni HAC con lo stato del
blocco precedente; varianza per fascia di congestione; GARCH(1,1) e GJR-GARCH
quando ARCH emerge sulla validation. I parametri della varianza restano fissati
prima del testing; l'aggiornamento sequenziale usa solo l'innovazione precedente.

QLIKE confronta le previsioni con la varianza costante entro ciascuna variabile.
Il GJR verifica l'asimmetria; EGARCH e regimi latenti non vengono aggiunti
automaticamente sulla sola base della non normalità o delle fasce descrittive.
La dipendenza rimasta nella media può contribuire ai segnali ARCH: leggere
congiuntamente lo step 5.

Tabelle e confronti sono in `outputs/notebook_diagnostics/ethereum/step6/`.
I risultati riguardano questa finestra; i p-value sono diagnostici e non corretti
per confronti multipli. `findings.md` riporta solo anomalie osservate e verificate
dopo l'esecuzione. I modelli non generano utilizzo fuori dal suo supporto [0, 2].
