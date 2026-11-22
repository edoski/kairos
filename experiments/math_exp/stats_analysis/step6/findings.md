# Step 6 — findings

Risultati su 5.000 innovazioni testing, blocchi **25585230–25590229**, il
22 luglio 2026. Le varianze sono stimate sui 5.000 residui validation precedenti;
nessun parametro della varianza viene scelto usando gli esiti del testing.

## Il clustering della volatilità è diverso fra p50 e p90

ARCH-LM(10) sul testing dà p-value **7,22 × 10⁻⁴⁷ per X**,
**1,05 × 10⁻⁵² per log p50** e **4,17 × 10⁻³⁷ per la dispersione**.
Per **log p90 il p-value è 0,927**; anche Ljung–Box dei quadrati non rifiuta
in questa finestra. Il GARCH non viene quindi aggiunto automaticamente a p90:
già sulla validation ARCH non emergeva (p = 0,991).

Da discutere: p50 e dispersione richiedono una dinamica della varianza che questo
controllo non identifica per p90. Un mancato rifiuto non prova varianza costante;
la dinamica rimasta nella media dello step 5 può contribuire ai segnali ARCH.

## Il miglior fit asimmetrico non garantisce la migliore previsione

GJR-GARCH ha AIC validation inferiore al GARCH simmetrico per tutte e tre le
variabili stimate. Nel testing, però, il QLIKE del GARCH è migliore per
**log p50 (1,1118 contro 1,1979)** e **dispersione (1,2366 contro 1,3247)**.
Per X il GJR migliora il QLIKE (1,0116 contro 1,0228), ma conserva dipendenza nei
quadrati standardizzati (Ljung–Box(50) p = 0,00533); il GARCH simmetrico dà
p = 0,195. Anche il GARCH di log p50 lascia dipendenza residua (p = 0,00154).

Da discutere: l'asimmetria migliora il fit ma non basta a scegliere l'estensione;
prestazione previsiva e adeguatezza dei residui possono indicare compromessi
diversi. QLIKE va confrontato entro la stessa variabile; minore è migliore.

## Errori delle fee più ampi dopo congestione alta

Nei **557 blocchi** preceduti da utilizzo oltre q90 validation, il quadrato medio
dell'innovazione è **6,983 contro 3,059 per log p50** e **5,752 contro 2,558 per
la dispersione** nei restanti 4.443 blocchi: circa **2,28 e 2,25 volte**.

Da discutere: verificare la stabilità di questa associazione su altri periodi
prima di introdurre un modello a regimi. La fascia è osservabile dal blocco
precedente; il confronto descrittivo non identifica causalità o un regime latente.

Evidenze: [ARCH-LM](../../../../outputs/notebook_diagnostics/ethereum/step6/arch_lm.csv),
[Ljung–Box dei quadrati](../../../../outputs/notebook_diagnostics/ethereum/step6/squared_ljung_box.csv),
[modelli della varianza](../../../../outputs/notebook_diagnostics/ethereum/step6/variance_models.csv),
[fasce di congestione](../../../../outputs/notebook_diagnostics/ethereum/step6/congestion_variance.csv).
I risultati sono locali a questa finestra, con test esplorativi senza correzione
multipla. EGARCH e regimi latenti restano ipotesi da verificare.
