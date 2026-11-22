# Step 11 — Validazione fuori campione e arresto ottimo

Il [notebook](dataset_ethereum.ipynb) copre i 22 punti della
[checklist](../../../../docs/math_dev/ethereum_eip1559_optimal_stopping_summary.md),
ciascuno con Markdown di scopo e codice. Eseguire prima lo step 1; gli helper
dello step 10 sono importati direttamente, senza variabili di altri kernel.

## Previsioni

Tre finestre disgiunte di 30.000 blocchi: 20.000 training, 5.000 validation e
5.000 testing. Si valutano cinque candidati su tutte le origini consecutive:
**150.000 previsioni**, 256 campioni congiunti ciascuna, ristima ogni 1.000 origini
sui 20.000 blocchi precedenti. La validation di ciascun periodo sceglie il log
score categorico medio; il testing misura senza riselezionare.

I bin sono comuni e fissati sul training, con atomi distinti per X=0, X=2 e fee
nulla. Il log score regolarizzato con mezzo conteggio per cella non è una densità
continua. CRPS, RMSE/MAE e quantili hanno unità separate: X, log1p(wei/gas),
gwei/gas. La media delle fee è `mean(expm1(Y))`.

Nessuno dei candidati condiziona esplicitamente il kernel stocastico su B;
GARCH aggiunge la storia della varianza. Sono restrizioni rispetto allo stato
completo analizzato nello step 9. ARCH grezzo descrive il processo; test sui PIT
centrati cercano dinamica distribuzionale residua, senza isolare la sola varianza.
P-value iid e confronti multipli restano esplorativi. Una verifica con 2.048
campioni sulle prime 200 origini testing misura l'errore Monte Carlo nei log e
nelle fee in livelli; q99 con 256 campioni rimane rumoroso.

## Benchmark di Bellman

Il kernel empirico congiunto è stimato sul solo training iniziale. La politica
è un benchmark distinto dal modello scelto per previsione. Lo stato usa base fee
nota del figlio e X/p50 del padre chiuso; le offerte non vedono il blocco target.

Ricorrenza EIP-1559 e gas sono interi. Nelle simulazioni il gas limit resta
all'ultimo valore training; la prima base fee di ogni decisione usa il limite
reale del parent. Bellman è adattiva, con interpolazione nelle fee in livelli,
griglia e quadratura finite. I domini sono annidati: fuori griglia si invia
subito e si registra il fallback. Una griglia più fitta verifica la sensibilità.

K=2/3/5 condividono 200 origini per ruolo e periodo, distanti 25 blocchi e con
cinque esiti completi. Confronti: invio immediato, deadline e soglia q25 training.
Offerte: p50 del parent, suo raddoppio, fee fissa q90 **tra blocchi** dei p50
training arrotondata per eccesso a un wei; quest'ultima non è il P90 interno a un blocco.

I costi assumono inclusione e pagamento del tip offerto, con L=100.000 gas fissi.
Il proxy retrospettivo con P50 del blocco scelto resta separato. Per l'obiettivo
risk-neutral conta la riduzione del **costo medio**, distinta da media e mediana
dei risparmi percentuali per origine. Non vengono inviate transazioni.

## Risultati e controlli

CSV/JSON e previsioni/costi per origine sono in
`outputs/notebook_diagnostics/ethereum/step11/`; anomalie verificate in
[findings.md](findings.md). Gli helper [validation.py](validation.py) e
[stopping.py](stopping.py) hanno test dedicati in
`tests/test_statistical_forecasts.py` e `tests/test_statistical_stopping.py`.
