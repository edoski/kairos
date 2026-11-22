# Step 2 — anomalie descrittive da discutere con Alessio

Esecuzione locale del 21 novembre 2026 sull'intero dataset Ethereum,
**1.654.536 blocchi**. Sono descrittive, non test di causalità o di salti.

- **Le medie delle priority fee sono dominate dalle code.** Per p50 la mediana è
  **0,010 gwei/gas**, la media **0,2434** e il massimo **13.491,8933**;
  per p90 la mediana è **1,000**, la media **2,1636**. La kurtosis in eccesso
  è circa **448.241** per p50 e **82.726** per p90: una distribuzione normale
  in livelli non riassume adeguatamente queste osservazioni.
- **Il log non rende le priority fee gaussiane.** La kurtosis in eccesso rimane
  **8,25** per log p50 e **57,64** per log p90, con asimmetria negativa.
  I Q–Q mostrano deviazioni anche nella coda inferiore, influenzata dai valori
  nulli; non basta interpretare tutti gli scostamenti come coda superiore pesante.
- **Congestione e volatilità delle fee non coincidono sempre.** Il giorno con
  massima deviazione standard di log p50 è il **29 marzo 2026** (**6,316**),
  ma la sua quota di blocchi X≥1,9 (**7,57%**) non supera il 95° percentile
  delle quote giornaliere. Il 4 aprile mostra una separazione simile.
  Da discutere: modellare separatamente livello, dispersione e congestione?
- **Associazione contemporanea fra base fee e priority fee.** La correlazione
  Spearman dei log è **0,563** con p50 e **0,405** con p90. La differenza fra
  percentili invita a preservarne i ruoli distinti; il contributo predittivo dei
  lag deve essere valutato nello step 8, senza usare la correlazione come prova.

Evidenze: [notebook](dataset_ethereum.ipynb),
`outputs/notebook_diagnostics/ethereum/step2/{descriptive_statistics.csv,distribution_shape.csv,daily_congestion_volatility.csv,fee_spearman.csv}`.
I confronti giornalieri escludono i due giorni parziali ai bordi.
