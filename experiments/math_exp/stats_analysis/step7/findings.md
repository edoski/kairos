# Step 7 — findings

Esecuzione sul dataset Ethereum Zenodo 22094893, **1.654.536 blocchi**. Le descrittive usano tutto il campione. Le innovazioni provengono dallo step 5 sui blocchi **25560240–25590229**: 19.990 residui training, 5.000 validation e 5.000 testing, nella finestra del 18–22 luglio 2026. I test iid sono diagnostici, con dipendenza seriale e confronti multipli non corretti.

## 1. Code e asimmetria rimangono dopo la previsione della media

Nel campione completo, la kurtosi in eccesso delle fee originali raggiunge circa **448.241 per p50** e **82.726 per p90**: pochi valori estremi dominano i momenti. I log riducono questa scala ma non rendono gaussiane le variabili.

Anche nel testing rolling, i residui delle log fee sono fortemente asimmetrici: skewness **−3,44** per p50 e **−5,88** per p90, con kurtosi in eccesso **28,55** e **114,54**. La dispersione ha invece skewness **+3,67** e kurtosi **29,96**. Q-Q e Jarque–Bera concordano sulla non normalità; i p-value iid non vanno interpretati come prove di indipendenza o di salti.

**Da discutere:** quanto delle code inferiori dei log deriva da priority fee nulle o molto basse, e quanto rimane dopo il trattamento della volatilità? La non normalità non dimostra errori nel dataset o salti del processo.

Evidenze: [forma delle distribuzioni](../../../../outputs/notebook_diagnostics/ethereum/step7/shape_report.csv), [Jarque–Bera](../../../../outputs/notebook_diagnostics/ethereum/step7/jarque_bera.csv), Q-Q nel [notebook](dataset_ethereum.ipynb).

## 2. Gli estremi delle differenze si susseguono molto più spesso dell'indipendenza

Per soglie pari al quantile 99% delle variazioni assolute, un evento estremo è seguito da un altro nel blocco successivo nel **10,78%** dei casi per l'utilizzo, **32,64%** per log p50 e **38,83%** per log p90. La quota marginale degli estremi è l'1% per costruzione: i rapporti sono circa **10,8**, **32,6** e **38,8**.

**Da discutere:** verificare la concentrazione degli eventi nei livelli e nelle innovazioni prima di proporre regimi o self-excitation. Un singolo picco seguito dal rientro genera due differenze grandi e adiacenti: parte del clustering può quindi essere meccanica. Le soglie sono descrittive, non una previsione della frequenza futura.

Evidenza: [cluster degli estremi](../../../../outputs/notebook_diagnostics/ethereum/step7/extreme_clustering.csv).

## 3. Student-t migliora le densità delle fee; il risultato non si estende all'utilizzo

Con parametri stimati soltanto sui residui training, Student-t migliora il log score medio sul testing di **0,272** per log p50, **0,271** per log p90 e **0,234** per la dispersione. Gli intervalli HAC95% delle differenze sono rispettivamente **[0,209; 0,335]**, **[0,206; 0,335]** e **[0,168; 0,301]**. I gradi di libertà stimati sono circa **3,28**, **2,60** e **3,78**.

Per l'utilizzo, invece, i gradi di libertà della t arrivano a circa **6,2 miliardi** e il guadagno di log score è soltanto **0,00000023**: è praticamente il limite gaussiano, senza un vantaggio sostanziale. Gli errori training sono in-sample, quelli testing derivano da previsioni rolling; eventuali cambiamenti di scala fra periodi restano rilevanti.

**Da discutere:** valutare innovazioni con code più ampie per le fee, insieme alla volatilità dello step 6. Una densità marginale migliore non certifica un kernel condizionato adeguato; nessuna distribuzione gaussiana o t non vincolata va usata per simulare direttamente l'utilizzo in `[0,2]`.

Evidenza: [confronto delle distribuzioni](../../../../outputs/notebook_diagnostics/ethereum/step7/innovation_distributions.csv).

## 4. La forma GPD cambia drasticamente al cambiare della soglia

Sui massimi di cluster dei residui assoluti training, separati da almeno sei blocchi, la stima di forma `xi` di log p50 passa da **+0,79** e **+0,84** alle soglie q95 e q97,5 a **−1,32** a q99. Per la dispersione passa da **+0,59** e **+1,12** a **−0,72**. I cluster alle soglie più alte sono soltanto **144** e **150**.

**Da discutere:** questa instabilità non sostiene un'estrapolazione delle code con una singola GPD. Le code assolute mescolano i due segni; soglia, declustering e stabilità temporale richiedono validazione separata. Non stimiamo probabilità di eventi oltre il campione con questi fit esplorativi.

Evidenza: [sensibilità GPD](../../../../outputs/notebook_diagnostics/ethereum/step7/gpd_threshold_sensitivity.csv).

## 5. Il picco principale rimane senza verifica esterna completa

Il blocco **24743487** ha p50 e p90 di circa **13.491,89 gwei/gas**, con **12 transazioni** e utilizzo del limite gas di circa **8,19%** (`X = 0,1637`, relativo al target). Il riscontro RPC salvato nello step 1 lascia questo blocco **non verificato**, insieme a `23937276`, `23937277` e `25104161`; gli altri sette controlli sono confermati.

**Da discutere:** verificare le transazioni del picco e la ponderazione per gas prima di attribuirgli una causa. IQR e coerenza strutturale non certificano la genuinità del singolo tip. Il servizio RPC è la fonte originaria, non una verifica indipendente; nessun dato è stato eliminato e nessuna nuova richiesta RPC è stata eseguita da questo step.

Evidenza: [verifiche RPC salvate](../../../../outputs/notebook_diagnostics/ethereum/step1/extreme_rpc_review.csv), [notebook](dataset_ethereum.ipynb), [step 1](../step1/dataset_ethereum.ipynb).
