# Recent Neurocomputing comparison and gap decision

Checked 6 November 2026. The cutoff concerns online availability, not only issue dates. No experiment or manuscript was modified by this review. The exact three manuscript bibliography entries are in `recent_journal_entries.bib`.

## Decision

The defensible question is **when a conventional fixed-prototype Gaussian ridge classifier is guaranteed to return a nearest-prototype label throughout a continuous bandwidth–penalty region, using training-derived quantities before fitting its readout**. This is more specific than scale selection, prototype interpretation, sample influence or generic parameter-interval certification, all of which have established predecessors.

The new manuscript's operation is distinct from the three recent Neurocomputing studies below. The literature evidence supports this bounded comparison; it does not establish universal absence of a similar theorem. Prior safe regularization-path methods must also be attributed. The new theorem, independent proof and empirical coverage are the evidence that must establish the contribution.

## Verified recent-paper records

### N1 — Learned prototypes and softmax influence

**Mahsa Fazaeli-Javan and Kamaledin Ghiasi-Shirazi.** *Sample-based interpretability of softmax neurons via learned prototypes.* Neurocomputing **694**, 133904 (14 September 2026). DOI **10.1016/j.neucom.2026.133904**.

**Access:** Primary publisher-indexed abstract, introduction, section excerpts, conclusion excerpt and author/CRediT blocks. Direct full-text page returned 403. No complete full-text review is claimed.

**Verified content:** The ±ED-WTA representation assigns positive and negative prototypes to softmax neurons. Analysis of their formation links decisions to a limited set of near-boundary training samples. The experiments use MNIST, FERET and Fashion-MNIST. The paper studies learned prototype formation and sample contributions, not the fixed ridge-RBF family used here. The current manuscript may describe this positive capability; it should not infer an absent theorem from inaccessible sections.

**Authorship correction:** “Xiao et al.” is wrong for this DOI. Both the publisher author block and CRediT identify Fazaeli-Javan and Ghiasi-Shirazi. Use key `fazaeli2026`.

Primary URL: https://www.sciencedirect.com/science/article/abs/pii/S0925231226013019 . Retrieval evidence: `turn50search1`, `turn50search7`, `turn62search1`.

### N2 — Gaussian KAN scale geometry

**Amir Noorizadegan, Sifan Wang and Leevan Ling.** *Making Gaussian Kolmogorov–Arnold networks reliable and accurate.* Neurocomputing **703**, 134771. DOI **10.1016/j.neucom.2026.134771**. Online **10 August 2026**; assigned issue date **28 November 2026**. It was available before the review cutoff.

**Access:** Final publisher metadata and institutional record; full author manuscript **arXiv:2604.21174v3, 12 August 2026**, with formulation, theoretical statements, experimental design, findings and Section 6 inspected. Earlier v1/v2 titles and two-author lists are superseded for current citation purposes.

**Verified content:** The first-layer feature map uses coordinate-wise Gaussian bases on uniformly spaced one-dimensional centers. Its overlap/conditioning analysis supplies a practical scale interval tied to grid spacing; experiments cover approximation and physics-informed settings. Section 6 explicitly identifies classification and operator learning as directions for further examination. This is the authors' stated extension, not an assertion that our theorem fulfills their exact proposed experiment. Their scale criterion does not itself evaluate the target classifier family in our study.

Primary metadata: https://scholars.hkbu.edu.hk/en/publications/making-gaussian-kolmogorovarnold-networks-reliable-and-accurate/ . Full inspected author version: https://arxiv.org/html/2604.21174v3 . Locations: Sections 2–4 and 6; v3 lines 811–814 for future work. References: `turn53search1`, `turn60view0`, `turn62view0`, `turn64view0`.

### N3 — Partition-of-unity Gaussian KANs

**Amir Noorizadegan.** *Partition-of-unity Gaussian Kolmogorov–Arnold networks.* Neurocomputing, 135408, online **14 October 2026**. DOI **10.1016/j.neucom.2026.135408**. No unverified volume is entered.

**Access:** Publisher metadata/abstract; full author manuscript **arXiv:2604.23599v2, 3 May 2026**, with feature definition, normalization, numerical design and conclusion inspected. The author version predates publication; byte-equivalence to the final publisher text is not claimed.

**Verified content:** Shepard-type normalization divides each edge's Gaussian responses by their sum. This gives constant reproduction and a normalized finite-feature kernel. Experiments compare scale sensitivity across approximation/PDE settings and related basis choices. The conclusion identifies discontinuous targets as a less uniform case and proposes adaptive scales, higher-order constructions and operator/time-dependent extensions. This paper changes the representation to stabilize approximation; the present analysis preserves the given feature family and certifies a class-label relation across parameter choices.

Primary URL: https://www.sciencedirect.com/science/article/pii/S0925231226028067 . Full inspected author version: https://arxiv.org/html/2604.23599v2 . Locations: Section 2.1, Section 4, Section 5 (lines 570–578). References: `turn50search4`, `turn55view1`, `turn58view3`, `turn60view1`, `turn64view2`.

### N4 — Additional venue benchmark, not required in the manuscript

**Sofie Lövdal, Elina L. van den Brandhof, Michael Biehl and the Alzheimer's Disease Neuroimaging Initiative.** *Iterated relevance matrix analysis for improved classification and robustness in prototype-based learning schemes.* Neurocomputing **670**, 132474 (14 March 2026), online 20 December 2025. DOI **10.1016/j.neucom.2025.132474**.

**Access:** Published PDF from University of Groningen; methods, results and discussion inspected. It combines relevance matrices from successive GMLVQ solutions, testing stability and classification using repeated training subsets on three datasets. The output is a more stable learned metric and associated classifier. This establishes that prototype interpretability and robustness already have operation-specific quantitative evaluations. It is contextual, not a direct predecessor to a Gaussian ridge parameter-region certificate.

Primary published PDF: https://pure.rug.nl/ws/portalfiles/portal/1473001156/1-s2.0-S0925231225031467-main.pdf . Metadata: https://research.rug.nl/en/publications/iterated-relevance-matrix-analysis-for-improved-classification-an/ . References: `turn58view0`, `turn62view1`, `turn64view1`.

## Closest-prior-work comparison for the actual proposed result

| Research line | Object and operation already established | Present question carried forward |
|---|---|---|
| Saralajew et al., AAAI 2025, DOI 10.1609/aaai.v39i19.34233 | RBF prototype semantics and a probabilistic architecture with constrained interpretation; source already inspected in the baseline ledger and theory review | Keep a conventional ridge readout and establish a sufficient region of nearest-prototype label agreement |
| Fazaeli-Javan and Ghiasi-Shirazi, 2026 | Learned softmax prototypes and training-sample contributions | Certify an equality of labels across a family of refitted ridge solutions, rather than decompose a particular learned softmax representation |
| Noorizadegan et al., 2026 | Gaussian feature geometry, conditioning and a practical scale interval in KAN approximation | Combine fixed multivariate prototype geometry with class labels and ridge penalties to bound a particular classification decision |
| Noorizadegan, 2026 | Normalize Gaussian edge features to improve scale behavior | Analyze the unmodified Gaussian-ridge family and its agreement with selected prototype labels |
| Ndiaye et al., ICML 2019 | Safe regions and prediction/validation bounds along regularization paths with fixed design; independently verified by the editorial reviewer | Vary the Gaussian feature matrix and penalty jointly and use an analytic prototype-label reference, not a fitted anchor model |
| Proposed construction | Class-specific endpoint response aggregates, Gaussian selected-row symmetry, spectral floor, exact supremum of the chosen penalty majorant | Sufficient query-specific guarantee on every point in (0,t] × [λ0,∞), with abstention when the condition fails |

Ndiaye primary paper: https://proceedings.mlr.press/v97/ndiaye19a/ndiaye19a.pdf . Its full-text inspection was performed by the separate editorial reviewer; this report records the handoff rather than claiming a second independent full-text read.

## Claims the comparison does and does not support

Supported: the proposed theorem addresses a precise continuous-region label-agreement operation not supplied by the inspected recent papers' stated methods. Gaussian scale sensitivity, prototype influence, basic residual bounds and regularization-interval reasoning are established ingredients. The new argument must credit these predecessors and establish its own result through the theorem and useful measured coverage.

No firstness claim is justified by this bounded search. Do not describe label agreement as causal explanation, human interpretability validation or predictive correctness. Do not turn the KAN authors' classification future-work sentence into a claim that they requested this different architecture or theorem. Do not label N1 full-text verified. No evidence was found here that the 2026 Softmax paper proves the same continuous-region condition; its inaccessible sections prevent a comprehensive absence claim.

## Final manuscript-specific check

The current `work/v2/manuscript/main.tex` Related Work paragraphs correctly distinguish learned sample contributions, normalized/conditioned feature representations, and the present fixed-ridge parameter-region result. The corrected Fazaeli-Javan and Ghiasi-Shirazi attribution is required throughout prose, table and bibliography. The phrase “supporting and opposing sample influences” is supported by the ±ED-WTA decomposition at the accessed level; it should not be expanded into a causal influence guarantee. The KAN paragraph's function-approximation and differential-equation setting is supported. The later author v3 is the correct accessed version for the reliability paper.
