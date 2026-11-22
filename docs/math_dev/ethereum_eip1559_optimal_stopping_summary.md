# Ethereum EIP-1559 Gas Fee Modelling for Finite-Horizon Optimal Stopping

## 1. Objective and scope

The goal is to choose the block in which to submit a smart-contract
transaction so as to minimize expected transaction cost, subject to a
hard deadline (K).

The initial model makes two simplifying assumptions:

1.  Submitting the transaction is treated as equivalent to its
    acceptance/inclusion. This is reasonable as a first approximation if
    the offered priority fee is sufficiently high relative to the
    inclusion requirement.
2.  The objective is risk-neutral: minimize expected transaction cost. A
    concave utility function is therefore not needed in the baseline
    formulation. Risk aversion can be studied later as an extension.

If the gas requirement (L) is fixed, minimizing expected gas expenditure
is equivalent to minimizing expected gas price.

## 2. Available dataset

The dataset contains one observation per Ethereum block, with columns:

  --------------------------------------------------------------------------
  Field                                  Meaning / role
  -------------------------------------- -----------------------------------
  `block_number`                         Discrete-time index

  `timestamp`                            Block timestamp

  `base_fee_per_gas`                     EIP-1559 base fee applicable to the
                                         block

  `gas_used`                             Gas consumed in the block

  `gas_limit`                            Block gas limit

  `tx_count`                             Number of transactions

  `effective_priority_fee_per_gas_p50`   Median effective priority fee in the block

  `effective_priority_fee_per_gas_p90`   90th percentile effective priority fee in the block

The p50 and p90 priority-fee statistics are useful proxies for the fee
competition in a block. They are not, by themselves, exact estimates of
the minimum tip required for a new transaction to be included.

## 3. Time convention and information available at the decision time

Let block (n) cover the interval $(t_n,t_{n+1})$. At the beginning of
block $n$, before its utilization and priority-fee statistics are
observed, the decision-maker knows:

-   $B_n$: the base fee applicable to block $n$;
-   $X_{n-1}$: utilization of the previous block;
-   $P_{n-1}$: the previous block's priority-fee statistic.

Define target-relative block utilization as

$$ X_n = 2\frac{\mathrm{gas\_used}_n}{\mathrm{gas\_limit}_n}.$$

Thus $X_n=1$ corresponds to target utilization and, approximately,
$0\leq X_n\leq 2$.

For the priority fee, choose a consistent statistic. A natural baseline
is

$$ P_n=P_n^{50},$$

with p90 used as a conservative alternative or as an additional measure
of fee dispersion. Do not mix p50 and p90 without explicitly defining
the state and transition model.

### 3.1 Observable state

The proposed observable state at the beginning of block $n$ is

$$ {S_n=(B_n,X_{n-1},P_{n-1}).} $$

This is the information on which the block-$n$ submission decision may
depend.

The corresponding decision filtration is

$$ \mathcal F_n = \sigma(B_0,\ldots,B_n,X_0,\ldots,X_{n-1}, P_0,\ldots,P_{n-1}). $$


In particular, $B_n,X_{n-1},P_{n-1}$ are observable at the decision
time, whereas $X_n,P_n$ are not. A valid stopping time $\tau$
must satisfy

$$ {\tau\leq n}\in\mathcal F_n. $$

This is an information-timing issue: the variables can be adapted to a
larger filtration, but current-block utilization and priority fees must
not be used to make the decision at the beginning of that same block.

## 4. EIP-1559 base-fee transition

The base fee is not an unconstrained stochastic process. Its next value
is mechanically determined by current base fee and current block
utilization.

Ignoring integer rounding and protocol edge cases,

$$ B_{n+1}=f(B_n,X_n)=B_n\left(1+\frac{X_n-1}{8}\right). $$

The exact implementation should reproduce EIP-1559 integer arithmetic
and its minimum adjustment rules.

This suggests modelling utilization and priority fees stochastically,
then deriving the base-fee path from the protocol recurrence. It is
preferable to fitting an independent GBM or CIR process directly to the
base fee.

### Structural validation

For every consecutive block pair:

1.  Calculate the protocol-predicted $B_{n+1}$ from $B_n$ and $X_n$.
2.  Compare it with the observed next-block base fee.
3.  Investigate discrepancies, accounting for integer rounding, protocol
    rules, missing blocks, and data alignment.

This is a protocol-consistency check rather than a conventional
hypothesis test.

## 5. Markov transition model

The proposed state transition is

$$ S_{n+1}=(B_{n+1},X_n,P_n). $$

Given $S_n=(B_n,X_{n-1},P_{n-1})$, the stochastic part of the
transition is the joint conditional distribution

$$Q(dx,dp\mid S_n)=\Pr(X_n\in dx,P_n\in dp\mid B_n,X_{n-1},P_{n-1}). $$

The next state is then obtained by applying the deterministic base-fee
update:

$$ S_{n+1}= \left(B_n\left(1+\frac{X_n-1}{8}\right), X_n,P_n\right), $$

with the exact protocol formula used in implementation.









$\color{red}{\text{I don't think the factorization is valid since I expect strong correlation between block congestion and priority fees}}$


A possible factorization is

$$ Q(dx,dp\mid S_n) = Q_X(dx\mid S_n),Q_P(dp\mid X_n,S_n). $$

This permits priority fees to depend on current utilization, while
recognizing that both (X_n) and (P_n) are unknown at the decision time.
In the Bellman expectation, one integrates over their joint conditional
distribution.

Illustrative conditional specifications include

$$ X_n\sim  F_X(\cdot\mid X_{n-1},P_{n-1},B_n)$$

and

$$ \log(1+P_n)\sim F_P(\cdot\mid X_n,X_{n-1},P_{n-1},B_n). $$

These are candidate structures, not assumptions that should be imposed
without diagnostics.

### Markov sufficiency

The state $S_n=(B_n,X_{n-1},P_{n-1})$ is a proposed state, not a
proven sufficient Markov state. Test whether older lags contain
additional predictive information. If they do, augment the state, for
example with $X_{n-2}$, $P_{n-2}$, or further lags.

## 6. Cost and optimal stopping formulation

Let $L$ denote the transaction's gas requirement and
$\widehat P_n$ the priority fee offered when submitting in block
$n$. The effective gas price, under the simplifying inclusion
assumption, is

$$ G_n=B_n+\widehat P_n, $$

and transaction cost is

$$ C_n=L(B_n+\widehat P_n). $$

The offer $\widehat P_n$ must be specified using information
available at the decision time, for example as a policy based on $S_n$.
A historical p50 or p90 is a proxy for the competitive environment, not
necessarily the exact inclusion threshold.

For a deadline at block $K$, the risk-neutral problem is

$$\boxed{\inf_{\tau\in\mathcal T_K}\mathbb E[C_\tau],\qquad 0\leq\tau\leq K,}$$

where $\mathcal T_K$ is the set of stopping times with respect
to $(\mathcal F_n)$.

Define

$$ V_n(s)=\inf_{\tau\in\{n,\ldots,K\}}\mathbb E[C_\tau\mid S_n=s]. $$

The terminal condition is

$$ V_K(s)=\mathbb E[C_K\mid S_K=s]=L\left(B_K+\mathbb E[\widehat P_K\mid S_K=s]\right), $$

and the Bellman recursion for $n<K$ is

$$ \boxed{V_n(s)=\min\left\{\mathbb E[C_n\mid S_n=s],\mathbb E[V_{n+1}(S_{n+1})\mid S_n=s]\right\},} $$


The optimal policy stops when immediate cost is no greater than the
conditional expected value of continuing, and must stop at $K$.

This formulation is a little different from classical optimal stopping problems since
at the beginning of block $K$, the decision maker observes $S_K=s$, but does not yet observe the block-$K$ utilization or priority-fee statistics.
## 7. Empirical variables to construct

Before fitting models, construct:

1.  **Target-relative utilization** $
   X_n=2\frac{\mathrm{gas\_used}_n}{\mathrm{gas\_limit}_n}. $

2.  **Base-fee log return** $ r_n^B=\log(B_{n+1}/B_n). $
    This should be explained almost entirely by $X_n$ through the
    protocol rule.

3.  **Log priority-fee variables** $Y_n^{50}=\log(1+P_n^{50}),\qquad Y_n^{90}=\log(1+P_n^{90}). $

4.  **Priority-fee dispersion** $ D_n=Y_n^{90}-Y_n^{50}. $

5.  **Block interval** $\Delta t_n=t_{n+1}-t_n. $

6.  **Changes/innovations** in utilization and log priority-fee series.

Check that p90 is at least p50, that units are consistent, and that the
data are correctly aligned by block number.

# Statistical Analysis Checklist — Ethereum EIP-1559 Optimal Stopping Model

## 1. Data integrity and preprocessing

- [ ] Check for duplicate block numbers.
- [ ] Check that block numbers are consecutive and identify missing blocks.
- [ ] Check for missing values in all relevant columns.
- [ ] Check that timestamps are ordered and identify anomalous block intervals.
- [ ] Verify that `gas_used`, `gas_limit`, and `base_fee_per_gas` are positive and plausible.
- [ ] Verify that priority-fee percentiles satisfy $P_n^{90}\geq P_n^{50}$.
- [ ] Check units and scaling of all fee variables.
- [ ] Identify extreme observations and determine whether they are genuine or data errors.
- [ ] If the deadline is defined in wall-clock time, examine the distribution of block intervals.

### Construct derived variables

- [ ] Target-relative gas utilization:
  $
X_n=2\frac{\mathrm{gas_used}_n}{\mathrm{gas_limit}_n}.
  $
- [ ] Log priority-fee variables:
 $[
  Y_n^{50}=\log(1+P_n^{50}),\qquad
  Y_n^{90}=\log(1+P_n^{90}).
  $
- [ ] Priority-fee dispersion:
  $
  D_n=Y_n^{90}-Y_n^{50}.
  $
- [ ] Log base-fee changes:
  $
  r_n^B=\log(B_{n+1}/B_n).
  $
- [ ] Block intervals:
  $
  \Delta t_n=t_{n+1}-t_n.
  $

## 2. Descriptive statistics and visualization

- [ ] Compute mean, median, standard deviation, minimum, maximum, and selected quantiles for all variables.
- [ ] Examine skewness and excess kurtosis.
- [ ] Plot time series of base fee, utilization, p50 priority fee, and p90 priority fee.
- [ ] Plot log transformations and first differences.
- [ ] Plot rolling means and rolling standard deviations.
- [ ] Plot the empirical distributions and Q-Q plots.
- [ ] Examine the relationship between utilization and priority fees using scatter plots and conditional averages.
- [ ] Examine the relationship between base fee and priority fees.
- [ ] Identify periods of unusually high congestion and fee volatility.

## 3. Validate the EIP-1559 base-fee mechanism

The base fee is mechanically determined by the previous block's utilization. Ignoring integer rounding and protocol-specific details:


$B_{n+1}=B_n\left(1+\frac{X_n-1}{8}\right).
$
- [ ] Reconstruct the expected next-block base fee from the observed utilization.
- [ ] Compare reconstructed and observed base fees.
- [ ] Investigate every discrepancy.
- [ ] Implement the exact EIP-1559 integer arithmetic for a definitive validation.
- [ ] Confirm that the base-fee series is correctly aligned with the block utilization series.

This is primarily a **structural consistency check**, rather than a conventional statistical hypothesis test.

## 4. Stationarity and structural breaks

Perform the following tests on relevant levels, differences, and transformed variables.

- [ ] Augmented Dickey-Fuller (ADF) test — null hypothesis: unit root.
- [ ] KPSS test — null hypothesis: stationarity.
- [ ] Consider Phillips-Perron as an additional unit-root test.
- [ ] Repeat tests on first differences where appropriate.
- [ ] Examine whether conclusions are sensitive to deterministic trends and lag selection.
- [ ] Test for structural breaks, for example using Bai-Perron multiple-break tests.
- [ ] Examine whether identified breaks correspond to changes in Ethereum activity, protocol conditions, or market structure.

**Interpretation of ADF and KPSS results:**

| ADF            | KPSS           | Interpretation                                 |
| -------------- | -------------- | ---------------------------------------------- |
| Reject         | Fail to reject | Evidence supporting stationarity               |
| Fail to reject | Reject         | Evidence supporting nonstationarity            |
| Reject         | Reject         | Possible structural breaks or misspecification |
| Fail to reject | Fail to reject | Inconclusive                                   |

Do not automatically difference every nonstationary series: the choice of transformation should reflect the economic and stochastic structure of the model.

## 5. Serial dependence and lag selection

The proposed observable state is:

$
S_n=(B_n,X_{n-1},P_{n-1}).$


Test whether the included lagged variables adequately capture temporal dependence.

- [ ] Plot ACF and PACF for utilization, priority fees, and their transformations.
- [ ] Plot ACF and PACF for first differences and model residuals.
- [ ] Perform Ljung-Box tests at lags 5, 10, 20, and 50.
- [ ] Test whether lagged utilization predicts current utilization.
- [ ] Test whether lagged priority fees predict current priority fees.
- [ ] Test whether older lags provide additional predictive information.
- [ ] Compare models with one, two, and more lags.
- [ ] Compare nested models using likelihood-ratio tests where applicable.
- [ ] Compare AIC and BIC across candidate specifications.
- [ ] Evaluate the additional lags using rolling out-of-sample forecasts.

If older lags remain predictive, consider augmenting the state with additional lagged variables.

## 6. Conditional heteroskedasticity and volatility dynamics

- [ ] Fit an initial conditional-mean model for each relevant stochastic variable.
- [ ] Examine residuals and squared residuals.
- [ ] Perform ARCH-LM tests on the residuals.
- [ ] Perform Ljung-Box tests on squared residuals.
- [ ] Examine rolling conditional volatility.
- [ ] Check whether volatility depends on utilization, base fees, or priority-fee levels.
- [ ] Determine whether volatility clusters over time.

If significant conditional heteroskedasticity is found, consider:

- [ ] GARCH(1,1) or alternative GARCH specifications.
- [ ] Asymmetric volatility models, such as GJR-GARCH or EGARCH.
- [ ] Regime-dependent volatility.

## 7. Distributional properties, heavy tails, and jumps

- [ ] Examine skewness and kurtosis of the original variables and model residuals.
- [ ] Use Q-Q plots to assess departures from Gaussian distributions.
- [ ] Perform Jarque-Bera tests as a supplementary diagnostic.
- [ ] Examine the frequency and magnitude of extreme observations.
- [ ] Check whether extreme observations occur independently or in clusters.
- [ ] Examine positive and negative extremes separately.
- [ ] Compare Gaussian and Student-t innovation distributions.
- [ ] Examine tail behaviour using empirical exceedances.
- [ ] Consider Generalized Pareto Distribution (GPD) modelling for sufficiently extreme tails.

If the data exhibit isolated extreme movements, consider jump or mixture models. If extreme movements cluster, investigate regime-switching or self-exciting dynamics.

Non-normality alone is not evidence of jumps.

## 8. Dependence between utilization and priority fees

The joint transition distribution matters because the next base fee depends on utilization, while the priority fee may also depend on utilization.

- [ ] Regress current priority fees on lagged priority fees and utilization.
- [ ] Test whether lagged utilization significantly predicts current priority fees.
- [ ] Regress current utilization on lagged utilization and priority fees.
- [ ] Test whether lagged priority fees significantly predict current utilization.
- [ ] Examine residual correlation between the two conditional-mean models.
- [ ] Examine dependence beyond linear correlation, especially during high-congestion periods.
- [ ] Compare conditional distributions across utilization ranges.
- [ ] Investigate whether p50 and p90 priority fees have different dynamics.
- [ ] Consider modelling the median and dispersion jointly rather than treating p50 and p90 as independent series.

A useful initial specification is:


$Y_n^{50}
=\alpha+\beta_1X_{n-1}
+\beta_2Y_{n-1}^{50}
+\varepsilon_n^P.$


$
X_n
=\gamma+\gamma_1X_{n-1}
+\gamma_2Y_{n-1}^{50}
+\varepsilon_n^X.$


The tests on $\beta_1$ and $\gamma_2$ help assess cross-dependence.

If dependence is material, estimate a joint conditional distribution rather than independently simulating utilization and priority fees.

## 9. Markov state sufficiency

The proposed state is:

$
S_n=(B_n,X_{n-1},P_{n-1}).
$


The objective is to assess whether this state contains sufficient information for predicting the next stochastic transition.

- [ ] Estimate a baseline model using the proposed state.
- [ ] Add $X_{n-2}$ and test whether it improves prediction.
- [ ] Add $P_{n-2}$ and test whether it improves prediction.
- [ ] Test additional lags if residual diagnostics suggest remaining dependence.
- [ ] Investigate whether `tx_count` adds predictive information.
- [ ] Investigate whether block intervals add predictive information, if observable at decision time.
- [ ] Compare AIC, BIC, likelihood-ratio tests, and out-of-sample performance.
- [ ] Examine whether state sufficiency changes across market regimes.

If important predictive information remains outside the state, consider augmenting it or introducing a latent regime variable.

For example, a regime-switching model could use a latent state $Z_n$, with the decision maker maintaining a belief:

$
\pi_n(j)=\Pr(Z_n=j\mid\mathcal F_n).
$


A finite collection of statistical tests cannot prove the Markov property. The practical objective is to establish that the proposed state is an adequate predictive state.

## 10. Candidate stochastic models

Fit a progressively more sophisticated collection of models.

### Model 1 — Simple baseline

- [ ] Bounded autoregressive model for utilization.
- [ ] AR(1) model for log-transformed priority fees.
- [ ] Deterministic EIP-1559 base-fee update.

### Model 2 — Conditional volatility

- [ ] Bounded autoregressive utilization model.
- [ ] AR-GARCH model for log priority fees.
- [ ] Deterministic base-fee update.

### Model 3 — Regime switching

- [ ] Markov-switching utilization model.
- [ ] Regime-dependent priority-fee dynamics.
- [ ] Regime-dependent volatility.
- [ ] Estimate regime transition probabilities.

### Model 4 — Heavy tails and jumps

- [ ] Heavy-tailed innovation distributions.
- [ ] Mixture distributions.
- [ ] Jump component if supported by the data.
- [ ] Preserve dependence between utilization and priority fees.

**Important modelling constraint:** utilization is bounded approximately between 0 and 2. Avoid an unconstrained Gaussian autoregression that can generate impossible values.

Possible alternatives include:

- [ ] Beta regression applied to $X_n/2$.
- [ ] Zero/one-inflated Beta distributions if boundary observations occur.
- [ ] Discretized Markov-chain models.
- [ ] Empirical conditional transition distributions.

## 11. Model selection and out-of-sample validation

Do not select the final model solely using AIC, BIC, or in-sample goodness of fit.

### Statistical adequacy

- [ ] Check residual autocorrelation.
- [ ] Check residual heteroskedasticity.
- [ ] Check distributional assumptions.
- [ ] Check tail behaviour.
- [ ] Check structural stability.
- [ ] Simulate paths and verify that generated values are plausible.

### Probabilistic forecasting

Use rolling-origin validation: estimate the model using data available up to block $n$, then forecast block $n+1$.

- [ ] Compare conditional-mean forecasts using RMSE and MAE.
- [ ] Compare predictive distributions using log predictive scores.
- [ ] Compare predictive distributions using CRPS.
- [ ] Evaluate quantile forecasts and quantile coverage.
- [ ] Pay particular attention to upper-tail priority-fee forecasts.
- [ ] Repeat the procedure over multiple evaluation periods.

### Optimal stopping performance

- [ ] Estimate the transition kernel using the training sample.
- [ ] Solve the finite-horizon Bellman recursion.
- [ ] Apply the resulting stopping policy to held-out periods.
- [ ] Evaluate realized transaction costs.
- [ ] Compare against immediate submission.
- [ ] Compare against submission at the deadline.
- [ ] Compare against simple threshold policies.
- [ ] Evaluate performance under alternative priority-fee offer assumptions.
- [ ] Examine sensitivity to the horizon (K).
- [ ] Examine performance during periods of high congestion and volatility.

## 12. Recommended implementation sequence

- [ ] Validate and clean the raw dataset.
- [ ] Construct utilization, priority-fee transformations, dispersion, and block intervals.
- [ ] Validate the EIP-1559 base-fee recurrence.
- [ ] Produce descriptive statistics and plots.
- [ ] Perform stationarity and structural-break analysis.
- [ ] Analyse serial dependence and select candidate lags.
- [ ] Test for conditional heteroskedasticity.
- [ ] Analyse tails, extremes, and possible jumps.
- [ ] Test utilization-priority-fee dependence.
- [ ] Assess the sufficiency of the proposed Markov state.
- [ ] Fit the simple bounded-utilization and log-AR priority-fee baseline.
- [ ] Compare GARCH, heavy-tailed, and regime-switching alternatives.
- [ ] Perform rolling out-of-sample probabilistic validation.
- [ ] Estimate the joint transition kernel.
- [ ] Solve the finite-horizon optimal stopping problem.
- [ ] Evaluate the stopping policy on held-out data.

