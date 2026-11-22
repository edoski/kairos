# Step 1 — anomalie da discutere con Alessio

Esecuzione locale del 21 novembre 2026 sui **1.654.536 blocchi** originali.
Manifest SHA-256: `4a8482552e3730ad68243a042eaa92b112450b36411f11a18947e9682d2e62e0`.

- **Cinque blocchi non equivalgono a sessanta secondi.** Il **2,2843%** delle
  1.654.531 finestre complete supera 60 secondi; massimo **168 secondi**.
  Sono presenti **7.727 intervalli oltre 12 secondi**, senza buchi nei numeri di
  blocco. Sono compatibili con slot senza blocco canonico, senza provarne la causa.
  Da discutere: la deadline dell'optimal stopping è in blocchi o in tempo reale?
- **Picco p50 con scarso utilizzo.** Il blocco **24.743.487** raggiunge circa
  **13.491,893 gwei/gas** sia p50 sia p90, con 12 transazioni e circa l'8,2%
  del gas disponibile utilizzato. I blocchi vicini hanno p50 molto inferiori.
  Il picco non dimostra congestione e la sua genuinità resta da verificare.
- **Verifica esterna incompleta.** La cache RPC del 18 novembre riporta 7 conferme,
  nessuna discordanza e 4 casi senza risposta: **23.937.276, 23.937.277,
  24.743.487, 25.104.161**. I valori confermati sono stati riconciliati oggi con
  il dataset; le quattro assenze non sono state promosse a conferme.
  Il servizio coincide con la fonte originaria, quindi manca un riscontro indipendente.
- **Percentili nulli nei blocchi vuoti.** I **653 blocchi vuoti** hanno p50=p90=0
  per convenzione della fonte. Nelle distribuzioni occorre distinguerli da
  transazioni incluse con tip nullo; non sono stati rimossi.
- **IQR degenere per il gas limit.** L'IQR nullo segnala qualsiasi valore diverso
  da 60 milioni, circa il 22% dei blocchi: non dimostra altrettanti errori.
  Anche i 181.470 limiti dispari richiedono di distinguere X teorico dal target
  intero del protocollo, pur con differenza numerica molto piccola.

Evidenze: [notebook](dataset_ethereum.ipynb),
`outputs/notebook_diagnostics/ethereum/step1/{preprocessing_summary.json,extreme_audit.csv,extreme_review_sample.csv,extreme_rpc_review.csv,block_interval_report.csv,deadline_scenario.csv}`.
Tutti i controlli d'integrità sono passati; nessuna riga esclusa o corretta.
