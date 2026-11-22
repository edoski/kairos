# Step 8 — findigs

Esecuzione sul dataset Ethereum Zenodo 22094893, 1.654.536 blocchi. Le distribuzioni condizionate usano tutto il campione; le regressioni usano soltanto i blocchi **25560230–25590229**, dal **18 al 22 luglio 2026 UTC**, con 20.000 training, 5.000 validation e 5.000 testing. Le associazioni non identificano rapporti causali.

## 1. Più utilizzo non coincide con priority fee incluse più alte

Nel campione completo, la mediana **tra blocchi** della priority fee p50 è **0,03508 gwei/gas** quando `X ≤ 0,5`, contro **0,002343** quando `X > 1,8`. Per p90 i valori sono **1,9792** e **0,4280 gwei/gas**. La relazione contemporanea osservata va quindi nella direzione opposta all'idea che un blocco più pieno implichi sempre tip più alti.

**Da discutere:** quali composizioni delle transazioni incluse e quali variazioni fra periodi spiegano questa associazione? Sono percentili delle transazioni incluse ponderati per gas, non una tariffa che garantisce l'inclusione. Il confronto aggrega periodi diversi e non è una stima causale dell'effetto della congestione.

Evidenza: [distribuzioni condizionate](../../../../outputs/notebook_diagnostics/ethereum/step8/conditional_distributions.csv).

## 2. Cross-lag significativi, ma vantaggi previsivi piccoli e instabili

L'utilizzo ritardato ha coefficienti HAC positivi su log p50 (**0,4184**, IC95% **0,3220–0,5147**) e log p90 (**0,4066**, **0,3343–0,4789**). Aggiungerlo al solo lag proprio peggiora però il MSE nella validation dello **0,75%** e **1,73%**, mentre nel testing lo migliora dell'**1,34%** e **0,74%**. Nella direzione inversa, il lag di p50 peggiora il MSE dell'utilizzo nello stesso testing dello **0,38%**; p90 lo migliora soltanto dello **0,15%**.

Il termine quadratico dell'utilizzo migliora il MSE delle fee nel testing di circa **1,79%** per p50 e **1,14%** per p90 rispetto al modello cross-lag lineare. Per p90, tuttavia, peggiora dello **0,63%** sui soli **256** blocchi con `X` precedente almeno 1,8.

**Da discutere:** verificare la stabilità su altri periodi prima di ampliare lo stato. La significatività in una finestra non dimostra un guadagno operativo stabile; i confronti sono esplorativi senza correzione multipla.

Evidenze: [coefficienti](../../../../outputs/notebook_diagnostics/ethereum/step8/cross_lag_coefficients.csv), [MSE](../../../../outputs/notebook_diagnostics/ethereum/step8/cross_lag_forecasts.csv), [non linearità](../../../../outputs/notebook_diagnostics/ethereum/step8/nonlinear_dependence.csv).

## 3. La dipendenza rimane nelle innovazioni

Nel testing, le correlazioni Pearson delle innovazioni utilizzo–fee sono **−0,243** per p50 e **−0,201** per p90; Spearman è **−0,294** e **−0,274**. Quando `X` precedente è almeno 1,8, Pearson diventa **−0,337** e **−0,304**, su 256 osservazioni.

**Da discutere:** un kernel che campioni separatamente utilizzo e fee perderebbe la dipendenza osservata in questa finestra. Il segnale motiva una verifica della distribuzione congiunta; non dimostra causalità, sufficienza Markov o stabilità fuori da questo periodo.

Evidenza: [dipendenza residua](../../../../outputs/notebook_diagnostics/ethereum/step8/residual_dependence.csv).

## 4. Mediana e dispersione sono fortemente anticorrelate, anche per costruzione

La correlazione residua tra log p50 e `D = log p90 − log p50` è **−0,8925** nel modello congiunto. L'identità stessa può produrre una componente algebrica di questa anticorrelazione: da sola non prova un regime o un meccanismo economico.

Il modello congiunto migliora il MSE di log p50 del **2,03%** e della dispersione del **2,84%** rispetto ai rispettivi AR(1), ma peggiora quello dell'utilizzo dello **0,30%**.

**Da discutere:** valutare mediana e dispersione insieme preservando `D ≥ 0`, affiancando correlazione utilizzo–fee e confronto fuori campione. Il comportamento dei due percentili non giustifica simularli indipendentemente.

Evidenze: [correlazioni del modello congiunto](../../../../outputs/notebook_diagnostics/ethereum/step8/joint_residual_correlation.csv), [MSE congiunto](../../../../outputs/notebook_diagnostics/ethereum/step8/median_dispersion_joint.csv).
