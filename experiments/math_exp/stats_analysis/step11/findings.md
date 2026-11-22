# Step 11 — findings

Esecuzione reale su tre finestre disgiunte di 30.000 blocchi: **3–8 dicembre
2025**, **27–31 marzo 2026**, **18–22 luglio 2026**. Ogni periodo ha 20.000
training, 5.000 validation e 5.000 testing. Sono state prodotte **150.000
previsioni rolling** sui cinque candidati; nessuna scelta usa il testing.
Fonte UUID/SHA e parametri nel [manifest analitico](../../../../outputs/notebook_diagnostics/ethereum/step11/analysis_scope.json).

## 1. Una distribuzione migliore nei log può essere molto peggiore nei costi

Il kernel empirico vince il log score categorico validation in tutti e tre i
periodi. Il GARCH, però, ha CRPS **nei log** leggermente migliore dell'empirico
nei primi due testing: **2,1515 contro 2,1669**, **2,2866 contro 2,2906**.
Passando alle fee in livelli il quadro cambia drasticamente:

| Testing | CRPS GARCH, gwei/gas | CRPS empirico, gwei/gas |
| --- | ---: | ---: |
| Inizio | 4.392,49 | 0,2190 |
| Centro | 3,2531 | 0,3056 |
| Fine | 21.874,82 | 0,0819 |

**Da discutere:** l'esponenziale amplifica pochi draw estremi del GARCH.
Un buon punteggio sui log non basta per il costo risk-neutral in livelli.
Questi sono score delle distribuzioni campionate, non costi realmente pagati.
I kernel omettono B esplicito e restano ristretti rispetto allo stato dello
step 9; il miglior candidato della griglia non è un modello validato globalmente.

Evidenze: [ranking validation](../../../../outputs/notebook_diagnostics/ethereum/step11/validation_ranking.csv),
[CRPS](../../../../outputs/notebook_diagnostics/ethereum/step11/crps_scores.csv).

## 2. Il candidato selezionato non assorbe la dinamica della distribuzione

Anche con l'empirico selezionato, Ljung–Box(50) dei residui testing rifiuta
per X e log p50 nei tre periodi. ARCH(10) sui **ranghi predittivi centrati**
ha p-value inferiori a **1,5×10⁻¹³** in tutte e sei le combinazioni.
È dinamica distribuzionale residua: il test non isola la sola varianza.
ARCH sui residui grezzi descrive invece la volatilità del processo e non
dimostra, da solo, che un modello della varianza sia sbagliato.

La copertura q95 delle log fee selezionate è **92,46%**, **89,38%** e **91,80%**,
contro il nominale 95%. A q99 è **98,20%**, **98,32%**, **98,34%**, ma quest'ultimo
confronto risente maggiormente della precisione dell'ensemble finito.

**Da discutere:** valutare stato e distribuzione insieme, usando anche gli
ampliamenti dello step 9. P-value iid, molti confronti, dipendenza seriale e
precisione Monte Carlo impediscono di leggere questi controlli come prove di
Markov, indipendenza o calibrazione globale.

Evidenze: [residui](../../../../outputs/notebook_diagnostics/ethereum/step11/residual_autocorrelation.csv),
[ranghi e volatilità](../../../../outputs/notebook_diagnostics/ethereum/step11/residual_heteroskedasticity.csv),
[coperture](../../../../outputs/notebook_diagnostics/ethereum/step11/quantile_coverage.csv).

## 3. La precisione Monte Carlo è fragile nelle fee in livelli

Sulle prime 200 origini testing, passando da 256 a 2.048 campioni dello stesso
modello, la massima differenza assoluta della **media p50 prevista** raggiunge
circa **0,430**, **9,453** e **1,098 gwei/gas** nei tre periodi. Per il q99
le massime differenze sono **4,978**, **98,695** e **56,036 gwei/gas**.

**Da discutere:** centro e code delle fee richiedono precisioni diverse. Il
numero di campioni resta quello fissato prima del confronto, senza aggiustare
il modello per migliorare il testing; questa verifica mostra il limite numerico.
Le medie in livelli e q99 per una singola origine non vanno trattati come
stime precise. Non sono cambiamenti nei dati o nei parametri stimati.

Evidenza: [sensibilità Monte Carlo](../../../../outputs/notebook_diagnostics/ethereum/step11/monte_carlo_precision.csv).

## 4. I benefici del benchmark dipendono dall'offerta e dall'inclusione assunta

Su **200 origini testing per periodo**, K=5, la riduzione del **costo medio**
rispetto all'invio immediato cambia molto con lo scenario:

| Testing | p50 del padre | Due volte p50 del padre | Fee fissa q90 training |
| --- | ---: | ---: | ---: |
| Inizio | 8,48% | 16,49% | −0,32% |
| Centro | 36,78% | 51,73% | 0,77% |
| Fine | 15,88% | 22,61% | 1,20% |

La fee fissa è il q90 **tra blocchi dei p50 training**, arrotondato per eccesso
a un wei, non il P90 delle transazioni incluse in un blocco.
Con p50 del padre la media dei risparmi percentuali per origine è invece
**5,93%**, **12,63%**, **6,64%**: non coincide con il rapporto dei costi medi.
Il segno dipende anche dall'orizzonte: nel periodo finale **K=2 aumenta il costo
medio del 13,86%**, mentre K=5 lo riduce del 15,88% nello stesso scenario.

Nel periodo centrale Bellman costa **0,1916 gwei/gas** contro **0,5215** della
deadline nello scenario d'offerta; il proxy retrospettivo con P50 del blocco
scelto è invece **0,5669 contro 0,2615**, invertendo quel confronto.

**Da discutere:** quanto del vantaggio dipende dalla possibilità di pagare il
tip del padre? Il P50 del blocco selezionato supera quell'offerta nel **52%**,
**74,5%**, **58%** delle origini dei tre testing. Non prova mancata inclusione:
P50 non è la soglia necessaria per includere una nuova transazione. Però non
abbiamo verificato mempool, ricevute o inclusione controfattuale. I risparmi
sono condizionati alle assunzioni e non attestano risparmi operativi reali.

Evidenze: [costi](../../../../outputs/notebook_diagnostics/ethereum/step11/policy_costs.csv),
[confronto appaiato](../../../../outputs/notebook_diagnostics/ethereum/step11/savings_vs_immediate.csv),
[offerte](../../../../outputs/notebook_diagnostics/ethereum/step11/offer_assumptions.csv),
[esiti per origine](../../../../outputs/notebook_diagnostics/ethereum/step11/policy_outcomes.parquet).

## 5. Il risultato comprende fallback e approssimazioni della griglia

Con K=5 e p50 del padre, Bellman invia subito perché fuori dominio in
**20/200**, **5/200**, **0/200** origini testing. I risultati includono questi
fallback; non sono sempre azioni della ricorsione interna alla griglia.

Sulle prime cinquanta origini, una griglia e quadratura più fitte cambiano
**4**, **1**, **2** azioni nei tre periodi. Le differenze medie di costo
sono circa **−0,000870**, **−0,000131**, **+0,000061 gwei/gas**. È un controllo
locale di sensibilità, non una prova di convergenza dell'intera politica.
Il gas limit futuro è fissato a **60 milioni**, valore finale training;
il parent reale allo stop ha un limite diverso in **84**, **53**, **19** casi
su 200. La prima base fee nota usa comunque sempre il limite reale del padre.

**Da discutere:** estendere il dominio e verificare la quadratura prima di
interpretare Bellman come soluzione operativa. Il kernel è empirico congiunto,
la griglia è finita e non viene risolto il Bellman di un GARCH senza includere
il suo stato di volatilità.

Evidenze: [scope politica](../../../../outputs/notebook_diagnostics/ethereum/step11/policy_training_scope.csv),
[sensibilità numerica](../../../../outputs/notebook_diagnostics/ethereum/step11/bellman_numerical_sensitivity.csv),
[esiti e fallback](../../../../outputs/notebook_diagnostics/ethereum/step11/policy_outcomes.parquet).

## 6. Le fasce estreme hanno poca o nessuna evidenza operativa

Le origini ad alta congestione sono **38**, **22**, **9**; quelle ad alta
volatilità sono **5**, **0**, **14**. Le soglie q90 sono fissate sul training e
usano soltanto storia osservabile. Nel periodo centrale non c'è quindi una
misura della prestazione operativa nella fascia di volatilità alta.

**Da discutere:** raccogliere altri periodi e più origini estreme prima di
generalizzare. Le tre finestre brevi e questi conteggi non sostengono una
superiorità stabile in condizioni di stress.

Evidenza: [prestazioni per fascia](../../../../outputs/notebook_diagnostics/ethereum/step11/policy_regime_performance.csv).
