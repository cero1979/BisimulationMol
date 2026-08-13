# JBCB Editorial Manager upload order

Upload only `submission_jbcb/JBCB_EditorialManager.zip` as the initial
`Manuscript` item. Editorial Manager will unpack the ten root-level files.

Assign item types and order as follows:

| Order | File | Item type | Description |
|---:|---|---|---|
| 1 | `main_jbcb.tex` | Manuscript | Main manuscript source |
| 2 | `bibliography_jbcb.bbl` | Manuscript | Precompiled bibliography |
| 3 | `references_jbcb.bib` | Manuscript | BibTeX source database |
| 4 | `ws-jbcb.cls` | Manuscript | Official JBCB class |
| 5 | `ws-jbcb.bst` | Manuscript | Official JBCB bibliography style |
| 6 | `Fig1.pdf` | Figure | Figure 1 |
| 7 | `Fig3.pdf` | Figure | Figure 2 |
| 8 | `Fig8.pdf` | Figure | Figure 3 |
| 9 | `Fig2a.pdf` | Figure | Figure 4(a) |
| 10 | `Fig2b.pdf` | Figure | Figure 4(b) |

Do not assign any source file as Supplemental Material. Tables are embedded in
`main_jbcb.tex`, so no separate Table item is required. Do not upload
`main_jbcb.pdf`; it is a local preview and Editorial Manager warns against a PDF
and primary TeX source with the same basename.

After assigning types and order, rebuild the PDF and inspect all pages before
approval. Cross-references must contain numbers rather than `??`, all four
figures and four tables must be present, and the reference list must contain 21
entries.
