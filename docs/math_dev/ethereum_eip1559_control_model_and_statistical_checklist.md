# Ethereum EIP-1559: Finite-Horizon Submission, Fee-Control, and Model Selection

## 1. Objective and modelling scope

The objective is to minimize the expected transaction cost by choosing, at each block, whether to wait or submit, and—if submitting—which priority fee to offer.

The transaction may be cancelled/replaced and reissued with a different priority fee at a later block. Thus, after a failed inclusion attempt, the controller can choose a new fee at the next decision time.

The deadline is hard: if the transaction has not been included by the end of the final eligible block, a penalty \(M<\infty\) is incurred.

The key modelling distinction is:

- **Market dynamics:** how the observable network state evolves.
- **Inclusion mechanism:** the probability and state-dependent consequences of being included after offering a particular priority fee.
- **Decision problem:** how to choose waiting or a fee offer to minimize expected total cost.

The main empirical objective is not to predict every state variable as accurately as possible. It is to obtain a model that leads to a lower and reliably estimated out-of-sample expected transaction cost. State-distribution accuracy still matters insofar as it affects the Bellman expectations and the estimated policy value.

---

## 2. Observed data and state

The available block-level dataset contains:

- `block_number`
- `timestamp`
- `base_fee_per_gas`
- `gas_used`
- `gas_limit`
- `tx_count`
- `effective_priority_fee_per_gas_p50`
- `effective_priority_fee_per_gas_p90`

Define target-relative utilization

\[
X_n=\frac{\mathrm{gas\_used}_n}{\mathrm{gas\_limit}_n/2},
\qquad 0\leq X_n\leq 2
\]

(up to protocol and data conventions).

Let

\[
B_n=\text{base fee at the beginning of block }n,
\]

and let \(P_n\) denote a chosen block-level priority-fee statistic or a vector of statistics, for example

\[
P_n=(P_n^{50},P_n^{90}).
\]

The proposed observable state at the beginning of block \(n\) is

\[
\boxed{S_n=(B_n,X_{n-1},P_{n-1}).}
\]

If both p50 and p90 are retained, the state is formally higher-dimensional:

\[
S_n=(B_n,X_{n-1},P_{n-1}^{50},P_{n-1}^{90}).
\]

The state must contain only information available at the decision time. In particular, block-\(n\) utilization and priority-fee statistics are not known when deciding at the beginning of block \(n\).

The EIP-1559 base fee is mechanically updated from the previous block's utilization. Ignoring integer rounding and protocol details,

\[
B_{n+1}=B_n\left(1+\frac{X_n-1}{8}\right).
\]

The exact protocol update should be used in implementation. Consequently, the stochastic modelling effort should focus primarily on utilization and priority-fee dynamics, rather than treating the base fee as an independent process.

---

## 3. Actions, inclusion indicator, and cost

At the beginning of block \(n\), the action is either:

1. **Wait:** do not submit in block \(n\).
2. **Submit:** offer a priority fee \(\hat P\in\mathcal P\).

Let

\[
I_n(\hat P)\in\{0,1\}
\]

be the indicator that the transaction is included in block \(n\) when the offered priority fee is \(\hat P\).

Define the state-dependent inclusion probability

\[
q_n(s,\hat P)
=\Pr(I_n(\hat P)=1\mid S_n=s).
\]

The intended interpretation is that \(q_n\) depends on the observable state and the offered fee. Randomness in inclusion represents external factors not fully captured by the state, such as block congestion and competition from other transactions.

If the transaction requires \(L\) units of gas, the successful inclusion cost is

\[
G_n(s,\hat P)=L(B_n+\hat P).
\]

For clarity, many derivations below use cost per unit of gas, \(L=1\). Multiply all gas-price costs by \(L\) to recover total transaction cost.

The one-step cost under a submission action is

\[
\boxed{c_n(s,\hat P,I_n)=I_n(\hat P)L(B_n+\hat P).}
\]

Thus the immediate cost is zero if inclusion does not occur in that block. Failure is not treated as a terminal event: the transaction can be reissued with a new fee in the next block.

Waiting also has zero immediate cost.

At the final eligible block, failure to obtain inclusion leads to the terminal penalty \(M\).

### Fee action space

A convenient theoretical restriction is a compact interval

\[
\mathcal P=[0,P_{\max}].
\]

If costs are measured per unit of gas and the terminal penalty is \(M\), offers with \(\hat P>M\) cannot improve on accepting the penalty \(M\), since successful inclusion would itself cost more than \(M\) (assuming nonnegative base fees). Thus one may use \(P_{\max}=M\) as a convenient bound under this normalization.

If total cost is \(L(B_n+\hat P)\), the corresponding comparison must include \(L\); the bound on \(\hat P\) should be derived consistently from the units and the penalty.

---

## 4. Joint transition model: state and inclusion

The relevant stochastic object is not just the transition distribution of \(S_{n+1}\). It is the **joint conditional kernel** of the next state and the inclusion outcome:

\[
\boxed{
K_n(ds',di\mid s,\hat P)
=
\Pr(S_{n+1}\in ds',I_n(\hat P)=i
\mid S_n=s,\hat P).
}
\]

This allows inclusion and the next state to be dependent. For example, an unusually congested block may both make inclusion less likely and affect the next block's utilization or priority-fee environment.

The joint kernel can be decomposed as

\[
\begin{aligned}
K_n(ds',1\mid s,\hat P)
&=q_n(s,\hat P)K_n^1(ds'\mid s,\hat P),\\
K_n(ds',0\mid s,\hat P)
&=(1-q_n(s,\hat P))K_n^0(ds'\mid s,\hat P),
\end{aligned}
\]

where \(K_n^1\) and \(K_n^0\) are the conditional next-state distributions given inclusion and failure.

This decomposition is useful conceptually:

- \(q_n(s,\hat P)\) describes the probability of inclusion.
- \(K_n^1\) describes the next state conditional on inclusion.
- \(K_n^0\) describes the next state conditional on failure.

A simplifying assumption sometimes used is that the inclusion event is conditionally independent of the next state given \((S_n,\hat P)\), in which case \(K_n^1=K_n^0\). This assumption is **not** imposed in the present model.

### Candidate construction

A possible generative construction is:

1. Given \(S_n=s\), generate the next-block market variables, such as \(X_n\) and \(P_n\), from a conditional joint distribution.
2. Update \(B_{n+1}\) mechanically using the EIP-1559 rule.
3. Generate \(I_n(\hat P)\) using an inclusion mechanism that may depend on \(s\), \(\hat P\), and the same random congestion variables used in step 1.

Using shared random factors is one way to preserve dependence between inclusion and the next state.

---

## 5. Bellman equation

Let \(V_n(s)\) be the minimum expected remaining cost at the beginning of block \(n\), conditional on \(S_n=s\).

Define the value of waiting:

\[
W_n(s)=
\mathbb E[V_{n+1}(S_{n+1})\mid S_n=s].
\]

If we submit with fee \(\hat P\), the realized cost-plus-continuation expression is

\[
I_n(\hat P)L(B_n+\hat P)
+
(1-I_n(\hat P))V_{n+1}(S_{n+1}).
\]

Therefore,

\[
\begin{aligned}
V_n(s)=\min\Bigg\{&
W_n(s),\\
&\inf_{\hat P\in\mathcal P}
\mathbb E\Big[
I_n(\hat P)L(B_n+\hat P)
+(1-I_n(\hat P))V_{n+1}(S_{n+1})
\mid S_n=s
\Big]\Bigg\}.
\end{aligned}
\]

Equivalently, subtracting the waiting value,

\[
\boxed{
V_n(s)=W_n(s)+
\min\left\{
0,\inf_{\hat P\in\mathcal P}
\mathbb E\left[
I_n(\hat P)
\left(L(B_n+\hat P)-V_{n+1}(S_{n+1})\right)
\mid S_n=s
\right]
\right\}.
}
\]

This is the central recursion. It does **not** assume independence between inclusion and \(S_{n+1}\).

The terminal condition is

\[
\boxed{V_{N+1}(s)=M.}
\]

At the final eligible block,

\[
\begin{aligned}
V_N(s)=M+\min\Bigg\{0,\inf_{\hat P\in\mathcal P}
\mathbb E\Big[
I_N(\hat P)
\big(L(B_N+\hat P)-M\big)
\mid S_N=s
\Big]\Bigg\}.
\end{aligned}
\]

If the cost is already normalized per unit of gas, set \(L=1\).

### Conditional-expectation interpretation

For \(q_n(s,\hat P)>0\),

\[
\begin{aligned}
&\mathbb E[
I_n(\hat P)(L(B_n+\hat P)-V_{n+1}(S_{n+1}))
\mid S_n=s]\\
&=q_n(s,\hat P)\left[
L(B_n+\hat P)
-\mathbb E[V_{n+1}(S_{n+1})
\mid S_n=s,I_n(\hat P)=1]
\right].
\end{aligned}
\]

The continuation value inside this expression is conditional on **successful inclusion**, not the unconditional waiting value. This is where dependence between inclusion and the next state enters.

---

## 6. Existence assumptions for an optimal policy

A useful set of sufficient assumptions for a finite-horizon existence result is:

1. **State space:** the state space is a Borel subset of a Euclidean space (hence standard Borel).
2. **Action space:** \(\mathcal P\) is compact; the complete action set consists of waiting plus submission fees in \(\mathcal P\).
3. **Joint transition kernel:** \(K_n(ds',di\mid s,\hat P)\) is a well-defined stochastic kernel and is weakly continuous in \((s,\hat P)\), under the chosen topology.
4. **One-step cost:** the expected one-step cost is well-defined and has suitable regularity. A simple sufficient case is bounded continuous cost; otherwise impose suitable integrability/uniform-integrability conditions.
5. **Terminal cost:** \(M\) is finite and measurable (here it is constant).

Under suitable versions of these assumptions, finite-horizon dynamic programming and measurable-selection results yield a measurable optimal Markov policy. Weak continuity and compactness are convenient sufficient conditions, not necessary ones. More general existence results can use inf-compactness and lower-semicontinuity conditions.

### What is the one-step cost in this model?

For the submission action it is

\[
c_n(s,\hat P,I_n)=I_nL(B_n+\hat P).
\]

For the wait action it is zero. The terminal cost is \(M\).

The one-step cost is therefore bounded if, for example,

\[
0\leq B_n\leq B_{\max},\qquad
0\leq\hat P\leq P_{\max}<\infty,
\]

because then

\[
0\leq c_n\leq L(B_{\max}+P_{\max}).
\]

If the base fee is unbounded on the theoretical state space, use integrability conditions instead, for example finite conditional first moments, with stronger uniform-integrability assumptions where needed to establish continuity of expected costs.

**Important:** fitting a GARCH or empirical transition model does not automatically establish weak continuity. It must be checked for the particular specification. A finite empirical/discretized kernel may require a different existence theorem.

---

## 7. Inclusion-probability model: a tractable starting point

A possible smooth specification is

\[
q_n(s,\hat P)
=
\sigma\left(
\frac{\log(1+\hat P)-m(s)}{d(s)}
\right),
\qquad
\sigma(z)=\frac{1}{1+e^{-z}},
\]

where \(d(s)>0\).

Here:

- \(m(s)\) is a state-dependent fee level around which inclusion probability rises.
- \(d(s)\) controls how gradual or sharp the transition is.
- Both can depend on lagged p50/p90 fees, utilization, and possibly the base fee.

For example, with \(Y^{50}_{n-1}=\log(1+P^{50}_{n-1})\) and \(Y^{90}_{n-1}=\log(1+P^{90}_{n-1})\), one could begin with

\[
m(s)=\beta_0+\beta_1Y^{50}_{n-1}
+\beta_2(Y^{90}_{n-1}-Y^{50}_{n-1})
+\beta_3X_{n-1}.
\]

This is a **candidate functional form**, not an inclusion probability identified by the current block-level dataset.

The block-level data contain fees of included transactions, but not the offers made by transactions that remained pending. Consequently, they do not directly identify \(q_n(s,\hat P)\). Calibration requires transaction-level/mempool data, an external inclusion dataset, or explicit structural assumptions. If only the present dataset is available, treat inclusion parameters as uncertain and perform sensitivity analysis rather than claiming empirical identification.

---

# Part II — Statistical analysis and model choice

## 8. Decision-focused model selection: the governing principle

The primary goal is not to minimize one-step prediction error for \(X_n\), \(P_n\), or \(S_{n+1}\). It is to choose a model that produces a good policy and a reliable estimate of its expected cost.

A model can predict the next state very accurately but still give poor decisions if it misrepresents:

- the upper tail of priority fees;
- congestion persistence;
- the dependence between inclusion and the next state;
- the cost of waiting near the deadline;
- the response of inclusion probability to the offered fee.

Conversely, a model with somewhat worse global state-prediction scores may give a better stopping/submission policy if it captures the cost-relevant regions accurately.

The model-selection hierarchy should therefore be:

1. **Primary:** out-of-sample expected cost under the policy learned by the model.
2. **Primary:** cost reduction relative to relevant benchmark policies.
3. **Primary:** robustness and uncertainty of the estimated cost reduction.
4. **Secondary:** calibration of inclusion probabilities and cost-relevant conditional distributions.
5. **Diagnostic:** generic state-prediction scores such as RMSE.

State prediction remains necessary to compute Bellman expectations, but it is not the final objective.

---

## 9. Data integrity and derived variables

### Checks

- [ ] Check duplicate and missing block numbers.
- [ ] Identify missing blocks and timestamp gaps.
- [ ] Check positive and plausible base fees, gas usage, and gas limits.
- [ ] Check p90 priority fee is at least p50.
- [ ] Check units and any changes in data collection methodology.
- [ ] Identify protocol upgrades or structural breaks that may change the data-generating process.
- [ ] Distinguish genuine extreme observations from data errors.

### Derived variables

- [ ] Target-relative utilization:
  \[
  X_n=\frac{\mathrm{gas\_used}_n}{\mathrm{gas\_limit}_n/2}.
  \]
- [ ] Log priority-fee variables:
  \[
  Y_n^{50}=\log(1+P_n^{50}),\qquad
  Y_n^{90}=\log(1+P_n^{90}).
  \]
- [ ] Fee dispersion:
  \[
  D_n=Y_n^{90}-Y_n^{50}.
  \]
- [ ] Base-fee log change:
  \[
  r_n^B=\log(B_{n+1}/B_n).
  \]
- [ ] Block interval:
  \[
  \Delta t_n=t_{n+1}-t_n.
  \]
- [ ] Optional transaction-count intensity, e.g. \(\log(1+\mathrm{tx\_count}_n)\).

### Descriptive analysis

- [ ] Plot all series and rolling means/variances.
- [ ] Compute quantiles, skewness, and kurtosis.
- [ ] Plot distributions and Q-Q plots.
- [ ] Plot utilization against p50, p90, and fee dispersion.
- [ ] Examine high-congestion periods separately.
- [ ] Check whether relationships change over time.

---

## 10. Validate the EIP-1559 base-fee mechanism

The base fee is mechanically related to previous-block utilization. Reconstruct \(B_{n+1}\) from \(B_n\) and \(X_n\), using the exact protocol arithmetic.

- [ ] Compare reconstructed and observed next-block base fees.
- [ ] Investigate discrepancies, rounding, minimum changes, and data alignment.
- [ ] Confirm the correct block indexing.

This is a structural consistency check, not a model-selection test. It prevents wasting effort fitting an independent stochastic process to a protocol-determined variable.

---

## 11. Time-series diagnostics for utilization and priority fees

Perform these diagnostics on \(X_n\), \(Y_n^{50}\), \(Y_n^{90}\), and \(D_n\), as appropriate.

### Stationarity and breaks

- [ ] Augmented Dickey-Fuller (ADF): null is a unit root.
- [ ] KPSS: null is stationarity.
- [ ] Optionally Phillips-Perron as a supplementary unit-root test.
- [ ] Repeat on differences where economically appropriate.
- [ ] Bai-Perron multiple structural-break tests or another break-detection method.
- [ ] Check whether conclusions change across protocol/market regimes.

Do not difference a series mechanically just because a unit-root test rejects stationarity. Choose transformations consistent with the intended conditional model.

### Serial dependence

- [ ] ACF and PACF plots.
- [ ] Ljung-Box tests at several horizons, e.g. 5, 10, 20, 50.
- [ ] Test whether older lags add information beyond the proposed state.
- [ ] Compare one-, two-, and multi-lag conditional models.
- [ ] Use likelihood-ratio tests for nested models where valid.
- [ ] Compare AIC/BIC as supporting diagnostics.
- [ ] Check residual autocorrelation after fitting each candidate model.

These tests help assess whether \(S_n=(B_n,X_{n-1},P_{n-1})\) is a sufficiently informative state. They cannot prove the Markov property.

### Conditional volatility

- [ ] Fit an initial conditional-mean model.
- [ ] ARCH-LM test on residuals.
- [ ] Ljung-Box test on squared residuals.
- [ ] Inspect rolling variance and volatility clustering.
- [ ] Test whether volatility depends on congestion or fee levels.

If volatility clustering is material, compare GARCH-type models against constant-variance alternatives.

### Tails and extremes

- [ ] Skewness and excess kurtosis.
- [ ] Q-Q plots.
- [ ] Jarque-Bera as a supplementary normality diagnostic.
- [ ] Examine large positive innovations and their temporal clustering.
- [ ] Compare Gaussian and Student-t innovations.
- [ ] Consider generalized Pareto tail modelling for sufficiently extreme exceedances.
- [ ] Distinguish isolated jumps from persistent high-volatility/congestion regimes.

Non-Gaussian residuals do not by themselves establish the presence of jumps.

---

## 12. Conditional dependence and joint transition specification

The next-state variables should not be modelled independently without evidence.

### Regressions

For example, estimate

\[
Y_n^{50}
=\alpha+\beta_1X_{n-1}
+\beta_2Y_{n-1}^{50}
+\varepsilon_n^P
\]

and

\[
X_n
=\gamma+\gamma_1X_{n-1}
+\gamma_2Y_{n-1}^{50}
+\varepsilon_n^X.
\]

- [ ] Test whether lagged utilization predicts priority fees.
- [ ] Test whether lagged priority fees predict utilization.
- [ ] Add p90 or the p90–p50 spread where relevant.
- [ ] Examine residual cross-correlation.
- [ ] Test nonlinear dependence and dependence during congestion.
- [ ] Compare separate regressions with a joint innovation model.
- [ ] Consider a copula, multivariate Student-t, conditional empirical distribution, or regime mixture if dependence is material.

Utilization is bounded. A standard unconstrained Gaussian AR model can generate impossible values. Consider Beta regression for \(X_n/2\), boundary-inflated Beta models where needed, or a bounded/discretized transition model.

### Markov-state adequacy

- [ ] Compare the proposed state with versions adding \(X_{n-2}\), \(P_{n-2}\), and other available lagged features.
- [ ] Test whether `tx_count` improves conditional prediction or policy value.
- [ ] Check whether residual dependence remains after conditioning on the proposed state.
- [ ] Examine stability across congestion regimes.

Retain additional state variables only if they materially improve decision performance or are needed to make the transition model sufficiently Markovian.

---

## 13. Inclusion model: what can and cannot be learned from the current dataset

This is the principal data limitation.

The available block-level dataset records transactions that were included. It does not record all fee offers that were pending and not included. Therefore it does not directly identify

\[
q_n(s,\hat P)=\Pr(I_n(\hat P)=1\mid S_n=s).
\]

The p50 and p90 of included transactions are useful indicators of the fee competition among successful transactions, but they are not direct estimates of the inclusion probability for a new transaction offering \(\hat P\).

### With the current dataset

- [ ] Use p50, p90, their spread, and utilization to construct candidate state-dependent fee-competition features.
- [ ] Specify a family of plausible inclusion curves, e.g. logistic curves.
- [ ] Enforce monotonicity in the offered priority fee:
  \[
  \hat P_1\leq\hat P_2
  \implies q_n(s,\hat P_1)\leq q_n(s,\hat P_2).
  \]
- [ ] Enforce \(0\leq q_n\leq1\).
- [ ] Explore multiple slopes and fee thresholds.
- [ ] Perform sensitivity analysis over all inclusion parameters.
- [ ] Avoid describing the resulting \(q\) as empirically estimated unless inclusion outcomes and unsuccessful offers are observed.

### Additional data that would identify/calibrate inclusion more credibly

- [ ] Transaction submission/broadcast timestamps.
- [ ] Offered priority fee and max fee per gas.
- [ ] Transaction gas requirement.
- [ ] Inclusion block or time-to-inclusion.
- [ ] Pending/mempool observations, including transactions not yet included.
- [ ] Replacement/cancellation history.
- [ ] Network and block congestion at submission time.

With such data, estimate an inclusion or discrete-time hazard model. Account for right-censoring: transactions not included before the data window ends are not necessarily permanent failures.

Possible methods:

- Logistic regression for one-block inclusion.
- Discrete-time survival/hazard regression for time-to-inclusion.
- Generalized additive models for nonlinear fee effects.
- Gradient-boosted models, with monotonicity constraints where appropriate.
- Calibration plots, Brier score, log loss, and reliability analysis.

The inclusion model should be validated on held-out transactions and periods, not only on the same observations used for fitting.

---

## 14. Candidate market-dynamics models

Compare a small, interpretable set before using more complex specifications.

### Model A: bounded autoregression + log-AR

- Bounded conditional model for utilization.
- AR model for log p50 and/or fee dispersion.
- Joint innovations if residual dependence requires it.
- Exact EIP-1559 base-fee update.

### Model B: conditional volatility

- Bounded utilization model.
- Log-AR-GARCH or Student-t GARCH for priority-fee variables.
- Joint innovations or dependence model.

### Model C: regime switching

- Two- or three-regime Markov-switching model.
- Regime-dependent utilization and priority-fee dynamics.
- Regime-dependent volatility and transition probabilities.

### Model D: heavy-tailed or empirical conditional model

- Student-t or mixture innovations.
- Conditional empirical resampling or a flexible conditional distribution.
- Preserve cross-dependence between utilization and priority fees.

### Model E: jump or self-exciting extension

Use only if the diagnostics indicate extreme movements not adequately captured by heavy tails or regime switching. Jump models add complexity and should demonstrate decision-value improvement.

For each model, assess whether the induced joint kernel for \((S_{n+1},I_n)\) has the regularity needed for the intended existence theorem. If a discrete empirical kernel is used, consider a suitable more general theorem rather than assuming weak continuity.

---

## 15. Decision-focused model comparison

This section is the most important for the research objective.

### 15.1 Define benchmark policies

Evaluate every candidate model against the same benchmarks:

- [ ] Always submit immediately with a fixed priority fee.
- [ ] Always wait until the final eligible block, then submit using a specified fee.
- [ ] A simple state-dependent fee threshold policy.
- [ ] The best fixed-fee policy selected using training data.
- [ ] The learned optimal policy under each candidate model.

Benchmarks must obey the same deadline, fee constraints, and inclusion assumptions.

### 15.2 Train/test design

Use chronological rather than random splits.

- [ ] Fit transition and inclusion models on an initial training period.
- [ ] Tune hyperparameters and policy parameters on a validation period.
- [ ] Freeze the policy before evaluating on a later test period.
- [ ] Use rolling-origin or walk-forward evaluation to assess stability.
- [ ] Avoid leakage: no block-\(n\) statistics may enter a decision made at the beginning of block \(n\).

### 15.3 Primary decision metrics

For each policy \(\pi\), estimate its held-out expected cost:

\[
\widehat J(\pi)
=\frac{1}{R}\sum_{r=1}^{R} C^{(r)}(\pi),
\]

where \(C^{(r)}(\pi)\) is the total realized cost in test episode \(r\), including the terminal penalty if inclusion fails by the deadline.

Report:

- [ ] Mean total cost.
- [ ] Cost reduction relative to each benchmark:
  \[
  \widehat\Delta(\pi)
  =\widehat J(\pi_{\mathrm{benchmark}})
  -\widehat J(\pi).
  \]
- [ ] Percentage cost reduction.
- [ ] Standard error and confidence interval for cost reduction.
- [ ] Frequency of deadline failure.
- [ ] Mean and distribution of submission block.
- [ ] Mean offered priority fee.
- [ ] Cost distribution and upper quantiles.
- [ ] Results by congestion regime and deadline length.

Use paired comparisons: evaluate candidate and benchmark policies on the same test episodes and, where simulation is involved, use common random numbers. This reduces variance in policy comparisons.

Use block/bootstrap methods or episode-level resampling that respects temporal dependence. Do not treat adjacent blocks as independent observations.

### 15.4 Policy-value uncertainty

- [ ] Bootstrap the training data and refit the model/policy.
- [ ] Evaluate each refitted policy on common held-out episodes.
- [ ] Quantify uncertainty in the estimated cost reduction.
- [ ] Examine whether policy choices are stable across bootstrap replications.
- [ ] Perform sensitivity analysis over uncertain inclusion parameters.
- [ ] Report worst-case or robust cost over a plausible parameter set, if appropriate.

A model with a slightly lower estimated mean cost but very high uncertainty may be less attractive than a robust model with a reliably positive cost reduction.

### 15.5 Decision-weighted diagnostics

In addition to generic predictive scores, inspect model performance where it can change the action:

- [ ] States where the model is nearly indifferent between waiting and submitting.
- [ ] High-congestion states.
- [ ] States close to the deadline.
- [ ] Fee offers around the steep part of the inclusion curve.
- [ ] States where the estimated policy changes between candidate models.

Errors in these regions are more consequential than errors in states where all models recommend the same action.

---

## 16. Secondary predictive diagnostics

These are useful for detecting misspecification, but should not determine the final model alone.

- [ ] RMSE and MAE for conditional means of utilization and fees.
- [ ] Log predictive score.
- [ ] Continuous ranked probability score (CRPS).
- [ ] Quantile coverage, especially upper-tail fee forecasts.
- [ ] Residual ACF and squared-residual ACF.
- [ ] Distributional calibration of simulated state paths.

The final model should be judged primarily by out-of-sample policy value and robustness, with these diagnostics used to understand why a model succeeds or fails.

---

## 17. Simulation and policy evaluation

For each candidate model:

1. Estimate the state transition model from training data.
2. Specify or calibrate the inclusion mechanism.
3. Preserve dependence between inclusion and next-state innovations.
4. Solve the finite-horizon Bellman recursion numerically.
5. Obtain the policy:
   \[
   \pi_n^*(s)\in\{\text{wait},\text{submit }\hat P_n^*(s)\}.
   \]
6. Simulate or replay independent test episodes.
7. Record realized inclusion costs and terminal penalties.
8. Compare policy values with benchmarks.

When using historical replay, be careful: the historical block data alone do not reveal the counterfactual inclusion outcome for an arbitrary offered fee. Counterfactual policy evaluation therefore requires a calibrated inclusion model or additional transaction/mempool data. Simulated results should be labelled as conditional on the assumed inclusion mechanism.

---

## 18. Recommended practical order of work

### Phase 1 — Prepare and understand the data

- [ ] Validate block sequence and EIP-1559 base-fee update.
- [ ] Construct utilization and log fee variables.
- [ ] Produce descriptive plots and summary statistics.
- [ ] Test stationarity, structural breaks, serial dependence, volatility, and tails.

### Phase 2 — Estimate market dynamics

- [ ] Fit bounded utilization and log-fee baseline models.
- [ ] Test cross-dependence.
- [ ] Compare AR, GARCH, heavy-tailed, regime-switching, and empirical alternatives.
- [ ] Check whether the proposed observable state is sufficiently informative.

### Phase 3 — Specify inclusion

- [ ] Start with a monotone logistic inclusion curve.
- [ ] Treat its parameters as assumptions/sensitivity parameters unless additional inclusion data are obtained.
- [ ] Preserve dependence between inclusion and next-state variables.
- [ ] If possible, collect transaction-level and mempool data to estimate a hazard/inclusion model.

### Phase 4 — Solve and evaluate the control problem

- [ ] Implement the Bellman recursion with \(V_{N+1}=M\).
- [ ] Numerically optimize the priority fee at each state.
- [ ] Compare with immediate-submission, deadline-submission, and fixed-fee benchmarks.
- [ ] Evaluate on chronological held-out periods.
- [ ] Quantify confidence intervals for cost reduction.
- [ ] Perform inclusion-parameter and model uncertainty sensitivity analyses.

---

## 19. Main methodological conclusions

1. The correct stochastic object is the joint kernel of \((S_{n+1},I_n)\) conditional on \((S_n,\hat P)\), not just a transition model for the state.
2. The Bellman equation must retain the dependence between inclusion and the next state:
   \[
   V_n(s)=W_n(s)+\min\left\{0,\inf_{\hat P}
   \mathbb E[I_n(\hat P)(L(B_n+\hat P)-V_{n+1}(S_{n+1}))\mid S_n=s]\right\}.
   \]
3. The terminal condition is \(V_{N+1}(s)=M\).
4. The one-step submission cost is \(I_nL(B_n+\hat P)\); failure has zero immediate cost and leads to the next state.
5. The current block-level dataset can support estimation of market-state dynamics, but cannot by itself identify the probability that a newly submitted transaction is included at an arbitrary offered fee.
6. Inclusion probabilities should therefore be calibrated using additional data or treated as uncertain modelling assumptions with sensitivity analysis.
7. The final model should be selected primarily by out-of-sample expected cost reduction, benchmark comparisons, and robustness—not by state-prediction RMSE alone.
