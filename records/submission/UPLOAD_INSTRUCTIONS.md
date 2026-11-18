# Clean Neural Networks submission package

R8 integrates the approved Figure 3 after Section 4.6. The reviewed R7 scientific content and seven original figures remain preserved. The complete clean archive contains only journal-facing files; it contains no internal reviews, audit logs, old manuscript versions, response drafts, or restoration instructions.

## File roles for the submission portal

- Manuscript.pdf: integrated 41-page article with the approved additional schematic.
- LaTeX_Source.zip: clean, complete editable source; main.tex is the entry point. It builds to the same rendered R8 PDF.
- Cover_Letter.pdf: updated transfer letter naming Neural Networks and Mathematical and Computational Analysis.
- Highlights.txt: five editable bullets, each within 85 characters.
- Title_Page.docx: preserved author details, affiliation, ORCID and keywords.
- Declaration_of_Competing_Interest.docx: preserved declaration.
- Figures/: eight separate vector PDF figures; the original seven are unchanged.
- Supplementary_Research_Artifacts.zip: the complete unchanged 706024849-byte research supplement. Its original frozen filename was Supplementary_Research_Artifacts_R4.zip; only the outer filename has been cleaned.

The source ZIP includes the manuscript figures for compilation; the separate figure files are the same bytes for portal figure upload. Upload one version of each document in the portal's relevant category.

## Downloads

Neural_Networks_R8_Clean_Upload_Files.zip is the small upload set. It omits only the large numerical supplement. Use the supplement from the complete package or your existing verified R4 supplement, with SHA-256 ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8.

The complete clean package is supplied in two transport ZIPs because of its size. Download both, extract into one folder, then run:

    python3 restore_clean_submission.py

This restores Neural_Networks_R8_Clean_Submission_Package.zip. Extract that archive to obtain the clean upload files and complete supplement together. The restoration script verifies both part hashes and the full archive before completing. The transport ZIPs themselves are download containers, not journal uploads.

## Preserved records and repository

The full R7 review, numerical audit and baseline remain preserved separately. R8 adds the approved schematic and updates its production layout. No journal reviewer-response document existed in the supplied release, so none was invented; independent-review responses remain author records. The existing GitHub repository is updated under journal/Neural_Networks_Submission_R8/. The original R7 folder and all trained evidence remain unchanged.

The direct Neural Networks author-guide page returned 403 during this preparation. Official Elsevier submission guidance was inspected; current portal file categories and author attestations must be checked when completing the transfer. The complete numerical supplement should accompany submission. The publisher's transfer/submission workflow has not been performed here.

Official guide attempted: https://www.sciencedirect.com/journal/neural-networks/publish/guide-for-authors
Official general file guidance: https://www.elsevier.support/publishing/answer/how-do-i-prepare-my-files-for-submission-in-editorial-manager
