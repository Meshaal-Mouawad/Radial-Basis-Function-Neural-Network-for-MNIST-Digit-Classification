# Independent mathematical review: finite-width prototype agreement

Review date: 6 November 2026. Scope: the proposed Gaussian RBF nearest-prototype agreement certificate over the complete parameter rectangle `(0, t] × [lambda0, infinity)`. This review independently derived the result, tested generated examples, and checked the role of established residual bounds. No MNIST or Fashion-MNIST evaluation data were read.

## Decision

**PASS for the sharpened theorem, under the explicit assumptions below.** The algebra, center-block spectral bound, width monotonicity and ridge-penalty uniformity are valid. The sharpened certificate is analytically no weaker than the basic certificate. The theorem establishes a sufficient parameter-region guarantee before solving the readout. Its empirical coverage and specialist-journal contribution require the separate frozen experiment and literature review.

One related claim needs correction if it is used: distinct selected centers alone do not establish the small-width limit `H → S`. Non-center training observations can duplicate a selected center. A counterexample below invalidates an unrestricted nearest-prototype-collapse corollary; it does not invalidate the finite certificate.

## Assumptions and notation

Let `X` contain `N` fixed training inputs in Euclidean space. Select `K` distinct training row indices and let `S` be their `N × K` selector matrix, so `S^T S = I`. Let `Y` be the `N × C` one-hot label matrix and `Y_C = S^T Y` the prototype labels. The classifier uses

\[
 H_\sigma(i,j)=\exp[-\|x_i-c_j\|^2/(2\sigma^2)],\quad
 G_{\sigma,\lambda}=H_\sigma^T H_\sigma+\lambda I,\quad
 W_{\sigma,\lambda}=G_{\sigma,\lambda}^{-1}H_\sigma^T Y.
\]

The objective uses the **sum** of squared residuals plus `lambda ||W||_F^2`, without an intercept. A mean-residual objective would replace the algebraic penalty by `N lambda`. The same isotropic width is used for all Gaussian units. Prototype coordinates and all input preprocessing are fixed throughout the parameter rectangle.

The endpoint is `t > 0`, the ridge lower endpoint is `lambda0 >= 0`, and the certificate is evaluated only when the lower denominator defined below is positive. Distinct prototype coordinates ensure that the unregularized Gaussian center block is nonsingular. Even when coordinates repeat, every positive-ridge fit remains unique; the certificate can simply abstain when its denominator vanishes.

## Independently verified derivation

### 1. Nonnegative feature perturbation

Write `H_sigma = S + E_sigma`. The selected self-responses equal one, so `E_sigma` is entrywise nonnegative and entrywise nondecreasing in `sigma`. Its selected-row block `E_C = S^T E_sigma` is symmetric. At the endpoint `t`, define

\[
 V=E_CY_C,\qquad
 P=E_{\bar C}^T Y_{\bar C},\qquad
 Q=E_t^T(E_tY_C).
\]

All three matrices are nonnegative. Their entries bound the corresponding matrices at every smaller positive width. `P` here contains **non-prototype rows only**. The basic bound's matrix `E_t^T Y` equals `V + P`; confusing these definitions would change the implementation.

### 2. Exact residual decomposition

Set `a = 1 + lambda` and use the prototype-only reference `W_0 = Y_C/a`. Direct expansion gives

\[
 R=H^TY-GW_0
 =\frac{\lambda-1}{1+\lambda}V+P-\frac{1}{1+\lambda}Q.
\]

This identity uses the symmetry of the prototype Gaussian block. It separates three mechanisms: cross-prototype responses, labeled non-prototype responses, and the quadratic overlap correction. For any two different classes `a` and `b`, write `V_ab = V[:,a] + V[:,b]` and similarly for `P_ab,Q_ab`. Entrywise triangle inequalities imply

\[
 (1+\lambda)|R[:,a]-R[:,b]|
 \leq |\lambda-1|V_{ab}+(1+\lambda)P_{ab}+Q_{ab}.
\]

The right side is an upper bound; the exact residual can have cancellations. Report the exact decomposition as an identity and the nonnegative expression as a majorant.

### 3. Spectral lower bound

Let `B_t = S^T H_t = I + E_C(t)` and

\[
 \beta=\max_i\sum_{j\ne i}B_t(i,j),\qquad
 c=[\max(1-\beta,0)]^2.
\]

The Gaussian center matrix is symmetric positive semidefinite, and Gershgorin gives `lambda_min(B_sigma) >= max(1-beta,0)` for all `sigma <= t`. Since `H_sigma^T H_sigma >= B_sigma^T B_sigma`,

\[
 \lambda_{\min}(G_{\sigma,\lambda})\geq c+\lambda.
\]

The clipping must occur **before squaring**. Squaring `1-beta` when `beta > 1` would produce an invalid positive lower bound. The condition `c + lambda0 > 0` is required to evaluate the certificate. A zero denominator means abstention.

### 4. Uniform ridge bound

Define the class-pair quantity

\[
 D_{ab}=\max\left\{
 \left\|\frac{|\lambda_0-1|V_{ab}+(1+\lambda_0)P_{ab}+Q_{ab}}{c+\lambda_0}\right\|_2,
 \|V_{ab}+P_{ab}\|_2
 \right\}.
\]

For `lambda >= lambda0`, let `delta = lambda-lambda0`. The inequality `|lambda-1| <= |lambda0-1|+delta` bounds the numerator by its lower-endpoint numerator plus `delta(V_ab+P_ab)`. Dividing by `c+lambda` produces a convex combination of the lower-endpoint vector and `V_ab+P_ab`. Convexity of the Euclidean norm therefore proves the bound `D_ab` uniformly in `lambda`.

Combining this result with the inverse-norm residual bound proves

\[
 \left\|(1+\lambda)(W[:,a]-W[:,b])-(Y_C[:,a]-Y_C[:,b])\right\|_2\leq D_{ab}
\]

throughout the rectangle. The construction uses endpoint `V,P,Q,c`, so it also holds uniformly in all `0 < sigma <= t`.

A sharper characterization is available without changing the stated formula: for `lambda0 <= 1`, the nonnegative majorant at `lambda0` componentwise dominates the one at `lambda=1`, using `c <= 1`. Above one, the vector is exactly a convex combination of the endpoint-one and infinity vectors. Thus the two endpoints also capture the supremum of the norm of this particular majorant. This is optional explanatory detail, not required for the theorem.

### 5. Query margin and decision agreement

Choose a nearest prototype `j0` for query `x`, with its class `a`, and define

\[
 r_j(t)=\exp[-(d_j^2-d_{j0}^2)/(2t^2)],\qquad d_j=\|x-c_j\|.
\]

The nearest component is one. Every component is nondecreasing in width, so `r_j(sigma) <= r_j(t)` for smaller widths. Dividing the query feature vector by its positive nearest activation leaves all classifier decisions unchanged. The prototype-reference class margin is at least

\[
 m_{ab}(t)=1-\sum_{j:Y_C(j,b)=1}r_j(t).
\]

Positive contributions from other prototypes of class `a` were discarded, so this is a lower bound. Cauchy–Schwarz then shows that the normalized learned class margin is strictly positive whenever

\[
 \boxed{m_{ab}(t)>\|r(t)\|_2 D_{ab}\quad\text{for every }b\ne a.}
\]

The conclusion is that **every fitted readout in the entire rectangle predicts class `a` for this query**. No readout fit is needed to evaluate the sufficient condition. Query feature rescaling is valid because it multiplies all class scores by the same positive scalar. Training-row normalization is not part of this proof and must not be introduced in the experiment.

### 6. Dominance over the basic bound

The basic class-pair constant is

\[
 D^{basic}_{ab}=\left\|\frac{(1+\lambda_0)(V_{ab}+P_{ab})+Q_{ab}}{c+\lambda_0}\right\|_2.
\]

Its vector componentwise dominates the sharpened lower-endpoint vector because `|lambda0-1| <= 1+lambda0`. It also dominates `V_ab+P_ab`, because `c <= 1`. Hence `D_ab <= D_ab^basic`. Using the same query-margin rule, every query certified by the basic method must also be certified by the sharpened method, apart from numerical threshold conventions. At `lambda0=0` the two bounds coincide. Strict improvements are possible for positive lower penalties.

## Independent synthetic audit

Executed script: `independent_theory/check_certificate.py`. Result record: `independent_theory/synthetic_audit.json`. The deterministic generator used seed `6700611` and created 60 small Euclidean training geometries with variable dimension, sample count, prototype count and class count. It generated near-prototype and unconstrained query locations, five upper widths, and four lower penalties. For every endpoint, it checked five interior/endpoint widths and several finite penalties including `1e8`.

| Check | Observed result |
|---|---:|
| Endpoint conditions | 1,200 |
| Total query/parameter evaluations | 237,150 |
| Certified endpoint queries, counted across conditions | 5,271 |
| Certified query/parameter checks | 117,975 |
| Prediction disagreements on certified checks | **0** |
| Maximum residual-identity absolute discrepancy | 1.42e-14 |
| Maximum computed excess over uniform coefficient bound | 1.11e-16 |
| Finite directed class-pair bounds compared | 6,976 |
| Strictly smaller sharpened pair bounds | 3,290 |

These counts describe implementation checks on generated cases. The proof supplies the continuum statement. The grid check does not independently exhaust the continuum.

## Edge cases and implementation disposition

| Situation | Required treatment |
|---|---|
| `c + lambda0 = 0` | Abstain; do not replace the denominator by epsilon. |
| `beta >= 1`, positive `lambda0` | Use `c=0`; the positive-ridge bound remains valid. |
| Nearest tie across different classes | The strict margin against a tied competing class is nonpositive, so the certificate abstains. |
| Nearest tie within the same class | The proof still works using either tied prototype; unique-nearest assumption can be retained for simpler exposition. |
| A class has no selected prototype | Keep that class among competitors; non-prototype labels enter `P` and are not dropped. |
| Duplicate selected coordinates | Positive ridge remains well defined; the denominator or margin can cause abstention. For zero ridge, enforce the theorem's nonsingularity assumptions. |
| Duplicates outside the selected rows | Allowed by the finite theorem. They can invalidate the simple small-width collapse corollary. |
| Row-normalized query activations | Valid, and useful to prevent narrow-width underflow. Compute distance gaps directly. |
| Row-normalized training activations, added bias, class weights, anisotropic/per-center widths | These change the model or monotonic/symmetry structure and require a separate derivation. |
| Strict boundary equality | Not certified; preserve strict inequality. |

### Counterexample to an unrestricted small-width corollary

Take training rows `(0, label0)`, `(3, label1)`, `(0, label1)`, `(0, label1)`. Select the first two rows as prototypes. Their coordinates are distinct. As the width decreases, the first readout row tends to `(1,2)/(3+lambda)`, so a query near zero is classified as class 1 although its nearest selected prototype carries class 0. At width `0.1` and query `0.01`, the independent calculation produces that disagreement for penalties `0`, `1`, and `100`. The record is `independent_theory/duplicate_counterexample.json`.

A sufficient simple condition for `H_sigma → S` is that every selected center coordinate occurs in exactly its selected training row. Alternatively, a more general limit can account explicitly for duplicate groups and their label counts. The finite theorem needs neither shortcut because `P,V,Q` retain the actual nonzero responses.

## Existing tools and the specific capability to evaluate

The step `error = inverse × residual` and its norm bound are established linear algebra. David Bindel's primary Cornell Matrix Computations notes state the residual-based bound explicitly under “Residual-based bounds” (2025-09-10, lines 130–132): https://www.cs.cornell.edu/courses/cs6210/2025fa/lec/2025-09-10.html . This source was opened; retrieval `turn76view0`. Gershgorin, Cauchy–Schwarz, convexity and Gaussian-kernel positive definiteness are likewise standard tools.

The specific construction under evaluation combines: the selected-row Gaussian identity `H=S+E`; the prototype/non-prototype residual decomposition; monotone endpoint majorants; the center-block spectral floor; and a two-endpoint ridge argument. Its output is a sufficient **whole-rectangle decision agreement guarantee without fitting a readout**, rather than the result of checking a fitted classifier's label against a nearest prototype. Its proposed intellectual contribution should be described at that level.

Rosenfeld et al. (ICML 2020) provide deterministic analytical prediction certificates against changed training labels. Their official abstract was inspected: https://proceedings.mlr.press/v119/rosenfeld20b.html (retrieval `turn76view1`). That prior capability prevents treating generic prediction certificates or training-label robustness as absent. The current theorem addresses a different varying object: width and regularization with fixed labels, tied to nearest-prototype decision agreement. The recent-journal literature agent must establish how this exact capability compares with current RBF/prototype work. This review does not infer universal novelty from a bounded unsuccessful keyword search.

## Numerical and editorial requirements

The theorem is a real-arithmetic statement. The synthetic implementation uses float64 and a positive margin guard of `1e-12`; the observed small discrepancies are at the expected floating-point scale. This audit does not turn an arbitrary guard into a formally proved rounding enclosure. Record the experiment's precision and guard, preserve certificate margins, inspect near-boundary cases at higher precision, and avoid claiming machine-verified interval arithmetic unless it is actually implemented. Query normalization prevents prediction underflow from masquerading as a label-disagreement result.

The primary empirical requirements are the measured certified coverage, actual nearest-prototype agreement, the coverage gain over the basic bound, the response to width and penalty, and the cost of the certificate calculation separated from full fitting. A failed certificate means the sufficient condition does not establish agreement. Retain all observed counterexamples outside its certified region and every negative coverage result.

**Final disposition:** the proof is suitable for the frozen experiment. Keep the uniformity and model assumptions explicit; retain the standard tools' attribution; correct any unrestricted duplicate-sensitive small-width corollary; and make no submission-readiness decision from this mathematical pass alone.

## Addendum: final theory report and count baseline

The completed `work/v2/theory.md` was subsequently read. Its exact residual, penalty supremum, monotone bandwidth frontier and duplicate-input scope agree with this independent derivation. For fixed `lambda0`, increasing `t` increases each nonnegative numerator and decreases the denominator floor; the query competitor mass and response norm also increase. The certified set is therefore nested as the upper width decreases. The penalty-floor monotonicity follows because the exact supremum of the selected majorant is taken over a shrinking domain.

The proposed cancellation-aware norm/count comparator is also valid. With `eta = ||E_t||_F`, `n_ab = ||Y[:,a]-Y[:,b]||_2^2`, and `k_ab = ||Y_C[:,a]-Y_C[:,b]||_2^2`,

\[
 D^{count}_{ab}=\frac{(1+\lambda_0)\eta\sqrt{n_{ab}}+\eta^2\sqrt{k_{ab}}}{c+\lambda_0}.
\]

The inequalities `||E^T|z|||_2 <= eta ||z||_2` and `||E^TE|z_C|||_2 <= eta^2 ||z_C||_2`, followed by the triangle inequality, show `D_sharp <= D_basic <= D_count`. This comparator retains the same certificate semantics while discarding the detailed label-specific overlap vectors. It is a stronger and more informative baseline than a direct norm expansion that separately bounds canceled prototype terms.

The scientific outcome is nearest-prototype **label agreement over a parameter region**. Use that exact language for the theorem and empirical metrics. A causal or human-interpretability conclusion would require different evidence and is not supplied by this label-agreement result.
