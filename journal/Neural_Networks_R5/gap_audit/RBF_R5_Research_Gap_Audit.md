# RBF R5: research-gap audit and review decision

**Author:** Dr. Meshaal Mouawad  
**Manuscript:** Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers  
**Target:** Neural Networks  
**Search date:** 15 November 2026, Asia/Riyadh (execution UTC date: 14 November 2026).  
**Decision:** READY TO DRAFT WITH VERIFIED EVIDENCE; for the already integrated R5, proceed to independent specialist review.

## A. Decision and frontier coverage

The precise R5 contribution survives the bounded prior-work challenge. It supplies computable sufficient conditions for a fixed query to retain its nearest selected prototype's label throughout a Gaussian bandwidth–ridge penalty region, together with strict disagreement exclusions and local-band tail certificates. The manuscript already states this contribution and attributes the older geometric, statistical and regularization-path results. No new mandatory manuscript change was identified.

The independent frontier search ran 47 queries in 13 batches, curated 18 distinct papers, and included seven Neural Networks records: three from the 2026 online/issue frontier, two from 2025 and two from 2024. Five full texts had selected methods or theorem passages inspected in this pass; Ndiaye's introduction was also revisited, and the prior full-text checks of Srihari and Ndiaye were retained. These counts exclude the root's complementary searches and its selected-section inspection of the time-scale RBF paper. The separate ledgers preserve actual queries, source identities, access levels and failed routes. Retrieved search hits are not counted as independently verified papers.

| Frontier | Verified research activity | Relevance to the R5 question |
|---|---|---|
| 2026 | Fan et al.: adaptive local RBF support for PDEs; Jiang and Li: relation-aware prototypes for few-shot classification; Luo et al.: prompt-prototype continual learning | Current Gaussian-support and prototype-learning work establishes active neighboring topics. Their inspected publisher previews concern different model and prediction objects. |
| 2025 | Mhaskar: approximation with non-symmetric kernel networks; Li et al.: prototype denoising for continual learning | Mathematical kernel analysis and prototype reliability remain visible in the target journal. |
| 2024 | D'Agostino et al.: learned Gaussian precision geometry, feature interpretation and two regularizers; generalized M-sparse RBF work: sparse fault-tolerant construction | D'Agostino is the closest recent target-journal comparator. Exploring geometry and output regularization jointly is already established. |

Fan's paper has a 2026 article-date record and a January 2027 issue assignment. This audit treats it as an early-online frontier record, with the exact publisher online date still index-supported. Exact bibliographic details and links for all seven records appear in `search_ledger.json` and `frontier_challenge.md`.

## B. Research lineage and cross-journal challenge

The lineage is a connection between complementary results, rather than a claim that one journal left a task for another to finish.

| Established capability | Closest verified source and location | Remaining R5 question |
|---|---|---|
| Finite-scale nearest-neighbour and potential-function decision-surface identity | Srihari, White and Snabb (1979), Information Sciences, Sections 2–4; DOI 10.1016/0020-0255(79)90030-6; inherited primary full-text verification | What training-derived test controls a fixed query with learned multiclass coefficient-ridge weights over a joint width–penalty region? |
| Statistical analysis of coefficient-regularized RBFs | Que and Belkin (2016), AISTATS, Sections 3–4 and Theorems 1–2; https://proceedings.mlr.press/v51/que16.pdf | How can the fitted label be compared with a prescribed nearest-prototype reference throughout the parameter family? |
| Query-score and validation bounds along regularization paths | Shibagaki et al. (2015), Section 3.1; Ndiaye et al. (2019), Section 4, Lemma 4; https://proceedings.mlr.press/v97/ndiaye19a.html | How can agreement be enclosed when Gaussian features change with width as the ridge penalty also varies? |
| Nearby components can be outweighed in a learned decision; architectural response | Saralajew et al. (2025), Sections 2–3; DOI 10.1609/aaai.v39i19.34233 | Which regions preserve the same geometric label while retaining the conventional ridge readout? |
| Learned Gaussian geometry and empirical regularizer exploration | D'Agostino et al. (2024), Sections 3, 3.1, 4.3 and 5; DOI 10.1016/j.neunet.2024.106335 | Can label equality be guaranteed for every parameter pair in a declared region rather than observed only at selected settings? |

Cross-journal challenges covered alternative terminology. Qian et al.'s safe RBF training concerns gradient-update preservation (DOI 10.1016/j.neucom.2024.128150). Li and Qiao's three-way RBF classifier concerns imbalanced classification (DOI 10.1016/j.engappai.2024.109811). The PALACE preprint's Theorem 5.1 concerns sampling-based agreement with population centroids (arXiv:2605.04046). Khuddush and Georgiev's Section 6 bounds dynamic-equation state error using residuals (DOI 10.3390/math14183335). These inspected objects differ from the R5 equality property; the access level for each comparison is retained in the ledger.

## C. Gap register

The independent inference is recorded separately from what prior authors stated. An uninspected limitations section is marked uninspected; silence is never converted into a claim that the authors declared the R5 gap.

| Candidate | Author-stated boundary inspected | Independent inference and challenge | Verdict |
|---|---|---|---|
| Fixed-query agreement across Gaussian width and coefficient-ridge penalty | Shibagaki specifies a fixed-input binary setup; Que's numerical section discusses full-RBF computational burden. Neither is recorded as declaring this research gap. | Closest geometry, statistical and path results answer different quantified questions. R5 supplies a training-derived, multiclass region test with varying Gaussian design and a fixed labeled prototype reference. | CONFIRMED WITHIN VERIFIED SEARCH SCOPE; central residual/implicit gap |
| Computable signed local-band tail certificate | No author-declared matching gap was extracted. | Strict limiting margins and continuity motivate local existence. R5 supplies an explicit endpoint enclosure and finite tail threshold that can be evaluated. This serves the central certificate framework. | CONFIRMED WITHIN VERIFIED SEARCH SCOPE; subordinate result |
| General nearest-neighbour/radial-rule equivalence | Srihari's identity conditions are directly inspected in the inherited primary record. | Finite-scale geometric equivalence already has a published analytical treatment. | ALREADY ADDRESSED |
| Recognition that weighted scores can oppose the nearest prototype; parameter exploration | Saralajew's discussion addresses interpretability; D'Agostino's method and experiments use geometry and readout regularizers. | Mismatch and multi-parameter exploration are established. Their use does not by itself establish a new contribution. | ALREADY ADDRESSED |
| Large-penalty limits or continuity alone | Standard residual/inverse identity explicitly attributed in R5 to Bindel's course notes. | These are mathematical tools. The manuscript-specific finite bounds and signed enclosures are assessed within the integrated construction. | ALREADY ADDRESSED as standalone foundations |
| Predictive superiority or computational speedup | This is a claim about the present study, not an inherited limitation. | All 328 primary validation-competitive readouts have zero full-width coverage; archived probe counts do not measure saved runtime. | NOT TESTABLE WITH AVAILABLE EVIDENCE for measured speedup; predictive-improvement claim unsupported |

## D. Ranked contribution and exact question

**Rank 1 — Continuous label-persistence analysis.** For fixed labeled training observations, selected training prototypes and a query, which bandwidth–penalty regions guarantee that the fitted Gaussian RBF class equals the nearest-prototype class, and which contain a strict disagreement? This question has a decisive mathematical answer: explicit sufficient conditions, exclusion witnesses and unresolved cases. It gives a precise domain of validity to a proximity-based label summary.

**Rank 2 — Signed local bands.** Use the class-vote limit and a signed interval enclosure to certify additional width bands at sufficiently large penalties. This extends the first result to a second declared region geometry and belongs within the same paper.

**Rank 3 — Empirical characterization.** Use the preserved model family to locate guarantees relative to validation competitiveness, finite penalty paths, prototype budget, seed variation and class composition. These observations explain the reach of the theory. They are supporting empirical findings rather than a separate general-priority claim.

**Supported contribution statement:** The study establishes training-derived tests of nearest-prototype label persistence across a family of Gaussian coefficient-ridge classifiers, using class-wise residual bounds, a two-endpoint penalty envelope, strict disagreement thresholds and signed local-band enclosures, with empirical characterization from 2,880 archived readouts. The precise advance is the computable joint-region analysis relative to a fixed prototype label.

## E. Design and evidence chain

| Question | Decisive method or comparator | Existing verified evidence |
|---|---|---|
| Does the label persist over the full requested region? | Prototype/non-prototype residual decomposition; spectral floor; exact supremum of the selected nonnegative majorant; strict class margin | Main source lemmas, two-endpoint proposition and uniform agreement theorem; independent constructed-case checks in the manuscript and frozen evidence |
| Can the requested property be excluded? | Strict opposing limiting class vote plus finite sufficient threshold; observed finite witnesses | `ridge_theory.tex`; R3 witness reconstruction; R4 sampled paths preserve censored cases and repeat reversals |
| Can narrower width bands be certified? | Signed endpoint enclosure and finite-penalty correction; positive-class-sum comparison | `ridge_theory.tex`, `new_results.tex`, protected R3 local-band outputs |
| Do competitive fitted models receive full-width coverage? | Validation-only 95%-of-best rule within each dataset/seed/budget group; fixed 90% and 99% sensitivity rules | All 30 groups, 2,880 readouts; 328 primary competitive readouts, all with zero coverage; independent reconstruction PASS |
| What does certified-subset accuracy contain? | Equal-coverage gated-distance comparator; class-specific counts, selected accuracy, accepted recall and overlap | 20 endpoint settings, 40 selector rows, 400 class rows; independently reconstructed |
| Are finite penalty paths monotone in agreement? | All six archived penalties per width; strict score guard; retain every sign change | 190,405 of 3,366,480 query-width paths return to agreement after disagreement; maximum five sampled sign changes |
| What additional evidence is recovered by fixed probe sequences? | Prespecified F0/F1 replay; exact overlap with L0/L+; operation counts | 420 region/bank records and 21,630 probe steps; saved runtime and speedup remain NOT SUPPORTED |

These checks reuse the trained data. No new fitting or numerical pipeline rerun was required by the literature audit. The verified R4 claim-to-evidence map and independent numerical reports are included as inherited baseline records in the review package.

## F. Integrated-manuscript decision

R5 already opens the abstract with the relationship between prototype similarity and the learned class decision, then states the unresolved region question, method and principal quantitative evidence. Its Introduction teaches the two decision paths before formal notation. Related work distinguishes finite-scale potential identities, coefficient-ridge theory, learned prototype mechanisms and fixed-design regularization-path bounds. The comparison table names the varying object for each guarantee.

Direct source inspection found no assertion that the large-penalty limit, continuity, two-parameter sweeps or nearest-prototype mismatch alone is novel. Therefore the audit requires no replacement prose and no R6 manuscript. The authoritative LaTeX and its 40-page compiled PDF remain byte-identical to the previously built and visually inspected R5. The new deliverable adds the current gap audit to the review package.

## G. Verification gates and completion

| Gate | Outcome | Evidence |
|---|---|---|
| J1 — Current | PASS within bounded scope | 2026 → 2025 → 2024 target-journal search and seven curated target records; dates/access levels recorded |
| J2 — Cross-journal | PASS within bounded scope | Alternative geometric, statistical, path, safe-training and centroid-certificate challenges; actual queries retained |
| J3 — Distinction | PASS | Separate author statements and independent inference in both source ledger and gap register |
| J4 — Valid gap | PASS | Fixed-query label equality over a declared model family changes the scope of a proximity-based summary |
| J5 — Closest predecessor | PASS for precise integrated contribution | Srihari, Que, Shibagaki, Ndiaye, Saralajew and D'Agostino compared by assumptions, varying object and output |
| J6 — Test | PASS | Proof obligations and explicit finite counter-witnesses answer the specified property |
| J7 — Evidence | PASS | Frozen independent numerical verification and claim map; null and adverse findings retained |
| J8 — Reader | PASS | R5 cold-reader review and direct abstract/Introduction/Related work comparison |
| J9 — Sources | PASS at recorded access levels | Exact pivotal attributions checked; partial-access records carry partial-access claims |
| J10 — Journal | PASS for scope | Official Neural Networks description includes mathematical and computational analysis of neural networks |

**Completion:** Original preservation/analysis/integration stages A–I are closed in the R4 audit. R5 reader-first editing, citation checks, compilation, all-page PDF inspection and exact archive verification are complete. This additional methodology audit is complete. The frozen R5 manuscript is ready to send for independent specialist review. The Neural Networks transfer/submission remains pending.

**Efficient next action:** Send the audited R5 review package to the independent reviewer. Resume implementation only for a concrete reviewer finding. The recorded cost plan assigns Sol/Medium to routine editing, Sol/High to mathematical or numerical verification, and Astra/High to a bounded independent scientific review. These are role assignments, not measured pricing or claimed historical execution. This frontier audit used an explicitly configured Sol/High agent; the prior scientific review recorded Astra/High. No paid compute or new model training was initiated.

## Limitations and remaining external decisions

The search is a bounded current-frontier challenge, not a census of all publications. Recent peripheral target-journal records were available as indexed publisher previews; their full theorem bodies were not inspected. Kuncheva and Bezdek's 1998 generalized-nearest-prototype paper has verified primary bibliographic identity but an uninspected primary scientific body. Sun and Wang's review reference chain was not inspected. Lin's adaptive KRR parameter selection was inspected at abstract/preview level. These access gaps are recorded and are not used to assert full-text absence of an equivalent theorem. The present narrowed contribution survives the inspected pivotal evidence; no universal priority claim is made.

The earlier independent scientific assessment rated Neural Networks significance BORDERLINE and scientific validity PASS. This audit adds a current literature comparison; it does not replace that significance judgment. Publisher upload requirements and the transfer submission still require completion in the submission workflow. Large derived R4 arrays remain preserved in the full revision archive; GitHub contains the original trained evidence, restoration records, analysis scripts and small summaries. Historical model assignments absent from old execution receipts remain unknown.

## Record links

- Existing repository: https://github.com/Meshaal-Mouawad/Radial-Basis-Function-Neural-Network-for-MNIST-Digit-Classification
- Frozen manuscript commit: `059e0204c1fee7b52bae744cda65a7e0b7399d1c`
- Official journal scope: https://shop.elsevier.com/journals/neural-networks/0893-6080
- Search and access records: `search_ledger.json`, `root_search_ledger.json`, `frontier_challenge.md`
- Audit integrity and closure: `AUDIT_DECISION.json`, `SHA256_MANIFEST.json`
- Original R5 main source SHA-256: `1a0d865b5a9bed22be8597f7891f9235a62831e41615ecc321f1c061b5aa8672`
- Original R5 PDF SHA-256: `6a00a5573e2f46ca85e6913988c766928b8628cb902cd1a2a6f0a5e8262f4041`
