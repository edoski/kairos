# Step 8 — Dipendenza fra utilizzo e priority fee

[Notebook Ethereum](dataset_ethereum.ipynb), da eseguire dopo lo step 1 nel kernel `.venv/bin/python`.

Tutti i punti della [checklist](../../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md) sono implementati: regressioni cross-lag nelle due direzioni con errori HAC, correlazione delle innovazioni, non linearità e congestione, distribuzioni condizionate, confronto p50/p90 e stato mediana–dispersione. Ogni punto ha una cella Markdown di scopo e il relativo codice.

Le distribuzioni descrittive usano tutti i blocchi; le regressioni usano gli ultimi 30.000 blocchi contigui (20.000 training, 5.000 validation, 5.000 testing). I modelli sono fissati prima della verifica e non selezionati sul testing. I regressori del target n sono del blocco chiuso n−1. Nessuna simulazione non vincolata viene proposta per l'utilizzo.

CSV dei risultati in `outputs/notebook_diagnostics/ethereum/step8/`. L'eventuale `findings.md` contiene soltanto anomalie osservate nell'esecuzione reale.
