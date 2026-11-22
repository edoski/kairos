# Step 10 — findings

Sono stati stimati **15 modelli reali**: cinque candidati sui soli primi 20.000 blocchi di tre finestre disgiunte di 30.000 blocchi. Finestre: **3–8 dicembre 2025**, **27–31 marzo 2026**, **18–22 luglio 2026 UTC**. Le anomalie seguenti riguardano i fit e un controllo generativo di **512 percorsi a cinque blocchi** da fine training; non sono risultati di selezione fuori campione. UUID e SHA sono nel [manifest analitico](../../../../outputs/notebook_diagnostics/ethereum/step10/analysis_scope.json).

## 1. GARCH può produrre fee sproporzionate pur avendo supporto finito condizionato

Nel periodo centrale, la persistenza stimata della varianza è **0,99698**. Il controllo dei percorsi produce un massimo simulato di circa **20,97 milioni di gwei/gas**, contro un massimo training di **1.610,94 gwei/gas**; lo **0,43%** dei valori Y generati supera il massimo training. Nel periodo finale il massimo GARCH simulato è circa **6.194,62 gwei/gas**.

**Da discutere:** la media finita non garantisce plausibilità o stabilità per una decisione risk-neutral. Con un esponenziale applicato alle log fee, pochi percorsi possono dominare il costo atteso. Non abbiamo nascosto il problema con un cap superiore: il candidato richiede confronto probabilistico e controllo delle code nello step 11 prima di un impiego operativo.

Evidenze: [GARCH](../../../../outputs/notebook_diagnostics/ethereum/step10/garch_parameters.csv), [plausibilità dei percorsi](../../../../outputs/notebook_diagnostics/ethereum/step10/path_plausibility.csv).

## 2. La censura dell'utilizzo crea una massa artificiale nei blocchi perfettamente pieni

Non esistono osservazioni `X=2` esatte nei tre training. La baseline censurata genera invece valori `X=2` nel **4,10%**, **2,93%** e **1,91%** dei passi simulati nei periodi iniziale, centrale e finale. Anche gli altri modelli autoregressivi censurati producono masse ai bordi.

**Da discutere:** rispettare `[0,2]` è necessario ma non sufficiente. La censura risolve l'impossibilità fisica di X esterni al supporto, ma può deformare la distribuzione e la ricorrenza della base fee. Confrontare frequenze dei bordi e calibrazione con il kernel empirico congiunto prima di scegliere il modello.

Evidenze: [applicabilità Beta e conteggi degli atomi](../../../../outputs/notebook_diagnostics/ethereum/step10/beta_applicability.csv), [masse simulate](../../../../outputs/notebook_diagnostics/ethereum/step10/path_plausibility.csv).

## 3. Il regime di utilizzo alto non mostra la persistenza che il nome potrebbe suggerire

Con soglia osservata `X≥1,5`, la probabilità del regime alto dopo un blocco alto è **17,50%**, **14,70%** e **13,70%** nei tre training. Dopo un blocco basso è invece **21,69%**, **20,54%** e **18,68%**. Il regime alto è dunque meno probabile dopo sé stesso che dopo il regime basso.

**Da discutere:** questi sono stati osservati del gas, non un HMM di congestione latente. Non attribuire alle due classi un'interpretazione di persistenza economica non supportata dalla matrice. Il generatore usa realmente le probabilità stimate e ne verifica le quote; la quantizzazione del gas conserva il regime anche con gas limit dispari.

Evidenza: [matrici e controllo generativo](../../../../outputs/notebook_diagnostics/ethereum/step10/regime_transitions.csv).

## 4. Le componenti della miscela cambiano significato tra periodi

La seconda componente gaussiana pesa circa **5,19%**, **19,15%** e **3,37%** nei tre periodi. Nei primi due, la sua media delle innovazioni log fee è circa **−11,80** e **−9,84**: cattura soprattutto variazioni verso fee basse, non una componente di salti positivi. Nell'ultimo periodo è molto più dispersa, con deviazione standard **6,46**, contro **1,74** della prima componente.

**Da discutere:** le due componenti convergono numericamente, ma le etichette non rappresentano uno stesso meccanismo stabile fra periodi. Non chiamarle automaticamente stato normale e salto. La Student-t diagnostica stima inoltre circa **1,29** gradi di libertà nel periodo centrale; non è usata come kernel generativo sui log, perché il costo esponenziale non avrebbe media finita.

Evidenze: [miscela stimata](../../../../outputs/notebook_diagnostics/ethereum/step10/mixture_parameters.csv), [Student-t diagnostica](../../../../outputs/notebook_diagnostics/ethereum/step10/student_t_diagnostic.csv).

Il kernel empirico resta un benchmark a supporto finito, con **20 celle occupate** in ciascun periodo e almeno **83/109/126** transizioni per cella. Non può generare nuove fee oltre il massimo training e non condiziona sulla base fee: questi limiti sono dichiarati, non risolti dai controlli sopra.
