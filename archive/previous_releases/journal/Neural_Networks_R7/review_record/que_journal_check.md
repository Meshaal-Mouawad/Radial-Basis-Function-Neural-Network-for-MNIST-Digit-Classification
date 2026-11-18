# Que–Belkin publication check

Recommendation: retain the existing AISTATS 2016 citation. The journal publication is verified, and no newly inspected journal theorem provides a reason to replace or add a reference. The journal's methods and theorem text was inaccessible in this check, so its mathematical additions remain unverified.

## Publication identity

Qichao Que and Mikhail Belkin, **Back to the Future: Radial Basis Function Network Revisited**, *IEEE Transactions on Pattern Analysis and Machine Intelligence* **42**(8), 1856–1867 (August 2020). DOI: **10.1109/TPAMI.2019.2906594**. IEEE records online publication on 25 March 2019. The journal title uses singular *Network*.

The conference publication is **Back to the Future: Radial Basis Function Networks Revisited**, AISTATS 2016, PMLR **51**, 1375–1383. Its title uses plural *Networks*.

## Exact access and source record

| Source | URL | Access achieved | Used for |
|---|---|---|---|
| IEEE publisher record | https://doi.org/10.1109/TPAMI.2019.2906594 | Search-indexed publisher metadata, full abstract, section headings, and first introduction paragraph; direct open redirects to IEEE document 8673620 and returns JavaScript robot-verification screen | Journal identity and advertised scope |
| IEEE document | https://ieeexplore.ieee.org/document/8673620/ | Direct open: robot-verification screen | Access failure recorded |
| IEEE PDF entry point | https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8673620 | Tool reports inaccessible URL; no PDF obtained | Access failure recorded |
| PMLR conference landing page | https://proceedings.mlr.press/v51/que16.html | Publication metadata and abstract accessible | Conference identity |
| PMLR conference PDF | https://proceedings.mlr.press/v51/que16.pdf | Full primary PDF accessible, nine pages | Methods and theorem inspection |
| PMLR conference supplementary PDF | https://proceedings.mlr.press/v51/que16-supp.pdf | Full primary PDF accessible, thirteen pages; its opening and theorem/proof-bearing text were available | Confirms primary extended/proof resource exists; not a journal surrogate |
| Author publication list | https://misha.belkin-wang.org/papers.html | Accessible; AISTATS entry links to the proceedings | Author-side route checked; no journal full-text route identified |

Search evidence identifiers for reproducibility in the parent conversation: IEEE detailed indexed record `turn63search0`; DOI live access `turn60view0`; PMLR PDFs `turn60view1`, `turn60view2`; conference method and theorem extraction `turn65view0`, `turn65view1`; author list `turn64view0`, `turn65view2`. The review relies on primary IEEE/PMLR/author sources. PubMed and DBLP results independently corroborated identity and were not used to infer mathematical scope.

## Relevant inspected material

The AISTATS paper already establishes the comparison used by R6: coefficient-square regularization of RBF networks and its data-dependent-kernel interpretation. Section 2, equation (2), minimizes empirical loss plus a squared coefficient penalty. The accompanying embedding explanation identifies square-loss training as ordinary ridge regression in RBF feature space (printed pp. 1376–1377). Theorem 1 bounds estimation error; Corollary 1 gives a generalization rate (p. 1378). Section 4.2/Theorem 2 relates weighted k-means RBF estimation error to quantization error; Theorem 3 describes the limiting distribution of k-means centers (p. 1380). These inspected results address approximation, estimation, and center selection rather than a query's nearest-prototype label agreement jointly throughout a bandwidth–penalty region.

The journal abstract advertises the same two regularization families and a kernel interpretation, theoretical analysis, experiments, use of unlabeled data, and computational advantages. Its indexed headings are Introduction; RBF Networks: Generalization Analysis; RBF Networks for Semi-Supervised Learning; k-Means RBF Networks; Experiments. These primary-record observations establish broad overlap of subject matter. They do not establish equivalence of theorems or absence of additional journal analysis.

## Citation decision

Retain the 2016 conference citation for the claim actually supported by the inspected primary full text. Do not add the 2020 journal article solely because it is longer or more recent. If the final author-facing record needs a status for the optional R6 item, use: **journal identity verified; citation retained; theorem-level journal comparison unresolved owing to full-text access**.

Suggested minimal record, without a manuscript change: “The IEEE TPAMI publication was verified (42(8):1856–1867, 2020; DOI 10.1109/TPAMI.2019.2906594). We retained Que and Belkin (2016), whose primary full text directly supports the coefficient-regularization and data-dependent-kernel comparison.”

## Limitations

Journal Section 2 onward and its theorem statements were not inspected. No claim is made that the two versions are mathematically identical, that the journal lacks a particular certificate, or that the optional theorem-level comparison is complete. No manuscript or bibliography file was edited. This report was created as a review artifact in the parent task's requested directory on 17 November 2026.
