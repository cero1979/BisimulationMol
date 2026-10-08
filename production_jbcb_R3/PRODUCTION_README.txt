JBCB-1505R3 - Production files
Author: Carlos Ramirez Ovalle

Main manuscript: main_jbcb_R3.tex
Compiled manuscript: main_jbcb_R3.pdf
Manuscript title (matching the acceptance email):
Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models

Supplement: Supplementary_Validation_R3.tex and Supplementary_Validation_R3.pdf
Class for both documents: ws-jbcb.cls
Main artwork: R3_Fig1.pdf, R3_Fig2.pdf, R3_Fig3.pdf, R3_Fig4.pdf
Supplementary artwork: R3_SFig1.pdf, R3_SFig2.pdf
Author biography: author_biography.txt

The archive is flat: keep all files together in one directory.
Compile each master with pdfLaTeX three times to resolve cross-references:

pdflatex -interaction=nonstopmode -halt-on-error main_jbcb_R3.tex
pdflatex -interaction=nonstopmode -halt-on-error Supplementary_Validation_R3.tex

Both bibliographies are embedded in their respective TeX files. No external
.bib, .bst or BibTeX run is required. The PDF figures are supplied in their
original format, without conversion to JPEG. A PDF-capable TeX engine and
the standard packages named in the sources are required.

The scientific text and artwork are unchanged from the current R3 sources.
The main manuscript, supplement and PDF metadata use the full manuscript
title from the acceptance email.
No author photograph is included; the acceptance email marks it optional.
This is a production package, not a choice of Open Access publication.

Biography source supplied by the author:
https://perfilesycapacidades.javeriana.edu.co/es/persons/carlosovalle/
