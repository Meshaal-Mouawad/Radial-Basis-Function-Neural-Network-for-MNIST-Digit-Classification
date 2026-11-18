# Clean journal package check

**PASS.** The staged files are suitable for the journal upload package. The manuscript PDF is byte-identical to the reviewed R7 PDF. Its SHA-256 is `06364ad4ebd0f5a01fd5099550d39862c691be931a97daf4cc09e16c3754fb71`.

| File | Verified result |
| --- | --- |
| `LaTeX_Source.zip` | All 29 root-level members are byte-identical to their R7 counterparts. The archive includes every explicit LaTeX input, all seven referenced figure PDFs, the document class, bibliography style, bibliography database, and generated bibliography. The recorded clean build used the included style and database and produced 40 pages. An additional rendering comparison matched all 40 pages pixel for pixel. |
| `Figures/` | All seven standalone figure PDFs are readable and byte-identical to the R7 source figures. |
| `Highlights.txt` | Five bullets of 70, 57, 71, 72, and 72 characters, within the 85-character limit. |
| `Title_Page.docx` | The title, sole author Meshaal Mouawad, affiliation, corresponding email, and keywords match R7. The ORCID is preserved from the author-supplied title page. |
| `Declaration_of_Competing_Interest.docx` | The title and sole author match R7. The declaration matches the manuscript verbatim. |
| `Cover_Letter.pdf` | The one-page letter faithfully reproduces the retained text. R7 supports the results summarized in the letter, including the 2,880 archived readouts and zero full-width certificate coverage for all 328 readouts under the primary competitive rule. The historical letters support the prior Neurocomputing manuscript ID and choice of Neural Networks for the proposed transfer. The letter requests consideration and makes no claim of a new journal response, acceptance, or completed submission. |
| `Supplementary_Research_Artifacts.zip` | The preserved source ZIP passed its CRC check and has the expected SHA-256, `ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8`. This is the checksum to verify under the journal filename in the assembled archive. |

The checksum manifest matches the 13 staged files and the expected supplement. The Mathematical and Computational Analysis section named in the letter appears in the publisher’s journal description. [Neural Networks journal description](https://shop.elsevier.com/journals/neural-networks/0893-6080)

## Limits of this check

This audit covered the staged upload files and preserved supplement. The final archive assembly and restoration are verified separately. Portal requirements and submission confirmation remain pending.
