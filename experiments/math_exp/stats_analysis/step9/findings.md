# Step 9 — findings

Esecuzione reale su tre finestre Ethereum di 30.000 blocchi: 3–8 dicembre 2025,
27–31 marzo 2026 e 18–22 luglio 2026. Ogni testing contiene 5.000 previsioni a
un blocco. Fonte: dataset `e7b17cfb-320d-4e6c-93c1-06dbc24f312d`, SHA-256
`4a8482552e3730ad68243a042eaa92b112450b36411f11a18947e9682d2e62e0`.

## 1. Il baseline lineare perde informazione sulle priority fee

La validation sceglie i lag congiunti fino a **10** per log p50 in tutti e tre
i periodi. Sul testing il MSE diminuisce rispetto allo stato baseline:

| Periodo | Riduzione MSE log p50 | Differenza media di perdita | IC 95% HAC della differenza |
| --- | ---: | ---: | ---: |
| Inizio | 6,94% | 1,011 | [0,639; 1,383] |
| Centro | 6,19% | 1,148 | [0,822; 1,475] |
| Fine | 13,18% | 0,522 | [0,328; 0,715] |

La perdita è l'errore quadratico di `log(1 + p50 in wei/gas)`; una differenza
positiva favorisce il modello ampliato. Gli intervalli usano HAC a 50 lag.
La scelta al massimo della griglia non dimostra che dieci lag bastino.

**Da discutere:** i lag più vecchi aiutano queste medie lineari. Il risultato
può motivare uno stato più ricco oppure una media non lineare sullo stato
esistente: non prova, da solo, che il vero processo violi la proprietà di Markov.

## 2. Per X il beneficio è piccolo e cambia con periodo e congestione

Il modello scelto sulla validation migliora il MSE testing dello **0,28%**
all'inizio, **2,43%** al centro e **1,24%** alla fine. All'inizio viene scelto
il conteggio delle transazioni del parent, ma l'intervallo HAC della
differenza di perdita include zero: **[−0,00213; 0,00416]**.
I lag congiunti fino a 10, considerati come alternativa già fissata,
peggiorano X del **2,02%** nel primo periodo.

Nel periodo finale il modello scelto migliora X dell'**1,67%** nella fascia
ordinaria, ma peggiora il MSE del **7,19%** nella fascia ad alta congestione.
Quest'ultima contiene solo **133 target**. Le fasce usano X del parent con
soglia al 95° percentile del solo training: sono confronti descrittivi,
non regimi latenti identificati né confronti corretti per molteplicità.

Inoltre il modello scelto per X nel primo periodo produce **tre previsioni
superiori a 2**, circa **2,251**, **2,162** e **2,029**, ai blocchi
`23961422`, `23962365` e `23963104`. Non sono state troncate per nascondere
la violazione. Una media lineare diagnostica non è un kernel generativo valido
per l'utilizzo vincolato.

## 3. Piccoli p-value training non garantiscono utilità fuori campione

Per log p50 il contributo del numero di transazioni del parent ha p-value
Wald HAC molto piccoli nel primo e nel secondo periodo, rispettivamente
**2,05×10⁻¹¹** e **9,95×10⁻⁹**. Il guadagno MSE testing è però appena
**0,085%** e **−0,003%**; nel periodo finale è **−0,348%**.

Anche l'intervallo precedente del parent non mostra un vantaggio consistente:
per log p50 i guadagni testing sono **−0,018%**, **−0,097%** e **0,034%**.
È osservabile alla decisione, ma questi confronti non sostengono una sua
aggiunta stabile alla media delle fee.

## 4. Rimane dipendenza nei residui dei modelli scelti

Ljung–Box(50) sui residui testing rifiuta per tutte le sei combinazioni di
periodo e risposta selezionate sulla validation. Per log p50 i p-value sono
circa **0,00243**, **0,0000253** e **6,92×10⁻⁷⁷**; per X sono circa
**1,08×10⁻⁷**, **3,78×10⁻¹¹⁴** e **0,00255**.

Sono segnali diagnostici, sensibili anche alle condizioni della varianza
e alla specificazione. Il miglioramento della media non chiude la verifica
dell'intera distribuzione di transizione. P-value e confronti multipli sono
esplorativi; LR/AIC/BIC usano una likelihood gaussiana di lavoro.
Nessuna causa di mercato o proprietà di Markov è stata verificata.

Evidenze: [notebook](dataset_ethereum.ipynb),
[confronti dei modelli](../../../../outputs/notebook_diagnostics/ethereum/step9/model_comparison.csv),
[risultati rolling](../../../../outputs/notebook_diagnostics/ethereum/step9/rolling_scores.csv),
[fasce di congestione](../../../../outputs/notebook_diagnostics/ethereum/step9/regime_comparison.csv),
[diagnostiche residui](../../../../outputs/notebook_diagnostics/ethereum/step9/residual_diagnostics.csv),
[supporto delle previsioni](../../../../outputs/notebook_diagnostics/ethereum/step9/X_prediction_support.csv).
