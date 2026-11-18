# Finite-parameter certificate for nearest-prototype decisions

Status: mathematical development and synthetic verification, 6 November 2026. No MNIST training, reserved observations, reserved labels, or new empirical outcomes were accessed in this work. The previous study remains unchanged.

## Main result and contribution scope

A class-aware training residual and the selected-prototype Gram matrix give a sufficient condition under which the ridge RBF classifier has the same label as the nearest selected prototype **for every bandwidth in (0, t] and every ridge penalty in [lambda_0, infinity)**. The condition can be evaluated without fitting the output weights or constructing the full training Gram matrix H^T H. Its preparation uses O(N K C) arithmetic after feature construction, where C is the number of classes; the full normal matrix uses O(N K^2).

The exact residual identity, standard matrix norm inequalities and Gershgorin theorem are mathematical ingredients, not separate novelty claims. The candidate research contribution is their combination into a fit-free parameter-region certificate, its label-sensitive decomposition, a closed-form maximization over the unbounded penalty interval, and measured useful coverage against suitable baselines. Novelty relative to the literature remains the literature/editorial team's gate.

This theorem certifies a label-equivalent nearest-prototype decision summary. Label agreement alone does not establish a causal explanation or human interpretability. Use the precise term **nearest-prototype label agreement** in the scientific claim.

## 1. Setup

There are N fixed training vectors x_i, with one-hot labels Y in {0,1}^{N x C}. The K prototypes are K distinct selected training-row indices. Their labels are Y_C = S^T Y, where S in {0,1}^{N x K} is the selection matrix with S^T S = I_K. Different selected rows may contain identical vectors; the finite theorem handles them through its applicability condition. Centers are fixed throughout the bandwidth and penalty region.

The Gaussian feature matrix is

H_sigma[i,j] = exp(-||x_i - c_j||^2 / (2 sigma^2)), sigma > 0.

The classifier fits the sum-of-squares objective ||H_sigma W - Y||_F^2 + lambda ||W||_F^2, with no added intercept and lambda >= 0. When lambda = 0, the theorem requires its stated positive eigenvalue lower bound, which makes the least-squares solution unique. The fitting rule is then

G_sigma,lambda = H_sigma^T H_sigma + lambda I,
W_sigma,lambda = G_sigma,lambda^{-1} H_sigma^T Y.

For a query x, the class score is h_sigma(x)^T W_sigma,lambda. All mathematical statements concern real arithmetic. Numerical implementation needs explicit tie handling, underflow-safe query scaling, tolerances and validation.

## 2. Nonnegative overlap quantities

Let E_sigma = H_sigma - S. Because a prototype's response at its own selected row is one, E_sigma is entrywise nonnegative and its entries are nondecreasing with sigma. Let E_C,sigma = S^T E_sigma. A common Euclidean Gaussian width makes this K x K matrix symmetric, with zero diagonal. This symmetry is essential to the simplified residual identity below.

Let R denote the rows not selected as prototypes. At an upper bandwidth t, form three K x C matrices:

V_t = E_C,t Y_C,
P_t = E_R,t^T Y_R,
Q_t = E_t^T (E_t Y_C).

All three are nonnegative and entrywise nondecreasing with t. Their roles are explicit:

- V_t collects overlap among the selected prototypes, grouped by their labels.
- P_t collects the labeled responses of non-prototype observations.
- Q_t collects the two-stage overlap contribution associated with the prototype-label reference weights.

Q_t must be computed as E_t^T(E_t Y_C), not by forming E_t^T E_t. The latter introduces the unnecessary K x K full-training Gram matrix. The three quantities can also be accumulated in blocks or a single pass over training rows.

The prototype Gram matrix is B_t = S^T H_t = I + E_C,t. Define

beta_t = max_j sum_{k != j} B_t[j,k],
gamma_t = max(1 - beta_t, 0)^2.

Thus 0 <= gamma_t <= 1.

## 3. Exact training residual identity

Use the reference weights W_0(lambda) = Y_C/(1+lambda), and let tau = 1+lambda. Define the normal-equation residual

R_sigma,lambda = H_sigma^T Y - G_sigma,lambda W_0(lambda).

The exact identity is

R_sigma,lambda = ((lambda-1)/(lambda+1)) V_sigma + P_sigma - Q_sigma/(lambda+1).  (1)

Proof. H^T Y = Y_C + V + P. Since S^T E = E^T S = E_C,
H^T H = I + 2 E_C + E^T E.
Substitution into the residual cancels Y_C and leaves (1). Consequently,

W_sigma,lambda - W_0(lambda) = G_sigma,lambda^{-1} R_sigma,lambda.  (2)

The sign change in the V coefficient at lambda=1 is an exact algebraic feature of this decomposition. It does not by itself imply a corresponding change of classification accuracy.

For classes a and b, write V_ab = V[:,a] + V[:,b], and similarly P_ab,Q_ab. Since all three component matrices are nonnegative, the pairwise residual obeys

|R[:,a] - R[:,b]| <= (|lambda-1| V_ab + (lambda+1) P_ab + Q_ab)/(lambda+1).  (3)

At any sigma <= t, the right-hand numerator can use the t quantities by their entrywise monotonicity.

## 4. Eigenvalue lower bound

The selected rows are a subset of H_sigma, so

H_sigma^T H_sigma >= B_sigma^T B_sigma

in the positive semidefinite order. B_sigma is real symmetric. If beta_t < 1, Gershgorin gives lambda_min(B_sigma) >= 1-beta_sigma >= 1-beta_t > 0 for every sigma <= t. Therefore

lambda_min(G_sigma,lambda) >= gamma_t + lambda.  (4)

For beta_t >= 1, gamma_t=0 and (4) reduces to the valid ridge lower bound lambda. Thus the rectangle must satisfy gamma_t + lambda_0 > 0. If this fails, the certificate is inapplicable and abstains; it must not divide by zero or infer model instability.

## 5. Closed-form maximization over all penalties

For each class pair, define the nonnegative vector

F_ab(lambda;t) = [|lambda-1| V_ab,t + (lambda+1) P_ab,t + Q_ab,t] / (gamma_t+lambda).

Equations (2)-(4) imply

(1+lambda) ||(W-W_0)[:,a] - (W-W_0)[:,b]||_2 <= ||F_ab(lambda;t)||_2.  (5)

For lambda >= lambda_0, the absolute-value triangle inequality gives

|lambda-1| <= |lambda_0-1| + (lambda-lambda_0).

Let theta = (gamma_t+lambda_0)/(gamma_t+lambda), which lies in (0,1]. Entrywise,

F_ab(lambda;t) <= theta F_ab(lambda_0;t) + (1-theta)(V_ab,t + P_ab,t).

The Euclidean norm is monotone for nonnegative vectors and convex. Hence the uniform bound is

K_ab(t,lambda_0) = max{ ||F_ab(lambda_0;t)||_2, ||V_ab,t + P_ab,t||_2 }.  (6)

Moreover, (6) is the exact supremum of the selected residual-norm majorant over lambda >= lambda_0: its two values are attained at lambda_0 and in the lambda -> infinity limit, and the preceding inequality supplies the converse bound. This is exact maximization of a majorant, not exact worst-case model discrepancy.

A simpler valid baseline replaces |lambda-1| V by (lambda+1)V. Its uniform bound is

K_basic,ab = ||[(1+lambda_0)(V_ab,t+P_ab,t)+Q_ab,t]/(gamma_t+lambda_0)||_2.  (7)

The sharp bound (6) never exceeds (7). Its finite endpoint is componentwise bounded by (7); its infinity endpoint is also bounded by (7), because gamma_t <= 1. When lambda_0=0, these two versions coincide.

A cancellation-aware Frobenius baseline replaces the retained class-specific overlap vectors by norm/count bounds. Let eta_t=||E_t||_F, n_ab be the number of training labels in {a,b}, and k_ab the number of prototype labels in {a,b}. Then

K_count,ab = [(1+lambda_0) eta_t sqrt(n_ab) + eta_t^2 sqrt(k_ab)]/(gamma_t+lambda_0).  (7a)

This follows from ||E^T |Y_a-Y_b|||_2 <= eta_t sqrt(n_ab) and ||E^T E |Y_C,a-Y_C,b|||_2 <= eta_t^2 sqrt(k_ab), applied to the basic majorant. The hierarchy is K_sharp <= K_basic <= K_count. A still looser direct residual-perturbation bound adds 2 eta_t sqrt(k_ab) to the numerator by separately bounding the prototype-block terms. The cancellation-aware version is the stronger norm baseline and prevents relying only on an avoidably loose comparator.

## 6. Query-specific rectangle theorem

Let j_0 be the nearest prototype to a query x, with label a. The implementation may require a unique nearest prototype; ties with other classes will in any event fail the strict condition below. Define at upper bandwidth t

r_j(t) = exp[-(||x-c_j||^2 - ||x-c_j0||^2)/(2t^2)],
L_b(t) = 1 - sum_{j: label(c_j)=b} r_j(t), for b != a,
n_t = ||r(t)||_2.

The certificate is

L_b(t) > n_t K_ab(t,lambda_0) for every b != a.  (8)

If gamma_t+lambda_0 > 0 and (8) holds, then

argmax_c h_sigma(x)^T W_sigma,lambda[:,c] = a

for every sigma in (0,t] and every finite lambda >= lambda_0.

Proof. Divide h_sigma by its positive j_0 response. This positive scaling does not change the classifier's decision. The resulting normalized responses r_j(sigma) satisfy r_j(sigma) <= r_j(t), since their nonnegative squared-distance gaps are fixed. The prototype-reference score margin between a and b, multiplied by (1+lambda), is

r(sigma)^T(Y_C[:,a]-Y_C[:,b]) >= 1 - sum_{j:label=b} r_j(t) = L_b(t).

The same-class terms besides j_0 are nonnegative, so discarding them provides a lower bound. By Cauchy-Schwarz and (5)-(6), the absolute change of this scaled pairwise margin caused by W-W_0 is at most ||r(sigma)||_2 K_ab <= n_t K_ab. Condition (8) therefore keeps every competitor margin strictly positive throughout the entire rectangle. This proves a unique winning class a.

## 7. Monotonicity and useful operation

For a fixed penalty floor lambda_0, K_ab(t,lambda_0) is nondecreasing in t: its nonnegative numerators increase while gamma_t decreases. n_t and competitor response sums also increase. Therefore a rectangle certified at t is certified at every smaller upper bandwidth. This permits a bisection search for a per-query certified bandwidth frontier, using training-derived quantities without refitting the readout at each candidate.

The exact-majorant supremum in (6) is nonincreasing when lambda_0 increases because the maximization domain shrinks. Raising the penalty floor can therefore expand the certificate's valid region. A finite penalty threshold is not guaranteed, because the infinity endpoint V+P can itself obstruct certification.

Preparation costs O(NKC) after Gaussian features have been computed, plus K x K prototype geometry. V uses O(K^2 C); P and Q use O(NKC); pair-bound preparation uses O(K C^2). Query class masses can use the one-hot labels in O(K), followed by C-1 scalar comparisons. A streaming implementation accumulates P and Q using O(KC+K^2) state, excluding raw data and query batches. A material runtime advantage is an empirical question; do not claim one from arithmetic orders alone. If a requested region is uncertified, the method abstains rather than rejecting nearest-prototype agreement.

An ordinary post-fit comparison of the full model label with the nearest-prototype label is cheaper for a single already-fitted model. That check only addresses the queried parameter point. The present operation is certification of a continuous bandwidth interval and an unbounded penalty interval before fitting the readout.

## 8. Small-width limit and counterexample

If prototype inputs are distinct, and no other training input coincides with a prototype, then H_sigma -> S as sigma -> 0. Thus W_sigma,lambda -> Y_C/(1+lambda), H_sigma^T H_sigma -> I and the feature condition number tends to one for fixed finite lambda >= 0. A query with a unique nearest prototype has normalized r_sigma -> e_j0, so its limiting class is the nearest prototype's label.

Do not present this elementary limit as novel. Do not state it without its duplicate-input assumption. A synthetic counterexample uses training inputs [0,0,0,3] with labels [0,1,1,1] and selected prototypes at row 0 and row 3. At tiny bandwidth and lambda=1, the readout is [[0.25,0.5],[0,0.5]]. A query at 0 is assigned class 1 even though the selected nearest prototype has class 0. The finite certificate remains valid and does not certify this configuration.

The finite theorem does not require the asymptotic assumptions: its positive lower-bound and strict-margin conditions are sufficient on their own.

## 9. Synthetic verification and required empirical tests

Executable synthetic check: `work/v2/theory/check_certificate.py`; results: `work/v2/theory/synthetic_verification.json`.

The check used 100 independent random synthetic datasets, 6,555 query/parameter-rectangle checks, 4,394 certified query rectangles, and 163,875 fitted comparisons at multiple interior and boundary bandwidth/penalty values. It observed zero certified-label violations, zero residual-majorant failures, zero eigenvalue-bound failures at the declared floating-point tolerance, and zero cases in which the sharpened bound exceeded the basic bound. It also verified the contradictory-duplicate counterexample above. Numerical checks support the implementation; the continuum guarantee comes from the proof.

The empirical design should record:

1. Certificate applicability and unconditional/conditional coverage separately.
2. The primary sharp certificate and basic majorant baseline on identical centers, data and parameter rectangles.
3. A geometry-only/global norm baseline if its independent derivation is verified.
4. Numerical label agreement at declared interior points and boundaries, with underflow-safe query scaling.
5. The distribution of certified bandwidth frontiers and variation with penalty floors and prototype budgets.
6. Full-model classification accuracy and exact nearest-prototype agreement as descriptive context, retaining all disagreements and uncertified cases.
7. Runtime phases for certificate preparation, full readout training, and query evaluation; no speed claim without repeated matched measurements.
8. Distinct dataset/center-condition checks and any failure of useful coverage, rather than silently narrowing the evaluated grid after outcomes.

The previously examined MNIST test outcomes remain exploratory. The reserved 4,027 observations identified by the experiment-design agent must only be evaluated after the final protocol and code are frozen.

## 10. Prior-work check and novelty exclusions

### Direct motivating paper

Saralajew, Rana, Villmann and Shaker (2025), *A Robust Prototype-Based Network with Interpretable RBF Classifier Foundations*, AAAI. DOI 10.1609/aaai.v39i19.34233. Primary author full text: https://arxiv.org/html/2412.15499v3, version dated 17 April 2025. Sections 2-3 explicitly analyze unconstrained RBF readout weights and explain that the closest components need not determine the predicted class; their response is a probabilistic classification architecture and input-perturbation robustness analysis. Our candidate instead verifies when a fixed ridge RBF shares the nearest-prototype label over a parameter region. This distinction does not negate their interpretability results and does not establish a human-interpretability claim. Access: full relevant sections inspected. Retrieval ref: turn56view0.

### Boundaries established by other primary research

Voracek and Hein (2022), *Provably Adversarially Robust Nearest Prototype Classifiers*, https://arxiv.org/abs/2207.07208. The verified abstract concerns adversarial input perturbations of a nearest-prototype classifier and exact/minorizing distances to altered decisions. Our parameter-region question concerns a ridge readout classifier, with the query and prototype inputs fixed. Access: abstract; attempted HTML full text unavailable. Retrieval ref: turn54academia9.

Rosenfeld et al. (2020), *Certified Robustness to Label-Flipping Attacks via Randomized Smoothing*, ICML, https://proceedings.mlr.press/v119/rosenfeld20b.html. The primary record establishes pointwise certificates against changes to training labels and includes multiclass classification. A new claim of first label-perturbation certification would therefore be false. The present theorem keeps all labels fixed and varies Gaussian width and ridge penalty. Access: publisher abstract/full introductory PDF extract, not an exhaustive full-paper review. Retrieval refs: turn70search0 and turn70search35.

Noorizadegan et al. (2026), *Making Gaussian KANs Reliable and Accurate*, DOI 10.1016/j.neucom.2026.134771, and the September 2026 Neurocomputing work on Softmax learned-prototype sample influence are being inspected by the journal-literature agent. Their identities and exact scopes must be taken from that agent's verified ledger before incorporation. In particular, sample-influence decomposition and the distinction between conditioning and accuracy must not be claimed as new in isolation.

The bounded searches did not retrieve this exact parameter-rectangle certificate. That observation supports further comparison, not an assertion that no predecessor exists. Claims of novelty must name the operation that the closest verified methods do not provide.
