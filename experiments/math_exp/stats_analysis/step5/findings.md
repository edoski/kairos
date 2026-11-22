# Step 5 — findings

Risultati dell'esecuzione sui 30.000 blocchi finali del dataset, dal 18 al
22 luglio 2026. Il testing comprende i blocchi **25585230–25590229**:
5.000 previsioni a un blocco, con ristima sui soli dati precedenti.

## Un solo lag perde informazione, soprattutto sulle priority fee

La validation sceglie **10 lag per tutte e quattro le variabili**, il massimo
della griglia esaminata. Sul testing AR(10) riduce il MSE rispetto ad AR(1) del
**22,54% per log p50**, **12,10% per log p90**, **17,85% per la dispersione** e
**1,14% per X**. L'effetto sull'utilizzo è quindi molto più piccolo.

Da discutere: lo stato con un solo lag sembra troppo corto per le fee in questa
finestra. La scelta al bordo della griglia non dimostra che dieci lag bastino;
questo non autorizza a scegliere altri lag guardando il testing.

## Anche dopo dieci lag rimane dipendenza nei residui

Ljung–Box(50) sui residui testing restituisce p-value **0,000293 per X**,
**8,70 × 10⁻⁶⁵ per log p50**, **4,56 × 10⁻²⁰ per log p90** e
**1,87 × 10⁻¹³⁹ per la dispersione**. I piccoli coefficienti visibili nelle ACF
possono quindi avere struttura congiunta statisticamente rilevante.

Da discutere: i lag aggiuntivi migliorano la media, ma non chiudono la diagnostica
dello stato. Occorre leggere questi segnali insieme a volatilità, code e
dipendenza congiunta degli step 6–8.

Evidenze: [confronto rolling](../../../../outputs/notebook_diagnostics/ethereum/step5/rolling_scores.csv),
[implicazioni per lo stato](../../../../outputs/notebook_diagnostics/ethereum/step5/state_implications.csv),
[Ljung–Box](../../../../outputs/notebook_diagnostics/ethereum/step5/ljung_box.csv).
Le conclusioni sono locali a circa quattro giorni; i p-value sono diagnostici,
senza correzione multipla. I confronti LR/AIC/BIC usano likelihood gaussiane
condizionate, non un kernel validato per l'utilizzo vincolato in [0, 2].
