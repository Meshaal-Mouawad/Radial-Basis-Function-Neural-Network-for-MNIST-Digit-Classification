# R5 source revision consistency

All reviewed substantive source attributions match the verified evidence.

The review covers only Introduction and Related work, including the comparison table. It checks citation-bearing paraphrases against the source evidence already recorded. No manuscript edits or numerical work were performed.

## Findings

No attribution corrections required.

## Checked attributions

| Location | Sources | Assessment |
|---|---|---|
| Introduction, line 44; Related work, line 67 | broomhead1988 | supported. Publisher abstract states nonlinear adaptive interpolation learning reduces to linear equations. |
| Introduction, line 48; Related work, line 65; table row 95 | srihari1979 | supported. Full primary PDF Sections 2–4 explicitly compares nearest-sample and class-summed exponential potentials, finite scale, decision-surface identity, and geometric conditions/algorithm. |
| Introduction, line 48; Related work, line 67; table row 100 | saralajew2025 | supported. Author full text Section 2 explains unconstrained-weight reweighting of near/far components; Section 3 constructs probabilistic CBC extension with robustness analysis. |
| Related work, line 69; table row 101 | fazaeli2026 | supported at abstract/preview level. Publisher abstract/introduction verifies positive/negative learned prototypes, softmax-neuron interpretation, and reported near-boundary training-sample influence. |
| Related work, line 72; table rows 96–97 | bugmann1998, radhakrishnan2023 | supported. Bugmann primary abstract supports Voronoi-like normalized-response interpretation. Radhakrishnan Theorem 3 gives a 1-NN regime, and the following paragraph explicitly gives the Gaussian narrow-limit analogy. |
| Introduction, line 48; Related work, line 74; table row 99 | que2016 | supported. Publisher full text covers coefficient regularization, training-point centers, data-dependent kernels, and weighted k-means quantization error. |
| Related work, line 76; table rows 98, 102–103 | dagostino2024, wurzberger2024, noorizadegan2026reliable, noorizadegan2026partition | supported. Relevant author/publisher full-text passages verify learnable precision/spectrum, deep RBF initialization/distance calculation, Gaussian feature-block conditioning, and normalized edge constant reproduction. |
| Related work, line 81; table rows 104–105 | voracek2022, rosenfeld2020 | supported at abstract level. PMLR primary abstracts identify input-perturbation and training-label-flip certificate objects respectively. |
| Introduction, line 48; Related work, line 83; table rows 106–107 | shibagaki2015, ndiaye2019 | supported. Publisher full text establishes score/CV bounds from approximate solutions and duality-gap solution regions along regularization paths with fixed design. |
| Related work, line 85 | bindel2025 | supported. Primary course notes explicitly give inverse times residual solution-error identity. |

## Srihari primary access and exact comparison

The successful primary full-text tool reference is **`turn23view0`**, from [the Michigan institutional PDF](https://deepblue.lib.umich.edu/bitstream/handle/2027.42/23481/0000434.pdf?sequence=1). That retrieval returned the 11-page published article and 294 extracted lines, including the relevant body sections. No local PDF was downloaded. Subsequent screenshot attempts and the root’s fresh request returned HTTP 403; these failures do not change what the earlier successful extraction contained.

Srihari fixes prescribed positive class-associated exponential potentials and analyzes identity of binary input-space decision surfaces. R5 fixes a query, fits signed multiclass coefficients by ridge regression, and certifies agreement throughout bandwidth–penalty regions.

R5 correctly introduces this source as an older identity-conditions study and does not attribute coefficient-ridge fitting or a two-parameter certificate to it. The entry preserves the verified author order, year, journal, volume, and pages. The 1980 related article is not needed as a second addition.

## Exact reviewed inputs

| File | SHA-256 | Bytes |
|---|---|---|
| `working_R5/source/main.tex` | `1a0d865b5a9bed22be8597f7891f9235a62831e41615ecc321f1c061b5aa8672` | 57635 |
| `working_R5/source/references.bib` | `4d3d47cb7b9f28e5f83ad2fdc7e2b5b3d310abd7ae393bdb9d29f2ac483eb076` | 6997 |
| `upload/Universal_Literature_Review_Prompt(1).md` | `f887ab176ab88e2e252117c30a97a516f80cf9c9d1fb1e35b86cc0f2b66929d1` | 5438 |
| `r5_editorial/review/literature_verification.md` | `e9881cc256d741e62af5a34c137a6a997b01c51d78fe2fcdd5381b45ed51d12e` | 14421 |
| `r5_editorial/review/literature_verification.json` | `ae0caaa98e05f7dcfda7a749c58bbbabe05ea5bc58bdf4a9a7c0a755ffa74bc9` | 15598 |
| `r5_editorial/review/srihari1979_verified.bib` | `8540a2784eadea0d33ed48007df6c1d3dd4e49b3ae21cac03dbb020530040460` | 407 |

The section hashes in the JSON record identify the exact extracted Introduction and Related work slices. A subsequent source edit requires checking the changed passage against this recorded review.

Execution configuration: `gpt-6.1-sol`, reasoning effort `high`, `fork_turns="none"`, confirmed by root from successful spawn arguments. Backend model identity was not independently measured.

Final receipt: checked the root-designated R5 candidate after removal of the Bugmann clause and tightening of the introduction mechanism. No attribution correction remains.

Production refresh: bibliography spacing and the abstract’s explicit validation-comparator wording were updated. Introduction, Related work, and reference hashes remain unchanged; no relevant attribution delta. The input table now identifies the final production candidate.
