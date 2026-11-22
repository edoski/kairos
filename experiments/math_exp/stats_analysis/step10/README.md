# Step 10 — Candidati stocastici

[Notebook Ethereum](dataset_ethereum.ipynb), dopo step 1 e 7, nel kernel `.venv/bin/python`. Ogni punto della sezione 10 della checklist ha una coppia Markdown/codice dedicata.

Si stimano realmente cinque candidati in tre periodi disgiunti: AR(1) bounded con innovazioni congiunte empiriche; AR-GARCH; due regimi osservati Markov; miscela gaussiana bivariata; transizioni empiriche condizionate su celle X/Y. Gli ultimi due includono code e dipendenza senza Student-t generativa sui log. I regimi sono osservati, non HMM latenti.

`transition_models.py` è condiviso con lo step 11. `sample_joint` riceve il padre chiuso X/Y e una varianza GARCH già predittiva h_next; restituisce draw X/Y e varianza h_following. `filtered_variance` percorre soltanto gli esiti osservati post-training. Le simulazioni usano EIP-1559 esatta e gas limit del padre costante.

X rimane in [0,2], Y≥0; nessun cap superiore alle fee. La Student-t è stimata solo come diagnostica e rifiutata come kernel risk-neutral. Beta e componente di salto sono valutate con decisioni motivate, non introdotte senza evidenza. Nessun candidato condiziona esplicitamente il kernel stocastico su B; GARCH aggiunge la storia della varianza. B entra nella ricorrenza deterministica e nel costo. Il kernel empirico non genera nuovi massimi oltre il training: benchmark esplicitamente limitato.

Risultati in `outputs/notebook_diagnostics/ethereum/step10/`; eventuali anomalie verificate in `findings.md`. I test del modulo sono in `tests/test_statistical_transition_models.py`.

Le diagnostiche dello step 7 richiamate per discutere i salti hanno scope diversi: clustering su tutto il dataset, compresi validation/testing, e GPD sul solo training di luglio. Sono contesto esplorativo, non selezione training-only dei candidati né prova di assenza di salti negli altri periodi. La medesima griglia di cinque candidati è valutata in tutte le finestre.
